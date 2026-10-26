import json
import os
from pathlib import Path
from typing import Dict, List


def write_predictions(output_dir: Path, ordered_ids: List[str], completed: Dict[str, str]) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    reports = [{"input_image_name": input_id, "report": completed.get(input_id, "")} for input_id in ordered_ids]
    ids = [r["input_image_name"] for r in reports]
    if len(ids) != len(set(ids)):
        raise RuntimeError("Duplicate input_image_name in predictions")
    if len(reports) != len(ordered_ids):
        raise RuntimeError("Prediction count mismatch")
    payload = {"generated_reports": reports}
    tmp_path = output_dir / "predictions.json.tmp"
    final_path = output_dir / "predictions.json"
    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    with tmp_path.open("r", encoding="utf-8") as f:
        json.load(f)
    os.replace(tmp_path, final_path)
    return final_path
