# MR Report Generation: Medical Image Insights & FDU

This repository documents the **Qwen3.5-4B LoRA ep5** artifact submitted to the Forithmus MR Report Generation track. It includes the submitted inference-source snapshot, a sanitized training configuration, a Docker build template, artifact identifiers, and disclosures about weights and platform status.

> **Submission status:** the last known platform record for this artifact is `failed`; no official score or rank was returned for that run. The platform leaderboard is authoritative for any later team result. See [`docs/RESULTS.md`](docs/RESULTS.md).

## Submitted Artifact

- Model: Qwen3.5-4B, LoRA fine-tuned for five epochs; merged model checkpoint `checkpoint-4825`, initialized from SFT checkpoint `checkpoint-1930`.
- Base model ID: [`Qwen/Qwen3.5-4B`](https://huggingface.co/Qwen/Qwen3.5-4B) (model card lists Apache-2.0).
- Training data: the 61,744-record MR-RATE `1:4-clean` CoT training set. The model receives images and an instruction at inference, not ground-truth disease labels.
- Inference: T1w/T2w/FLAIR NIfTI inputs, common-plane selection, ms-swift `TransformersEngine` (not vLLM), SDPA, sequential per-study preprocessing, inference batch size 4, temperature 0, maximum 2,048 new tokens.
- Submitted container image tag: `mrrate-qwen35-lora-ep5-nifti:batch4-test-20260829`.
- Model weights were shipped separately from the container image to the platform. They are **not publicly available** and are not included here.
- The platform log recorded 2,029 study inputs. The submission's last known status is failed; this does not establish that all 2,029 predictions were completed.
- Exact artifact sizes, SHA-256 digests, platform submission identifier, known status, and compliance notes: [`docs/SUBMISSION_ARTIFACTS.md`](docs/SUBMISSION_ARTIFACTS.md).

## Track Contract

The container reads one study ZIP per input under `/input`, lazily extracts each study, and writes one flat `/output/predictions.json` with one report per study. The generated `<finding>` section is removed; only the free-text `<report>` body is emitted. Completed studies are checkpointed under `/checkpoint` for restartability. The public Docker template enables fail-fast on inference errors; the historical submitted image did not explicitly enable that behavior, as described in [`docs/SUBMISSION_ARTIFACTS.md`](docs/SUBMISSION_ARTIFACTS.md).

See the official [MR report-generation example Docker](https://github.com/forithmus/VLM3D-Dockers/tree/main/mr_challenges/reportgen_example_docker) and [VLM3D-Dockers submission guide](https://github.com/forithmus/VLM3D-Dockers/blob/main/README.md) for the organizer's current input, output, offline-runtime, and validation requirements.

## Repository Contents

- `docker/src/`: NIfTI/study loading, modality and acquisition-plane selection, model inference, post-processing, output writing, and checkpoint support.
- `docker/entrypoint.sh`: offline runtime entry point.
- `docker/Dockerfile.submission.template`: sanitized build template. It expects an authorized compatible base image; the original base image is private and is not redistributed.
- `docker/requirements.txt`: supplemental runtime dependencies.
- `configs/`: sanitized model/training/inference configuration; private host paths are omitted.
- `docs/`: method, weights, results, exact artifact identities, and reproduction notes.

## Model, Data, and Reproduction

MR-RATE images, patient reports, labels, base-model files, and final checkpoint files are not redistributed. The weight availability response in the challenge questionnaire was `unavailable / access restricted`; this repository provides no download or access-request route. See [`docs/MODEL_WEIGHTS.md`](docs/MODEL_WEIGHTS.md).

The data source is the [official MR-RATE repository](https://github.com/forithmus/MR-RATE) and its [Hugging Face dataset](https://huggingface.co/datasets/Forithmus/MR-RATE-atlas). The official repository states that MR-RATE datasets and model weights are under CC BY-NC-SA 4.0; users must review those terms before reuse. The base model has its own license, shown on its model card. These upstream terms are not replaced by this repository's no-license notice.

The original runtime used an internal `med-swift` base image. Consequently, this repository contains the source snapshot and a build template, but cannot independently reproduce the submitted binary without authorized access to that base image and the separate weights. The Docker archive and model weights are intentionally not stored in GitHub; their exact digests are recorded for identification. [`docs/REPRODUCTION.md`](docs/REPRODUCTION.md) lists the build/test flow and its prerequisites.

## Team and Contact

- Team: Medical Image Insights & FDU.
- Repository: [trensetter/VLM3D-MR-Report-Medical-Image-Insights-FDU](https://github.com/trensetter/VLM3D-MR-Report-Medical-Image-Insights-FDU).
- Use GitHub Issues for documentation or code questions. Do not post patient data, private reports, credentials, or requests for restricted model files.

## License

No license is granted by this repository. The upstream model, dataset, and runtime dependencies remain subject to their respective owners' terms.
