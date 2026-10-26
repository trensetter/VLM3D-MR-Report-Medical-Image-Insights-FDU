# Method

## Task

Given a brain MR study, generate a structured finding section followed by a free-text radiology report. The model receives the study and an instruction; ground-truth disease labels are not passed in as inference input.

## Training Target

The SFT target uses two consecutive sections:

1. `<finding>` contains a JSON list. Each finding records a diagnosis label, anatomy, and a short imaging description.
2. `<report>` contains the free-text report.

The training data was the MR-RATE `1:4-clean` CoT training set, recorded as 61,744 records for this run. The checkpoint metadata records a five-epoch LoRA run initialized from an earlier SFT checkpoint. Source data, patient reports, and patient-level identifiers remain private and are not redistributed here. The reported data count describes training records, not a claim about the size of the full MR-RATE collection.

## Model and Optimization

- Base model: Qwen3.5-4B.
- Fine-tuning: LoRA, rank 64, alpha 128, RS-LoRA, `all-linear` targets.
- Recorded run: 5 epochs, learning rate `5e-5`, maximum sequence length 81920, per-device batch size 4, gradient accumulation 4, DeepSpeed ZeRO-2, BF16, FlashAttention 2.
- Initialization lineage: an earlier SFT checkpoint identified as `checkpoint-1930`; the submitted merged artifact is identified as `checkpoint-4825`.

This describes the recorded run configuration. Effective global batch size depends on the training world size and is therefore not inferred here.

## Inference Preprocessing

- The container accepts one study ZIP per case and processes studies lazily in scratch space; extracted files are removed after processing.
- It identifies T1w, T2w, and FLAIR NIfTI series, chooses a shared acquisition plane when possible, and ranks candidates using filename/plane and brain-coverage checks.
- The selected volumes are resampled to a common `256 x 256 x 192` tensor, normalized channel-wise, and arranged as video frames for the Qwen multimodal processor.
- CPU preprocessing is pipelined with inference using a worker pool and bounded prefetch. Generation uses the vLLM engine with an inference batch size of 4.

See `docker/src/preprocessing.py`, `docker/src/qwen35_nifti_template.py`, and `docker/src/model_runner.py` for the implementation. The submitted image enabled vLLM's async engine, but generation was orchestrated through the submission-time batch pipeline. This source snapshot does not include the later experimental `MRRATE_ASYNC_INFER=1` batch-orchestration code. The match to the archived submission image is based on file chronology, not a recorded source commit or image build attestation.

## Output and Restartability

The model response contains `<finding>` and `<report>` sections. The container extracts the report body and writes exactly one entry per study to `/output/predictions.json`. Completed results are appended to `/checkpoint`, allowing a restarted container to skip already-completed studies.

The challenge's report-generation score is computed by the platform. Local label extraction from the structured finding section is not the official report-to-label extraction pipeline and must not be described as the official CRG score.

## Availability and Reproducibility

The final checkpoint (`checkpoint-4825`) is not publicly available; the authors marked weights unavailable/restricted in the challenge questionnaire. This repository contains neither the checkpoint nor the submitted Docker image. The original runtime base was private, and the archived image is not cryptographically tied to this source snapshot, so this repository documents the method and a reconstructed inference-code snapshot rather than a fully reproducible binary build.
