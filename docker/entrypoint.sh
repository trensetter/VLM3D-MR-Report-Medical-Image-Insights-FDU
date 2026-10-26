#!/bin/sh
set -eu

export TRANSFORMERS_OFFLINE=1
export HF_HUB_OFFLINE=1
export PYTHONUNBUFFERED=1

echo "Starting MR-RATE Qwen3.5 LoRA ep5 merged NIfTI submission"
echo "Input: /input"
echo "Output: /output"
echo "Checkpoint: /checkpoint"
echo "Weights: ${FORITHMUS_WEIGHTS_DIR:-/weights}"

exec python /opt/app/src/main.py
