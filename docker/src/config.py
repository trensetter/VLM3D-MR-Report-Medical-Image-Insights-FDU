import os
from pathlib import Path


INPUT_DIR = Path(os.environ.get("FORITHMUS_INPUT_DIR", "/input"))
OUTPUT_DIR = Path(os.environ.get("FORITHMUS_OUTPUT_DIR", "/output"))
CHECKPOINT_DIR = Path(os.environ.get("FORITHMUS_CHECKPOINT_DIR", "/checkpoint"))
SCRATCH_DIR = Path(os.environ.get("MRRATE_SCRATCH_DIR", "/tmp/mrrate_work"))

WEIGHTS_DIR = Path(os.environ.get("FORITHMUS_WEIGHTS_DIR", "/weights"))
MODEL_DIR = Path(os.environ.get("MRRATE_MODEL_DIR", str(WEIGHTS_DIR / "model")))

MODEL_TYPE = os.environ.get("MRRATE_MODEL_TYPE", "qwen3_5")
TEMPLATE_TYPE = os.environ.get("MRRATE_TEMPLATE_TYPE", "med-Qwen3-5-multi-channel-wl")
ATTN_IMPL = os.environ.get("MRRATE_ATTN_IMPL", "sdpa")
TORCH_DTYPE = os.environ.get("MRRATE_TORCH_DTYPE", "bfloat16")

MAX_NEW_TOKENS = int(os.environ.get("MRRATE_MAX_NEW_TOKENS", "2048"))
TEMPERATURE = float(os.environ.get("MRRATE_TEMPERATURE", "0"))
INFER_BATCH_SIZE = int(os.environ.get("MRRATE_INFER_BATCH_SIZE", "4"))
PREPROCESS_WORKERS = max(1, int(os.environ.get("MRRATE_PREPROCESS_WORKERS", "4")))
PREPROCESS_PREFETCH = max(1, int(os.environ.get("MRRATE_PREPROCESS_PREFETCH", str(INFER_BATCH_SIZE))))
VLLM_USE_ASYNC_ENGINE = os.environ.get("MRRATE_VLLM_USE_ASYNC_ENGINE", "1") == "1"
VLLM_GPU_MEMORY_UTILIZATION = float(os.environ.get("MRRATE_VLLM_GPU_MEMORY_UTILIZATION", "0.9"))
VLLM_MAX_MODEL_LEN = int(os.environ.get("MRRATE_VLLM_MAX_MODEL_LEN", "49152"))
VLLM_MAX_NUM_SEQS = int(os.environ.get("MRRATE_VLLM_MAX_NUM_SEQS", str(INFER_BATCH_SIZE)))
VLLM_MM_PROCESSOR_CACHE_GB = float(os.environ.get("MRRATE_VLLM_MM_PROCESSOR_CACHE_GB", "0"))
VLLM_ENFORCE_EAGER = os.environ.get("MRRATE_VLLM_ENFORCE_EAGER", "0") == "1"
VLLM_ATTENTION_BACKEND = os.environ.get("MRRATE_VLLM_ATTENTION_BACKEND", "FLASH_ATTN")
VLLM_GDN_PREFILL_BACKEND = os.environ.get("MRRATE_VLLM_GDN_PREFILL_BACKEND", "triton")
FAIL_FAST = os.environ.get("MRRATE_FAIL_FAST", "0") == "1"
SAVE_RAW_GENERATIONS = os.environ.get("MRRATE_SAVE_RAW", "0") == "1"
ALLOW_INPUT_DIRS = os.environ.get("MRRATE_ALLOW_INPUT_DIRS", "0") == "1"

TARGET_SHAPE = (256, 256, 192)
MODALITY_ORDER = ("t1w", "t2w", "flair")
SYSTEM_PROMPT = "You are a professional radiologist."
USER_PROMPT = (
    "<video>Carefully interpret the MR images.\n"
    "First, identify all findings in structured JSON inside <finding> tags. "
    "Then, write a complete radiology report inside <report> tags."
)
