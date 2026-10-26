import re


REPORT_RE = re.compile(r"<report>\s*(.*?)\s*</report>", re.IGNORECASE | re.DOTALL)
REPORT_START_RE = re.compile(r"<report>\s*", re.IGNORECASE)
FINDING_RE = re.compile(r"<finding>.*?</finding>", re.IGNORECASE | re.DOTALL)

CONTROL_TOKENS = [
    "<|im_start|>",
    "<|im_end|>",
    "<|vision_start|>",
    "<|vision_end|>",
    "<|video_pad|>",
    "<finding>",
    "</finding>",
    "<report>",
    "</report>",
]

TURN_MARKERS = [
    "<|im_start|>user",
    "<|im_start|>assistant",
    "\nUser:",
    "\nuser:",
    "\nAssistant:",
    "\nassistant:",
]


def _truncate_after_answer(text: str) -> str:
    candidates = []
    end = text.lower().find("</report>")
    if end >= 0:
        candidates.append(end + len("</report>"))
    for marker in TURN_MARKERS + ["<|im_end|>"]:
        pos = text.find(marker)
        if pos >= 0:
            candidates.append(pos)
    if candidates:
        return text[: min(candidates)]
    return text


def _dedupe_consecutive_sentences(text: str) -> str:
    parts = re.split(r"(?<=[.!?。！？])\s+", text)
    kept = []
    last = None
    repeat = 0
    for part in parts:
        key = re.sub(r"\s+", " ", part.strip().lower())
        if not key:
            continue
        if key == last:
            repeat += 1
            if repeat >= 2:
                continue
        else:
            last = key
            repeat = 0
        kept.append(part.strip())
    return " ".join(kept)


def extract_report(raw_text: str, max_chars: int = 6000) -> str:
    text = _truncate_after_answer(raw_text or "").strip()
    match = REPORT_RE.search(text)
    if match:
        report = match.group(1)
    else:
        start = REPORT_START_RE.search(text)
        report = text[start.end():] if start else text
        report = FINDING_RE.sub("", report)
    for token in CONTROL_TOKENS:
        report = report.replace(token, "")
    report = re.sub(r"\s+", " ", report).strip()
    report = _dedupe_consecutive_sentences(report)
    if len(report) > max_chars:
        report = report[:max_chars].rsplit(" ", 1)[0].strip()
    return report
