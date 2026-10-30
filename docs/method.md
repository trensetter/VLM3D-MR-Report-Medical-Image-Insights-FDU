# Method

## Task

Given a brain MR study, generate a structured finding section followed by a free-text radiology report. The model receives the study and an instruction; ground-truth disease labels are not passed in as inference input.

## Training Target

The SFT target uses two consecutive sections:

1. `<finding>` contains a JSON list. Each finding records a diagnosis label, anatomy, and a short imaging description.
2. `<report>` contains the free-text report.

The training data was the MR-RATE `1:4-clean` CoT training set, recorded as 61,744 records for this run. The checkpoint metadata records a five-epoch LoRA run initialized from an earlier SFT checkpoint. Source data, patient reports, and patient-level identifiers remain private and are not redistributed here. The reported data count describes training records, not a claim about the size of the full MR-RATE collection.

## Model and Optimization

- Base model: [`Qwen/Qwen3.5-4B`](https://huggingface.co/Qwen/Qwen3.5-4B); the model card lists Apache-2.0.
- Fine-tuning: LoRA, rank 64, alpha 128, RS-LoRA, `all-linear` targets.
- Recorded run: 5 epochs, learning rate `5e-5`, maximum sequence length 81920, per-device batch size 4, gradient accumulation 4, DeepSpeed ZeRO-2, BF16, FlashAttention 2.
- Initialization lineage: an earlier SFT checkpoint identified as `checkpoint-1930`; the submitted merged artifact is identified as `checkpoint-4825`.

This describes the recorded run configuration. Effective global batch size depends on the training world size and is therefore not inferred here.

## Inference Preprocessing

- `/input` contains one un-extracted study ZIP per case. The program extracts and preprocesses studies sequentially in local scratch, removes each extracted ZIP tree, and keeps up to four preprocessed study tensors for a generation batch. In the organizer's ZIP layout, the loader searches image directories in this order: `atlas_img`, `coreg_img`, `atlas`, then `img`; platform logs for this submission show it selected files from `atlas/`.
- It searches for T1w, T2w, and FLAIR NIfTI series. It chooses the plane present in the largest number of modalities (preferring axial on ties), then selects a series matching that plane when available. Filename suffix and, when multiple candidates exist, brain-mask coverage participate in candidate selection. T1 selection prefers a filename without `_coreg_`; this preference is not applied to T2w/FLAIR.
- Selected volumes are resampled to `256 x 256 x 192`; missing modalities are zero-filled. A custom Qwen template applies foreground-aware per-channel Z-score scaling to `[0,255]` and arranges the depth axis as video frames. This is a video-like multimodal representation, not a temporal MRI acquisition.
- Inference uses ms-swift's `TransformersEngine`, BF16, `device_map=cuda:0`, SDPA, inference batch size 4, `temperature=0`, and maximum 2,048 new tokens. The submitted version did **not** use vLLM or parallel preprocessing workers.
- The prompt asks for structured findings followed by a free-text report, but post-processing writes only the report body to the platform output.
- Runtime network access is not required; the entrypoint sets `TRANSFORMERS_OFFLINE=1` and `HF_HUB_OFFLINE=1`.

See `docker/src/preprocessing.py`, `docker/src/qwen35_nifti_template.py`, and `docker/src/model_runner.py` for the implementation. The source files were synchronized from the local build context associated with the submitted batch-4 Transformers image. The platform log independently confirms the TransformersEngine runtime. There is no signed provenance record binding the uploaded image digest to a Git commit, so this repository does not claim a cryptographic source-to-image attestation.

## Output and Restartability

The model response contains `<finding>` and `<report>` sections. The container extracts the report body and writes exactly one entry per study to `/output/predictions.json`. Completed results are appended to `/checkpoint`, allowing a restarted container to skip already-completed studies.

The organizer's MR contract is documented in the [official reference container](https://github.com/forithmus/VLM3D-Dockers/tree/main/mr_challenges/reportgen_example_docker): study ZIPs are mounted at `/input`, and the expected output is a flat `predictions.json` containing `generated_reports` with `<STUDY>.nii.gz` identifiers. The challenge's report-generation score is computed by the platform. Local label extraction from the structured finding section is not the official report-to-label extraction pipeline and must not be described as the official CRG score.

## Availability and Reproducibility

The final checkpoint (`checkpoint-4825`) is not publicly available; the authors marked weights unavailable/restricted in the challenge questionnaire. This repository contains neither the checkpoint nor the submitted Docker image. The original runtime base was private. The image and weight archive digests are documented in [`SUBMISSION_ARTIFACTS.md`](SUBMISSION_ARTIFACTS.md), but the image is not attested to a public source commit and a clean build cannot be reproduced without the private base and weights.

The training data originated from the [official MR-RATE project](https://github.com/forithmus/MR-RATE) and its [dataset repository](https://huggingface.co/datasets/Forithmus/MR-RATE-atlas). The upstream project states that its datasets and model weights are licensed CC BY-NC-SA 4.0. This repository does not redistribute those materials or grant rights beyond their upstream terms.
