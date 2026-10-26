# MR Report Generation: Medical Image Insights & FDU

Method and inference-code documentation for the Medical Image Insights & FDU MR report-generation submission to the VLM3D Challenge.

> This repository contains source code and experiment documentation only. It does not redistribute MR-RATE images, patient reports, model checkpoints, or the submitted Docker image.

## Submission Snapshot

- Model: Qwen3.5-4B with LoRA fine-tuning; the submitted artifact was the merged model checkpoint identified as `checkpoint-4825`.
- Training: 5-epoch run initialized from an earlier SFT checkpoint (`checkpoint-1930`); see [`configs/qwen35_lora_ep5.yaml`](configs/qwen35_lora_ep5.yaml) for the recorded settings and lineage.
- Inference: NIfTI input, T1w/T2w/FLAIR channels, vLLM generation with batch size 4, and parallel CPU preprocessing.
- Image selection: select a shared acquisition plane where available, prefer axial among equally available planes, and apply the brain-coverage / filename ranking implemented in [`docker/src/preprocessing.py`](docker/src/preprocessing.py).
- Runtime contract: read studies from `/input`, write `/output/predictions.json`, and maintain restart state under `/checkpoint`.
- Training data: 61,744 records from the MR-RATE `1:4-clean` CoT training set, as recorded for this run. Dataset files and patient-level information are not redistributed.
- Public weight status: unavailable. The final checkpoint was reported as not available in the accompanying questionnaire; this repository does not offer a download or access-request process. See [`docs/MODEL_WEIGHTS.md`](docs/MODEL_WEIGHTS.md).
- Official challenge metrics and submission status: see the MR Report Generation leaderboard on the [Forithmus Research Hub](https://research.forithmus.com/) and search for team `Medical Image Insights & FDU`; details are in [`docs/RESULTS.md`](docs/RESULTS.md).

The submission-time image used a private prebuilt runtime base. It enabled the vLLM async engine, but did not use the later experimental asynchronous batch-orchestration pipeline (`MRRATE_ASYNC_INFER=1`); that later variant is intentionally not included in this submission snapshot. The source directory is the best match to the submission package by file timestamps, but the archived image has no build manifest tying its layers cryptographically to this source snapshot. Treat it as a reconstructed submission-time source snapshot, not a verified byte-for-byte build record.

## Team and Contact

- Team: Medical Image Insights & FDU.
- Repository contact: use GitHub Issues for documentation or code questions. Do not post patient data, private reports, credentials, or requests for restricted model files.

## Repository Layout

- `docker/src/`: inference, study I/O, NIfTI preprocessing, model adapter, and output/checkpoint handling.
- `docker/entrypoint.sh`: offline container entry point.
- `docker/Dockerfile.submission.template`: Dockerfile template requiring a compatible local runtime base image.
- `docker/requirements.txt`: supplemental pinned Python dependencies used by the build.
- `configs/`: sanitized training and inference configuration summaries; paths to private data are omitted.
- `docs/`: method, weight availability, and evaluation documentation.

## Data and Weight Access

MR-RATE data and the final model weights are not included. The questionnaire reports the weights as unavailable; this repository does not provide a public download or access route. Do not add data, patient reports, credentials, registry tokens, or model files to this repository. See [`docs/MODEL_WEIGHTS.md`](docs/MODEL_WEIGHTS.md) for the artifact identity and availability statement.

## Evaluation Results

Official leaderboard metrics and the current submission status are maintained by the challenge platform. See [`docs/RESULTS.md`](docs/RESULTS.md) for where to find the team's entry. No local test-set metric is presented as an official result.

## Reproduction Notes

The Docker source expects a compatible environment with the versions in `docker/requirements.txt` and the matching ms-swift/vLLM multimodal runtime. The original base image was an internal image and is not published here. Therefore, the Dockerfile is a build template, not a claim that this repository alone reproduces the submitted binary image.

## License

No license is granted by this repository. Reuse or redistribution is not authorized unless the authors add a license after reviewing code, base-model, and dataset terms.
