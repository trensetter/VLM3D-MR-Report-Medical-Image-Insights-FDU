import os
import shutil
import zipfile
from pathlib import Path
from typing import Iterable, List


def scan_input_zips(input_dir: Path) -> List[Path]:
    return sorted(p for p in input_dir.iterdir() if p.is_file() and p.suffix.lower() == ".zip")


def scan_input_studies(input_dir: Path, allow_dirs: bool = False) -> List[Path]:
    items = [p for p in input_dir.iterdir() if p.is_file() and p.suffix.lower() == ".zip"]
    if allow_dirs:
        items.extend(p for p in input_dir.iterdir() if p.is_dir())
    return sorted(items, key=lambda p: p.stem)


def safe_extract_zip(zip_path: Path, dst_dir: Path) -> None:
    dst_dir.mkdir(parents=True, exist_ok=True)
    root = dst_dir.resolve()
    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.infolist():
            target = (dst_dir / member.filename).resolve()
            if os.path.commonpath([str(root), str(target)]) != str(root):
                raise RuntimeError(f"Unsafe zip member path: {member.filename}")
        zf.extractall(dst_dir)


def find_study_root(extract_dir: Path) -> Path:
    children = [p for p in extract_dir.iterdir() if p.is_dir()]
    image_subdirs = ("atlas_img", "coreg_img", "atlas", "img")
    if len(children) == 1 and any((children[0] / subdir).exists() for subdir in image_subdirs):
        return children[0]
    return extract_dir


def list_nifti_files(study_root: Path) -> List[Path]:
    for subdir in ("atlas_img", "coreg_img", "atlas", "img"):
        root = study_root / subdir
        if root.exists():
            files = sorted(p for p in root.rglob("*") if p.is_file() and p.name.endswith(".nii.gz"))
            if files:
                return files
    return sorted(p for p in study_root.rglob("*") if p.is_file() and p.name.endswith(".nii.gz"))


def reset_dir(path: Path) -> None:
    shutil.rmtree(path, ignore_errors=True)
    path.mkdir(parents=True, exist_ok=True)
