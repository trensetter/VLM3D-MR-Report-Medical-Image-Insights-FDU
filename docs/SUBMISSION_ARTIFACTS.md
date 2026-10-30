# Submission Artifact Record

This file identifies the Qwen3.5-4B LoRA ep5 artifact that was submitted to the MR Report Generation challenge. It is intentionally separate from later local experiments.

## Platform Submission

| Field | Recorded value |
| --- | --- |
| Challenge | MR Report Generation (`mr-report-generation`) |
| Model | Qwen3.5-4B LoRA, five-epoch run |
| Initialization | SFT `checkpoint-1930` |
| Submitted checkpoint | Merged `checkpoint-4825` |
| Platform submission ID | `ebf21859-c90f-459a-907c-8e2d945b68fd` |
| Submitted image tag | `mrrate-qwen35-lora-ep5-nifti:batch4-test-20260829` |
| Image archive | `image.tar.gz`, 12,862,934,946 bytes |
| Image archive SHA-256 | `605a24856b20460bf0aa428203539e0323e5123c9047cad3ffedb8d435feb53e` |
| Weights archive | `weights.zip`, 9,098,710,899 bytes |
| Weights archive SHA-256 | `b5cf43526f50760fc15604db28bf239e8ca7cbffaef6b377f68a12b9fbd5d61d` |
| Public model files | [sleepyhores/mrrate-qwen35-4b-reportgen-submission](https://huggingface.co/sleepyhores/mrrate-qwen35-4b-reportgen-submission) |
| Public shard 1 SHA-256 | `db8f65950861a7f77a17e80530a9b8d6e981dccbf8f48d56ba56f3a7c11cfd32` |
| Public shard 2 SHA-256 | `8ff83e6ec272957e7114839e637ab79176a34e9a8ee6c85be4fd117e458b286f` |
| Submitted compute tier | `gpu-a100-40` |
| Time budget | 600 minutes |
| Runtime log | 2,029 study inputs discovered; this alone does not confirm all were completed |
| Last known status | `failed`; no official score/rank was returned |

The image and original weight-archive digests above were independently checked between the server and the author's Mac. The Hugging Face repository hosts the model files from that weights archive, with host-specific and training-only metadata removed from `args.json`; the tensor shards are unchanged. The submitted image was based on a private `med-swift:v4-20260821-2` runtime and is not publicly distributed. The archived image cannot be rebuilt from this public repository alone because the base image is private. No signed build provenance binds the image digest to this GitHub commit.

## Inference Configuration

- ms-swift `TransformersEngine`, `device_map=cuda:0`, inference batch size 4; study preprocessing was sequential (not a worker pool).
- SDPA attention; BF16; no vLLM settings were active in this submitted image.
- `temperature=0`, `max_new_tokens=2048`.
- Input modalities: T1w, T2w, FLAIR; the plane present in the most modalities is selected, with axial preferred on ties. Platform logs show atlas-space series were selected.
- Output: report body only, one item per study, in the MR track's flat `predictions.json` schema.
- Runtime is offline; model weights are provided separately to the platform under `/weights`.

## Official Contract Checklist

- **Input:** one study ZIP per case under `/input`; extract and process one study at a time.
- **Output:** `/output/predictions.json` with `{"generated_reports": [{"input_image_name": "<STUDY>.nii.gz", "report": "..."}]}`.
- **Weights:** separate `weights.zip` was mounted at `/weights` for the platform run. The public merged model files are hosted on Hugging Face, not in this GitHub repository; see [`MODEL_WEIGHTS.md`](MODEL_WEIGHTS.md).
- **Offline:** `TRANSFORMERS_OFFLINE=1` and `HF_HUB_OFFLINE=1` are set by the entrypoint.
- **Non-root image user:** the Dockerfile declares `USER appuser`.
- **Restartability:** completed studies are recorded under `/checkpoint`.
- **Failure behavior:** the historical config defaulted `MRRATE_FAIL_FAST` to `0`; per-study failures could be converted to empty reports and the program could continue. This does not meet the organizer's current fail-loud checklist. The public Docker template sets `MRRATE_FAIL_FAST=1`; that is a documented correction, not a claim about the historical image.
- **Submission checklist status:** the historical Docker declared a non-root `appuser`, ran offline, used the separate weight mount, produced the flat MR output schema, and wrote restart state. Its failure-handling default was a known gap against the current checklist. The archive was 12.86 GB decimal, below the organizer's documented 15 GB compressed-image limit.

## Later Candidate Not Represented Here

A separate vLLM image candidate was built later and locally tested; it is not the image identified by the submission record above. A still later `checkpoint-2162` package was prepared under the `allsplits ep8 A-decoding` experiment, with a dataset identifier containing `plus_val_test_all`. Neither is represented here as the official submitted artifact or as approved for the hidden evaluation split. Do not conflate these candidates with submission `ebf21859-c90f-459a-907c-8e2d945b68fd`.

## Source of Truth

Platform status and official metrics can change. Check the [Forithmus Research Hub](https://research.forithmus.com/) and search the MR Report Generation leaderboard for **Medical Image Insights & FDU**. The status above is the last known record supplied for this specific artifact.
