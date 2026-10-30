# Model Weights

## Artifact Identity and Download

- Model: merged Qwen3.5-4B checkpoint from the five-epoch LoRA run.
- Training checkpoint: `checkpoint-4825`, initialized from SFT `checkpoint-1930`.
- Public model files: [sleepyhores/mrrate-qwen35-4b-reportgen-submission](https://huggingface.co/sleepyhores/mrrate-qwen35-4b-reportgen-submission).
- The published model files preserve the submitted tensor weights. Host-specific paths and training-only references in `args.json` were removed; the original platform `weights.zip` digest is recorded separately in [`SUBMISSION_ARTIFACTS.md`](SUBMISSION_ARTIFACTS.md).

Download the files into the directory structure expected by the container (`/weights/model`):

```bash
python -m pip install -U huggingface_hub
mkdir -p weights/model
hf download sleepyhores/mrrate-qwen35-4b-reportgen-submission \
  --local-dir weights/model
```

Verify that the model files are present:

```bash
test -f weights/model/config.json
test -f weights/model/model-00001-of-00002.safetensors
test -f weights/model/model-00002-of-00002.safetensors
test -f weights/model/model.safetensors.index.json
```

## Apply the Weights

Mount the parent `weights` directory so the model is visible inside the container at `/weights/model`:

```bash
mkdir -p input output checkpoint
docker run --rm --gpus all --network none \
  -v "$PWD/input:/input:ro" \
  -v "$PWD/output:/output" \
  -v "$PWD/checkpoint:/checkpoint" \
  -v "$PWD/weights:/weights:ro" \
  mrrate-qwen35-lora-ep5-nifti:latest
```

The input directory must contain one organizer-format study ZIP per case. The container writes `/output/predictions.json` and restart state under `/checkpoint`.

## Runtime Environment and Data

The historical competition Docker image is not publicly distributed. Its original base, `med-swift:v4-20260821-2`, is an internal image; building the provided Docker template requires authorized access to a compatible base image. The model weights alone are not a complete runnable environment. See [`REPRODUCTION.md`](REPRODUCTION.md) for build and validation prerequisites.

MR-RATE images, reports, labels, and hidden evaluation data are not included. Users must obtain permitted data access from the dataset owner and comply with the dataset and base-model terms. This repository does not grant clinical-use permission or a separate license for the checkpoint; review upstream terms before use.

Do not commit local weights, access tokens, MRI files, or reports to GitHub. See [`SUBMISSION_ARTIFACTS.md`](SUBMISSION_ARTIFACTS.md) for artifact identity and hashes.
