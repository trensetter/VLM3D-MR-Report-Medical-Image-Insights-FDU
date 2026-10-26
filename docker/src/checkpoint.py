import json
import os
from pathlib import Path
from typing import Dict


def load_completed(checkpoint_dir: Path) -> Dict[str, str]:
    path = checkpoint_dir / "completed.jsonl"
    completed: Dict[str, str] = {}
    if not path.exists():
        return completed
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            completed[row["input_image_name"]] = row.get("report", "")
    return completed


def _append_jsonl(path: Path, row: Dict[str, str]) -> None:
    line = json.dumps(row, ensure_ascii=False) + "\n"
    try:
        with path.open("a", encoding="utf-8") as f:
            f.write(line)
            f.flush()
            os.fsync(f.fileno())
        return
    except PermissionError:
        if not path.exists():
            raise

    tmp_path = path.with_name(f".{path.name}.tmp.{os.getpid()}")
    with tmp_path.open("w", encoding="utf-8") as out:
        with path.open("r", encoding="utf-8") as src:
            for old_line in src:
                out.write(old_line)
        out.write(line)
        out.flush()
        os.fsync(out.fileno())
    os.replace(tmp_path, path)


def append_completed(checkpoint_dir: Path, input_image_name: str, report: str) -> None:
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    path = checkpoint_dir / "completed.jsonl"
    _append_jsonl(path, {"input_image_name": input_image_name, "report": report})


def append_raw_generation(output_dir: Path, input_image_name: str, raw_generation: str, report: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    study_uid = input_image_name.removesuffix(".nii.gz")
    path = output_dir / "raw_generations.jsonl"
    row = {
        "study_uid": study_uid,
        "input_image_name": input_image_name,
        "pred_llm": raw_generation,
        "pred_report": report,
    }
    _append_jsonl(path, row)
