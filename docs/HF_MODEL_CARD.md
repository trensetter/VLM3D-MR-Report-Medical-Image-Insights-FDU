---
base_model:
- Qwen/Qwen3.5-4B
pipeline_tag: image-text-to-text
tags:
- magnetic-resonance-imaging
- radiology-report-generation
- mr-rate
license: cc-by-nc-sa-4.0
---

# MR-RATE Qwen3.5-4B Report Generation

This repository contains the merged Qwen3.5-4B checkpoint used for the Medical Image Insights & FDU submission to the Forithmus MR Report Generation track.

## Checkpoint

- Fine-tuning: five-epoch LoRA run, merged for inference.
- Submitted checkpoint: `checkpoint-4825`, initialized from SFT `checkpoint-1930`.
- The model files are the submitted model tensors. Host-specific paths and training-only references were removed from `args.json` before public release.
- The original platform archive SHA-256 is recorded in the [GitHub artifact record](https://github.com/trensetter/VLM3D-MR-Report-Medical-Image-Insights-FDU/blob/main/docs/SUBMISSION_ARTIFACTS.md).

## Inference

The model expects the custom MR-RATE inference template and preprocessing code in the companion [GitHub repository](https://github.com/trensetter/VLM3D-MR-Report-Medical-Image-Insights-FDU). It uses T1w, T2w, and FLAIR modalities, converts the selected volumes into a video-like input, and emits a structured finding section plus a report; the challenge container outputs only the free-text report body.

Download the model files into the expected directory:

```bash
python -m pip install -U huggingface_hub
mkdir -p weights/model
hf download sleepyhores/mrrate-qwen35-4b-reportgen-submission \
  --local-dir weights/model
```

Mount the `weights` directory at `/weights` in a compatible container. The expected model path is `/weights/model`.

## Environment and Data

The historical competition Docker image and its internal `med-swift:v4-20260821-2` base image are not publicly distributed. The companion GitHub repository provides the inference source and a Docker template, but rebuilding the exact submitted environment requires authorized access to a compatible `med-swift` base. MR-RATE images and reports are not included; obtain data access from the dataset owner.

## Results and Limitations

Check the official [Forithmus MR Report Generation challenge page and leaderboard](https://research.forithmus.com/challenges/mr-report-generation) for the current score and rank of **Medical Image Insights & FDU**. The fine-tuned checkpoint is licensed under CC BY-NC-SA 4.0 for non-commercial use and is intended for research; it is not validated for clinical use. Review the base-model and dataset terms before use. The GitHub source-code license is separate and does not relicense this checkpoint.
