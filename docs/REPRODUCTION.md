# Build and Local Validation

This guide follows the organizer's current [VLM3D-Dockers README](https://github.com/forithmus/VLM3D-Dockers/blob/main/README.md) and the [MR report-generation reference container](https://github.com/forithmus/VLM3D-Dockers/tree/main/mr_challenges/reportgen_example_docker). The public template is a compliance-oriented reconstruction, not a byte-for-byte recipe for the historical image.

## Prerequisites

- Docker with NVIDIA Container Toolkit and a supported GPU.
- An authorized compatible `med-swift` runtime image. The original base `med-swift:v4-20260821-2` is private and is not published by this repository. The runtime must already include the Python/CUDA/ms-swift dependencies listed in `docker/requirements.txt`; the template does not fetch packages at build or runtime.
- The separate, authorized model-weight bundle arranged under `/weights/model`. The actual checkpoint is not publicly available, so a public clone alone cannot run model inference.
- `forithmus` CLI authentication and the `mr-report-generation` challenge context for platform-schema testing.

## Build

Set `MRRATE_BASE_IMAGE` to the exact compatible image available in your authorized registry, then build from the repository root:

```bash
export MRRATE_BASE_IMAGE='YOUR_AUTHORIZED_REGISTRY/med-swift:v4-20260821-2'
docker build \
  --build-arg MRRATE_BASE_IMAGE="$MRRATE_BASE_IMAGE" \
  -f docker/Dockerfile.submission.template \
  -t mrrate-qwen35-lora-ep5-nifti:latest .
```

The Dockerfile runs as `appuser`, enables offline Transformers/Hugging Face mode, and sets `MRRATE_FAIL_FAST=1`. The latter follows the organizer's current requirement to exit non-zero on inference errors; it is a correction to the historical submitted Dockerfile and does not alter the recorded archive checksum in [`SUBMISSION_ARTIFACTS.md`](SUBMISSION_ARTIFACTS.md). The template uses the historical non-vLLM TransformersEngine implementation.

## Generate and Test the Contract

```bash
forithmus init mr-report-generation
forithmus generate
forithmus test mrrate-qwen35-lora-ep5-nifti:latest --timeout 1200
```

The `forithmus` synthetic set checks container startup and output shape; it does not validate clinical quality. The model weights must be available at runtime. The expected report-generation output is one `/output/predictions.json` containing a `generated_reports` array, with an entry for every study.

## Package the Docker Image

```bash
docker save mrrate-qwen35-lora-ep5-nifti:latest | gzip > image.tar.gz
```

Weights are a separate platform artifact, not copied into the image or this GitHub repository. The organizer requires the files inside `weights.zip` to be at the archive root and expects the bundle to be mounted at `/weights`. The checkpoint described in this repository is unavailable, so this package step cannot be completed from a public clone.

## Platform Submission

The historical submission status is recorded as failed; do not re-submit or incur compute charges based only on this documentation. If a new submission is intentionally made, use the current CLI and challenge page, select the requested tier/time budget, pass the Docker archive and an authorized weights archive separately, and verify the output schema first. A later submission is a new platform run and does not resume the historical failed run unless the platform explicitly offers that action.
