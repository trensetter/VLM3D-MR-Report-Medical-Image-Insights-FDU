import re
import os
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import nibabel as nib
import numpy as np
import torch
from scipy.ndimage import zoom

from config import MODALITY_ORDER, TARGET_SHAPE


PLANE_ALIASES = {
    "axi": "AXIAL",
    "axial": "AXIAL",
    "tra": "AXIAL",
    "trans": "AXIAL",
    "sag": "SAGITTAL",
    "sagittal": "SAGITTAL",
    "cor": "CORONAL",
    "coronal": "CORONAL",
    "obl": "OBLIQUE",
    "oblique": "OBLIQUE",
}

PLANE_PRIORITY = ("AXIAL", "SAGITTAL", "CORONAL", "OBLIQUE")
RAW_PLANE_RE = re.compile(
    r"-raw-(axi|axial|tra|trans|sag|sagittal|cor|coronal|obl|oblique)(?:-(\d+))?\.nii\.gz$",
    re.IGNORECASE,
)
MIN_BRAIN_MASK_COVERAGE = float(os.environ.get("MRRATE_MIN_BRAIN_MASK_COVERAGE", "0.65"))
_BRAIN_MASK_CACHE: Dict[str, Optional[np.ndarray]] = {}


def _tokens(name: str) -> List[str]:
    stem = name.lower().replace(".nii.gz", "")
    return [t for t in re.split(r"[^a-z0-9]+", stem) if t]


def detect_modality(path: Path) -> Optional[str]:
    toks = _tokens(path.name)
    joined = " ".join(toks)
    if "flair" in toks or "t2flair" in toks or "t2 flair" in joined:
        return "flair"
    if "t2w" in toks or "t2" in toks:
        return "t2w"
    if "t1w" in toks or "t1" in toks:
        return "t1w"
    return None


def detect_plane(path: Path) -> Optional[str]:
    toks = _tokens(path.name)
    for tok in toks:
        if tok in PLANE_ALIASES:
            return PLANE_ALIASES[tok]
    for key, plane in PLANE_ALIASES.items():
        if f"raw-{key}" in path.name.lower() or f"_{key}" in path.name.lower():
            return plane
    return None


def _plane_priority(plane: Optional[str]) -> int:
    if plane in PLANE_PRIORITY:
        return PLANE_PRIORITY.index(plane)
    return len(PLANE_PRIORITY)


def _suffix_rank(path: Path) -> Tuple[int, int]:
    match = RAW_PLANE_RE.search(path.name)
    if not match:
        return (1, 999)
    suffix = match.group(2)
    return (1 if suffix else 0, int(suffix or 0))


def _candidate_score(path: Path, preferred_plane: Optional[str] = None, prefer_uncoreg: bool = False) -> Tuple[int, int, int, int, str]:
    plane = detect_plane(path)
    suffix_missing_rank, suffix_number = _suffix_rank(path)
    return (
        0 if preferred_plane and plane == preferred_plane else 1,
        0 if prefer_uncoreg and "_coreg_" not in path.name.lower() else 1,
        suffix_missing_rank,
        suffix_number,
        path.name,
    )


def _study_root_from_image(path: Path) -> Optional[Path]:
    if path.parent.name in {"atlas_img", "coreg_img", "img", "atlas"}:
        return path.parent.parent
    return None


def _load_brain_mask(study_root: Optional[Path]) -> Optional[np.ndarray]:
    if study_root is None:
        return None
    key = str(study_root)
    if key in _BRAIN_MASK_CACHE:
        return _BRAIN_MASK_CACHE[key]

    masks: List[Path] = []
    for mask_dir_name in ("atlas_seg", "seg"):
        mask_dir = study_root / mask_dir_name
        if mask_dir.exists():
            masks.extend(sorted(mask_dir.glob("*brain-mask.nii.gz")))
    if not masks:
        _BRAIN_MASK_CACHE[key] = None
        return None

    try:
        mask = nib.load(str(masks[0])).get_fdata(dtype=np.float32) > 0.5
    except Exception:
        mask = None
    _BRAIN_MASK_CACHE[key] = mask
    return mask


def _brain_mask_coverage(path: Path) -> Optional[float]:
    mask = _load_brain_mask(_study_root_from_image(path))
    if mask is None:
        return None
    try:
        vol = nib.load(str(path)).get_fdata(dtype=np.float32)
    except Exception:
        return None
    if vol.ndim > 3:
        vol = vol[..., 0]
    if vol.shape != mask.shape:
        return None
    vol = np.nan_to_num(vol.astype(np.float32), nan=0.0, posinf=0.0, neginf=0.0)
    nonzero = np.abs(vol) > 1e-6
    if not nonzero.any() or not mask.any():
        return 0.0
    vals = np.abs(vol[nonzero])
    threshold = max(float(np.percentile(vals, 20)), float(np.percentile(vals, 99)) * 0.01, 1e-6)
    foreground = np.abs(vol) > threshold
    if not foreground.any():
        return 0.0
    return float(np.logical_and(foreground, mask).sum() / mask.sum())


def _group_by_plane(candidates: List[Path]) -> Dict[str, List[Path]]:
    by_plane: Dict[str, List[Path]] = {}
    for path in candidates:
        plane = detect_plane(path)
        if plane:
            by_plane.setdefault(plane, []).append(path)
    return by_plane


def _pick_candidate(candidates: List[Path], preferred_plane: Optional[str] = None, prefer_uncoreg: bool = False) -> Optional[Path]:
    if not candidates:
        return None
    ranked = sorted(candidates, key=lambda path: _candidate_score(path, preferred_plane, prefer_uncoreg))
    if len(ranked) <= 1:
        return ranked[0]

    for path in ranked:
        if _load_brain_mask(_study_root_from_image(path)) is None:
            return path
        coverage = _brain_mask_coverage(path)
        if coverage is None or coverage >= MIN_BRAIN_MASK_COVERAGE:
            return path
    return ranked[0]


def _choose_shared_plane(grouped: Dict[str, List[Path]]) -> Optional[str]:
    planes = set()
    by_mod = {}
    for mod in MODALITY_ORDER:
        by_plane = _group_by_plane(grouped.get(mod, []))
        by_mod[mod] = by_plane
        planes.update(by_plane)
    if not planes:
        return None

    def score(plane: str) -> Tuple[int, int]:
        present = sum(1 for mod in MODALITY_ORDER if plane in by_mod[mod])
        return (-present, _plane_priority(plane))

    return sorted(planes, key=score)[0]


def select_modality_files(files: Iterable[Path]) -> Dict[str, Optional[Path]]:
    grouped: Dict[str, List[Path]] = {m: [] for m in MODALITY_ORDER}
    for path in files:
        mod = detect_modality(path)
        if mod in grouped:
            grouped[mod].append(path)

    shared_plane = _choose_shared_plane(grouped)

    selected: Dict[str, Optional[Path]] = {}
    selected["t1w"] = _pick_candidate(grouped["t1w"], preferred_plane=shared_plane, prefer_uncoreg=True)
    preferred_plane = shared_plane or (detect_plane(selected["t1w"]) if selected["t1w"] else None)
    selected["t2w"] = _pick_candidate(grouped["t2w"], preferred_plane=preferred_plane)
    selected["flair"] = _pick_candidate(grouped["flair"], preferred_plane=preferred_plane)
    return selected


def load_resampled_volume(path: Path, target_shape=TARGET_SHAPE) -> np.ndarray:
    vol = nib.load(str(path)).get_fdata(dtype=np.float32)
    if vol.ndim > 3:
        vol = vol[..., 0]
    if vol.ndim != 3:
        raise ValueError(f"Expected 3D NIfTI, got shape={vol.shape} for {path}")
    vol = np.nan_to_num(vol.astype(np.float32), nan=0.0, posinf=0.0, neginf=0.0)
    factors = tuple(float(t) / float(s) for t, s in zip(target_shape, vol.shape))
    out = zoom(vol, factors, order=1)
    if out.shape != target_shape:
        fixed = np.zeros(target_shape, dtype=np.float32)
        slices = tuple(slice(0, min(a, b)) for a, b in zip(out.shape, target_shape))
        fixed[slices] = out[slices]
        out = fixed
    return out.astype(np.float32, copy=False)


def load_study_tensor(nifti_files: List[Path]) -> torch.Tensor:
    selected = select_modality_files(nifti_files)
    vols = []
    missing = []
    for mod in MODALITY_ORDER:
        path = selected.get(mod)
        if path is None:
            vols.append(np.zeros(TARGET_SHAPE, dtype=np.float32))
            missing.append(mod)
        else:
            vols.append(load_resampled_volume(path))
    arr = np.stack(vols, axis=0)
    print({
        "selected_modalities": {k: str(v) if v else None for k, v in selected.items()},
        "missing_modalities": missing,
        "raw_tensor_shape": list(arr.shape),
    }, flush=True)
    return torch.from_numpy(arr)
