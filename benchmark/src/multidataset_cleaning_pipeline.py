#!/usr/bin/env python3
"""多数据集数据采集与清洗智能体流水线。"""

from __future__ import annotations

import csv
import hashlib
import http.client
import io
import json
import math
import os
import re
import shutil
import subprocess
import unicodedata
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
import yaml
from datasets import Dataset, DatasetDict, IterableDatasetDict, load_dataset
from PIL import Image

try:
    from .cleaning_semantics import AlignmentEngine, SolvabilityChecker, TextContextParser, VisualParser, normalize_structured_text
    from .pipeline_cleaning import finalize_cleaning_sample, rewrite_sample
    from .pipeline_collection import default_image_quality, extract_sample_structure, ingest_dataset_samples, preprocess_sample
    from .pipeline_reporting import (
        append_sample_result,
        build_source_unavailable_summary,
        finalize_dataset_report,
        init_dataset_bundle,
        write_run_summary,
        write_sample_bundle_if_needed,
    )
    from .pipeline_setup import SetupContext, build_setup_context, merge_cli_overrides, parse_args
except ImportError:
    from cleaning_semantics import AlignmentEngine, SolvabilityChecker, TextContextParser, VisualParser, normalize_structured_text
    from pipeline_cleaning import finalize_cleaning_sample, rewrite_sample
    from pipeline_collection import default_image_quality, extract_sample_structure, ingest_dataset_samples, preprocess_sample
    from pipeline_reporting import (
        append_sample_result,
        build_source_unavailable_summary,
        finalize_dataset_report,
        init_dataset_bundle,
        write_run_summary,
        write_sample_bundle_if_needed,
    )
    from pipeline_setup import SetupContext, build_setup_context, merge_cli_overrides, parse_args


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def json_default(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, bytes):
        return f"<bytes:{len(value)}>"
    if isinstance(value, Image.Image):
        return f"<PIL.Image mode={value.mode} size={value.size}>"
    raise TypeError(f"Object of type {type(value)!r} is not JSON serializable")


def write_json(path: Path, data: Any) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2, default=json_default)


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False, default=json_default))
            file.write("\n")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def stable_digest(parts: Sequence[str], length: int = 24) -> str:
    payload = "||".join(parts).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:length]


def to_plain_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, (list, tuple)):
        return "\n".join(to_plain_text(item) for item in value if to_plain_text(item))
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def normalize_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


NULL_LIKE_STRINGS = {"null", "none", "nan", "n/a", "na", "[]", "{}"}


def is_null_like_text(text: str) -> bool:
    normalized = normalize_whitespace(text).strip().lower()
    return normalized in NULL_LIKE_STRINGS


def is_missing_value(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip() or is_null_like_text(value)
    if isinstance(value, (list, tuple, set)):
        if not value:
            return True
        return all(is_missing_value(item) for item in value)
    if isinstance(value, dict):
        return not value
    return False


def parse_choice_map(value: Any) -> Dict[str, str]:
    if is_missing_value(value):
        return {}
    if isinstance(value, dict):
        choices: Dict[str, str] = {}
        for key, item in value.items():
            label = normalize_whitespace(str(key)).strip().upper()
            text = normalize_whitespace(to_plain_text(item))
            if re.fullmatch(r"[A-H]", label) and text and not is_null_like_text(text):
                choices[label] = text
        return choices
    if isinstance(value, (list, tuple)):
        choices = {}
        for index, item in enumerate(value):
            label = chr(ord("A") + index)
            text = normalize_whitespace(to_plain_text(item))
            if text and not is_null_like_text(text):
                choices[label] = text
        return choices
    text = normalize_whitespace(to_plain_text(value))
    if not text or is_null_like_text(text):
        return {}
    choices: Dict[str, str] = {}
    current_key: Optional[str] = None
    current_value: List[str] = []
    for line in text.splitlines():
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
    return {key: item for key, item in choices.items() if item and not is_null_like_text(item)}


def extract_json_object(text: str) -> Optional[Dict[str, Any]]:
    if not text:
        return None
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        snippet = text[start : end + 1]
        try:
            return json.loads(snippet)
        except json.JSONDecodeError:
            return None
    return None


@dataclass
class ModelConfig:
    base_url: str = "https://synai996.space/v1"
    api_key: str = os.environ.get("OPENAI_API_KEY", "")
    model: str = "gpt-5.4"
    reasoning_effort: str = "xhigh"
    temperature: float = 0.1
    timeout_seconds: int = 180
    enabled: bool = True
    agent_only_extraction: bool = False


@dataclass
class ThresholdConfig:
    min_width: int = 256
    min_height: int = 256
    min_sharpness_score: float = 0.22
    min_readability_score: float = 0.35
    min_contrast_score: float = 18.0
    reject_clean_score_below: float = 0.45
    review_clean_score_below: float = 0.62
    min_text_completeness_score: float = 0.60
    min_alignment_consistency: float = 0.55


@dataclass
class DatasetSpec:
    key: str
    display_name: str
    subject: str
    note: str
    source_kind: str
    source_locator: str
    split: Optional[str] = None
    hf_config_name: Optional[str] = None
    question_fields: List[str] = field(default_factory=list)
    answer_fields: List[str] = field(default_factory=list)
    image_fields: List[str] = field(default_factory=list)
    choice_fields: List[str] = field(default_factory=list)
    metadata_fields: List[str] = field(default_factory=list)
    force_requires_image: bool = False
    multi_solution_mode: str = "auto"


@dataclass
class PipelineConfig:
    sample_per_dataset: int = 30
    sample_strategy: str = "head"
    shuffle_seed: int = 42
    output_root: str = "benchmarkallinone/outputs/multidataset_cleaning"
    cleaning_version: str = "v3.1.0"
    batch_id_prefix: str = "benchmarkallinone-clean"
    save_sample_bundle: bool = True
    git_cache_root: str = "benchmarkallinone/outputs/repo_cache"
    model: ModelConfig = field(default_factory=ModelConfig)
    thresholds: ThresholdConfig = field(default_factory=ThresholdConfig)
    datasets: List[DatasetSpec] = field(default_factory=list)

    @classmethod
    def default_dataset_specs(cls) -> List[DatasetSpec]:
        return [
            DatasetSpec(
                key="geosqa",
                display_name="GeoSQA",
                subject="地理",
                note="论文页公开，但当前未配置稳定程序化下载入口",
                source_kind="source_unavailable",
                source_locator="https://aclanthology.org/D19-1597/",
            ),
            DatasetSpec(
                key="scemqa",
                display_name="SCEMQA",
                subject="数学、物理、生物、化学",
                note="GitHub 公开仓库，尝试自动发现数据文件",
                source_kind="github",
                source_locator="https://github.com/SceMQA/SceMQA",
                question_fields=["question", "problem", "query", "text"],
                answer_fields=["answer", "solution", "label"],
                image_fields=["image", "image_path", "img_path", "diagram"],
            ),
            DatasetSpec(
                key="geometry3k",
                display_name="Geometry3K",
                subject="数学",
                note="GitHub 公开仓库，尝试自动发现数据文件",
                source_kind="github",
                source_locator="https://github.com/lupantech/InterGPS",
                question_fields=["problem_text", "compact_text", "annotat_text", "problem", "question", "text"],
                answer_fields=["answer", "solution", "label"],
                image_fields=["img_diagram", "img_problem", "diagram", "image", "img_path", "image_path"],
                choice_fields=["choices", "compact_choices", "options"],
                force_requires_image=True,
            ),
            DatasetSpec(
                key="cmm_math",
                display_name="CMM-Math",
                subject="数学",
                note="Hugging Face 数据集",
                source_kind="huggingface",
                source_locator="ecnu-icalk/cmm-math",
                split="train",
                question_fields=["question"],
                answer_fields=["answer", "solution"],
                image_fields=["decoded_image", "image"],
                choice_fields=["options", "choices"],
            ),
            DatasetSpec(
                key="mathvision",
                display_name="MathVision",
                subject="数学",
                note="Hugging Face 数据集",
                source_kind="huggingface",
                source_locator="MathLLMs/MathVision",
                split="test",
                question_fields=["question"],
                answer_fields=["answer", "solution"],
                image_fields=["decoded_image", "image"],
                choice_fields=["options", "choices"],
            ),
            DatasetSpec(
                key="mm_math",
                display_name="MM-Math",
                subject="数学",
                note="Hugging Face 数据集",
                source_kind="huggingface",
                source_locator="THU-KEG/MM_Math",
                split="train",
            ),
            DatasetSpec(
                key="seephy",
                display_name="Seephy",
                subject="物理",
                note="当前仅论文入口，未配置稳定程序化下载源",
                source_kind="source_unavailable",
                source_locator="https://arxiv.org/abs/2509.06079",
            ),
            DatasetSpec(
                key="multi_physics",
                display_name="muti- physics",
                subject="物理",
                note="GitHub 公开仓库，尝试自动发现数据文件",
                source_kind="github",
                source_locator="https://github.com/luozhongze/Multi-Physics",
                question_fields=["question", "problem", "query", "text"],
                answer_fields=["answer", "solution", "label"],
                image_fields=["picture", "image", "image_path", "img_path", "figure"],
            ),
            DatasetSpec(
                key="physreason",
                display_name="PhysReason",
                subject="物理",
                note="GitHub 公开仓库，尝试自动发现数据文件",
                source_kind="github",
                source_locator="https://github.com/dxzxy12138/PhysReason",
                question_fields=["question", "problem", "query", "text"],
                answer_fields=["answer", "solution", "label"],
                image_fields=["image", "image_path", "img_path", "figure"],
            ),
            DatasetSpec(
                key="eee_bench",
                display_name="EEE-Bench",
                subject="电气电子工程领域",
                note="Hugging Face 数据集",
                source_kind="huggingface",
                source_locator="afdsafas/EEE-Bench",
                split="test",
                question_fields=["problem"],
                answer_fields=["solution"],
                image_fields=["image"],
            ),
            DatasetSpec(
                key="emma",
                display_name="EMMA",
                subject="数学、物理、代码、化学",
                note="当前仅论文入口，未配置稳定程序化下载源",
                source_kind="source_unavailable",
                source_locator="https://arxiv.org/abs/2501.05444",
            ),
        ]

    @classmethod
    def from_yaml(cls, path: Optional[str]) -> "PipelineConfig":
        if not path:
            return cls(datasets=cls.default_dataset_specs())
        with open(path, "r", encoding="utf-8") as file:
            raw = yaml.safe_load(file) or {}
        runtime = raw.get("runtime", {})
        model_raw = raw.get("model", {})
        threshold_raw = raw.get("thresholds", {})
        datasets_raw = raw.get("datasets", [])
        datasets = [DatasetSpec(**item) for item in datasets_raw] if datasets_raw else cls.default_dataset_specs()
        model_defaults = asdict(ModelConfig())
        model_data = {**model_defaults, **model_raw}
        env_api_key = os.environ.get("OPENAI_API_KEY", "")
        if env_api_key:
            model_data["api_key"] = env_api_key
        return cls(
            sample_per_dataset=runtime.get("sample_per_dataset", 30),
            sample_strategy=runtime.get("sample_strategy", "head"),
            shuffle_seed=runtime.get("shuffle_seed", 42),
            output_root=runtime.get("output_root", "outputs/multidataset_cleaning"),
            cleaning_version=runtime.get("cleaning_version", "v3.0.0"),
            batch_id_prefix=runtime.get("batch_id_prefix", "multidataset-clean"),
            save_sample_bundle=runtime.get("save_sample_bundle", True),
            git_cache_root=runtime.get("git_cache_root", "outputs/repo_cache"),
            model=ModelConfig(**model_data),
            thresholds=ThresholdConfig(**{**asdict(ThresholdConfig()), **threshold_raw}),
            datasets=datasets,
        )


@dataclass
class UnifiedSample:
    dataset_key: str
    dataset_display_name: str
    subject: str
    source_dataset: str
    source_split: str
    source_problem_id: str
    raw_question_text: str
    raw_answer_text: str
    images: List[Image.Image] = field(default_factory=list)
    image_sources: List[str] = field(default_factory=list)
    raw_record: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    choice_map: Dict[str, str] = field(default_factory=dict)
    force_requires_image: bool = False

    @property
    def image(self) -> Optional[Image.Image]:
        return self.images[0] if self.images else None

    @property
    def image_source(self) -> Optional[str]:
        return self.image_sources[0] if self.image_sources else None


class OpenAICompatibleClient:
    def __init__(self, config: ModelConfig):
        self.config = config

    def chat_json(self, system_prompt: str, user_prompt: str) -> Optional[Dict[str, Any]]:
        if not self.config.enabled or not self.config.api_key:
            return None
        debug = os.environ.get("PIPELINE_DEBUG_CHAT_JSON", "").strip().lower() in {"1", "true", "yes", "on"}
        debug_log_path = os.environ.get("PIPELINE_DEBUG_CHAT_JSON_LOG", "").strip()

        def emit_debug(message: str) -> None:
            if not debug:
                return
            if debug_log_path:
                path = Path(debug_log_path)
                ensure_dir(path.parent)
                with path.open("a", encoding="utf-8") as file:
                    file.write(message)
                    file.write("\n")
                return
            print(message, flush=True)

        url = self.config.base_url.rstrip("/") + "/chat/completions"
        payload = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": self.config.temperature,
            "response_format": {"type": "json_object"},
            "reasoning_effort": self.config.reasoning_effort,
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Connection": "close",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Authorization": f"Bearer {self.config.api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.config.timeout_seconds) as response:
                raw_body = response.read().decode("utf-8")
                body = json.loads(raw_body)
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace") if hasattr(exc, "read") else ""
            emit_debug(
                f"[chat_json debug] HTTPError status={getattr(exc, 'code', None)} reason={getattr(exc, 'reason', None)} body_preview={error_body[:400]}"
            )
            return None
        except urllib.error.URLError as exc:
            emit_debug(f"[chat_json debug] URLError reason={exc}")
            return None
        except http.client.RemoteDisconnected as exc:
            emit_debug(f"[chat_json debug] RemoteDisconnected reason={exc}")
            return None
        except ConnectionResetError as exc:
            emit_debug(f"[chat_json debug] ConnectionResetError reason={exc}")
            return None
        except TimeoutError as exc:
            emit_debug(f"[chat_json debug] TimeoutError reason={exc}")
            return None
        except json.JSONDecodeError as exc:
            emit_debug(f"[chat_json debug] Response JSON decode failed error={exc}")
            return None
        choices = body.get("choices") or []
        if not choices:
            emit_debug(f"[chat_json debug] Missing choices body_preview={json.dumps(body, ensure_ascii=False)[:400]}")
            return None
        message = choices[0].get("message") or {}
        content = message.get("content", "")
        if isinstance(content, list):
            content = "\n".join(item.get("text", "") for item in content if isinstance(item, dict))
        parsed = extract_json_object(to_plain_text(content))
        if parsed is None:
            emit_debug(f"[chat_json debug] Content JSON extraction failed content_preview={to_plain_text(content)[:400]}")
        return parsed


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
        match = re.search(r"\bChoices?\b\s*:?", text, flags=re.IGNORECASE)
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
        if any(token in question_text.lower() for token in ["respectively", "each", "for (a)", "for a", "for output", "outputs"]):
            return True
        return any(value.count(",") >= 1 or value.count(";") >= 1 for value in choices.values())


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


class BaseConnector:
    def __init__(self, spec: DatasetSpec, config: PipelineConfig):
        self.spec = spec
        self.config = config

    def sample(self) -> Tuple[str, List[UnifiedSample], Optional[str]]:
        raise NotImplementedError


class SourceUnavailableConnector(BaseConnector):
    def sample(self) -> Tuple[str, List[UnifiedSample], Optional[str]]:
        return "source_unavailable", [], "No stable programmatic public source configured"


PROJECT_ROOT = Path(__file__).resolve().parents[2]
WORKSPACE_ROOT = PROJECT_ROOT.parent
PROMPT_ROOT = PROJECT_ROOT / "prompts"
UNIFIED_EXTRACTION_PROMPT_PATH = PROMPT_ROOT / "extract_unified_sample.md"
LEGACY_EXTRACTION_PROMPT_PATH = PROMPT_ROOT / "extract_question_answer_image.md"


def read_prompt(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def normalize_image_path_list(value: Any) -> List[str]:
    if is_missing_value(value):
        return []
    if isinstance(value, (list, tuple)):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, dict):
        return normalize_image_path_list(value.get("path") or value.get("paths") or value.get("image") or value.get("url"))
    if isinstance(value, str):
        stripped = value.strip()
        return [stripped] if stripped else []
    return []


def resolve_image_candidate_path(path_str: str, base_dir: Path) -> Optional[Path]:
    candidate = Path(path_str)
    candidate_paths: List[Path] = []
    if candidate.is_absolute():
        candidate_paths.append(candidate)
    else:
        candidate_paths.append(base_dir / candidate)
        candidate_paths.append(PROJECT_ROOT / candidate)
        candidate_paths.append(WORKSPACE_ROOT / candidate)
    seen: set[str] = set()
    for item in candidate_paths:
        key = str(item)
        if key in seen:
            continue
        seen.add(key)
        if item.exists() and item.suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp", ".webp"}:
            return item
    return None


def choose_candidate_field(row: Dict[str, Any], candidates: List[str], fallback_regex: str) -> Optional[str]:
    for key in candidates:
        if key in row and not is_missing_value(row[key]):
            return key
    for key, value in row.items():
        if is_missing_value(value):
            continue
        if re.search(fallback_regex, key, flags=re.IGNORECASE):
            return key
    return None


def heuristic_extract_record_content(row: Dict[str, Any], spec: "DatasetSpec") -> Dict[str, Any]:
    question_field = choose_candidate_field(row, spec.question_fields or ["problem", "question"], r"question|problem|query|prompt|text")
    answer_field = choose_candidate_field(row, spec.answer_fields or ["solution", "answer"], r"answer|solution|label|target")
    image_field = choose_candidate_field(row, spec.image_fields or ["image", "image_path"], r"image|img|diagram|figure|picture|decoded_image")
    choice_field = choose_candidate_field(row, spec.choice_fields or ["options", "choices"], r"options|choices")
    raw_question = to_plain_text(row.get(question_field)) if question_field else ""
    raw_answer = to_plain_text(row.get(answer_field)) if answer_field else ""
    if is_null_like_text(raw_answer):
        raw_answer = ""
    choice_map = parse_choice_map(row.get(choice_field) if choice_field else None)
    raw_images = row.get(image_field) if image_field else row.get("images")
    image_paths = normalize_image_path_list(raw_images)
    if not image_paths and isinstance(raw_images, dict):
        image_paths = normalize_image_path_list(raw_images.get("path") or raw_images.get("image") or raw_images.get("url"))
    force_requires_image = bool(spec.force_requires_image)
    if raw_question:
        force_requires_image = force_requires_image or bool(
            re.search(r"\b(figure|diagram|graph|chart|image|shown|below|sample|下图|图中|示意图)\b", raw_question, flags=re.IGNORECASE)
        )
    return {
        "raw_question_text": raw_question,
        "raw_answer_text": raw_answer,
        "choice_map": choice_map,
        "image_paths": image_paths,
        "force_requires_image": force_requires_image,
        "extraction_notes": ["heuristic_field_extraction"],
        "question_field": question_field,
        "answer_field": answer_field,
        "image_field": image_field,
        "choice_field": choice_field,
    }


def prompt_extract_record_content(row: Dict[str, Any], spec: "DatasetSpec", client: "OpenAICompatibleClient") -> Dict[str, Any]:
    fallback = heuristic_extract_record_content(row, spec)
    prompt_path = UNIFIED_EXTRACTION_PROMPT_PATH if UNIFIED_EXTRACTION_PROMPT_PATH.exists() else LEGACY_EXTRACTION_PROMPT_PATH
    agent_only = bool(getattr(client.config, "agent_only_extraction", False))
    if not client.config.enabled or not client.config.api_key or not prompt_path.exists():
        if agent_only:
            return {
                "raw_question_text": "",
                "raw_answer_text": "",
                "choice_map": {},
                "image_paths": [],
                "force_requires_image": False,
                "extraction_notes": ["agent_only_extraction", "agent_extraction_failed"],
                "question_field": None,
                "answer_field": None,
                "image_field": None,
                "choice_field": None,
            }
        return fallback
    user_prompt = json.dumps(
        {
            "dataset_name": spec.display_name,
            "source_kind": spec.source_kind,
            "raw_record": row,
            "fallback": fallback,
        },
        ensure_ascii=False,
        indent=2,
        default=json_default,
    )
    result = client.chat_json(read_prompt(prompt_path), user_prompt)
    if not result:
        if agent_only:
            return {
                "raw_question_text": "",
                "raw_answer_text": "",
                "choice_map": {},
                "image_paths": [],
                "force_requires_image": False,
                "extraction_notes": ["agent_only_extraction", "agent_extraction_failed"],
                "question_field": None,
                "answer_field": None,
                "image_field": None,
                "choice_field": None,
            }
        return fallback
    extraction_notes = result.get("extraction_notes")
    if not isinstance(extraction_notes, list):
        extraction_notes = []
    extraction_notes = [to_plain_text(item) for item in extraction_notes if to_plain_text(item)]
    if agent_only:
        raw_question_text = normalize_whitespace(to_plain_text(result.get("raw_question_text") or result.get("question_text")))
        raw_answer_text = normalize_whitespace(to_plain_text(result.get("raw_answer_text") or result.get("answer_text")))
        choice_map = parse_choice_map(result.get("choice_map")) or {}
        image_paths = normalize_image_path_list(result.get("image_paths"))
        force_requires_image = result.get("force_requires_image")
        if not isinstance(force_requires_image, bool):
            force_requires_image = False
        extraction_notes.extend(["agent_only_extraction", "agent_extraction_success"])
        return {
            "raw_question_text": raw_question_text,
            "raw_answer_text": raw_answer_text,
            "choice_map": choice_map,
            "image_paths": image_paths,
            "force_requires_image": force_requires_image,
            "extraction_notes": sorted(set(extraction_notes)),
            "question_field": result.get("question_field"),
            "answer_field": result.get("answer_field"),
            "image_field": result.get("image_field"),
            "choice_field": result.get("choice_field"),
        }
    raw_question_text = normalize_whitespace(to_plain_text(result.get("raw_question_text") or result.get("question_text") or fallback["raw_question_text"]))
    raw_answer_text = normalize_whitespace(to_plain_text(result.get("raw_answer_text") or result.get("answer_text") or fallback["raw_answer_text"]))
    choice_map = parse_choice_map(result.get("choice_map")) or fallback["choice_map"]
    image_paths = normalize_image_path_list(result.get("image_paths")) or fallback["image_paths"]
    force_requires_image = result.get("force_requires_image")
    if not isinstance(force_requires_image, bool):
        force_requires_image = fallback["force_requires_image"]
    extraction_notes.append("prompt_extraction")
    return {
        **fallback,
        "raw_question_text": raw_question_text or fallback["raw_question_text"],
        "raw_answer_text": raw_answer_text or fallback["raw_answer_text"],
        "choice_map": choice_map,
        "image_paths": image_paths,
        "force_requires_image": force_requires_image,
        "extraction_notes": extraction_notes,
    }


def resolve_multiple_choice_answer_text(answer_text: str, choice_map: Dict[str, str]) -> str:
    answer = normalize_whitespace(answer_text)
    if not answer:
        return ""
    upper = answer.upper().strip()
    letter_match = re.fullmatch(r"\(?([A-Z])\)?", upper)
    if letter_match:
        key = letter_match.group(1)
        if key in choice_map:
            return normalize_whitespace(choice_map[key])
    mixed_match = re.match(r"^\(?([A-Z])\)?[\s.、:_-]+(.+)$", answer, flags=re.IGNORECASE)
    if mixed_match:
        answer = mixed_match.group(2).strip()
    return normalize_whitespace(answer)


class LocalFileConnector(BaseConnector):
    def iter_records(self, path: Path) -> Iterable[Dict[str, Any]]:
        suffix = path.suffix.lower()
        if suffix == ".jsonl":
            with path.open("r", encoding="utf-8", errors="ignore") as file:
                for line in file:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        row = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if isinstance(row, dict):
                        yield row
            return
        if suffix == ".json":
            with path.open("r", encoding="utf-8", errors="ignore") as file:
                data = json.load(file)
            if isinstance(data, list):
                for row in data:
                    if isinstance(row, dict):
                        yield row
                return
            if isinstance(data, dict):
                for key in ["data", "dataset", "datasets", "records", "items", "problems", "questions", "annotations"]:
                    value = data.get(key)
                    if isinstance(value, list):
                        for row in value:
                            if isinstance(row, dict):
                                yield row
                        return
                yield data
            return
        if suffix == ".csv":
            with path.open("r", encoding="utf-8", errors="ignore") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    yield dict(row)
            return
        if suffix == ".tsv":
            with path.open("r", encoding="utf-8", errors="ignore") as file:
                reader = csv.DictReader(file, delimiter="\t")
                for row in reader:
                    yield dict(row)
            return
        if suffix == ".parquet":
            try:
                import pandas as pd
            except Exception as exc:  # pragma: no cover
                raise RuntimeError("Parquet input requires pandas and pyarrow.") from exc
            df = pd.read_parquet(path)
            for row in df.to_dict(orient="records"):
                if isinstance(row, dict):
                    yield row
            return
        raise ValueError(f"Unsupported input format: {path.suffix}")

    def load_inline_images(self, value: Any, base_dir: Path) -> Tuple[List[Image.Image], List[str]]:
        images: List[Image.Image] = []
        sources: List[str] = []
        if is_missing_value(value):
            return images, sources
        if isinstance(value, np.ndarray):
            value = value.tolist()
        if isinstance(value, list):
            for item in value:
                child_images, child_sources = self.load_inline_images(item, base_dir)
                images.extend(child_images)
                sources.extend(child_sources)
            return images, sources
        if isinstance(value, Image.Image):
            return [value.convert("RGB")], ["inline://pil_image"]
        if isinstance(value, dict):
            bytes_data = value.get("bytes")
            path = value.get("path")
            if bytes_data is not None:
                try:
                    return [Image.open(io.BytesIO(bytes(bytes_data))).convert("RGB")], [path or "inline://image_bytes"]
                except Exception:
                    return images, sources
            if path:
                return self.load_inline_images(path, base_dir)
            nested_value = value.get("image") or value.get("images") or value.get("decoded_image")
            if nested_value is not None and nested_value is not value:
                return self.load_inline_images(nested_value, base_dir)
            return images, sources
        if isinstance(value, str):
            candidate = resolve_image_candidate_path(value, base_dir)
            if candidate is None:
                return images, sources
            try:
                return [Image.open(candidate).convert("RGB")], [str(candidate)]
            except Exception:
                return images, sources
        return images, sources

    def sample(self) -> Tuple[str, List[UnifiedSample], Optional[str]]:
        path = Path(self.spec.source_locator)
        if not path.exists():
            return "source_unavailable", [], f"Input not found: {path}"
        samples: List[UnifiedSample] = []
        prompt_client = OpenAICompatibleClient(self.config.model)
        for index, row in enumerate(self.iter_records(path)):
            extracted = prompt_extract_record_content(row, self.spec, prompt_client)
            raw_question = extracted["raw_question_text"]
            raw_answer = resolve_multiple_choice_answer_text(extracted["raw_answer_text"], extracted["choice_map"])
            images: List[Image.Image] = []
            image_sources: List[str] = []
            for path_str in extracted["image_paths"]:
                child_images, child_sources = self.load_inline_images(path_str, path.parent)
                images.extend(child_images)
                image_sources.extend(child_sources)
            if not images:
                image_field_candidates: List[str] = []
                explicit_image_field = extracted.get("image_field")
                if explicit_image_field:
                    image_field_candidates.append(str(explicit_image_field))
                for field_name in list(self.spec.image_fields or []) + ["image", "images", "decoded_image", "diagram"]:
                    if field_name and field_name not in image_field_candidates:
                        image_field_candidates.append(field_name)
                for field_name in image_field_candidates:
                    if field_name not in row:
                        continue
                    child_images, child_sources = self.load_inline_images(row.get(field_name), path.parent)
                    if child_images:
                        images.extend(child_images)
                        image_sources.extend(child_sources)
                        break
            if not raw_question and not images:
                continue
            samples.append(
                UnifiedSample(
                    dataset_key=self.spec.key,
                    dataset_display_name=self.spec.display_name,
                    subject=self.spec.subject,
                    source_dataset=self.spec.display_name,
                    source_split=self.spec.split or "local_file",
                    source_problem_id=str(row.get("id", row.get("problem_id", index))),
                    raw_question_text=raw_question,
                    raw_answer_text=raw_answer,
                    images=images,
                    image_sources=image_sources or extracted["image_paths"],
                    raw_record=row,
                    metadata={
                        "row_index": index,
                        "source_file": str(path),
                        "image_paths": extracted.get("image_paths", []),
                        "extraction_notes": extracted.get("extraction_notes", []),
                        "question_field": extracted.get("question_field"),
                        "answer_field": extracted.get("answer_field"),
                        "image_field": extracted.get("image_field"),
                        "choice_field": extracted.get("choice_field"),
                    },
                    choice_map=extracted["choice_map"],
                    force_requires_image=bool(extracted["force_requires_image"] or self.spec.force_requires_image),
                )
            )
        if self.config.sample_strategy == "random" and samples:
            rng = np.random.default_rng(self.config.shuffle_seed)
            indices = rng.permutation(len(samples)).tolist()[: self.config.sample_per_dataset]
            samples = [samples[i] for i in indices]
        else:
            samples = samples[: self.config.sample_per_dataset]
        return "available", samples, None


class HuggingFaceConnector(BaseConnector):
    def candidate_splits(self) -> List[str]:
        raw = [self.spec.split, "test", "validation", "val", "train"]
        return [item for item in raw if item]

    def load_dataset_any(self) -> Tuple[Optional[Dataset], Optional[str]]:
        last_error = None
        for split in self.candidate_splits():
            try:
                dataset = load_dataset(self.spec.source_locator, self.spec.hf_config_name, split=split)
                if isinstance(dataset, Dataset):
                    return dataset, split
            except Exception as exc:
                last_error = str(exc)
        try:
            dataset_obj = load_dataset(self.spec.source_locator, self.spec.hf_config_name)
            if isinstance(dataset_obj, DatasetDict):
                for split_name in dataset_obj.keys():
                    return dataset_obj[split_name], split_name
            if isinstance(dataset_obj, IterableDatasetDict):
                for split_name in dataset_obj.keys():
                    iterable = list(dataset_obj[split_name].take(self.config.sample_per_dataset))
                    return Dataset.from_list(iterable), split_name
        except Exception as exc:
            last_error = str(exc)
        return None, last_error

    def load_images(self, value: Any) -> Tuple[List[Image.Image], List[str]]:
        images: List[Image.Image] = []
        sources: List[str] = []
        if is_missing_value(value):
            return images, sources
        if isinstance(value, list):
            for item in value:
                child_images, child_sources = self.load_images(item)
                images.extend(child_images)
                sources.extend(child_sources)
            return images, sources
        if isinstance(value, Image.Image):
            return [value.convert("RGB")], ["inline://pil_image"]
        if isinstance(value, dict):
            path = value.get("path")
            bytes_data = value.get("bytes")
            if bytes_data:
                try:
                    image = Image.open(io.BytesIO(bytes_data)).convert("RGB")
                    return [image], [path or "inline://hf_image_bytes"]
                except Exception:
                    return images, sources
            if path and Path(path).exists():
                try:
                    return [Image.open(path).convert("RGB")], [str(path)]
                except Exception:
                    return images, sources
            nested_value = value.get("image") or value.get("images") or value.get("decoded_image")
            if nested_value is not None and nested_value is not value:
                return self.load_images(nested_value)
            return images, sources
        if isinstance(value, str) and not is_null_like_text(value) and Path(value).exists():
            try:
                return [Image.open(value).convert("RGB")], [value]
            except Exception:
                return images, sources
        return images, sources

    def resolve_answer_text(self, raw_answer: Any) -> str:
        if isinstance(raw_answer, list):
            joined = [normalize_whitespace(to_plain_text(item)) for item in raw_answer if normalize_whitespace(to_plain_text(item))]
            return "\n".join(joined)
        return to_plain_text(raw_answer)

    def sample_from_mm_math_raw_files(self) -> Tuple[str, List[UnifiedSample], Optional[str]]:
        from huggingface_hub import hf_hub_download
        import zipfile

        try:
            jsonl_path = Path(hf_hub_download(repo_id=self.spec.source_locator, repo_type="dataset", filename="MM_Math/MM_Math.jsonl"))
            zip_path = Path(hf_hub_download(repo_id=self.spec.source_locator, repo_type="dataset", filename="MM_Math/MM_Math.zip"))
        except Exception as exc:
            return "source_unavailable", [], str(exc)

        extract_root = Path(self.config.git_cache_root) / "hf_raw" / "mm_math"
        image_root = extract_root / "MM_Math"
        if not image_root.exists():
            ensure_dir(extract_root)
            with zipfile.ZipFile(zip_path) as zf:
                zf.extractall(extract_root)

        samples: List[UnifiedSample] = []
        prompt_client = OpenAICompatibleClient(self.config.model)
        with jsonl_path.open("r", encoding="utf-8") as file:
            for index, line in enumerate(file):
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                if not isinstance(row, dict):
                    continue
                extracted = prompt_extract_record_content(row, self.spec, prompt_client)
                raw_question = extracted["raw_question_text"]
                raw_answer = resolve_multiple_choice_answer_text(
                    self.resolve_answer_text(row.get("solution") or extracted["raw_answer_text"]),
                    extracted["choice_map"],
                )
                images: List[Image.Image] = []
                image_sources: List[str] = []
                file_name = to_plain_text(row.get("file_name"))
                if file_name:
                    candidate = image_root / file_name
                    if candidate.exists():
                        try:
                            images.append(Image.open(candidate).convert("RGB"))
                            image_sources.append(str(candidate))
                        except Exception:
                            images = []
                            image_sources = []
                if not raw_question and not images:
                    continue
                samples.append(
                    UnifiedSample(
                        dataset_key=self.spec.key,
                        dataset_display_name=self.spec.display_name,
                        subject=self.spec.subject,
                        source_dataset=self.spec.display_name,
                        source_split=self.spec.split or "hf_raw_files",
                        source_problem_id=str(row.get("id", row.get("problem_id", file_name or index))),
                        raw_question_text=raw_question,
                        raw_answer_text=raw_answer,
                        images=images,
                        image_sources=image_sources,
                        raw_record=row,
                        metadata={
                            "row_index": index,
                            "image_paths": [file_name] if file_name else [],
                            "extraction_notes": extracted.get("extraction_notes", []) + ["hf_raw_mm_math_images"],
                            "image_field": extracted.get("image_field"),
                        },
                        choice_map=extracted["choice_map"],
                        force_requires_image=bool(extracted["force_requires_image"] or self.spec.force_requires_image),
                    )
                )
                if len(samples) >= self.config.sample_per_dataset:
                    break
        return "available", samples, None

    def sample_from_physreason_zip(self) -> Tuple[str, List[UnifiedSample], Optional[str]]:
        from huggingface_hub import hf_hub_download
        import zipfile

        zip_name = "PhysReason-mini.zip"
        if self.spec.split and self.spec.split.lower() in {"train", "full"}:
            zip_name = "PhysReason-full.zip"
        try:
            zip_path = Path(hf_hub_download(repo_id=self.spec.source_locator, repo_type="dataset", filename=zip_name))
        except Exception as exc:
            return "source_unavailable", [], str(exc)

        extract_root = Path(self.config.git_cache_root) / "hf_raw" / "physreason"
        marker_dir = extract_root / Path(zip_name).stem
        if not marker_dir.exists():
            ensure_dir(extract_root)
            with zipfile.ZipFile(zip_path) as zf:
                zf.extractall(extract_root)

        problem_files = sorted(marker_dir.rglob("problem.json"))
        if not problem_files:
            return "source_unavailable", [], "No problem.json extracted from PhysReason zip"

        samples: List[UnifiedSample] = []
        prompt_client = OpenAICompatibleClient(self.config.model)
        for index, problem_path in enumerate(problem_files):
            try:
                data = json.loads(problem_path.read_text(encoding="utf-8"))
            except Exception:
                continue
            if not isinstance(data, dict):
                continue
            extracted = prompt_extract_record_content(data, self.spec, prompt_client)
            question_text = extracted["raw_question_text"]
            raw_answer = resolve_multiple_choice_answer_text(self.resolve_answer_text(extracted["raw_answer_text"]), extracted["choice_map"])
            images: List[Image.Image] = []
            image_sources: List[str] = []
            image_list = data.get("question_image_list") or []
            if isinstance(image_list, list):
                for rel in image_list:
                    candidate = problem_path.parent / to_plain_text(rel)
                    if not candidate.exists():
                        continue
                    try:
                        images.append(Image.open(candidate).convert("RGB"))
                        image_sources.append(str(candidate))
                    except Exception:
                        continue
            if not question_text and not images:
                continue
            samples.append(
                UnifiedSample(
                    dataset_key=self.spec.key,
                    dataset_display_name=self.spec.display_name,
                    subject=self.spec.subject,
                    source_dataset=self.spec.display_name,
                    source_split=self.spec.split or Path(zip_name).stem,
                    source_problem_id=problem_path.parent.name,
                    raw_question_text=question_text,
                    raw_answer_text=raw_answer,
                    images=images,
                    image_sources=image_sources,
                    raw_record=data,
                    metadata={
                        "row_index": index,
                        "image_paths": image_list,
                        "extraction_notes": extracted.get("extraction_notes", []) + ["hf_raw_physreason_images"],
                        "difficulty": data.get("difficulty"),
                    },
                    choice_map=extracted["choice_map"],
                    force_requires_image=bool(extracted["force_requires_image"] or image_sources),
                )
            )
            if len(samples) >= self.config.sample_per_dataset:
                break
        if not samples:
            return "source_unavailable", [], "No usable samples extracted from PhysReason zip"
        return "available", samples, None

    def sample(self) -> Tuple[str, List[UnifiedSample], Optional[str]]:
        dataset, detail = self.load_dataset_any()
        if dataset is None:
            if self.spec.key == "mm_math":
                return self.sample_from_mm_math_raw_files()
            if self.spec.key == "physreason":
                return self.sample_from_physreason_zip()
            return "source_unavailable", [], detail or "load_dataset failed"
        if self.config.sample_strategy == "random":
            dataset = dataset.shuffle(seed=self.config.shuffle_seed)
        rows = dataset.select(range(min(self.config.sample_per_dataset, len(dataset))))
        samples: List[UnifiedSample] = []
        prompt_client = OpenAICompatibleClient(self.config.model)
        for index, row in enumerate(rows):
            row = dict(row)
            extracted = prompt_extract_record_content(row, self.spec, prompt_client)
            raw_question = extracted["raw_question_text"]
            raw_answer = resolve_multiple_choice_answer_text(self.resolve_answer_text(extracted["raw_answer_text"]), extracted["choice_map"])
            image_field_candidates: List[str] = []
            explicit_image_field = extracted.get("image_field")
            if explicit_image_field:
                image_field_candidates.append(str(explicit_image_field))
            for field_name in list(self.spec.image_fields or []) + ["image", "images", "decoded_image", "diagram"]:
                if field_name and field_name not in image_field_candidates:
                    image_field_candidates.append(field_name)
            images: List[Image.Image] = []
            image_sources: List[str] = []
            seen_fields: set[str] = set()
            for field_name in image_field_candidates:
                if not field_name or field_name in seen_fields or field_name not in row:
                    continue
                seen_fields.add(field_name)
                child_images, child_sources = self.load_images(row.get(field_name))
                if child_images:
                    images.extend(child_images)
                    image_sources.extend(child_sources)
                    break
            if not images:
                for path_str in extracted["image_paths"]:
                    child_images, child_sources = self.load_images(path_str)
                    if child_images:
                        images.extend(child_images)
                        image_sources.extend(child_sources)
                        break
            if not raw_question and not images:
                continue
            samples.append(
                UnifiedSample(
                    dataset_key=self.spec.key,
                    dataset_display_name=self.spec.display_name,
                    subject=self.spec.subject,
                    source_dataset=self.spec.display_name,
                    source_split=detail or self.spec.split or "unknown",
                    source_problem_id=str(row.get("id", row.get("problem_id", index))),
                    raw_question_text=raw_question,
                    raw_answer_text=raw_answer,
                    images=images,
                    image_sources=image_sources or extracted["image_paths"],
                    raw_record=row,
                    metadata={
                        "row_index": index,
                        "image_paths": extracted.get("image_paths", []),
                        "extraction_notes": extracted.get("extraction_notes", []),
                        "question_field": extracted.get("question_field"),
                        "answer_field": extracted.get("answer_field"),
                        "image_field": extracted.get("image_field"),
                        "choice_field": extracted.get("choice_field"),
                    },
                    choice_map=extracted["choice_map"],
                    force_requires_image=bool(extracted["force_requires_image"] or self.spec.force_requires_image),
                )
            )
        return "available", samples, None


class GitHubConnector(BaseConnector):
    def ensure_repo(self) -> Tuple[Optional[Path], Optional[str]]:
        cache_root = Path(self.config.git_cache_root)
        ensure_dir(cache_root)
        target = cache_root / self.spec.key
        if target.exists() and (target / ".git").exists():
            return target, None
        if target.exists() and any(target.iterdir()):
            return target, None
        if target.exists():
            shutil.rmtree(target)
        clone = subprocess.run(
            ["git", "clone", "--depth", "1", self.spec.source_locator, str(target)],
            capture_output=True,
            text=True,
            timeout=300,
        )
        if clone.returncode != 0:
            detail = (clone.stderr or clone.stdout or "git clone failed").strip()
            return None, detail
        return target, None

    def discover_data_files(self, repo_dir: Path) -> List[Path]:
        scored: List[Tuple[int, Path]] = []
        for path in repo_dir.rglob("*"):
            if not path.is_file():
                continue
            suffix = path.suffix.lower()
            if suffix not in {".json", ".jsonl", ".csv", ".tsv"}:
                continue
            rel = str(path.relative_to(repo_dir)).lower()
            score = 0
            if any(token in rel for token in ["train", "test", "valid", "val", "dataset", "data", "problem", "question"]):
                score += 3
            if any(token in rel for token in ["image", "img", "diagram", "figure"]):
                score += 1
            if path.stat().st_size > 0:
                score += 1
            if self.spec.key == "geometry3k":
                if re.search(r"annotation_tool/data_collection/data_examples/\d+/data\.json$", rel):
                    score += 50
                if rel.endswith("logic_form.json"):
                    score -= 10
                if re.search(r"(?:^|/)diagram_parser/detection/.*\.csv$", rel):
                    score -= 30
                if re.search(r"(?:^|/).*labels.*\.csv$", rel):
                    score -= 20
            scored.append((score, path))
        scored.sort(key=lambda item: (-item[0], str(item[1])))
        return [path for _, path in scored]

    def parse_records_from_json(self, path: Path) -> List[Dict[str, Any]]:
        with path.open("r", encoding="utf-8", errors="ignore") as file:
            data = json.load(file)
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
        if isinstance(data, dict):
            for key in ["data", "dataset", "datasets", "records", "items", "problems", "questions", "annotations"]:
                value = data.get(key)
                if isinstance(value, list) and value and isinstance(value[0], dict):
                    return value
            if any(key in data for key in ["question", "problem", "problem_text", "compact_text", "annotat_text", "answer", "solution", "label", "choices", "options", "image", "diagram"]):
                return [data]
            flattened_rows: List[Dict[str, Any]] = []
            for bucket_name, value in data.items():
                if not isinstance(value, list):
                    continue
                dict_rows = [item for item in value if isinstance(item, dict)]
                if not dict_rows:
                    continue
                for item in dict_rows:
                    row = dict(item)
                    row.setdefault("category", bucket_name)
                    flattened_rows.append(row)
            if flattened_rows:
                return flattened_rows
        return []

    def parse_records_from_jsonl(self, path: Path) -> List[Dict[str, Any]]:
        rows = []
        with path.open("r", encoding="utf-8", errors="ignore") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(row, dict):
                    rows.append(row)
        return rows

    def parse_records_from_csv(self, path: Path, delimiter: str) -> List[Dict[str, Any]]:
        with path.open("r", encoding="utf-8", errors="ignore") as file:
            reader = csv.DictReader(file, delimiter=delimiter)
            return [dict(row) for row in reader]

    def load_records(self, path: Path) -> List[Dict[str, Any]]:
        if path.suffix.lower() == ".json":
            return self.parse_records_from_json(path)
        if path.suffix.lower() == ".jsonl":
            return self.parse_records_from_jsonl(path)
        if path.suffix.lower() == ".csv":
            return self.parse_records_from_csv(path, ",")
        if path.suffix.lower() == ".tsv":
            return self.parse_records_from_csv(path, "\t")
        return []

    def resolve_images(self, value: Any, base_dir: Path) -> Tuple[List[Image.Image], List[str]]:
        images: List[Image.Image] = []
        sources: List[str] = []
        if is_missing_value(value):
            return images, sources
        if isinstance(value, list):
            for item in value:
                child_images, child_sources = self.resolve_images(item, base_dir)
                images.extend(child_images)
                sources.extend(child_sources)
            return images, sources
        if isinstance(value, Image.Image):
            return [value.convert("RGB")], ["inline://pil_image"]
        if isinstance(value, dict):
            bytes_data = value.get("bytes")
            if bytes_data:
                try:
                    return [Image.open(io.BytesIO(bytes(bytes_data))).convert("RGB")], [value.get("path") or "inline://image_bytes"]
                except Exception:
                    return images, sources
            if "path" in value:
                return self.resolve_images(value["path"], base_dir)
            if "image" in value:
                return self.resolve_images(value["image"], base_dir)
            if "url" in value:
                return self.resolve_images(value["url"], base_dir)
            return images, sources
        if isinstance(value, str):
            candidate = resolve_image_candidate_path(value, base_dir)
            if candidate is None and not Path(value).suffix:
                for suffix in [".png", ".jpg", ".jpeg", ".bmp", ".webp"]:
                    candidate = resolve_image_candidate_path(str(Path(value).with_suffix(suffix)), base_dir)
                    if candidate is not None:
                        break
            if candidate is None:
                return images, sources
            try:
                return [Image.open(candidate).convert("RGB")], [str(candidate)]
            except Exception:
                return images, sources
        return images, sources

    def sample(self) -> Tuple[str, List[UnifiedSample], Optional[str]]:
        repo_dir, error = self.ensure_repo()
        if repo_dir is None:
            return "source_unavailable", [], error or "git clone failed"
        files = self.discover_data_files(repo_dir)
        if not files:
            return "source_unavailable", [], "No structured data files discovered in repository"
        samples: List[UnifiedSample] = []
        detail_errors: List[str] = []
        prompt_client = OpenAICompatibleClient(self.config.model)
        limit = self.config.sample_per_dataset
        for file_path in files[:40]:
            try:
                records = self.load_records(file_path)
            except Exception as exc:
                detail_errors.append(f"{file_path.name}: {exc}")
                continue
            if not records:
                continue
            for index, row in enumerate(records):
                row = dict(row)
                extracted = prompt_extract_record_content(row, self.spec, prompt_client)
                raw_question = extracted["raw_question_text"]
                raw_answer = resolve_multiple_choice_answer_text(extracted["raw_answer_text"], extracted["choice_map"])
                images: List[Image.Image] = []
                image_sources: List[str] = []
                image_field_candidates: List[str] = []
                explicit_image_field = extracted.get("image_field")
                if explicit_image_field:
                    image_field_candidates.append(str(explicit_image_field))
                for field_name in list(self.spec.image_fields or []) + ["image", "images", "image_path", "img_path", "diagram", "figure", "picture"]:
                    if field_name and field_name not in image_field_candidates:
                        image_field_candidates.append(field_name)
                seen_fields: set[str] = set()
                for field_name in image_field_candidates:
                    if not field_name or field_name in seen_fields or field_name not in row:
                        continue
                    seen_fields.add(field_name)
                    child_images, child_sources = self.resolve_images(row.get(field_name), file_path.parent)
                    if child_images:
                        images.extend(child_images)
                        image_sources.extend(child_sources)
                        break
                if not images:
                    for path_str in extracted["image_paths"]:
                        child_images, child_sources = self.resolve_images(path_str, file_path.parent)
                        if child_images:
                            images.extend(child_images)
                            image_sources.extend(child_sources)
                            break
                if not images and self.spec.key == "geometry3k":
                    for candidate_name in ["img_diagram.png", "img_problem.png", "img_diagram_point.png"]:
                        candidate = file_path.parent / candidate_name
                        if not candidate.exists():
                            continue
                        try:
                            images.append(Image.open(candidate).convert("RGB"))
                            image_sources.append(str(candidate))
                        except Exception:
                            continue
                if not raw_question and not images:
                    continue
                samples.append(
                    UnifiedSample(
                        dataset_key=self.spec.key,
                        dataset_display_name=self.spec.display_name,
                        subject=self.spec.subject,
                        source_dataset=self.spec.display_name,
                        source_split="repo_discovered",
                        source_problem_id=str(row.get("id", row.get("problem_id", len(samples)))),
                        raw_question_text=raw_question,
                        raw_answer_text=raw_answer,
                        images=images,
                        image_sources=image_sources or extracted["image_paths"],
                        raw_record=row,
                        metadata={
                            "data_file": str(file_path),
                            "image_paths": extracted.get("image_paths", []),
                            "extraction_notes": extracted.get("extraction_notes", []),
                            "question_field": extracted.get("question_field"),
                            "answer_field": extracted.get("answer_field"),
                            "image_field": extracted.get("image_field"),
                            "choice_field": extracted.get("choice_field"),
                        },
                        choice_map=extracted["choice_map"],
                        force_requires_image=bool(extracted["force_requires_image"] or self.spec.force_requires_image),
                    )
                )
                if self.config.sample_strategy != "random" and len(samples) >= limit:
                    break
            if self.config.sample_strategy != "random" and len(samples) >= limit:
                break
        if not samples:
            reason = "; ".join(detail_errors[:3]) if detail_errors else "No usable records extracted"
            return "source_unavailable", [], reason
        if self.config.sample_strategy == "random":
            rng = np.random.default_rng(self.config.shuffle_seed)
            indices = rng.permutation(len(samples)).tolist()[:limit]
            samples = [samples[i] for i in indices]
        else:
            samples = samples[:limit]
        return "available", samples, None

class RewriteAgent:
    def __init__(self, client: OpenAICompatibleClient, normalizer: TextNormalizer):
        self.client = client
        self.normalizer = normalizer

    def fallback_rewrite(self, dataset_name: str, question_text: str, normalized_answer: str, answer_type: str, choices: Dict[str, str]) -> Dict[str, Any]:
        question_only, _ = self.normalizer.split_question_and_choices(question_text)
        question_only = self.normalizer.strip_hint(question_only)
        if not choices:
            if answer_type == "option" and any(token in question_only.lower() for token in ["which picture", "in which picture", "which figure", "which diagram", "which graph", "shown below", "illustrated"]):
                return {
                    "strategy": "drop_image_index",
                    "rationale": "Visual selection question without textual choices should be dropped.",
                    "variants": [],
                    "discard_reason_codes": ["pure_image_index_choice"],
                }
            return {
                "strategy": "keep_open",
                "rationale": "Question is already open-ended.",
                "variants": [
                    {
                        "variant_id": "open_1",
                        "title": f"{dataset_name} 开放题",
                        "rewritten_question_text": question_only,
                        "expected_answer_type": answer_type,
                        "expected_answer": normalized_answer,
                        "split_role": "single",
                    }
                ],
                "discard_reason_codes": [],
            }
        if self.normalizer.is_pure_image_index_question(question_only, choices):
            return {
                "strategy": "drop_image_index",
                "rationale": "Pure image-index multiple choice question should be dropped.",
                "variants": [],
                "discard_reason_codes": ["pure_image_index_choice"],
            }
        if self.normalizer.is_compound_answer_question(question_only, choices):
            correct_text = choices.get(normalized_answer, "")
            pieces = [piece.strip() for piece in re.split(r"[;；]", correct_text) if piece.strip()]
            if not pieces:
                pieces = [correct_text] if correct_text else []
            variants = []
            for idx, piece in enumerate(pieces or [normalized_answer], start=1):
                variants.append(
                    {
                        "variant_id": f"open_{idx}",
                        "title": f"{dataset_name} 子题 {idx}",
                        "rewritten_question_text": f"{question_only}\n请只回答第 {idx} 个目标量。",
                        "expected_answer_type": "short_text",
                        "expected_answer": piece,
                        "split_role": f"part_{idx}",
                    }
                )
            return {
                "strategy": "split_open",
                "rationale": "Compound choice answer was split into multiple open-ended targets.",
                "variants": variants,
                "discard_reason_codes": [],
            }
        return {
            "strategy": "blank_open",
            "rationale": "Converted multiple choice into blank-style open-ended question.",
            "variants": [
                {
                    "variant_id": "open_1",
                    "title": f"{dataset_name} 开放题",
                    "rewritten_question_text": question_only,
                    "expected_answer_type": "numeric" if answer_type == "option" and choices.get(normalized_answer, "") else answer_type,
                    "expected_answer": choices.get(normalized_answer, normalized_answer),
                    "split_role": "single",
                }
            ],
            "discard_reason_codes": [],
        }

    def rewrite(self, dataset_name: str, normalized_question_text: str, normalized_answer_text: str, answer_type: str, choices: Dict[str, str]) -> Dict[str, Any]:
        fallback = self.fallback_rewrite(dataset_name, normalized_question_text, normalized_answer_text, answer_type, choices)
        if not self.client.config.enabled or not choices:
            return fallback
        system_prompt = (
            "You are the Question Rewrite Agent in a multimodal dataset cleaning pipeline. "
            "Convert multiple-choice questions into open-ended variants under strict rules. "
            "If the question is already open-ended, keep it. "
            "If it is a pure graph/diagram/waveform label selection question, drop it. "
            "If it is concept discrimination whose target is carried by options, rewrite it as a blank-style open question without options. "
            "If one option contains multiple atomic answers, split into multiple subquestions. Output strict JSON only."
        )
        user_prompt = json.dumps(
            {
                "dataset_name": dataset_name,
                "question_text": normalized_question_text,
                "choices": choices,
                "correct_option_letter": normalized_answer_text if answer_type == "option" else None,
                "correct_option_text": choices.get(normalized_answer_text, normalized_answer_text),
                "answer_type": answer_type,
                "fallback_result": fallback,
            },
            ensure_ascii=False,
            indent=2,
        )
        llm_result = self.client.chat_json(system_prompt, user_prompt)
        if not llm_result:
            return fallback
        strategy = to_plain_text(llm_result.get("strategy")).strip() or fallback["strategy"]
        variants = llm_result.get("variants")
        if not isinstance(variants, list):
            variants = fallback["variants"]
        if strategy == "drop_image_index":
            variants = []
        if not variants and strategy != "drop_image_index":
            return fallback
        return {
            "strategy": strategy,
            "rationale": to_plain_text(llm_result.get("rationale")) or fallback["rationale"],
            "variants": variants,
            "discard_reason_codes": llm_result.get("discard_reason_codes", fallback["discard_reason_codes"]),
            "llm_used": True,
        }


class DecisionAgent:
    def __init__(self, client: OpenAICompatibleClient):
        self.client = client

    def review_override(self, quality_components: Dict[str, Any], rewrite_report: Dict[str, Any], alignment_record: Dict[str, Any], solvability_report: Dict[str, Any], quality_flags: List[str]) -> Optional[Dict[str, Any]]:
        if not self.client.config.enabled:
            return None
        system_prompt = (
            "You are the Cleaning Decision Agent. Read the structured signals and decide one of pass/review/reject. "
            "Be conservative. If rewrite strategy is drop_image_index, reject. If alignment is risky, solvability is weak, or quality is borderline, review or reject. "
            "Return strict JSON with keys: decision, reason_codes, rationale."
        )
        user_prompt = json.dumps(
            {
                "quality_components": quality_components,
                "rewrite_report": rewrite_report,
                "alignment_record": alignment_record,
                "solvability_report": solvability_report,
                "quality_flags": quality_flags,
            },
            ensure_ascii=False,
            indent=2,
        )
        result = self.client.chat_json(system_prompt, user_prompt)
        if not result:
            return None
        decision = to_plain_text(result.get("decision")).strip().lower()
        if decision not in {"pass", "review", "reject"}:
            return None
        reason_codes = result.get("reason_codes")
        if not isinstance(reason_codes, list):
            reason_codes = []
        return {
            "decision": decision,
            "reason_codes": [to_plain_text(code) for code in reason_codes if to_plain_text(code)],
            "rationale": to_plain_text(result.get("rationale")),
        }


class MultiDatasetCleaningPipeline:
    def __init__(self, setup: SetupContext):
        self.setup = setup
        self.config = setup.config
        self.text_normalizer = TextNormalizer()
        self.image_analyzer = ImageQualityAnalyzer()
        self.client = OpenAICompatibleClient(self.config.model)
        self.rewrite_agent = RewriteAgent(self.client, self.text_normalizer)
        self.decision_agent = DecisionAgent(self.client)
        self.text_parser = TextContextParser()
        self.visual_parser = VisualParser()
        self.alignment_engine = AlignmentEngine()
        self.solvability_checker = SolvabilityChecker()
        self.pipeline_run_id = setup.pipeline_run_id
        self.ingest_batch_id = setup.ingest_batch_id
        self.output_root = setup.output_root
        self.run_dir = setup.run_dir
        self.dataset_root = setup.dataset_root
        self.aggregate_summary: Dict[str, Any] = dict(setup.aggregate_summary)
        self.local_file_connector_cls = LocalFileConnector
        self.huggingface_connector_cls = HuggingFaceConnector
        self.github_connector_cls = GitHubConnector
        self.source_unavailable_connector_cls = SourceUnavailableConnector
        self.utc_now = utc_now
        self.stable_digest = stable_digest
        self.is_null_like_text = is_null_like_text
        self.normalize_structured_text = normalize_structured_text
        self.to_plain_text = to_plain_text
        self.ensure_dir = ensure_dir
        self.sha256_bytes = sha256_bytes
        self.clamp = clamp
        self.math = math

    def run(self) -> Dict[str, Any]:
        dataset_summaries = []
        for spec in self.config.datasets:
            dataset_summaries.append(self.run_single_dataset(spec))
        self.aggregate_summary["datasets"] = dataset_summaries
        return write_run_summary(self.run_dir, self.aggregate_summary, write_json)

    def run_single_dataset(self, spec: DatasetSpec) -> Dict[str, Any]:
        source_status, samples, detail = ingest_dataset_samples(self, spec)
        dataset_dir = self.dataset_root / spec.key
        ensure_dir(dataset_dir)
        if source_status != "available":
            summary = build_source_unavailable_summary(spec, self.config, detail)
            write_json(dataset_dir / "summary.json", summary)
            return summary
        bundle = init_dataset_bundle()
        sample_dir = dataset_dir / "samples"
        artifact_dir = dataset_dir / "artifacts"
        image_dir = artifact_dir / "images"
        crop_dir = artifact_dir / "crops"
        ensure_dir(sample_dir)
        ensure_dir(image_dir)
        ensure_dir(crop_dir)
        for sample in samples:
            result = self.process_sample(spec, sample, image_dir, crop_dir)
            append_sample_result(bundle, result)
            write_sample_bundle_if_needed(self.config, sample_dir, result, write_json)
        return finalize_dataset_report(dataset_dir=dataset_dir, run_dir=self.run_dir, spec=spec, config=self.config, detail=detail, bundle=bundle, ensure_dir=ensure_dir, write_json=write_json, write_jsonl=write_jsonl)

    def persist_images(self, problem_id: str, images: Sequence[Image.Image], image_dir: Path) -> Tuple[List[Path], List[bytes], List[Dict[str, Any]]]:
        ensure_dir(image_dir)
        image_paths: List[Path] = []
        image_bytes_list: List[bytes] = []
        image_qualities: List[Dict[str, Any]] = []
        for index, image in enumerate(images, start=1):
            image_bytes = self.image_analyzer.pil_to_png_bytes(image)
            suffix = "primary" if index == 1 else f"aux_{index}"
            path = image_dir / f"{problem_id}_{suffix}.png"
            with path.open("wb") as file:
                file.write(image_bytes)
            image_paths.append(path)
            image_bytes_list.append(image_bytes)
            image_qualities.append(self.image_analyzer.analyze(image))
        return image_paths, image_bytes_list, image_qualities

    def determine_multi_solution_policy(self, spec: DatasetSpec) -> Dict[str, Any]:
        mode = (spec.multi_solution_mode or "auto").strip().lower()
        if mode == "auto":
            if spec.key in {"scemqa", "seephy", "multi_physics", "emma"}:
                mode = "conservative"
            elif spec.key in {"geometry3k", "cmm_math", "mathvision", "mm_math", "eee_bench", "physreason", "geosqa"}:
                mode = "aggressive"
            elif any(token in spec.subject for token in ["生物", "化学"]):
                mode = "conservative"
            elif any(token in spec.subject for token in ["数学", "电气", "物理"]):
                mode = "balanced"
            else:
                mode = "balanced"
        rationale_map = {
            "aggressive": "该数据集被视为具备较稳定的多解潜力，可进入更强的多解挖掘链路。",
            "balanced": "该数据集保留多解潜力评估，但不默认强推多解 agent。",
            "conservative": "该数据集更可能以单解题为主，不强推多解 agent，只保留基础可验证性与可标注性检查。",
        }
        return {"mode": mode, "should_push_multi_solution_agent": mode == "aggressive", "rationale": rationale_map.get(mode, rationale_map["balanced"])}

    def compute_initial_collection_scores(self, normalized_question_text: str, normalized_answer_text: str, answer_type: str, requires_image: bool, text_dominant: bool, image_qualities: Sequence[Dict[str, Any]], choices: Dict[str, str], multi_solution_policy: Dict[str, Any]) -> Dict[str, Any]:
        best_readability = max((quality.get("readability_score", 0.0) for quality in image_qualities), default=0.0)
        image_dependency = 0.9 if requires_image else 0.2 + 0.08 * int(bool(choices))
        multi_solution = 0.18
        if multi_solution_policy["mode"] == "aggressive":
            multi_solution += 0.28
        elif multi_solution_policy["mode"] == "balanced":
            multi_solution += 0.14
        if any(token in normalized_question_text.lower() for token in ["prove", "different", "all possible", "另一种", "不同", "证明"]):
            multi_solution += 0.18
        if len(choices) >= 4 and not text_dominant:
            multi_solution += 0.06
        verifiability = 0.2 + 0.42 * int(bool(normalized_answer_text))
        if answer_type in {"numeric", "option", "short_text"}:
            verifiability += 0.16
        if requires_image:
            verifiability += 0.12 * clamp(best_readability)
        return {
            "initial_image_dependency_score": round(clamp(image_dependency), 4),
            "initial_multi_solution_score": round(clamp(multi_solution), 4),
            "initial_verifiability_score": round(clamp(verifiability), 4),
        }

    def compute_potential_scores(self, normalized_question_text: str, normalized_answer_text: str, answer_type: str, requires_image: bool, image_qualities: Sequence[Dict[str, Any]], choices: Dict[str, str], variant_count: int, text_structure: Dict[str, Any], alignment_record: Dict[str, Any], solvability_report: Dict[str, Any]) -> Dict[str, Any]:
        keyword_hits = len(re.findall(r"\b(calculate|determine|find|derive|prove|which|what|if|compute|write|求|计算|判断)\b", normalized_question_text, flags=re.IGNORECASE))
        math_hits = len(re.findall(r"[=+\-*/^()]", normalized_question_text))
        best_readability = max((quality.get("readability_score", 0.0) for quality in image_qualities), default=0.0)
        multimodal_strength = 0.18 + 0.42 * int(requires_image) + 0.15 * bool(text_structure.get("requires_visual_grounding")) + 0.15 * alignment_record.get("consistency_score", 0.0) + 0.10 * clamp(best_readability)
        multi_step = 0.18 + 0.18 * clamp(keyword_hits / 4.0) + 0.18 * clamp(math_hits / 20.0) + 0.18 * clamp(len(text_structure.get("conditions", [])) / 4.0) + 0.10 * clamp(len(text_structure.get("targets", [])) / 2.0) + 0.08 * clamp(variant_count / 3.0)
        verifiability = 0.22 + 0.20 * solvability_report.get("score_breakdown", {}).get("answer_verifiable", 0.0) + 0.16 * solvability_report.get("score_breakdown", {}).get("target_clear", 0.0) + 0.14 * solvability_report.get("score_breakdown", {}).get("rewrite_complete", 0.0) + 0.14 * alignment_record.get("consistency_score", 0.0) + 0.14 * int(bool(normalized_answer_text))
        if answer_type == "numeric":
            verifiability += 0.08
        elif answer_type == "option":
            verifiability += 0.06
        review_priority = "high" if alignment_record.get("alignment_status") != "good" or solvability_report.get("decision_hint") != "pass" or len(image_qualities) > 1 or variant_count > 1 else "normal"
        return {
            "requires_image": requires_image,
            "multimodal_strength_score": round(clamp(multimodal_strength), 4),
            "multi_step_score": round(clamp(multi_step), 4),
            "verifiability_score": round(clamp(verifiability), 4),
            "review_priority": review_priority,
        }

    def process_sample(self, spec: DatasetSpec, sample: UnifiedSample, image_dir: Path, crop_dir: Path) -> Dict[str, Any]:
        preprocessed = preprocess_sample(self, spec, sample, image_dir)
        rewritten = rewrite_sample(self, spec, sample, preprocessed)
        extracted = extract_sample_structure(self, sample, preprocessed, rewritten["open_variants"])
        return finalize_cleaning_sample(self, spec, sample, crop_dir, preprocessed, extracted, rewritten)


def main() -> None:
    args = parse_args()
    config = PipelineConfig.from_yaml(args.config)
    config = merge_cli_overrides(config, args)
    ensure_dir(Path(config.output_root))
    setup = build_setup_context(config, ensure_dir=ensure_dir, stable_digest=stable_digest, utc_now=utc_now)
    pipeline = MultiDatasetCleaningPipeline(setup)
    summary = pipeline.run()
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
