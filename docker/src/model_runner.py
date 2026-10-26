import os
from typing import List

os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

import torch

import qwen35_nifti_template  # noqa: F401
from config import (
    INFER_BATCH_SIZE,
    MAX_NEW_TOKENS,
    MODEL_DIR,
    MODEL_TYPE,
    SYSTEM_PROMPT,
    TEMPLATE_TYPE,
    TEMPERATURE,
    TORCH_DTYPE,
    USER_PROMPT,
    VLLM_ATTENTION_BACKEND,
    VLLM_ENFORCE_EAGER,
    VLLM_GDN_PREFILL_BACKEND,
    VLLM_GPU_MEMORY_UTILIZATION,
    VLLM_MAX_MODEL_LEN,
    VLLM_MAX_NUM_SEQS,
    VLLM_MM_PROCESSOR_CACHE_GB,
    VLLM_USE_ASYNC_ENGINE,
)
from swift.infer_engine import InferRequest, RequestConfig, VllmEngine


def _dtype(name: str):
    if name == "bfloat16":
        return torch.bfloat16
    if name == "float16":
        return torch.float16
    if name == "float32":
        return torch.float32
    return None


class ReportGenerator:
    def __init__(self):
        if not MODEL_DIR.exists():
            raise FileNotFoundError(f"Model directory not found: {MODEL_DIR}")
        print(f"Loading vLLM model from {MODEL_DIR}", flush=True)
        print(
            "vLLM config: "
            f"batch={INFER_BATCH_SIZE}, max_num_seqs={VLLM_MAX_NUM_SEQS}, "
            f"max_model_len={VLLM_MAX_MODEL_LEN}, "
            f"gpu_memory_utilization={VLLM_GPU_MEMORY_UTILIZATION}, "
            f"attention_backend={VLLM_ATTENTION_BACKEND}, "
            f"gdn_prefill_backend={VLLM_GDN_PREFILL_BACKEND}",
            flush=True,
        )
        self.engine = VllmEngine(
            model_id_or_path=str(MODEL_DIR),
            model_type=MODEL_TYPE,
            template_type=TEMPLATE_TYPE,
            torch_dtype=_dtype(TORCH_DTYPE),
            use_hf=True,
            use_async_engine=VLLM_USE_ASYNC_ENGINE,
            gpu_memory_utilization=VLLM_GPU_MEMORY_UTILIZATION,
            max_model_len=VLLM_MAX_MODEL_LEN,
            max_num_seqs=VLLM_MAX_NUM_SEQS,
            limit_mm_per_prompt={"video": 1},
            mm_processor_cache_gb=VLLM_MM_PROCESSOR_CACHE_GB,
            enforce_eager=VLLM_ENFORCE_EAGER,
            enable_lora=False,
            engine_kwargs={
                "attention_backend": VLLM_ATTENTION_BACKEND,
                "gdn_prefill_backend": VLLM_GDN_PREFILL_BACKEND,
            },
        )
        self.request_config = RequestConfig(
            max_tokens=MAX_NEW_TOKENS,
            temperature=TEMPERATURE,
            stop=["<|im_end|>", "<|im_start|>user", "<|im_start|>assistant"],
        )
        print("vLLM model loaded", flush=True)

    def generate(self, video: torch.Tensor) -> str:
        return self.generate_batch([video])[0]

    def generate_batch(self, videos: List[torch.Tensor]) -> List[str]:
        requests = []
        for video in videos:
            request = InferRequest(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": USER_PROMPT},
                ],
                videos=[video],
            )
            requests.append(request)
        responses = self.engine.infer(requests, self.request_config, use_tqdm=False)
        outputs = []
        for response in responses:
            if isinstance(response, Exception):
                raise response
            outputs.append(response.choices[0].message.content or "")
        return outputs
