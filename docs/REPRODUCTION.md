# Build and Local Validation

This guide follows the organizer's current [VLM3D-Dockers README](https://github.com/forithmus/VLM3D-Dockers/blob/main/README.md) and the [MR report-generation reference container](https://github.com/forithmus/VLM3D-Dockers/tree/main/mr_challenges/reportgen_example_docker). The public template is a compliance-oriented reconstruction, not a byte-for-byte recipe for the historical image.

## Prerequisites

- Docker with NVIDIA Container Toolkit and a supported GPU.
- An authorized compatible `med-swift` runtime image. The original base `med-swift:v4-20260821-2` is private and is not published by this repository. The runtime must already include the Python/CUDA/ms-swift dependencies listed in `docker/requirements.txt`; the template does not fetch packages at build or runtime.
- The publicly downloadable merged checkpoint arranged under `/weights/model`; follow [`MODEL_WEIGHTS.md`](MODEL_WEIGHTS.md).
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

The `forithmus` synthetic set checks container startup and output shape; it does not validate clinical quality. Download the model files as described in [`MODEL_WEIGHTS.md`](MODEL_WEIGHTS.md) and mount them at `/weights/model`. The expected report-generation output is one `/output/predictions.json` containing a `generated_reports` array, with an entry for every study.

## Package the Docker Image

```bash
docker save mrrate-qwen35-lora-ep5-nifti:latest | gzip > image.tar.gz
```

Weights are separate from the Docker image. For platform submission, the organizer expects a `weights.zip` whose contents are at the archive root and mounts the bundle at `/weights`. For local use, download the Hugging Face model files into `weights/model` and mount the parent directory at `/weights`. The public GitHub repository does not provide the internal `med-swift` base image needed to rebuild the exact historical container.

## Platform Submission

Before submitting, verify the current CLI and challenge requirements, select the requested tier and time budget, provide the Docker archive and an authorized weights archive, and validate the output schema. A new submission starts a new platform run; it resumes prior progress only if the platform explicitly provides a continuation option for that submission.
