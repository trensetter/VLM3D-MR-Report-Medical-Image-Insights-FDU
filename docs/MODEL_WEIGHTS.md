# Model Weights

## Artifact Identity

- Submitted model: Qwen3.5-4B LoRA, five-epoch run.
- Training checkpoint: `checkpoint-4825`, initialized from `checkpoint-1930`.
- The LoRA checkpoint was merged into a Hugging Face-compatible model directory for inference and packaged as a separate `weights.zip` for the platform.
- The archive's SHA-256 is recorded in [`SUBMISSION_ARTIFACTS.md`](SUBMISSION_ARTIFACTS.md). A digest identifies a file; it does not make that file publicly downloadable.

## Availability

The final checkpoint is **not publicly available**. The authors selected the unavailable/restricted option in the challenge questionnaire. There is no public download link or access-request process offered by this repository. This is a disclosure, not an invitation to request or redistribute the checkpoint.

The base Qwen3.5 model, MR-RATE data, patient reports, labels, LoRA adapter, and merged weights are not included. Their ownership and terms are separate; this repository does not grant redistribution rights.

## Docker Image and Weights

The platform submission used two artifacts: a Docker image archive and a separate `weights.zip`, mounted at `/weights` at runtime. Neither binary is stored in GitHub. The image archive is multi-gigabyte, and publishing it here would not be an appropriate substitute for the platform's artifact upload. The weights remain restricted as stated above.

Do not add model files, archives, patient data, or credentials to this repository. See [`SUBMISSION_ARTIFACTS.md`](SUBMISSION_ARTIFACTS.md) for the exact recorded filenames, sizes, and hashes.
