# Model Weights

## Artifact

- Submission: Qwen3.5-4B LoRA, five-epoch run.
- Final training checkpoint identifier: `checkpoint-4825`.
- The LoRA weights were merged into a Hugging Face-compatible model directory before Docker packaging.
- The run was initialized from SFT checkpoint `checkpoint-1930`.
- The recorded training and inference configuration is in [`../configs/qwen35_lora_ep5.yaml`](../configs/qwen35_lora_ep5.yaml).

## Availability

The final checkpoint is **not publicly available**. The authors selected the unavailable/restricted option for model-weight availability in the challenge questionnaire. There is no public download link and no access-request process offered by this repository. This is an availability disclosure, not an invitation to request or redistribute the checkpoint.

The checkpoint and submitted Docker image are not included in this repository. The base model and MR-RATE data are separate artifacts governed by their respective owners and terms; their status should not be inferred from the checkpoint statement above.

## Redistribution

No MR-RATE images, reports, labels, base-model files, LoRA adapters, merged weights, or API credentials are uploaded here. No external access to derived weights is provided. Do not infer permission to redistribute the base model, dataset, adapter, or merged checkpoint from this repository.
