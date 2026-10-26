from typing import List, Literal

import torch

from swift.template import register_template
from swift.template.template_inputs import StdTemplateInputs
from swift.template.templates.qwen import Qwen3_5Template, QwenTemplateMeta
from swift.template.utils import Context


FPS = 2


def mr_normalize_z_to_255(vol: torch.Tensor, ignore_background: bool = True, eps: float = 1e-8) -> torch.Tensor:
    if vol.dim() == 3:
        vol = vol.unsqueeze(0)
    vol = torch.nan_to_num(vol.float(), nan=0.0, posinf=0.0, neginf=0.0)
    out_list = []
    for c in range(vol.shape[0]):
        x = vol[c]
        if not x.any():
            x = torch.ones_like(x)
        if ignore_background:
            mask = x > eps
            x_valid = x[mask] if mask.any() else x.reshape(-1)
        else:
            x_valid = x.reshape(-1)
        if x_valid.numel() == 0:
            out_list.append(torch.zeros_like(x))
            continue
        mu = x_valid.mean()
        sigma = x_valid.std()
        if (not torch.isfinite(mu)) or (not torch.isfinite(sigma)) or sigma < eps:
            mu = torch.nan_to_num(x.mean(), nan=0.0, posinf=0.0, neginf=0.0)
            sigma = torch.nan_to_num(x.std(), nan=1.0, posinf=1.0, neginf=1.0)
            if (not torch.isfinite(sigma)) or sigma < eps:
                sigma = torch.ones_like(mu)
        x_z = (x - mu) / (sigma + eps)
        x_min = x_z.min()
        x_max = x_z.max()
        x_01 = (x_z - x_min) / (x_max - x_min + eps)
        out_list.append(torch.nan_to_num(x_01 * 255.0, nan=0.0, posinf=255.0, neginf=0.0))
    return torch.stack(out_list, dim=0)


def to_qwen_video(video: torch.Tensor) -> torch.Tensor:
    if not isinstance(video, torch.Tensor):
        raise TypeError(f"Expected torch.Tensor video, got {type(video)!r}")
    if video.dim() != 4:
        raise ValueError(f"Expected 4D video tensor, got shape={tuple(video.shape)}")
    if video.shape[0] in (3, 5):
        video = video[:3]
        video = mr_normalize_z_to_255(video, ignore_background=True)
        return video.permute(3, 0, 2, 1).contiguous()
    if video.shape[1] == 3:
        return video.contiguous()
    raise ValueError(f"Unsupported video tensor shape={tuple(video.shape)}")


class MedQwen35NiftiTemplate(Qwen3_5Template):
    version = "med-v3.5"
    norm_bbox = "none"

    def replace_tag(
        self,
        media_type: Literal["image", "video", "audio"],
        index: int,
        inputs: StdTemplateInputs,
    ) -> List[Context]:
        from qwen_vl_utils import fetch_image

        assert media_type in {"image", "video"}
        kwargs = {"image_patch_size": self.processor.image_processor.patch_size}

        if media_type == "image":
            inputs.images[index] = fetch_image({"image": inputs.images[index]}, **kwargs)
            if self.mode == "lmdeploy":
                return ["<|vision_start|>", [-100], "<|vision_end|>"]
            return ["<|vision_start|><|image_pad|><|vision_end|>"]

        video = to_qwen_video(inputs.videos[index])
        video_metadata = {
            "fps": FPS,
            "frames_indices": list(range(len(video))),
            "total_num_frames": len(video),
        }

        if self.mode == "vllm":
            inputs.videos[index] = video, video_metadata
            return ["<|vision_start|><|video_pad|><|vision_end|>"]

        inputs.mm_processor_kwargs.setdefault("video_metadata", []).append(video_metadata)
        inputs.mm_processor_kwargs["do_sample_frames"] = False
        inputs.videos[index] = video
        return ["<|video_pad|>"]

    def prepare_generate_kwargs(self, generate_kwargs: dict, *, model=None):
        for name in ["data", "source"]:
            generate_kwargs.pop(name, None)
        return generate_kwargs


register_template(QwenTemplateMeta(
    template_type="med-Qwen3-5-multi-channel-wl",
    template_cls=MedQwen35NiftiTemplate,
))
