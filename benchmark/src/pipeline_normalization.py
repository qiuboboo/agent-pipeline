from __future__ import annotations

import io
import math
import re
import unicodedata
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from PIL import Image

try:
    from .pipeline_utils import clamp, is_null_like_text, normalize_whitespace, to_plain_text
except ImportError:
    from pipeline_utils import clamp, is_null_like_text, normalize_whitespace, to_plain_text


class TextNormalizer:
    IMAGE_HINT_PATTERN = re.compile(
        r"\b(figure|fig\.?|diagram|graph|chart|circuit|schematic|shown in the figure|shown below|waveform|table|image)\b",
        re.IGNORECASE,
    )
    NUMERIC_PATTERN = re.compile(r"^[+-]?(?:\d+(?:\.\d+)?|\.\d+)$")
    PURE_IMAGE_INDEX_PATTERN = re.compile(r"^(diagram|graph|figure|waveform|plot|curve|option|image)\s*[A-H0-9]+$", re.IGNORECASE)
    EXAM_HEADER_PATTERNS = [
        re.compile(r"^【[^】]*(?:试题|试卷|考试|模拟|联考|月考|期中|期末|诊断|测验|练习|专题)[^】]*】\s*"),
        re.compile(r"^[\(（][^\)）]*(?:年|届|高考|中考|模拟|联考|月考|期中|期末|诊断|测试|试题|试卷|理|文)[^\)）]*[\)）]\s*"),
        re.compile(r"^(?:\d{4}\s*年[^。；，,:：]{0,40}(?:模拟|联考|月考|期中|期末|诊断|测试|试题|试卷))[:：\s]*"),
        re.compile(r"^(?:来源|出自|题源)[:：]\s*[^。；\n]+"),
    ]
    SCORE_ANNOTATION_PATTERN = re.compile(
        r"(?:^|(?<=[\s，。；;:：]))[\(（【\[]?\s*(?:本题|此题)?\s*(?:满分\s*)?\d+\s*分\s*[】\)）\]]?(?=$|[\s，。；;:：])"
    )

    def strip_exam_boilerplate(self, text: str) -> str:
        value = text.strip()
        changed = True
        while value and changed:
            changed = False
            for pattern in self.EXAM_HEADER_PATTERNS:
                updated = pattern.sub("", value, count=1).strip()
                if updated != value:
                    value = updated
                    changed = True
        value = self.SCORE_ANNOTATION_PATTERN.sub(" ", value)
        value = re.sub(r"^[\)\]】）\-—–:：\s]+", "", value)
        return normalize_whitespace(value)

    def normalize_text(self, text: Any) -> str:
        value = unicodedata.normalize("NFKC", to_plain_text(text))
        value = value.replace("\u00a0", " ")
        value = value.replace("_x000C_", "")
        value = re.sub(r"<\s*image\s*>", " ", value, flags=re.IGNORECASE)
        value = re.sub(r"\*\*Choices:\*\*", "Choices:", value, flags=re.IGNORECASE)
        value = self.strip_exam_boilerplate(value)
        return normalize_whitespace(value)

    def strip_hint(self, text: str) -> str:
        text = re.sub(r"^Hint\s*:\s.*?(?=Question\s*:)", "", text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r"Please answer[^\n]*", "", text, flags=re.IGNORECASE)
        return normalize_whitespace(text)

    def normalize_answer(self, answer: Any) -> str:
        value = self.normalize_text(answer).strip(". ")
        if not value or is_null_like_text(value):
            return ""
        if re.fullmatch(r"[A-Za-z]", value):
            return value.upper()
        if self.NUMERIC_PATTERN.fullmatch(value):
            number = float(value)
            if number.is_integer():
                return str(int(number))
            return f"{number:.6f}".rstrip("0").rstrip(".")
        return value

    def detect_language(self, text: str) -> str:
        if re.search(r"[\u4e00-\u9fff]", text):
            return "zh"
        if re.search(r"[A-Za-z]", text):
            return "en"
        return "unknown"

    def infer_answer_type(self, answer: str) -> str:
        if not answer:
            return "unknown"
        if re.fullmatch(r"[A-Z]", answer):
            return "option"
        if self.NUMERIC_PATTERN.fullmatch(answer):
            return "numeric"
        if any(sep in answer for sep in [",", ";", "，", "；"]):
            return "set"
        if len(answer.split()) <= 8:
            return "short_text"
        return "text"

    def split_question_and_choices(self, text: str) -> Tuple[str, str]:
        match = re.search(r"\bChoices?\b\s*: ?", text, flags=re.IGNORECASE)
        if not match:
            return text, ""
        return normalize_whitespace(text[: match.start()]), normalize_whitespace(text[match.end() :])

    def extract_choice_map(self, text: str) -> Dict[str, str]:
        _, choice_block = self.split_question_and_choices(text)
        if not choice_block:
            return {}
        choices: Dict[str, str] = {}
        current_key: Optional[str] = None
        current_value: List[str] = []
        for line in choice_block.splitlines():
            stripped = line.strip()
            match = re.match(r"^[\(\[]?([A-H])[\)\].:]?\s*(.*)$", stripped)
            if match:
                if current_key is not None:
                    choices[current_key] = normalize_whitespace(" ".join(current_value))
                current_key = match.group(1).upper()
                current_value = [match.group(2).strip()]
            elif current_key is not None and stripped:
                current_value.append(stripped)
        if current_key is not None:
            choices[current_key] = normalize_whitespace(" ".join(current_value))
        return choices

    def infer_requires_image(self, question_text: str, image_count: int) -> bool:
        if image_count > 0:
            return True
        if self.IMAGE_HINT_PATTERN.search(question_text):
            return True
        return bool(re.search(r"<image\d*>|imagehere", question_text, flags=re.IGNORECASE))

    def text_completeness_score(self, raw_text: str, normalized_text: str) -> float:
        if not raw_text:
            return 0.0
        length_score = clamp(min(len(normalized_text), 500) / 280.0)
        question_bonus = 0.15 if "question" in normalized_text.lower() else 0.0
        choice_penalty = -0.05 if "choices" in normalized_text.lower() else 0.0
        return round(clamp(0.55 + 0.25 * length_score + question_bonus + choice_penalty), 4)

    def is_pure_image_index_question(self, question_text: str, choices: Dict[str, str]) -> bool:
        if not choices:
            return False
        if not any(token in question_text.lower() for token in ["graph", "diagram", "waveform", "figure", "plot", "curve"]):
            return False
        return all(self.PURE_IMAGE_INDEX_PATTERN.fullmatch(value or "") for value in choices.values())

    def is_compound_answer_question(self, question_text: str, choices: Dict[str, str]) -> bool:
        if not choices:
            return False
        text = question_text.lower()
        explicit_multi_target_markers = [
            "respectively",
            "each",
            "for (a)",
            "for a",
            "for output",
            "outputs",
            "分别",
            "依次",
            "两个问题",
            "两个量",
            "多个",
            "求出",
        ]
        if any(token in text for token in explicit_multi_target_markers):
            return True
        interval_like = re.compile(r"^[\[\(\{⟨<].*[\]\)\}⟩>]$")
        coordinate_like = re.compile(r"^\s*\(?\s*[^,;]+\s*,\s*[^,;]+\s*\)?\s*$")
        for value in choices.values():
            normalized = (value or "").strip()
            if not normalized:
                continue
            if interval_like.match(normalized) or coordinate_like.match(normalized):
                continue
            if value.count(";") >= 1 or value.count("；") >= 1:
                return True
        return False


class ImageQualityAnalyzer:
    def pil_to_png_bytes(self, image: Image.Image) -> bytes:
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()

    def grayscale_array(self, image: Image.Image) -> np.ndarray:
        return np.asarray(image.convert("L"), dtype=np.float32)

    def perceptual_hash(self, image: Image.Image, size: int = 8) -> str:
        resized = image.convert("L").resize((size, size), Image.Resampling.LANCZOS)
        pixels = np.asarray(resized, dtype=np.float32)
        avg = float(pixels.mean())
        bits = "".join("1" if value >= avg else "0" for value in pixels.flatten())
        return f"{int(bits, 2):0{size * size // 4}x}"

    def laplacian_variance(self, gray: np.ndarray) -> float:
        padded = np.pad(gray, ((1, 1), (1, 1)), mode="edge")
        center = padded[1:-1, 1:-1]
        lap = padded[:-2, 1:-1] + padded[2:, 1:-1] + padded[1:-1, :-2] + padded[1:-1, 2:] - 4.0 * center
        return float(np.var(lap))

    def contrast_score(self, gray: np.ndarray) -> float:
        return float(np.std(gray))

    def noise_score(self, gray: np.ndarray) -> float:
        coarse = np.asarray(
            Image.fromarray(gray.clip(0, 255).astype(np.uint8))
            .resize((max(1, gray.shape[1] // 4), max(1, gray.shape[0] // 4)), Image.Resampling.BILINEAR)
            .resize((gray.shape[1], gray.shape[0]), Image.Resampling.BILINEAR),
            dtype=np.float32,
        )
        return float(np.std(gray - coarse))

    def detect_content_bbox(self, gray: np.ndarray) -> Optional[Dict[str, int]]:
        mask = (gray / 255.0) < 0.97
        if mask.sum() == 0:
            return None
        ys, xs = np.where(mask)
        x1, x2 = int(xs.min()), int(xs.max())
        y1, y2 = int(ys.min()), int(ys.max())
        return {"x": x1, "y": y1, "width": int(x2 - x1 + 1), "height": int(y2 - y1 + 1)}

    def crop_integrity_score(self, bbox: Optional[Dict[str, int]], width: int, height: int) -> float:
        if bbox is None:
            return 0.0
        coverage_x = bbox["width"] / max(width, 1)
        coverage_y = bbox["height"] / max(height, 1)
        if coverage_x >= 0.96 and coverage_y >= 0.96:
            return 1.0
        margins = [bbox["x"], bbox["y"], width - (bbox["x"] + bbox["width"]), height - (bbox["y"] + bbox["height"])]
        clipped_edges = sum(margin <= 1 for margin in margins)
        return round(clamp(1.0 - 0.22 * clipped_edges), 4)

    def readability_score(self, blur_score: float, contrast_score: float, width: int, height: int, crop_integrity: float) -> float:
        sharpness = clamp(math.log1p(max(blur_score, 0.0)) / 8.0)
        contrast = clamp(contrast_score / 64.0)
        resolution = clamp(min(width / 512.0, height / 512.0))
        return round(clamp(0.4 * sharpness + 0.25 * contrast + 0.2 * resolution + 0.15 * crop_integrity), 4)

    def analyze(self, image: Image.Image) -> Dict[str, Any]:
        rgb = image.convert("RGB")
        gray = self.grayscale_array(rgb)
        width, height = rgb.size
        blur_score = self.laplacian_variance(gray)
        contrast = self.contrast_score(gray)
        noise = self.noise_score(gray)
        bbox = self.detect_content_bbox(gray)
        crop_integrity = self.crop_integrity_score(bbox, width, height)
        readability = self.readability_score(blur_score, contrast, width, height, crop_integrity)
        return {
            "width": width,
            "height": height,
            "blur_score": round(blur_score, 4),
            "contrast_score": round(contrast, 4),
            "noise_score": round(noise, 4),
            "readability_score": readability,
            "crop_integrity_score": crop_integrity,
            "roi_bbox": bbox,
            "perceptual_hash": self.perceptual_hash(rgb),
        }


def resolve_multiple_choice_answer_text(answer_text: str, choice_map: Dict[str, str], answer_index_base: Optional[int] = None) -> str:
    answer = normalize_whitespace(answer_text)
    if not answer:
        return ""
    upper = answer.upper().strip()
    letter_match = re.fullmatch(r"\(?([A-Z])\)?", upper)
    if letter_match:
        key = letter_match.group(1)
        if key in choice_map:
            return normalize_whitespace(choice_map[key])
    if choice_map and answer_index_base is not None:
        numeric_match = re.fullmatch(r"[+-]?\d+", answer)
        if numeric_match:
            try:
                index = int(answer) - answer_index_base
                labels = sorted(choice_map.keys())
                if 0 <= index < len(labels):
                    return normalize_whitespace(choice_map[labels[index]])
            except ValueError:
                pass
    return answer
