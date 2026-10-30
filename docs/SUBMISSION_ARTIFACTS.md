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
| Submitted compute tier | `gpu-a100-40` |
| Time budget | 600 minutes |
| Runtime log | 2,029 study inputs discovered; this alone does not confirm all were completed |
| Last known status | `failed`; no official score/rank was returned |

The image and weight digests above were independently checked between the server and the author's Mac. They identify the historical files but are not download links. The submitted image was based on a private `med-swift:v4-20260821-2` runtime. The archived binary cannot be rebuilt from this public repository alone because the base image and checkpoint are not public. No signed build provenance binds the image digest to this GitHub commit.

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
- **Weights:** separate `weights.zip`, mounted at `/weights`; no model weights are stored in this repository.
- **Offline:** `TRANSFORMERS_OFFLINE=1` and `HF_HUB_OFFLINE=1` are set by the entrypoint.
- **Non-root image user:** the Dockerfile declares `USER appuser`.
- **Restartability:** completed studies are recorded under `/checkpoint`.
- **Failure behavior:** the historical config defaulted `MRRATE_FAIL_FAST` to `0`; per-study failures could be converted to empty reports and the program could continue. This does not meet the organizer's current fail-loud checklist. The public Docker template sets `MRRATE_FAIL_FAST=1`; that is a documented correction, not a claim about the historical image.
- **Submission checklist status:** the historical Docker declared a non-root `appuser`, ran offline, used the separate weight mount, produced the flat MR output schema, and wrote restart state. Its failure-handling default was a known gap against the current checklist. The archive was 12.86 GB decimal, below the organizer's documented 15 GB compressed-image limit.

## Later Candidate Not Represented Here

A separate vLLM image candidate was built later and locally tested; it is not the image identified by the submission record above. A still later `checkpoint-2162` package was prepared under the `allsplits ep8 A-decoding` experiment, with a dataset identifier containing `plus_val_test_all`. Neither is represented here as the official submitted artifact or as approved for the hidden evaluation split. Do not conflate these candidates with submission `ebf21859-c90f-459a-907c-8e2d945b68fd`.

## Source of Truth

Platform status and official metrics can change. Check the [Forithmus Research Hub](https://research.forithmus.com/) and search the MR Report Generation leaderboard for **Medical Image Insights & FDU**. The status above is the last known record supplied for this specific artifact.
