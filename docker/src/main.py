import shutil
import traceback
from concurrent.futures import ThreadPoolExecutor

from checkpoint import append_completed, append_raw_generation, load_completed
from config import (
    ALLOW_INPUT_DIRS,
    CHECKPOINT_DIR,
    FAIL_FAST,
    INFER_BATCH_SIZE,
    INPUT_DIR,
    OUTPUT_DIR,
    PREPROCESS_PREFETCH,
    PREPROCESS_WORKERS,
    SAVE_RAW_GENERATIONS,
    SCRATCH_DIR,
)
from model_runner import ReportGenerator
from output_writer import write_predictions
from postprocess import extract_report
from preprocessing import load_study_tensor
from study_io import find_study_root, list_nifti_files, reset_dir, safe_extract_zip, scan_input_studies


def main() -> None:
    if not INPUT_DIR.exists():
        raise FileNotFoundError(f"Input directory does not exist: {INPUT_DIR}")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    SCRATCH_DIR.mkdir(parents=True, exist_ok=True)

    input_paths = scan_input_studies(INPUT_DIR, ALLOW_INPUT_DIRS)
    ordered_ids = [f"{p.stem}.nii.gz" for p in input_paths]
    print(f"Found {len(input_paths)} study inputs", flush=True)

    completed = load_completed(CHECKPOINT_DIR)
    print(f"Loaded {len(completed)} completed checkpoint rows", flush=True)

    if not input_paths:
        final_path = write_predictions(OUTPUT_DIR, ordered_ids, completed)
        print(f"No input studies found. Saved empty predictions: {final_path}", flush=True)
        return

    pending = [p for p in input_paths if f"{p.stem}.nii.gz" not in completed]
    if not pending:
        final_path = write_predictions(OUTPUT_DIR, ordered_ids, completed)
        print(f"All {len(input_paths)} studies already completed. Saved predictions: {final_path}", flush=True)
        return

    preprocess_items = []
    for index, input_path in enumerate(input_paths, start=1):
        study_id = input_path.stem
        output_id = f"{study_id}.nii.gz"
        if output_id in completed:
            print(f"[{index}/{len(input_paths)}] skip completed {study_id}", flush=True)
            continue
        preprocess_items.append({
            "index": index,
            "input_path": input_path,
            "study_id": study_id,
            "output_id": output_id,
        })
    print(
        f"Preprocess config: workers={PREPROCESS_WORKERS}, "
        f"prefetch={PREPROCESS_PREFETCH}, pending={len(preprocess_items)}",
        flush=True,
    )

    def write_completed(output_id: str, report: str) -> None:
        completed[output_id] = report
        append_completed(CHECKPOINT_DIR, output_id, report)
        write_predictions(OUTPUT_DIR, ordered_ids, completed)

    def preprocess_one(item):
        input_path = item["input_path"]
        study_id = item["study_id"]
        work_dir = SCRATCH_DIR / study_id
        try:
            print(f"[{item['index']}/{len(input_paths)}] preprocessing {study_id}", flush=True)
            if input_path.is_file():
                reset_dir(work_dir)
                safe_extract_zip(input_path, work_dir)
                study_root = find_study_root(work_dir)
            else:
                study_root = find_study_root(input_path)
            nifti_files = list_nifti_files(study_root)
            if not nifti_files:
                raise FileNotFoundError(f"No NIfTI files found in {input_path}")
            video = load_study_tensor(nifti_files)
            return {**item, "video": video}
        finally:
            if input_path.is_file():
                shutil.rmtree(work_dir, ignore_errors=True)

    batch = []
    with ThreadPoolExecutor(max_workers=PREPROCESS_WORKERS) as executor:
        futures = {}
        next_submit = 0
        next_consume = 0

        def submit_until_full() -> None:
            nonlocal next_submit
            while next_submit < len(preprocess_items) and len(futures) < PREPROCESS_PREFETCH:
                futures[next_submit] = executor.submit(preprocess_one, preprocess_items[next_submit])
                next_submit += 1

        submit_until_full()
        generator = ReportGenerator()

        def infer_batch(items) -> None:
            if not items:
                return
            study_ids = ", ".join(item["study_id"] for item in items)
            print(f"[batch] infer {len(items)} studies: {study_ids}", flush=True)
            try:
                raws = generator.generate_batch([item["video"] for item in items])
            except Exception:
                print(f"[batch] ERROR {study_ids}", flush=True)
                traceback.print_exc()
                if FAIL_FAST:
                    raise
                raws = [""] * len(items)

            for item, raw in zip(items, raws):
                report = extract_report(raw)
                if SAVE_RAW_GENERATIONS:
                    append_raw_generation(OUTPUT_DIR, item["output_id"], raw, report)
                print(f"[{item['index']}/{len(input_paths)}] report chars={len(report)}", flush=True)
                write_completed(item["output_id"], report)

        while next_consume < len(preprocess_items):
            future = futures.pop(next_consume)
            item = preprocess_items[next_consume]
            try:
                batch.append(future.result())
            except Exception:
                print(f"[{item['index']}/{len(input_paths)}] ERROR {item['study_id']}", flush=True)
                traceback.print_exc()
                if FAIL_FAST:
                    raise
                write_completed(item["output_id"], "")
            next_consume += 1
            submit_until_full()

            if len(batch) >= INFER_BATCH_SIZE:
                infer_batch(batch)
                batch.clear()

        infer_batch(batch)

    final_path = write_predictions(OUTPUT_DIR, ordered_ids, completed)
    print(f"Saved final predictions: {final_path}", flush=True)


if __name__ == "__main__":
    main()
