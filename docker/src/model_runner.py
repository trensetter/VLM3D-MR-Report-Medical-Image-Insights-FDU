from dataclasses import asdict
from typing import List

import torch

import qwen35_nifti_template  # noqa: F401
from config import ATTN_IMPL, INFER_BATCH_SIZE, MAX_NEW_TOKENS, MODEL_DIR, MODEL_TYPE, SYSTEM_PROMPT, TEMPLATE_TYPE, TEMPERATURE, TORCH_DTYPE, USER_PROMPT
from swift.infer_engine import InferRequest, RequestConfig, TransformersEngine


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
        print(f"Loading model from {MODEL_DIR}", flush=True)
        self.engine = TransformersEngine(
            model=str(MODEL_DIR),
            model_type=MODEL_TYPE,
            template_type=TEMPLATE_TYPE,
            max_batch_size=INFER_BATCH_SIZE,
            attn_impl=ATTN_IMPL,
            torch_dtype=_dtype(TORCH_DTYPE),
            device_map="cuda:0",
            use_hf=True,
        )
        self.request_config = RequestConfig(
            max_tokens=MAX_NEW_TOKENS,
            temperature=TEMPERATURE,
            stop=["<|im_end|>", "<|im_start|>user", "<|im_start|>assistant"],
        )
        print("Model loaded", flush=True)

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
            requests.append(asdict(request))
        responses = self.engine.infer(requests, self.request_config, use_tqdm=False)
        return [response.choices[0].message.content or "" for response in responses]
