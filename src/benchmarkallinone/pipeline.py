#!/usr/bin/env python3
"""多数据集数据采集与清洗智能体流水线。"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import io
import json
import math
import os
import re
import shutil
import subprocess
import threading
import time
import http.client
import ssl
import unicodedata
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
import yaml
from datasets import Dataset, DatasetDict, IterableDatasetDict, load_dataset
from PIL import Image

try:
    from .cleaning_semantics import (
        AlignmentEngine,
        SolvabilityChecker,
        TextContextParser,
        VisualParser,
        normalize_structured_text,
    )
except ImportError:
    from cleaning_semantics import (
        AlignmentEngine,
        SolvabilityChecker,
        TextContextParser,
        VisualParser,
        normalize_structured_text,
    )


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


def canonicalize_answer_text(text: Any) -> str:
    value = normalize_whitespace(to_plain_text(text))
    if not value:
        return ""
    value = re.sub(r"[。．\.,，；;:：!?！？]+$", "", value)
    value = re.sub(r"\s+", "", value)
    return value.casefold()


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
    reasoning_effort: str = "high"
    temperature: float = 0.1
    timeout_seconds: int = 180
    enabled: bool = True
    api_mode: str = "chat_completions"


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
    answer_index_base: Optional[int] = None
    multi_solution_mode: str = "auto"


@dataclass
class PipelineConfig:
    sample_per_dataset: int = 30
    sample_strategy: str = "head"
    shuffle_seed: int = 42
    sample_concurrency: int = 1
    output_root: str = "benchmarkallinone/outputs/multidataset_cleaning"
    cleaning_version: str = "v3.1.0"
    batch_id_prefix: str = "benchmarkallinone-clean"
    save_sample_bundle: bool = True
    git_cache_root: str = "benchmarkallinone/outputs/repo_cache"
    model: ModelConfig = field(default_factory=ModelConfig)
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
                answer_index_base=0,
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
        datasets_raw = raw.get("datasets", [])
        datasets = [DatasetSpec(**item) for item in datasets_raw] if datasets_raw else cls.default_dataset_specs()
        return cls(
            sample_per_dataset=runtime.get("sample_per_dataset", 30),
            sample_strategy=runtime.get("sample_strategy", "head"),
            shuffle_seed=runtime.get("shuffle_seed", 42),
            sample_concurrency=max(1, int(runtime.get("sample_concurrency", 1) or 1)),
            output_root=runtime.get("output_root", "outputs/multidataset_cleaning"),
            cleaning_version=runtime.get("cleaning_version", "v3.0.0"),
            batch_id_prefix=runtime.get("batch_id_prefix", "multidataset-clean"),
            save_sample_bundle=runtime.get("save_sample_bundle", True),
            git_cache_root=runtime.get("git_cache_root", "outputs/repo_cache"),
            model=ModelConfig(**{**asdict(ModelConfig()), **model_raw}),
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
        self._usage_lock = threading.Lock()
        self.usage_totals: Dict[str, Any] = {
            "request_count": 0,
            "successful_request_count": 0,
            "failed_request_count": 0,
            "retry_count": 0,
            "text_request_count": 0,
            "multimodal_request_count": 0,
            "requests_with_usage": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "cached_tokens": 0,
            "reasoning_tokens": 0,
            "total_request_seconds": 0.0,
            "last_error": None,
        }

    def snapshot_usage(self) -> Dict[str, Any]:
        with self._usage_lock:
            return {
                **self.usage_totals,
                "total_request_seconds": round(float(self.usage_totals.get("total_request_seconds", 0.0)), 3),
            }

    def usage_delta(self, before: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        baseline = before or {}
        after = self.snapshot_usage()
        delta: Dict[str, Any] = {}
        for key, value in after.items():
            if key == "last_error":
                continue
            previous = baseline.get(key, 0)
            if isinstance(value, float) or isinstance(previous, float):
                delta[key] = round(float(value) - float(previous), 3)
            else:
                delta[key] = int(value) - int(previous)
        delta["last_error"] = after.get("last_error")
        return delta

    def get_usage_summary(self) -> Dict[str, Any]:
        return self.snapshot_usage()

    def _extract_usage(self, body: Dict[str, Any]) -> Dict[str, int]:
        usage = body.get("usage") or {}
        prompt_details = usage.get("prompt_tokens_details") or usage.get("input_tokens_details") or {}
        completion_details = usage.get("completion_tokens_details") or usage.get("output_tokens_details") or {}
        prompt_tokens = usage.get("prompt_tokens", usage.get("input_tokens", 0)) or 0
        completion_tokens = usage.get("completion_tokens", usage.get("output_tokens", 0)) or 0
        total_tokens = usage.get("total_tokens", 0) or (prompt_tokens + completion_tokens)
        cached_tokens = prompt_details.get("cached_tokens", 0) or 0
        reasoning_tokens = completion_details.get("reasoning_tokens", 0) or 0
        return {
            "prompt_tokens": int(prompt_tokens),
            "completion_tokens": int(completion_tokens),
            "total_tokens": int(total_tokens),
            "cached_tokens": int(cached_tokens),
            "reasoning_tokens": int(reasoning_tokens),
        }

    def _build_payload(self, system_prompt: str, user_content: Any) -> Dict[str, Any]:
        return {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            "temperature": self.config.temperature,
            "response_format": {"type": "json_object"},
            "reasoning_effort": self.config.reasoning_effort,
            "stream": True,
        }

    def _build_responses_payload(self, system_prompt: str, user_content: Any) -> Dict[str, Any]:
        def to_responses_parts(content: Any) -> List[Dict[str, Any]]:
            parts: List[Dict[str, Any]] = []
            if isinstance(content, list):
                for item in content:
                    if not isinstance(item, dict):
                        continue
                    item_type = item.get("type")
                    if item_type == "text":
                        text_value = to_plain_text(item.get("text"))
                        if text_value:
                            parts.append({"type": "input_text", "text": text_value})
                    elif item_type == "image_url":
                        image_url = item.get("image_url") or {}
                        url_value = to_plain_text(image_url.get("url"))
                        if url_value:
                            parts.append({"type": "input_image", "image_url": url_value})
            else:
                text_value = to_plain_text(content)
                if text_value:
                    parts.append({"type": "input_text", "text": text_value})
            return parts or [{"type": "input_text", "text": "{}"}]

        return {
            "model": self.config.model,
            "input": [
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": system_prompt or ""}],
                },
                {
                    "role": "user",
                    "content": to_responses_parts(user_content),
                },
            ],
            "reasoning": {"effort": self.config.reasoning_effort},
            "stream": True,
        }

    def _read_sse_text(self, response: Any) -> str:
        chunks: List[str] = []
        for raw_line in response:
            try:
                line = raw_line.decode("utf-8", errors="ignore").strip()
            except Exception:
                continue
            if not line.startswith("data:"):
                continue
            data = line[5:].strip()
            if not data or data == "[DONE]":
                continue
            try:
                event = json.loads(data)
            except json.JSONDecodeError:
                continue
            event_type = event.get("type")
            if event_type == "response.output_text.delta":
                delta = to_plain_text(event.get("delta"))
                if delta:
                    chunks.append(delta)
            elif event_type in {"response.completed", "response.output_text.done"}:
                continue
        return "".join(chunks)

    def _post_responses(self, payload: Dict[str, Any], has_images: bool = False) -> Optional[Dict[str, Any]]:
        if not self.config.enabled or not self.config.api_key:
            return None
        with self._usage_lock:
            self.usage_totals["request_count"] += 1
            if has_images:
                self.usage_totals["multimodal_request_count"] += 1
            else:
                self.usage_totals["text_request_count"] += 1
        url = self.config.base_url.rstrip("/") + "/responses"
        last_error_text = None
        for attempt in range(1, 4):
            started = time.perf_counter()
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Accept": "text/event-stream",
                    "Connection": "close",
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                    "Authorization": f"Bearer {self.config.api_key}",
                },
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=self.config.timeout_seconds) as response:
                    content = self._read_sse_text(response)
            except urllib.error.HTTPError as exc:
                elapsed_seconds = time.perf_counter() - started
                with self._usage_lock:
                    self.usage_totals["failed_request_count"] += 1
                    self.usage_totals["total_request_seconds"] += elapsed_seconds
                try:
                    error_body = exc.read().decode("utf-8", errors="ignore")
                except Exception:
                    error_body = ""
                last_error_text = f"HTTP {exc.code}: {error_body[:240] or exc.reason}"
                retryable = exc.code in {408, 409, 429} or exc.code >= 500
                if retryable and attempt < 3:
                    with self._usage_lock:
                        self.usage_totals["retry_count"] += 1
                    time.sleep(min(2.0, 0.5 * attempt))
                    continue
                with self._usage_lock:
                    self.usage_totals["last_error"] = last_error_text
                return None
            except (urllib.error.URLError, http.client.RemoteDisconnected, ConnectionResetError, BrokenPipeError, ssl.SSLError, TimeoutError, json.JSONDecodeError) as exc:
                elapsed_seconds = time.perf_counter() - started
                with self._usage_lock:
                    self.usage_totals["failed_request_count"] += 1
                    self.usage_totals["total_request_seconds"] += elapsed_seconds
                last_error_text = f"{type(exc).__name__}: {exc}"
                if attempt < 3:
                    with self._usage_lock:
                        self.usage_totals["retry_count"] += 1
                    time.sleep(min(2.0, 0.5 * attempt))
                    continue
                with self._usage_lock:
                    self.usage_totals["last_error"] = last_error_text
                return None
            elapsed_seconds = time.perf_counter() - started
            parsed = extract_json_object(to_plain_text(content))
            if not parsed:
                with self._usage_lock:
                    self.usage_totals["failed_request_count"] += 1
                    self.usage_totals["total_request_seconds"] += elapsed_seconds
                    self.usage_totals["last_error"] = "Response missing JSON object."
                return None
            with self._usage_lock:
                self.usage_totals["successful_request_count"] += 1
                self.usage_totals["total_request_seconds"] += elapsed_seconds
                self.usage_totals["last_error"] = None
            parsed["_llm_usage"] = {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "cached_tokens": 0,
                "reasoning_tokens": 0,
            }
            parsed["_llm_elapsed_seconds"] = round(elapsed_seconds, 3)
            parsed["_llm_request_mode"] = "multimodal" if has_images else "text"
            return parsed
        with self._usage_lock:
            self.usage_totals["last_error"] = last_error_text
        return None

    def image_to_data_url(self, image: Image.Image) -> str:
        buffer = io.BytesIO()
        image.convert("RGB").save(buffer, format="PNG")
        encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{encoded}"

    def chat_json_parts(self, system_prompt: str, user_parts: Sequence[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        content_parts: List[Dict[str, Any]] = []
        for item in user_parts:
            if not isinstance(item, dict):
                continue
            part_type = item.get("type")
            if part_type == "text":
                text_value = to_plain_text(item.get("text"))
                if text_value:
                    content_parts.append({"type": "text", "text": text_value})
            elif part_type == "image":
                image = item.get("image")
                if isinstance(image, Image.Image):
                    content_parts.append(
                        {
                            "type": "image_url",
                            "image_url": {"url": self.image_to_data_url(image)},
                        }
                    )
            elif part_type == "image_url":
                url_value = to_plain_text(item.get("url"))
                if url_value:
                    content_parts.append({"type": "image_url", "image_url": {"url": url_value}})
        if not content_parts:
            content_parts = [{"type": "text", "text": "{}"}]
        has_images = any(part.get("type") == "image_url" for part in content_parts)
        if self.config.api_mode == "responses":
            return self._post_responses(self._build_responses_payload(system_prompt, content_parts), has_images=has_images)
        return self._post_json(self._build_payload(system_prompt, content_parts), has_images=has_images)

    def chat_json(self, system_prompt: str, user_prompt: str) -> Optional[Dict[str, Any]]:
        return self.chat_json_parts(system_prompt, [{"type": "text", "text": user_prompt}])

    def chat_json_with_images(self, system_prompt: str, user_prompt: str, images: Sequence[Image.Image]) -> Optional[Dict[str, Any]]:
        user_parts: List[Dict[str, Any]] = [{"type": "text", "text": user_prompt}]
        for image in list(images)[:3]:
            if isinstance(image, Image.Image):
                user_parts.append({"type": "image", "image": image})
        return self.chat_json_parts(system_prompt, user_parts)


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
        normalized = normalize_whitespace(question_text)
        if self.IMAGE_HINT_PATTERN.search(normalized):
            return True
        if re.search(r"<image\d*>|imagehere", normalized, flags=re.IGNORECASE):
            return True
        if image_count <= 0:
            return False
        implicit_visual_patterns = [
            r"\b(as shown|shown below|in the figure|according to the graph|based on the diagram)\b",
            r"\b(waveform|circuit|triangle|angle|point|line|curve|coordinate|shape)\b",
            r"(下图|如图|图中|示意图|曲线|电路图|几何图形|坐标系)",
        ]
        return any(re.search(pattern, normalized, flags=re.IGNORECASE) for pattern in implicit_visual_patterns)

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
    def __init__(self, spec: DatasetSpec, config: PipelineConfig, llm_client: Optional[OpenAICompatibleClient] = None):
        self.spec = spec
        self.config = config
        self.llm_client = llm_client or OpenAICompatibleClient(config.model)
        self._source_intake_agent: Optional[SourceIntakeAgent] = None

    def extract_record_content(self, row: Dict[str, Any]) -> Dict[str, Any]:
        if self._source_intake_agent is None:
            self._source_intake_agent = SourceIntakeAgent(self.llm_client)
        return self._source_intake_agent.extract(row, self.spec)

    def sample(self) -> Tuple[str, List[UnifiedSample], Optional[str]]:
        raise NotImplementedError


class SourceUnavailableConnector(BaseConnector):
    def sample(self) -> Tuple[str, List[UnifiedSample], Optional[str]]:
        return "source_unavailable", [], "No stable programmatic public source configured"


PROJECT_ROOT = Path(__file__).resolve().parents[2]
WORKSPACE_ROOT = PROJECT_ROOT.parent
PROMPT_ROOT = PROJECT_ROOT / "prompts"
COLLECTION_PROMPT_ROOT = PROMPT_ROOT / "collection"
CLEANING_PROMPT_ROOT = PROMPT_ROOT / "cleaning"
UNIFIED_EXTRACTION_PROMPT_PATH = PROMPT_ROOT / "extract_unified_sample.md"
LEGACY_EXTRACTION_PROMPT_PATH = PROMPT_ROOT / "extract_question_answer_image.md"
SOURCE_INTAKE_PROMPT_PATH = UNIFIED_EXTRACTION_PROMPT_PATH
ASSET_REGISTRY_PROMPT_PATH = COLLECTION_PROMPT_ROOT / "asset_registry.md"
POTENTIAL_SCORER_PROMPT_PATH = COLLECTION_PROMPT_ROOT / "potential_scorer.md"
CANDIDATE_REGISTRAR_PROMPT_PATH = COLLECTION_PROMPT_ROOT / "candidate_registrar.md"
REWRITE_AGENT_PROMPT_PATH = CLEANING_PROMPT_ROOT / "rewrite_agent.md"
NORMALIZATION_AGENT_PROMPT_PATH = CLEANING_PROMPT_ROOT / "normalization_agent.md"
SAMPLE_UNDERSTANDING_PROMPT_PATH = CLEANING_PROMPT_ROOT / "sample_understanding_agent.md"
GATE_DECISION_PROMPT_PATH = CLEANING_PROMPT_ROOT / "gate_decision_agent.md"


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
    reasoning_chain_field = choose_candidate_field(
        row,
        spec.metadata_fields or ["reasoning_chain", "chain_of_thought", "cot", "rationale", "explanation"],
        r"reasoning_chain|chain_of_thought|cot|rationale|explanation",
    )
    raw_question = to_plain_text(row.get(question_field)) if question_field else ""
    raw_answer = to_plain_text(row.get(answer_field)) if answer_field else ""
    if is_null_like_text(raw_answer):
        raw_answer = ""
    reasoning_chain = normalize_whitespace(to_plain_text(row.get(reasoning_chain_field))) if reasoning_chain_field else ""
    if is_null_like_text(reasoning_chain):
        reasoning_chain = ""
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
        "reasoning_chain": reasoning_chain,
        "has_reasoning_chain": bool(reasoning_chain),
        "choice_map": choice_map,
        "image_paths": image_paths,
        "force_requires_image": force_requires_image,
        "extraction_notes": ["heuristic_field_extraction"],
        "question_field": question_field,
        "answer_field": answer_field,
        "image_field": image_field,
        "choice_field": choice_field,
        "reasoning_chain_field": reasoning_chain_field,
    }


def prompt_extract_record_content(row: Dict[str, Any], spec: "DatasetSpec", client: "OpenAICompatibleClient") -> Dict[str, Any]:
    fallback = heuristic_extract_record_content(row, spec)
    prompt_path = UNIFIED_EXTRACTION_PROMPT_PATH if UNIFIED_EXTRACTION_PROMPT_PATH.exists() else LEGACY_EXTRACTION_PROMPT_PATH
    if not client.config.enabled or not client.config.api_key or not prompt_path.exists():
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
        return fallback
    raw_question_text = normalize_whitespace(to_plain_text(result.get("raw_question_text") or result.get("question_text") or fallback["raw_question_text"]))
    raw_answer_text = normalize_whitespace(to_plain_text(result.get("raw_answer_text") or result.get("answer_text") or fallback["raw_answer_text"]))
    choice_map = parse_choice_map(result.get("choice_map")) or fallback["choice_map"]
    image_paths = normalize_image_path_list(result.get("image_paths")) or fallback["image_paths"]
    force_requires_image = result.get("force_requires_image")
    if not isinstance(force_requires_image, bool):
        force_requires_image = fallback["force_requires_image"]
    extraction_notes = result.get("extraction_notes")
    if not isinstance(extraction_notes, list):
        extraction_notes = []
    extraction_notes = [to_plain_text(item) for item in extraction_notes if to_plain_text(item)]
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



def resolve_answer_source_text(row: Dict[str, Any], extracted: Dict[str, Any]) -> str:
    answer_field = extracted.get("answer_field")
    if isinstance(answer_field, str) and answer_field in row and not is_missing_value(row.get(answer_field)):
        return to_plain_text(row.get(answer_field))
    return to_plain_text(extracted.get("raw_answer_text"))



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
                raw_index = int(numeric_match.group(0))
            except ValueError:
                raw_index = None
            if raw_index is not None:
                choice_labels = [label for label in sorted(choice_map.keys()) if re.fullmatch(r"[A-H]", label)]
                resolved_index = raw_index - int(answer_index_base)
                if 0 <= resolved_index < len(choice_labels):
                    mapped_label = choice_labels[resolved_index]
                    mapped_answer = normalize_whitespace(choice_map.get(mapped_label, ""))
                    if mapped_answer:
                        return mapped_answer
    mixed_match = re.match(r"^\(?([A-Z])\)?[\s.、:_-]+(.+)$", answer, flags=re.IGNORECASE)
    if mixed_match and choice_map:
        label = mixed_match.group(1).upper()
        suffix = normalize_whitespace(mixed_match.group(2))
        choice_text = normalize_whitespace(choice_map.get(label, ""))
        if choice_text and (suffix == choice_text or suffix.casefold() == choice_text.casefold()):
            return choice_text
    return normalize_whitespace(answer)


def rewrite_answer_consistency_flags(normalized_answer_text: str, rewrite_report: Dict[str, Any], open_variants: Sequence[Dict[str, Any]]) -> List[str]:
    strategy = to_plain_text(rewrite_report.get("strategy")).strip().lower()
    if strategy not in {"blank_open", "keep_open"}:
        return []
    if len(open_variants) != 1:
        return []
    variant = open_variants[0] if isinstance(open_variants[0], dict) else {}
    expected_answer = to_plain_text(variant.get("expected_answer"))
    if canonicalize_answer_text(expected_answer) == canonicalize_answer_text(normalized_answer_text):
        return []
    return ["rewrite_expected_answer_mismatch", "answer_annotation_inconsistent", "gold_answer_mismatch"]


def rewrite_question_residual_flags(rewrite_report: Dict[str, Any], open_variants: Sequence[Dict[str, Any]]) -> List[str]:
    strategy = to_plain_text(rewrite_report.get("strategy")).strip().lower()
    if strategy not in {"blank_open", "keep_open"}:
        return []
    if len(open_variants) != 1:
        return []
    variant = open_variants[0] if isinstance(open_variants[0], dict) else {}
    rewritten_question = to_plain_text(variant.get("rewritten_question_text"))
    if not rewritten_question:
        return ["rewrite_missing_question_text"]
    if re.search(r"\b(which of the following|following statements?|following intervals?|which statement|which option|among the following)\b", rewritten_question, flags=re.IGNORECASE):
        return ["rewrite_mcq_residual"]
    return []


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
        for index, row in enumerate(self.iter_records(path)):
            extracted = self.extract_record_content(row)
            raw_question = extracted["raw_question_text"]
            raw_answer = resolve_multiple_choice_answer_text(
                resolve_answer_source_text(row, extracted),
                extracted["choice_map"],
                self.spec.answer_index_base,
            )
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
                        "reasoning_chain_field": extracted.get("reasoning_chain_field"),
                        "reasoning_chain": extracted.get("reasoning_chain", ""),
                        "has_reasoning_chain": bool(extracted.get("has_reasoning_chain", False)),
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
        with jsonl_path.open("r", encoding="utf-8") as file:
            for index, line in enumerate(file):
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                if not isinstance(row, dict):
                    continue
                extracted = self.extract_record_content(row)
                raw_question = extracted["raw_question_text"]
                raw_answer = resolve_multiple_choice_answer_text(
                    self.resolve_answer_text(row.get("solution") or resolve_answer_source_text(row, extracted)),
                    extracted["choice_map"],
                    self.spec.answer_index_base,
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
                            "extraction_notes": extracted.get("extraction_notes", []) + ["hf_raw_mm_math_fallback"],
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
        for index, problem_path in enumerate(problem_files):
            try:
                data = json.loads(problem_path.read_text(encoding="utf-8"))
            except Exception:
                continue
            if not isinstance(data, dict):
                continue
            qs = data.get("question_structure") if isinstance(data.get("question_structure"), dict) else {}
            context = to_plain_text(qs.get("context"))
            sub_questions = [to_plain_text(qs.get(key)) for key in sorted(qs.keys()) if key.startswith("sub_question")]
            question_text = context
            if sub_questions:
                question_text = (question_text + "\n\n" if question_text else "") + "\n".join(
                    f"{idx + 1}. {item}" for idx, item in enumerate(sub_questions) if item
                )
            raw_answer = resolve_multiple_choice_answer_text(self.resolve_answer_text(data.get("answer")), {})
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
                        "extraction_notes": ["hf_raw_physreason_fallback"],
                        "difficulty": data.get("difficulty"),
                    },
                    choice_map={},
                    force_requires_image=bool(image_sources),
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
        for index, row in enumerate(rows):
            row = dict(row)
            extracted = self.extract_record_content(row)
            raw_question = extracted["raw_question_text"]
            raw_answer = resolve_multiple_choice_answer_text(
                self.resolve_answer_text(resolve_answer_source_text(row, extracted)),
                extracted["choice_map"],
                self.spec.answer_index_base,
            )
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
                        "reasoning_chain_field": extracted.get("reasoning_chain_field"),
                        "reasoning_chain": extracted.get("reasoning_chain", ""),
                        "has_reasoning_chain": bool(extracted.get("has_reasoning_chain", False)),
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
                if re.search(r"data/geometry3k/(train|test|val)\.zip$", rel):
                    score += 40
                if re.search(r"annotation_tool/data_collection/data_examples/\d+/data\.json$", rel):
                    score += 30
                if re.search(r"diagram_parser/detection/.*\.csv$", rel):
                    score -= 50
                if rel.endswith("logic_form.json"):
                    score -= 10
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

    def sample_from_geometry3k_zip(self, repo_dir: Path) -> Tuple[str, List[UnifiedSample], Optional[str]]:
        import zipfile

        preferred_split = (self.spec.split or "test").strip().lower()
        preferred_split = {"valid": "val", "validation": "val"}.get(preferred_split, preferred_split)
        candidate_specs: List[Tuple[str, Path]] = []
        if preferred_split in {"train", "test", "val"}:
            candidate_specs.append((preferred_split, repo_dir / "data" / "geometry3k" / f"{preferred_split}.zip"))
        for split_name in ["test", "val", "train"]:
            candidate = (split_name, repo_dir / "data" / "geometry3k" / f"{split_name}.zip")
            if candidate not in candidate_specs:
                candidate_specs.append(candidate)

        chosen_split: Optional[str] = None
        zip_path: Optional[Path] = None
        for split_name, candidate_path in candidate_specs:
            if candidate_path.exists():
                chosen_split = split_name
                zip_path = candidate_path
                break
        if zip_path is None or chosen_split is None:
            return "source_unavailable", [], "No Geometry3K split zip found under data/geometry3k"

        samples: List[UnifiedSample] = []
        with zipfile.ZipFile(zip_path) as zf:
            problem_members = sorted(
                name for name in zf.namelist() if name.startswith(f"{chosen_split}/") and name.endswith("/data.json")
            )
            if not problem_members:
                return "source_unavailable", [], f"No data.json entries found in {zip_path.name}"
            for index, member in enumerate(problem_members):
                try:
                    data = json.loads(zf.read(member).decode("utf-8"))
                except Exception:
                    continue
                if not isinstance(data, dict):
                    continue
                problem_dir = str(Path(member).parent).replace("\\", "/")
                question_text = normalize_whitespace(
                    to_plain_text(
                        data.get("annotat_text")
                        or data.get("compact_text")
                        or data.get("problem_text")
                        or data.get("question")
                    )
                )
                choice_source = data.get("choices") or data.get("compact_choices")
                choice_map = parse_choice_map(choice_source)
                raw_answer = resolve_multiple_choice_answer_text(
                    to_plain_text(data.get("answer") or data.get("label") or data.get("solution")),
                    choice_map,
                    self.spec.answer_index_base,
                )
                images: List[Image.Image] = []
                image_sources: List[str] = []
                for candidate_name in ["img_diagram.png", "img_problem.png"]:
                    image_member = f"{problem_dir}/{candidate_name}"
                    if image_member not in zf.namelist():
                        continue
                    try:
                        images.append(Image.open(io.BytesIO(zf.read(image_member))).convert("RGB"))
                        image_sources.append(image_member)
                    except Exception:
                        continue
                if not question_text and not images:
                    continue
                question_field = "annotat_text" if data.get("annotat_text") else "compact_text" if data.get("compact_text") else "problem_text" if data.get("problem_text") else "question"
                answer_field = "answer" if data.get("answer") is not None else "label" if data.get("label") is not None else "solution"
                choice_field = "choices" if data.get("choices") is not None else "compact_choices" if data.get("compact_choices") is not None else None
                samples.append(
                    UnifiedSample(
                        dataset_key=self.spec.key,
                        dataset_display_name=self.spec.display_name,
                        subject=self.spec.subject,
                        source_dataset=self.spec.display_name,
                        source_split=chosen_split,
                        source_problem_id=str(data.get("id", Path(problem_dir).name)),
                        raw_question_text=question_text,
                        raw_answer_text=raw_answer,
                        images=images,
                        image_sources=image_sources,
                        raw_record=data,
                        metadata={
                            "row_index": index,
                            "data_file": f"{zip_path.relative_to(repo_dir)}::{member}",
                            "image_paths": image_sources,
                            "extraction_notes": ["geometry3k_zip_extraction"],
                            "question_field": question_field,
                            "answer_field": answer_field,
                            "image_field": "zip_members",
                            "choice_field": choice_field,
                        },
                        choice_map=choice_map,
                        force_requires_image=True,
                    )
                )
                if self.config.sample_strategy != "random" and len(samples) >= self.config.sample_per_dataset:
                    break
        if not samples:
            return "source_unavailable", [], f"No usable Geometry3K samples extracted from {zip_path.name}"
        if self.config.sample_strategy == "random":
            rng = np.random.default_rng(self.config.shuffle_seed)
            indices = rng.permutation(len(samples)).tolist()[: self.config.sample_per_dataset]
            samples = [samples[i] for i in indices]
        else:
            samples = samples[: self.config.sample_per_dataset]
        return "available", samples, chosen_split

    def sample(self) -> Tuple[str, List[UnifiedSample], Optional[str]]:
        repo_dir, error = self.ensure_repo()
        if repo_dir is None:
            return "source_unavailable", [], error or "git clone failed"
        if self.spec.key == "geometry3k":
            source_status, samples, detail = self.sample_from_geometry3k_zip(repo_dir)
            if source_status == "available" and samples:
                return source_status, samples, detail
        files = self.discover_data_files(repo_dir)
        if not files:
            return "source_unavailable", [], "No structured data files discovered in repository"
        samples: List[UnifiedSample] = []
        detail_errors: List[str] = []
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
                extracted = self.extract_record_content(row)
                raw_question = extracted["raw_question_text"]
                raw_answer = resolve_multiple_choice_answer_text(
                    resolve_answer_source_text(row, extracted),
                    extracted["choice_map"],
                    self.spec.answer_index_base,
                )
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

class BaseStructuredAgent:
    def __init__(self, client: OpenAICompatibleClient, prompt_path: Path, fallback_system_prompt: str):
        self.client = client
        self.prompt_path = prompt_path
        self.fallback_system_prompt = fallback_system_prompt

    def load_system_prompt(self) -> str:
        if self.prompt_path.exists():
            return read_prompt(self.prompt_path)
        return self.fallback_system_prompt

    def call_json(self, payload: Dict[str, Any], images: Optional[Sequence[Image.Image]] = None) -> Optional[Dict[str, Any]]:
        user_prompt = json.dumps(payload, ensure_ascii=False, indent=2, default=json_default)
        if images:
            return self.client.chat_json_with_images(self.load_system_prompt(), user_prompt, images)
        return self.client.chat_json(self.load_system_prompt(), user_prompt)


class SourceIntakeAgent(BaseStructuredAgent):
    def __init__(self, client: OpenAICompatibleClient):
        super().__init__(
            client,
            SOURCE_INTAKE_PROMPT_PATH,
            "You are the Source Intake Agent. Extract question text, answer text, choices, image paths, and image dependency from a raw sample. Return strict JSON only.",
        )

    def extract(self, row: Dict[str, Any], spec: DatasetSpec) -> Dict[str, Any]:
        fallback = heuristic_extract_record_content(row, spec)
        if not self.client.config.enabled or not self.client.config.api_key:
            return fallback
        llm_result = self.call_json(
            {
                "dataset_name": spec.display_name,
                "source_kind": spec.source_kind,
                "raw_record": row,
                "fallback": fallback,
            }
        )
        if not llm_result:
            return fallback
        raw_question_text = normalize_whitespace(
            to_plain_text(llm_result.get("raw_question_text") or llm_result.get("question_text") or fallback["raw_question_text"])
        )
        raw_answer_text = normalize_whitespace(
            to_plain_text(llm_result.get("raw_answer_text") or llm_result.get("answer_text") or fallback["raw_answer_text"])
        )
        choice_map = parse_choice_map(llm_result.get("choice_map")) or fallback["choice_map"]
        image_paths = normalize_image_path_list(llm_result.get("image_paths")) or fallback["image_paths"]
        force_requires_image = llm_result.get("force_requires_image")
        if not isinstance(force_requires_image, bool):
            force_requires_image = fallback["force_requires_image"]
        extraction_notes = llm_result.get("extraction_notes")
        if not isinstance(extraction_notes, list):
            extraction_notes = []
        extraction_notes = [to_plain_text(item) for item in extraction_notes if to_plain_text(item)]
        extraction_notes.append("source_intake_agent")
        return {
            **fallback,
            "raw_question_text": raw_question_text or fallback["raw_question_text"],
            "raw_answer_text": raw_answer_text or fallback["raw_answer_text"],
            "reasoning_chain": normalize_whitespace(to_plain_text(llm_result.get("reasoning_chain") or fallback.get("reasoning_chain") or "")),
            "has_reasoning_chain": bool(normalize_whitespace(to_plain_text(llm_result.get("reasoning_chain") or fallback.get("reasoning_chain") or ""))),
            "choice_map": choice_map,
            "image_paths": image_paths,
            "force_requires_image": force_requires_image,
            "extraction_notes": extraction_notes,
        }


class AssetRegistryAgent(BaseStructuredAgent):
    def __init__(self, client: OpenAICompatibleClient, normalizer: TextNormalizer):
        super().__init__(
            client,
            ASSET_REGISTRY_PROMPT_PATH,
            "You are the Asset Registry Agent. Audit question, answer, image, and metadata completeness for a candidate sample. Return strict JSON only.",
        )
        self.normalizer = normalizer

    def fallback_process(
        self,
        problem_id: str,
        question_text: str,
        answer_text: str,
        image_sources: Sequence[str],
        image_qualities: Sequence[Dict[str, Any]],
        metadata: Dict[str, Any],
        requires_image: bool,
        choice_count: int,
    ) -> Dict[str, Any]:
        image_manifest: List[Dict[str, Any]] = []
        image_total = max(len(image_sources), len(image_qualities))
        for index in range(image_total):
            source = image_sources[index] if index < len(image_sources) else f"inline://image_{index + 1}"
            quality = image_qualities[index] if index < len(image_qualities) else {}
            path = Path(source) if source and not str(source).startswith("inline://") else None
            exists = bool(quality.get("width") and quality.get("height")) or bool(path and path.exists())
            file_size = 0
            fmt = None
            if path and path.exists():
                try:
                    file_size = int(path.stat().st_size)
                except OSError:
                    file_size = 0
                fmt = path.suffix.lstrip(".") or None
            elif exists:
                fmt = "png"
            image_manifest.append(
                {
                    "path": to_plain_text(source),
                    "exists": exists,
                    "format": fmt,
                    "width": int(quality.get("width") or 0),
                    "height": int(quality.get("height") or 0),
                    "file_size": file_size,
                }
            )
        issues: List[str] = []
        if not question_text:
            issues.append("missing_question_text")
        if not answer_text:
            issues.append("missing_answer_text")
        has_image = any(item.get("exists") for item in image_manifest)
        if requires_image and not has_image:
            issues.append("missing_required_image")
        choice_required = bool(
            re.search(
                r"\b(which of the following|following statements?|following intervals?|which statement|which option|choices?)\b",
                question_text,
                flags=re.IGNORECASE,
            )
        )
        if choice_required and choice_count <= 0:
            issues.append("missing_choice_map")
        fallback = {
            "problem_id": problem_id,
            "image_manifest": image_manifest,
            "text_manifest": {
                "question_present": bool(question_text),
                "question_char_length": len(question_text),
                "language_hint": self.normalizer.detect_language(question_text),
            },
            "answer_manifest": {
                "answer_present": bool(answer_text),
                "answer_type": self.normalizer.infer_answer_type(answer_text),
                "answer_char_length": len(answer_text),
            },
            "issues": sorted(set(issues)),
            "registry_passed": bool(question_text) and bool(answer_text) and (has_image or not requires_image) and (not choice_required or choice_count > 0),
            "llm_used": False,
        }
        return fallback

    def process(
        self,
        problem_id: str,
        question_text: str,
        answer_text: str,
        image_sources: Sequence[str],
        image_qualities: Sequence[Dict[str, Any]],
        metadata: Dict[str, Any],
        requires_image: bool,
        choice_count: int,
    ) -> Dict[str, Any]:
        fallback = self.fallback_process(problem_id, question_text, answer_text, image_sources, image_qualities, metadata, requires_image, choice_count)
        if not self.client.config.enabled or not self.client.config.api_key:
            return fallback
        llm_result = self.call_json(
            {
                "problem_id": problem_id,
                "question_text": question_text,
                "answer_text": answer_text,
                "image_paths": list(image_sources),
                "choice_count": choice_count,
                "metadata": metadata,
                "asset_integrity": {
                    "requires_image": requires_image,
                    "image_quality_summaries": [
                        {
                            "width": quality.get("width"),
                            "height": quality.get("height"),
                            "readability_score": quality.get("readability_score"),
                            "contrast_score": quality.get("contrast_score"),
                        }
                        for quality in image_qualities
                    ],
                },
                "fallback": fallback,
            }
        )
        if not llm_result:
            return fallback
        image_manifest = llm_result.get("image_manifest")
        if not isinstance(image_manifest, list):
            image_manifest = fallback["image_manifest"]
        issues = llm_result.get("issues")
        if not isinstance(issues, list):
            issues = fallback["issues"]
        normalized_issues = [to_plain_text(item) for item in list(fallback["issues"]) + list(issues) if to_plain_text(item)]
        if choice_count > 0:
            normalized_issues = [
                item
                for item in normalized_issues
                if "choices are not provided" not in item.lower() and item.lower() != "missing_choice_map"
            ]
        text_manifest = llm_result.get("text_manifest") if isinstance(llm_result.get("text_manifest"), dict) else fallback["text_manifest"]
        answer_manifest = llm_result.get("answer_manifest") if isinstance(llm_result.get("answer_manifest"), dict) else fallback["answer_manifest"]
        return {
            "problem_id": problem_id,
            "image_manifest": image_manifest,
            "text_manifest": text_manifest,
            "answer_manifest": answer_manifest,
            "issues": sorted(set(normalized_issues)),
            "registry_passed": bool(fallback["registry_passed"]),
            "llm_used": True,
        }


class PotentialScorerAgent(BaseStructuredAgent):
    def __init__(self, client: OpenAICompatibleClient):
        super().__init__(
            client,
            POTENTIAL_SCORER_PROMPT_PATH,
            "You are the Potential Scorer Agent. Score image dependency, multi-step potential, and verifiability for a candidate sample. Return strict JSON only.",
        )

    def fallback_process(
        self,
        problem_id: str,
        normalized_question_text: str,
        normalized_answer_text: str,
        answer_type: str,
        requires_image: bool,
        text_dominant: bool,
        image_qualities: Sequence[Dict[str, Any]],
        choices: Dict[str, str],
        multi_solution_policy: Dict[str, Any],
        asset_registry_record: Dict[str, Any],
        fallback_scores: Dict[str, Any],
    ) -> Dict[str, Any]:
        risk_flags = list(asset_registry_record.get("issues", []))
        if not asset_registry_record.get("registry_passed", True):
            risk_flags.append("asset_registry_failed")
        if requires_image and not image_qualities:
            risk_flags.append("missing_required_image")
        return {
            "problem_id": problem_id,
            "image_dependency_score": round(float(fallback_scores.get("initial_image_dependency_score", 0.0)), 4),
            "multi_step_score": round(float(fallback_scores.get("initial_multi_solution_score", 0.0)), 4),
            "verifiability_score": round(float(fallback_scores.get("initial_verifiability_score", 0.0)), 4),
            "score_evidence": {
                "image_dependency": [
                    "requires_image=true" if requires_image else "requires_image=false",
                    f"image_count={len(image_qualities)}",
                    f"text_dominant={text_dominant}",
                ],
                "multi_step": [
                    f"multi_solution_policy={multi_solution_policy.get('mode', 'balanced')}",
                    f"choice_count={len(choices)}",
                    f"question_length={len(normalized_question_text)}",
                ],
                "verifiability": [
                    f"answer_type={answer_type}",
                    f"answer_present={bool(normalized_answer_text)}",
                    f"registry_passed={asset_registry_record.get('registry_passed', True)}",
                ],
            },
            "risk_flags": sorted(set(to_plain_text(flag) for flag in risk_flags if to_plain_text(flag))),
            "scoring_version": "fallback_v1",
            "llm_used": False,
        }

    def process(
        self,
        problem_id: str,
        normalized_question_text: str,
        normalized_answer_text: str,
        answer_type: str,
        requires_image: bool,
        text_dominant: bool,
        image_qualities: Sequence[Dict[str, Any]],
        choices: Dict[str, str],
        multi_solution_policy: Dict[str, Any],
        asset_registry_record: Dict[str, Any],
        fallback_scores: Dict[str, Any],
    ) -> Dict[str, Any]:
        fallback = self.fallback_process(
            problem_id,
            normalized_question_text,
            normalized_answer_text,
            answer_type,
            requires_image,
            text_dominant,
            image_qualities,
            choices,
            multi_solution_policy,
            asset_registry_record,
            fallback_scores,
        )
        if not self.client.config.enabled or not self.client.config.api_key:
            return fallback
        llm_result = self.call_json(
            {
                "problem_id": problem_id,
                "question_text": normalized_question_text,
                "answer_text": normalized_answer_text,
                "answer_type": answer_type,
                "requires_image": requires_image,
                "text_dominant": text_dominant,
                "choices": choices,
                "metadata": {
                    "multi_solution_policy": multi_solution_policy,
                    "image_quality_summaries": [
                        {
                            "width": quality.get("width"),
                            "height": quality.get("height"),
                            "readability_score": quality.get("readability_score"),
                            "contrast_score": quality.get("contrast_score"),
                        }
                        for quality in image_qualities
                    ],
                },
                "asset_registry_record": asset_registry_record,
                "fallback": fallback,
            }
        )
        if not llm_result:
            return fallback
        score_evidence = llm_result.get("score_evidence") if isinstance(llm_result.get("score_evidence"), dict) else fallback["score_evidence"]
        risk_flags = llm_result.get("risk_flags")
        if not isinstance(risk_flags, list):
            risk_flags = fallback["risk_flags"]
        def coerce_score(key: str) -> float:
            try:
                return round(clamp(float(llm_result.get(key))), 4)
            except (TypeError, ValueError):
                return fallback[key]
        return {
            "problem_id": problem_id,
            "image_dependency_score": coerce_score("image_dependency_score"),
            "multi_step_score": coerce_score("multi_step_score"),
            "verifiability_score": coerce_score("verifiability_score"),
            "score_evidence": score_evidence,
            "risk_flags": sorted(set(to_plain_text(flag) for flag in risk_flags if to_plain_text(flag))),
            "scoring_version": to_plain_text(llm_result.get("scoring_version") or "agent_v1"),
            "llm_used": True,
        }


class CandidateRegistrarAgent(BaseStructuredAgent):
    def __init__(self, client: OpenAICompatibleClient):
        super().__init__(
            client,
            CANDIDATE_REGISTRAR_PROMPT_PATH,
            "You are the Candidate Registrar Agent. Decide whether a sample should stay in the candidate pool and assign a priority. Return strict JSON only.",
        )

    def fallback_process(self, problem_id: str, asset_registry_record: Dict[str, Any], initial_scoring_record: Dict[str, Any]) -> Dict[str, Any]:
        priority = round(
            clamp(
                0.4 * float(initial_scoring_record.get("image_dependency_score", 0.0))
                + 0.3 * float(initial_scoring_record.get("multi_step_score", 0.0))
                + 0.3 * float(initial_scoring_record.get("verifiability_score", 0.0))
            ),
            4,
        )
        risk_flags = list(initial_scoring_record.get("risk_flags", []))
        issues = list(asset_registry_record.get("issues", []))
        question_present = bool((asset_registry_record.get("text_manifest") or {}).get("question_present"))
        answer_present = bool((asset_registry_record.get("answer_manifest") or {}).get("answer_present"))
        image_manifest = asset_registry_record.get("image_manifest") or []
        has_image = any(isinstance(item, dict) and item.get("exists") for item in image_manifest)
        recoverable_asset_state = answer_present and (question_present or has_image)
        if not asset_registry_record.get("registry_passed", True):
            if recoverable_asset_state:
                decision = "low_priority"
                reasons = sorted(
                    set(
                        [*issues, *risk_flags, "asset_incomplete_but_recoverable", "needs_ranked_follow_up"]
                    )
                )
            else:
                decision = "reject"
                reasons = sorted(set(issues or ["asset_registry_failed", "missing_core_assets"]))
        elif priority >= 0.62 and not risk_flags:
            decision = "keep"
            reasons = ["high_collection_value"]
        elif priority >= 0.35:
            decision = "low_priority"
            reasons = sorted(set((risk_flags or []) + ["needs_ranked_follow_up"]))
        else:
            decision = "reject"
            reasons = sorted(set((risk_flags or []) + ["low_collection_priority"]))
        return {
            "problem_id": problem_id,
            "priority": priority,
            "decision": decision,
            "decision_reasons": [to_plain_text(item) for item in reasons if to_plain_text(item)],
            "llm_used": False,
        }

    def process(self, problem_id: str, asset_registry_record: Dict[str, Any], initial_scoring_record: Dict[str, Any]) -> Dict[str, Any]:
        fallback = self.fallback_process(problem_id, asset_registry_record, initial_scoring_record)
        if not self.client.config.enabled or not self.client.config.api_key:
            return fallback
        llm_result = self.call_json(
            {
                "problem_id": problem_id,
                "asset_registry_record": asset_registry_record,
                "initial_scoring_record": initial_scoring_record,
                "fallback": fallback,
            }
        )
        if not llm_result:
            return fallback
        decision = to_plain_text(llm_result.get("decision")).strip().lower()
        if decision not in {"keep", "low_priority", "reject"}:
            decision = fallback["decision"]
        reasons = llm_result.get("decision_reasons")
        if not isinstance(reasons, list):
            reasons = fallback["decision_reasons"]
        try:
            priority = round(clamp(float(llm_result.get("priority"))), 4)
        except (TypeError, ValueError):
            priority = fallback["priority"]
        if decision == "reject" and fallback["decision"] == "low_priority":
            decision = fallback["decision"]
            reasons = fallback["decision_reasons"]
            priority = max(priority, fallback["priority"])
        return {
            "problem_id": problem_id,
            "priority": priority,
            "decision": decision,
            "decision_reasons": [to_plain_text(item) for item in reasons if to_plain_text(item)] or fallback["decision_reasons"],
            "llm_used": True,
        }


class NormalizationAgent(BaseStructuredAgent):
    def __init__(self, client: OpenAICompatibleClient, normalizer: TextNormalizer):
        super().__init__(
            client,
            NORMALIZATION_AGENT_PROMPT_PATH,
            "You are the Normalization Agent. Normalize question text, answer text, choices, and cleaning-path judgments for a candidate sample. Return strict JSON only.",
        )
        self.normalizer = normalizer

    def fallback_process(
        self,
        raw_question_text: str,
        raw_answer_text: str,
        choice_map: Dict[str, str],
        force_requires_image: bool,
        image_count: int,
    ) -> Dict[str, Any]:
        normalized_question_text = self.normalizer.strip_hint(self.normalizer.normalize_text(raw_question_text))
        normalized_answer_text = self.normalizer.normalize_answer(raw_answer_text)
        normalized_choice_map = parse_choice_map(choice_map) or dict(choice_map)
        requires_image = bool(force_requires_image or self.normalizer.infer_requires_image(normalized_question_text, image_count))
        text_dominant = not requires_image
        return {
            "normalized_question_text": normalized_question_text,
            "normalized_answer_text": normalized_answer_text,
            "normalized_choice_map": normalized_choice_map,
            "requires_image": requires_image,
            "text_dominant": text_dominant,
            "cleaning_path": "text_lightweight" if text_dominant else "multimodal_full",
            "normalization_notes": ["rule_based_normalization"],
            "llm_used": False,
        }

    def process(
        self,
        dataset_name: str,
        raw_question_text: str,
        raw_answer_text: str,
        choice_map: Dict[str, str],
        force_requires_image: bool,
        images: Sequence[Image.Image],
        image_qualities: Sequence[Dict[str, Any]],
    ) -> Dict[str, Any]:
        fallback = self.fallback_process(raw_question_text, raw_answer_text, choice_map, force_requires_image, len(images))
        if not self.client.config.enabled or not self.client.config.api_key:
            return fallback
        llm_result = self.call_json(
            {
                "dataset_name": dataset_name,
                "raw_question_text": raw_question_text,
                "raw_answer_text": raw_answer_text,
                "choice_map": choice_map,
                "force_requires_image": force_requires_image,
                "image_count": len(images),
                "image_quality_summaries": [
                    {
                        "width": quality.get("width"),
                        "height": quality.get("height"),
                        "readability_score": quality.get("readability_score"),
                        "contrast_score": quality.get("contrast_score"),
                        "crop_integrity_score": quality.get("crop_integrity_score"),
                    }
                    for quality in image_qualities
                ],
                "fallback": fallback,
            },
            images=images if images else None,
        )
        if not llm_result:
            return fallback
        normalized_question_text = normalize_whitespace(to_plain_text(llm_result.get("normalized_question_text") or fallback["normalized_question_text"])) or fallback["normalized_question_text"]
        normalized_answer_text = normalize_whitespace(to_plain_text(llm_result.get("normalized_answer_text") or fallback["normalized_answer_text"]))
        normalized_choice_map = parse_choice_map(llm_result.get("normalized_choice_map") or llm_result.get("choice_map")) or fallback["normalized_choice_map"]
        requires_image = llm_result.get("requires_image")
        if not isinstance(requires_image, bool):
            requires_image = fallback["requires_image"]
        text_dominant = llm_result.get("text_dominant")
        if not isinstance(text_dominant, bool):
            text_dominant = fallback["text_dominant"]
        cleaning_path = to_plain_text(llm_result.get("cleaning_path") or fallback["cleaning_path"]).strip() or fallback["cleaning_path"]
        if cleaning_path not in {"text_lightweight", "multimodal_full"}:
            cleaning_path = fallback["cleaning_path"]
        normalization_notes = llm_result.get("normalization_notes")
        if not isinstance(normalization_notes, list):
            normalization_notes = fallback["normalization_notes"]
        return {
            "normalized_question_text": normalized_question_text,
            "normalized_answer_text": normalized_answer_text,
            "normalized_choice_map": normalized_choice_map,
            "requires_image": requires_image,
            "text_dominant": text_dominant,
            "cleaning_path": cleaning_path,
            "normalization_notes": [to_plain_text(item) for item in normalization_notes if to_plain_text(item)] or fallback["normalization_notes"],
            "llm_used": True,
        }


class SampleUnderstandingAgent(BaseStructuredAgent):
    def __init__(self, client: OpenAICompatibleClient):
        super().__init__(
            client,
            SAMPLE_UNDERSTANDING_PROMPT_PATH,
            "You are the Multimodal Sample Understanding Agent. Judge completeness and whether text + image can be jointly understood. Return strict JSON only.",
        )

    def fallback_assess(
        self,
        dataset_name: str,
        normalized_question_text: str,
        normalized_answer_text: str,
        requires_image: bool,
        image_qualities: Sequence[Dict[str, Any]],
        quality_flags: Sequence[str],
    ) -> Dict[str, Any]:
        question_complete = bool(normalized_question_text)
        answer_complete = bool(normalized_answer_text)
        has_image = bool(image_qualities)
        reason_codes: List[str] = []
        risk_flags = sorted(
            set(
                to_plain_text(flag)
                for flag in quality_flags
                if to_plain_text(flag) in {"missing_question_text", "missing_answer", "missing_core_image", "multi_image_sample"}
            )
        )
        if not question_complete:
            completeness_status = "broken"
            joint_understanding_status = "not_understandable"
            reason_codes.append("missing_question_text")
        elif requires_image and not has_image:
            completeness_status = "broken"
            joint_understanding_status = "not_understandable"
            reason_codes.append("missing_required_image")
        elif not answer_complete:
            completeness_status = "partial"
            joint_understanding_status = "partially_understandable" if requires_image else "understandable"
            reason_codes.append("missing_answer")
        else:
            completeness_status = "complete"
            joint_understanding_status = "understandable"
            reason_codes.append("fallback_semantically_understandable")

        if not requires_image:
            image_support_status = "not_needed"
        elif not has_image:
            image_support_status = "missing_or_unusable"
        elif completeness_status == "complete":
            image_support_status = "clear_enough"
        else:
            image_support_status = "uncertain_but_usable"

        return {
            "dataset_name": dataset_name,
            "question_complete": question_complete,
            "answer_complete": answer_complete,
            "completeness_status": completeness_status,
            "image_support_status": image_support_status,
            "joint_understanding_status": joint_understanding_status,
            "reason_codes": sorted(set(reason_codes)),
            "risk_flags": risk_flags,
            "rationale": "Fallback understanding judgment is based on semantic field presence and image availability rather than hard metric thresholds.",
            "confidence": 0.58,
            "llm_used": False,
        }

    def assess(
        self,
        dataset_name: str,
        normalized_question_text: str,
        normalized_answer_text: str,
        answer_type: str,
        choices: Dict[str, str],
        requires_image: bool,
        images: Sequence[Image.Image],
        image_qualities: Sequence[Dict[str, Any]],
        quality_flags: Sequence[str],
    ) -> Dict[str, Any]:
        fallback = self.fallback_assess(
            dataset_name=dataset_name,
            normalized_question_text=normalized_question_text,
            normalized_answer_text=normalized_answer_text,
            requires_image=requires_image,
            image_qualities=image_qualities,
            quality_flags=quality_flags,
        )
        payload = {
            "dataset_name": dataset_name,
            "normalized_question_text": normalized_question_text,
            "normalized_answer_text": normalized_answer_text,
            "answer_type": answer_type,
            "choices": choices,
            "requires_image": requires_image,
            "image_count": len(images),
            "image_quality_summaries": [
                {
                    "width": quality.get("width"),
                    "height": quality.get("height"),
                    "blur_score": quality.get("blur_score"),
                    "contrast_score": quality.get("contrast_score"),
                    "readability_score": quality.get("readability_score"),
                    "crop_integrity_score": quality.get("crop_integrity_score"),
                }
                for quality in image_qualities
            ],
            "soft_quality_signals": list(quality_flags),
            "fallback_assessment": fallback,
        }
        llm_result = self.call_json(payload, images=images if requires_image else None)
        if not llm_result:
            return fallback
        completeness_status = to_plain_text(llm_result.get("completeness_status")).strip().lower()
        image_support_status = to_plain_text(llm_result.get("image_support_status")).strip().lower()
        joint_understanding_status = to_plain_text(llm_result.get("joint_understanding_status")).strip().lower()
        if completeness_status not in {"complete", "partial", "broken"}:
            return fallback
        if image_support_status not in {"not_needed", "clear_enough", "uncertain_but_usable", "missing_or_unusable"}:
            return fallback
        if joint_understanding_status not in {"understandable", "partially_understandable", "not_understandable"}:
            return fallback
        reason_codes = llm_result.get("reason_codes")
        if not isinstance(reason_codes, list):
            reason_codes = fallback["reason_codes"]
        risk_flags = llm_result.get("risk_flags")
        if not isinstance(risk_flags, list):
            risk_flags = fallback["risk_flags"]
        confidence = llm_result.get("confidence")
        try:
            confidence = float(confidence)
        except (TypeError, ValueError):
            confidence = fallback["confidence"]
        return {
            "dataset_name": dataset_name,
            "question_complete": bool(llm_result.get("question_complete", fallback["question_complete"])),
            "answer_complete": bool(llm_result.get("answer_complete", fallback["answer_complete"])),
            "completeness_status": completeness_status,
            "image_support_status": image_support_status,
            "joint_understanding_status": joint_understanding_status,
            "reason_codes": sorted(set(to_plain_text(code) for code in reason_codes if to_plain_text(code))),
            "risk_flags": sorted(set(to_plain_text(flag) for flag in risk_flags if to_plain_text(flag))),
            "rationale": to_plain_text(llm_result.get("rationale")) or fallback["rationale"],
            "confidence": round(max(0.0, min(1.0, confidence)), 4),
            "llm_used": True,
        }


class RewriteAgent(BaseStructuredAgent):
    def __init__(self, client: OpenAICompatibleClient, normalizer: TextNormalizer):
        super().__init__(
            client,
            REWRITE_AGENT_PROMPT_PATH,
            "You are the Question Rewrite Agent in a multimodal dataset cleaning pipeline. Convert multiple-choice questions into open-ended variants and return strict JSON only.",
        )
        self.normalizer = normalizer

    def fallback_rewrite(self, dataset_name: str, question_text: str, normalized_answer: str, answer_type: str, choices: Dict[str, str]) -> Dict[str, Any]:
        question_only, _ = self.normalizer.split_question_and_choices(question_text)
        question_only = self.normalizer.strip_hint(question_only)
        if not choices:
            if answer_type == "option" and any(token in question_only.lower() for token in ["which picture", "in which picture", "which figure", "which diagram", "which graph", "shown below", "illustrated"]):
                return {
                    "strategy": "blank_open",
                    "rationale": "Pure-image label selection tasks are in scope, so keep the task and require the answer as the correct option label.",
                    "variants": [
                        {
                            "variant_id": "open_1",
                            "title": f"{dataset_name} 图像标签题",
                            "rewritten_question_text": question_only,
                            "expected_answer_type": "short_text",
                            "expected_answer": normalized_answer,
                            "split_role": "single",
                        }
                    ],
                    "discard_reason_codes": [],
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
            resolved_answer = choices.get(normalized_answer, normalized_answer)
            return {
                "strategy": "blank_open",
                "rationale": "Pure-image choice questions remain valid tasks for this pipeline, so convert them into answer-with-label open questions instead of dropping them.",
                "variants": [
                    {
                        "variant_id": "open_1",
                        "title": f"{dataset_name} 图像标签题",
                        "rewritten_question_text": question_only,
                        "expected_answer_type": "short_text",
                        "expected_answer": resolved_answer,
                        "split_role": "single",
                    }
                ],
                "discard_reason_codes": [],
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
        resolved_answer = choices.get(normalized_answer, normalized_answer)
        resolved_answer_type = self.normalizer.infer_answer_type(self.normalizer.normalize_answer(resolved_answer))
        if resolved_answer_type == "option":
            resolved_answer_type = "short_text"
        return {
            "strategy": "blank_open",
            "rationale": "Converted multiple choice into blank-style open-ended question.",
            "variants": [
                {
                    "variant_id": "open_1",
                    "title": f"{dataset_name} 开放题",
                    "rewritten_question_text": question_only,
                    "expected_answer_type": resolved_answer_type,
                    "expected_answer": resolved_answer,
                    "split_role": "single",
                }
            ],
            "discard_reason_codes": [],
        }

    def rewrite(self, dataset_name: str, normalized_question_text: str, normalized_answer_text: str, answer_type: str, choices: Dict[str, str]) -> Dict[str, Any]:
        fallback = self.fallback_rewrite(dataset_name, normalized_question_text, normalized_answer_text, answer_type, choices)
        if not self.client.config.enabled or not choices:
            return fallback
        llm_result = self.call_json(
            {
                "dataset_name": dataset_name,
                "question_text": normalized_question_text,
                "choices": choices,
                "correct_option_letter": normalized_answer_text if answer_type == "option" else None,
                "correct_option_text": choices.get(normalized_answer_text, normalized_answer_text),
                "answer_type": answer_type,
                "fallback_result": fallback,
            }
        )
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
        discard_reason_codes = llm_result.get("discard_reason_codes")
        if not isinstance(discard_reason_codes, list):
            discard_reason_codes = fallback["discard_reason_codes"]
        if strategy in {"blank_open", "keep_open"} and fallback.get("variants"):
            fallback_variant = fallback["variants"][0] if isinstance(fallback["variants"][0], dict) else {}
            primary_variant = variants[0] if variants and isinstance(variants[0], dict) else {}
            variants = [
                {
                    "variant_id": to_plain_text(primary_variant.get("variant_id") or fallback_variant.get("variant_id") or "open_1"),
                    "title": to_plain_text(primary_variant.get("title") or fallback_variant.get("title") or f"{dataset_name} 开放题"),
                    "rewritten_question_text": to_plain_text(primary_variant.get("rewritten_question_text") or fallback_variant.get("rewritten_question_text")),
                    "expected_answer_type": to_plain_text(fallback_variant.get("expected_answer_type") or primary_variant.get("expected_answer_type") or "short_text"),
                    "expected_answer": to_plain_text(fallback_variant.get("expected_answer") or primary_variant.get("expected_answer")),
                    "split_role": to_plain_text(primary_variant.get("split_role") or fallback_variant.get("split_role") or "single"),
                }
            ]
        return {
            "strategy": strategy,
            "rationale": to_plain_text(llm_result.get("rationale")) or fallback["rationale"],
            "variants": variants,
            "discard_reason_codes": [to_plain_text(code) for code in discard_reason_codes if to_plain_text(code)],
            "llm_used": True,
        }


class DecisionAgent(BaseStructuredAgent):
    def __init__(self, client: OpenAICompatibleClient):
        super().__init__(
            client,
            GATE_DECISION_PROMPT_PATH,
            "You are the Gate Decision Agent in an agent-first cleaning pipeline. Decide pass, review, or reject using semantic usefulness rather than hard thresholds. Return strict JSON only.",
        )

    def fallback_decide(
        self,
        dataset_name: str,
        raw_question_text: str,
        raw_answer_text: str,
        quality_components: Dict[str, Any],
        sample_understanding: Dict[str, Any],
        rewrite_report: Dict[str, Any],
        open_variants: Sequence[Dict[str, Any]],
        alignment_record: Dict[str, Any],
        solvability_report: Dict[str, Any],
        quality_flags: Sequence[str],
        text_structure: Dict[str, Any],
    ) -> Dict[str, Any]:
        reason_codes: List[str] = []
        strategy = rewrite_report.get("strategy")
        completeness_status = sample_understanding.get("completeness_status", "partial")
        joint_status = sample_understanding.get("joint_understanding_status", "partially_understandable")
        image_support_status = sample_understanding.get("image_support_status", "uncertain_but_usable")
        if strategy == "drop_image_index":
            return {
                "decision": "review",
                "reason_codes": ["pure_image_choice_needs_review"],
                "rationale": "Rewrite stage classified the sample as a pure image-choice task. Since pure-image tasks are in scope, keep it for review instead of rejecting it outright.",
                "review_required": True,
                "llm_used": False,
            }
        if not raw_question_text:
            return {
                "decision": "reject",
                "reason_codes": ["missing_question_text"],
                "rationale": "The sample lacks a usable question signal.",
                "review_required": False,
                "llm_used": False,
            }
        if "text_only_without_visual_need" in quality_flags:
            return {
                "decision": "reject",
                "reason_codes": ["text_only_without_visual_need"],
                "rationale": "The sample can be solved from text alone and does not satisfy the required multimodal dependency.",
                "review_required": False,
                "llm_used": False,
            }
        if completeness_status == "broken" or joint_status == "not_understandable":
            return {
                "decision": "reject",
                "reason_codes": sorted(set(sample_understanding.get("reason_codes") or ["sample_not_understandable"])),
                "rationale": sample_understanding.get("rationale") or "The sample is not semantically understandable enough for annotation.",
                "review_required": False,
                "llm_used": False,
            }
        if not raw_answer_text:
            reason_codes.append("missing_answer")
        if not open_variants:
            reason_codes.append("rewrite_failed")
        if "asset_registry_failed" in quality_flags:
            reason_codes.append("asset_registry_failed")
        if "rewrite_mcq_residual" in quality_flags:
            reason_codes.append("rewrite_mcq_residual")
        if "rewrite_expected_answer_mismatch" in quality_flags:
            reason_codes.extend(["rewrite_expected_answer_mismatch", "answer_annotation_inconsistent", "gold_answer_mismatch"])
        if completeness_status == "partial":
            reason_codes.extend(sample_understanding.get("reason_codes", []))
        if image_support_status == "uncertain_but_usable":
            reason_codes.append("visual_evidence_uncertain")
        elif image_support_status == "missing_or_unusable":
            reason_codes.append("missing_required_image")
        if alignment_record.get("alignment_status") in {"bad", "risky"}:
            reason_codes.append("alignment_requires_review")
        if rewrite_report.get("strategy") == "split_open":
            reason_codes.append("split_variant_needs_review")
        if text_structure.get("text_structure_status") != "complete":
            reason_codes.append("text_structure_partial")
        if solvability_report.get("decision_hint") != "pass":
            reason_codes.extend(solvability_report.get("failure_codes", []))
        if "multi_image_sample" in quality_flags:
            reason_codes.append("multi_image_coordination_needed")
        if reason_codes:
            return {
                "decision": "review",
                "reason_codes": sorted(set(reason_codes)),
                "rationale": f"The sample from {dataset_name} appears recoverable and should be reviewed rather than rejected.",
                "review_required": True,
                "llm_used": False,
            }
        return {
            "decision": "pass",
            "reason_codes": ["meets_cleaning_requirements"],
            "rationale": f"The sample from {dataset_name} is semantically understandable and ready for annotation.",
            "review_required": False,
            "llm_used": False,
        }

    def decide(
        self,
        dataset_name: str,
        raw_question_text: str,
        raw_answer_text: str,
        quality_components: Dict[str, Any],
        sample_understanding: Dict[str, Any],
        rewrite_report: Dict[str, Any],
        open_variants: Sequence[Dict[str, Any]],
        alignment_record: Dict[str, Any],
        solvability_report: Dict[str, Any],
        quality_flags: Sequence[str],
        text_structure: Dict[str, Any],
    ) -> Dict[str, Any]:
        fallback = self.fallback_decide(
            dataset_name=dataset_name,
            raw_question_text=raw_question_text,
            raw_answer_text=raw_answer_text,
            quality_components=quality_components,
            sample_understanding=sample_understanding,
            rewrite_report=rewrite_report,
            open_variants=open_variants,
            alignment_record=alignment_record,
            solvability_report=solvability_report,
            quality_flags=quality_flags,
            text_structure=text_structure,
        )
        payload = {
            "dataset_name": dataset_name,
            "raw_question_text": raw_question_text,
            "raw_answer_text": raw_answer_text,
            "quality_components": quality_components,
            "sample_understanding": sample_understanding,
            "rewrite_report": rewrite_report,
            "open_variants": list(open_variants)[:2],
            "alignment_record": {
                "alignment_status": alignment_record.get("alignment_status"),
                "coverage_score": alignment_record.get("coverage_score"),
                "consistency_score": alignment_record.get("consistency_score"),
                "conflict_count": len(alignment_record.get("conflict_pairs", [])),
            },
            "solvability_report": {
                "solvability_score": solvability_report.get("solvability_score"),
                "decision_hint": solvability_report.get("decision_hint"),
                "failure_codes": solvability_report.get("failure_codes", []),
                "reasoning_path_exists": solvability_report.get("reasoning_path_exists"),
            },
            "text_structure": {
                "text_structure_status": text_structure.get("text_structure_status"),
                "question_type": text_structure.get("question_type"),
                "condition_count": len(text_structure.get("conditions", [])),
                "target_count": len(text_structure.get("targets", [])),
            },
            "soft_quality_signals": list(quality_flags),
            "fallback_decision": fallback,
        }
        llm_result = self.call_json(payload)
        if not llm_result:
            return fallback
        decision = to_plain_text(llm_result.get("decision")).strip().lower()
        if decision not in {"pass", "review", "reject"}:
            return fallback
        reason_codes = llm_result.get("reason_codes")
        if not isinstance(reason_codes, list):
            reason_codes = fallback["reason_codes"]
        review_required = llm_result.get("review_required")
        if not isinstance(review_required, bool):
            review_required = decision == "review"
        hard_review_reasons = {"split_variant_needs_review", "rewrite_failed", "rewrite_mcq_residual", "rewrite_expected_answer_mismatch", "answer_annotation_inconsistent", "gold_answer_mismatch", "asset_registry_failed"}
        if decision == "pass" and hard_review_reasons.intersection(set(fallback.get("reason_codes", []))):
            return fallback
        return {
            "decision": decision,
            "reason_codes": sorted(set(to_plain_text(code) for code in reason_codes if to_plain_text(code))) or fallback["reason_codes"],
            "rationale": to_plain_text(llm_result.get("rationale")) or fallback["rationale"],
            "review_required": review_required,
            "llm_used": True,
        }


class AgenticCleaningOrchestrator:
    def __init__(self, sample_understanding_agent: SampleUnderstandingAgent, decision_agent: DecisionAgent):
        self.sample_understanding_agent = sample_understanding_agent
        self.decision_agent = decision_agent

    def assess_sample(
        self,
        dataset_name: str,
        normalized_question_text: str,
        normalized_answer_text: str,
        answer_type: str,
        choices: Dict[str, str],
        requires_image: bool,
        images: Sequence[Image.Image],
        image_qualities: Sequence[Dict[str, Any]],
        quality_flags: Sequence[str],
    ) -> Dict[str, Any]:
        return self.sample_understanding_agent.assess(
            dataset_name=dataset_name,
            normalized_question_text=normalized_question_text,
            normalized_answer_text=normalized_answer_text,
            answer_type=answer_type,
            choices=choices,
            requires_image=requires_image,
            images=images,
            image_qualities=image_qualities,
            quality_flags=quality_flags,
        )

    def decide_gate(
        self,
        dataset_name: str,
        raw_question_text: str,
        raw_answer_text: str,
        quality_components: Dict[str, Any],
        sample_understanding: Dict[str, Any],
        rewrite_report: Dict[str, Any],
        open_variants: Sequence[Dict[str, Any]],
        alignment_record: Dict[str, Any],
        solvability_report: Dict[str, Any],
        quality_flags: Sequence[str],
        text_structure: Dict[str, Any],
    ) -> Dict[str, Any]:
        return self.decision_agent.decide(
            dataset_name=dataset_name,
            raw_question_text=raw_question_text,
            raw_answer_text=raw_answer_text,
            quality_components=quality_components,
            sample_understanding=sample_understanding,
            rewrite_report=rewrite_report,
            open_variants=open_variants,
            alignment_record=alignment_record,
            solvability_report=solvability_report,
            quality_flags=quality_flags,
            text_structure=text_structure,
        )


class MultiDatasetCleaningPipeline:
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.text_normalizer = TextNormalizer()
        self.image_analyzer = ImageQualityAnalyzer()
        self.client = OpenAICompatibleClient(config.model)
        self.source_intake_agent = SourceIntakeAgent(self.client)
        self.asset_registry_agent = AssetRegistryAgent(self.client, self.text_normalizer)
        self.potential_scorer_agent = PotentialScorerAgent(self.client)
        self.candidate_registrar_agent = CandidateRegistrarAgent(self.client)
        self.normalization_agent = NormalizationAgent(self.client, self.text_normalizer)
        self.rewrite_agent = RewriteAgent(self.client, self.text_normalizer)
        self.sample_understanding_agent = SampleUnderstandingAgent(self.client)
        self.decision_agent = DecisionAgent(self.client)
        self.agentic_orchestrator = AgenticCleaningOrchestrator(self.sample_understanding_agent, self.decision_agent)
        self.text_parser = TextContextParser()
        self.visual_parser = VisualParser()
        self.alignment_engine = AlignmentEngine()
        self.solvability_checker = SolvabilityChecker()
        self.pipeline_run_id = f"run_{stable_digest([utc_now(), 'multidataset-clean'], 16)}"
        self.ingest_batch_id = f"{config.batch_id_prefix}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
        self.output_root = Path(config.output_root)
        self.run_dir = self.output_root / self.pipeline_run_id
        self.records_dir = self.run_dir / "records"
        self.dataset_root = self.run_dir / "datasets"
        ensure_dir(self.records_dir)
        ensure_dir(self.dataset_root)
        self.aggregate_summary: Dict[str, Any] = {"pipeline_run_id": self.pipeline_run_id, "created_at": utc_now(), "datasets": []}

    def progress(self, message: str) -> None:
        print(message, flush=True)

    def default_image_quality(self) -> Dict[str, Any]:
        return {
            "width": None,
            "height": None,
            "blur_score": 0.0,
            "contrast_score": 0.0,
            "noise_score": 0.0,
            "readability_score": 0.0,
            "crop_integrity_score": 0.0,
            "roi_bbox": None,
            "perceptual_hash": None,
        }

    def connector_for(self, spec: DatasetSpec) -> BaseConnector:
        if spec.source_kind == "local_file":
            return LocalFileConnector(spec, self.config, self.client)
        if spec.source_kind == "huggingface":
            return HuggingFaceConnector(spec, self.config, self.client)
        if spec.source_kind == "github":
            return GitHubConnector(spec, self.config, self.client)
        return SourceUnavailableConnector(spec, self.config, self.client)

    def run(self) -> Dict[str, Any]:
        started_at = utc_now()
        started_perf = time.perf_counter()
        dataset_summaries = []
        total_datasets = len(self.config.datasets)
        self.progress(
            f"[Pipeline] run_id={self.pipeline_run_id} start datasets={total_datasets} output_dir={self.run_dir}"
        )
        for dataset_index, spec in enumerate(self.config.datasets, start=1):
            self.progress(
                f"[Pipeline] dataset {dataset_index}/{total_datasets} START key={spec.key} name={spec.display_name}"
            )
            dataset_summary = self.run_single_dataset(spec)
            dataset_summaries.append(dataset_summary)
            self.progress(
                f"[Pipeline] dataset {dataset_index}/{total_datasets} END key={spec.key} processed={dataset_summary.get('processed_samples', 0)} decisions={dataset_summary.get('decision_counts', {})}"
            )
        self.aggregate_summary["datasets"] = dataset_summaries
        self.aggregate_summary["sample_concurrency"] = self.config.sample_concurrency
        self.aggregate_summary["started_at"] = started_at
        self.aggregate_summary["finished_at"] = utc_now()
        self.aggregate_summary["elapsed_seconds"] = round(time.perf_counter() - started_perf, 3)
        self.aggregate_summary["llm_usage"] = self.client.get_usage_summary()
        write_json(self.run_dir / "summary.json", self.aggregate_summary)
        self.progress(
            f"[Pipeline] run_id={self.pipeline_run_id} finished elapsed={self.aggregate_summary['elapsed_seconds']}s"
        )
        return self.aggregate_summary

    def run_single_dataset(self, spec: DatasetSpec) -> Dict[str, Any]:
        started_at = utc_now()
        started_perf = time.perf_counter()
        usage_before = self.client.snapshot_usage()
        connector = self.connector_for(spec)
        source_status, samples, detail = connector.sample()
        dataset_dir = self.dataset_root / spec.key
        ensure_dir(dataset_dir)
        if source_status != "available":
            summary = {
                "dataset_key": spec.key,
                "dataset_name": spec.display_name,
                "subject": spec.subject,
                "source_status": "source_unavailable",
                "detail": detail,
                "requested_samples": self.config.sample_per_dataset,
                "processed_samples": 0,
                "decision_counts": {"pass": 0, "review": 0, "reject": 0},
                "rewrite_strategy_counts": {},
                "sample_concurrency": self.config.sample_concurrency,
                "started_at": started_at,
                "finished_at": utc_now(),
                "elapsed_seconds": round(time.perf_counter() - started_perf, 3),
                "llm_usage": self.client.usage_delta(usage_before),
            }
            write_json(dataset_dir / "summary.json", summary)
            self.progress(
                f"[Dataset {spec.key}] source unavailable detail={detail}"
            )
            return summary
        self.progress(
            f"[Dataset {spec.key}] source ready sampled={len(samples)}/{self.config.sample_per_dataset} concurrency={max(1, int(self.config.sample_concurrency or 1))}"
        )
        bundle = {
            "source_intake_records": [],
            "asset_registry_records": [],
            "initial_scoring_records": [],
            "candidate_registration_records": [],
            "normalization_records": [],
            "candidate_problem_records": [],
            "raw_asset_bundles": [],
            "candidate_pool_entries": [],
            "clean_pool_entries": [],
            "clean_problem_records": [],
            "normalized_assets": [],
            "problem_main_records": [],
            "asset_records": [],
            "text_structure_records": [],
            "visual_structure_records": [],
            "solvability_reports": [],
            "node_records": [],
            "cleaning_records": [],
            "reject_records": [],
            "alignment_records": [],
            "field_audit_records": [],
            "rewrite_reports": [],
            "open_ended_problem_variants": [],
        }
        result_mapping = {
            "source_intake_record": "source_intake_records",
            "asset_registry_record": "asset_registry_records",
            "initial_scoring_record": "initial_scoring_records",
            "candidate_registration_record": "candidate_registration_records",
            "normalization_record": "normalization_records",
            "candidate_problem_record": "candidate_problem_records",
            "raw_asset_bundle": "raw_asset_bundles",
            "candidate_pool_entry": "candidate_pool_entries",
            "clean_pool_entries": "clean_pool_entries",
            "clean_problem_record": "clean_problem_records",
            "normalized_assets": "normalized_assets",
            "problem_main_record": "problem_main_records",
            "asset_records": "asset_records",
            "text_structure_records": "text_structure_records",
            "visual_structure_records": "visual_structure_records",
            "solvability_reports": "solvability_reports",
            "node_records": "node_records",
            "cleaning_records": "cleaning_records",
            "reject_records": "reject_records",
            "alignment_records": "alignment_records",
            "field_audit_records": "field_audit_records",
            "rewrite_reports": "rewrite_reports",
            "open_ended_problem_variants": "open_ended_problem_variants",
        }
        sample_dir = dataset_dir / "samples"
        artifact_dir = dataset_dir / "artifacts"
        image_dir = artifact_dir / "images"
        crop_dir = artifact_dir / "crops"
        ensure_dir(sample_dir)
        ensure_dir(image_dir)
        ensure_dir(crop_dir)

        completed_samples = 0
        total_samples = len(samples)

        def emit_sample_progress(result: Dict[str, Any]) -> None:
            nonlocal completed_samples
            completed_samples += 1
            problem_main = result.get("problem_main_record", {})
            self.progress(
                f"[Dataset {spec.key}] sample {completed_samples}/{total_samples} source_problem_id={problem_main.get('source_problem_id', 'unknown')} problem_id={problem_main.get('problem_id', 'unknown')} decision={problem_main.get('clean_decision', 'unknown')} rewrite={problem_main.get('rewrite_strategy', 'unknown')}"
            )

        def consume_result(result: Dict[str, Any]) -> None:
            for result_key, bundle_key in result_mapping.items():
                value = result.get(result_key)
                if isinstance(value, list):
                    bundle[bundle_key].extend(value)
                elif value is not None:
                    bundle[bundle_key].append(value)
            if self.config.save_sample_bundle:
                sample_file = sample_dir / f"{result['problem_main_record']['problem_id']}.json"
                write_json(sample_file, result)
            emit_sample_progress(result)

        sample_concurrency = max(1, int(self.config.sample_concurrency or 1))
        if sample_concurrency == 1 or len(samples) <= 1:
            for sample in samples:
                consume_result(self.process_sample(spec, sample, image_dir, crop_dir))
        else:
            with ThreadPoolExecutor(max_workers=sample_concurrency) as executor:
                future_to_index = {
                    executor.submit(self.process_sample, spec, sample, image_dir, crop_dir): index
                    for index, sample in enumerate(samples)
                }
                for future in as_completed(future_to_index):
                    consume_result(future.result())

        records_dir = dataset_dir / "records"
        ensure_dir(records_dir)
        for key, rows in bundle.items():
            write_jsonl(records_dir / f"{key}.jsonl", rows)
        decision_counts = {"pass": 0, "review": 0, "reject": 0}
        rewrite_strategy_counts: Dict[str, int] = {}
        for record in bundle["problem_main_records"]:
            decision_counts[record["clean_decision"]] += 1
            strategy = record.get("rewrite_strategy", "unknown")
            rewrite_strategy_counts[strategy] = rewrite_strategy_counts.get(strategy, 0) + 1
        summary = {
            "dataset_key": spec.key,
            "dataset_name": spec.display_name,
            "subject": spec.subject,
            "source_status": "available",
            "detail": detail,
            "requested_samples": self.config.sample_per_dataset,
            "processed_samples": len(bundle["problem_main_records"]),
            "decision_counts": decision_counts,
            "rewrite_strategy_counts": rewrite_strategy_counts,
            "records_dir": str(records_dir.relative_to(self.run_dir)),
            "sample_concurrency": sample_concurrency,
            "started_at": started_at,
            "finished_at": utc_now(),
            "elapsed_seconds": round(time.perf_counter() - started_perf, 3),
            "llm_usage": self.client.usage_delta(usage_before),
        }
        write_json(dataset_dir / "summary.json", summary)
        return summary

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

    def build_candidate_problem_record(self, candidate_id: str, sample: UnifiedSample, initial_scores: Dict[str, Any], requires_image: bool, text_dominant: bool, cleaning_path: str, multi_solution_policy: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "candidate_id": candidate_id,
            "source_dataset": sample.dataset_display_name,
            "source_split": sample.source_split,
            "source_problem_id": sample.source_problem_id,
            "subject": sample.subject,
            "raw_question_text": sample.raw_question_text,
            "raw_answer_text": sample.raw_answer_text,
            "has_image": bool(sample.images),
            "image_count": len(sample.images),
            "requires_image": requires_image,
            "text_dominant": text_dominant,
            "recommended_cleaning_path": cleaning_path,
            "initial_image_dependency_score": initial_scores["initial_image_dependency_score"],
            "initial_multi_solution_score": initial_scores["initial_multi_solution_score"],
            "initial_verifiability_score": initial_scores["initial_verifiability_score"],
            "multi_solution_mining_policy": multi_solution_policy["mode"],
            "should_push_multi_solution_agent": multi_solution_policy["should_push_multi_solution_agent"],
            "multi_solution_policy_rationale": multi_solution_policy["rationale"],
            "metadata": sample.metadata,
            "created_at": utc_now(),
        }

    def build_raw_asset_bundle(self, candidate_id: str, problem_id: str, sample: UnifiedSample, image_qualities: Sequence[Dict[str, Any]], initial_scores: Dict[str, Any]) -> Dict[str, Any]:
        assets = [
            {"asset_role": "question_text_raw", "storage_uri": f"inline://{problem_id}/question_source", "is_present": bool(sample.raw_question_text)},
            {"asset_role": "answer_text_raw", "storage_uri": f"inline://{problem_id}/answer_source", "is_present": bool(sample.raw_answer_text)},
        ]
        image_total = max(len(sample.images), len(sample.image_sources), len(image_qualities))
        for index in range(image_total):
            quality = image_qualities[index] if index < len(image_qualities) else self.default_image_quality()
            source = sample.image_sources[index] if index < len(sample.image_sources) else f"inline://{problem_id}/image_{index + 1}"
            assets.append(
                {
                    "asset_role": "image_raw" if index == 0 else f"aux_image_raw_{index + 1}",
                    "storage_uri": source,
                    "is_present": index < len(sample.images),
                    "width": quality.get("width"),
                    "height": quality.get("height"),
                }
            )
        return {
            "raw_asset_bundle_id": f"bundle_{stable_digest([candidate_id, 'raw_assets'])}",
            "candidate_id": candidate_id,
            "source_dataset": sample.dataset_display_name,
            "source_problem_id": sample.source_problem_id,
            "assets": assets,
            "core_asset_completeness": {
                "has_question_text": bool(sample.raw_question_text),
                "has_answer_text": bool(sample.raw_answer_text),
                "image_count": len(sample.images),
                "has_multiple_images": len(sample.images) > 1,
            },
            "initial_scores": initial_scores,
            "created_at": utc_now(),
        }

    def build_candidate_pool_entry(self, candidate_id: str, sample: UnifiedSample, initial_scores: Dict[str, Any], cleaning_path: str, multi_solution_policy: Dict[str, Any]) -> Dict[str, Any]:
        priority_score = round(clamp(0.4 * initial_scores["initial_image_dependency_score"] + 0.3 * initial_scores["initial_multi_solution_score"] + 0.3 * initial_scores["initial_verifiability_score"]), 4)
        return {
            "candidate_pool_entry_id": f"cpool_{stable_digest([candidate_id, self.pipeline_run_id])}",
            "candidate_id": candidate_id,
            "source_dataset": sample.dataset_display_name,
            "source_problem_id": sample.source_problem_id,
            "candidate_status": "ready_for_cleaning",
            "priority_score": priority_score,
            "priority_tier": "high" if priority_score >= 0.72 else "normal",
            "recommended_cleaning_path": cleaning_path,
            "multi_solution_mining_policy": multi_solution_policy["mode"],
            "initial_scores": initial_scores,
            "created_at": utc_now(),
        }

    def build_open_variants(self, problem_id: str, rewrite_report: Dict[str, Any]) -> List[Dict[str, Any]]:
        variants: List[Dict[str, Any]] = []
        for idx, variant in enumerate(rewrite_report.get("variants", []), start=1):
            variants.append(
                {
                    "open_variant_id": f"open_{stable_digest([problem_id, str(idx)])}",
                    "parent_problem_id": problem_id,
                    "variant_index": idx,
                    "title": to_plain_text(variant.get("title") or f"开放题 {idx}"),
                    "rewritten_question_text": to_plain_text(variant.get("rewritten_question_text")),
                    "expected_answer_type": to_plain_text(variant.get("expected_answer_type") or "short_text"),
                    "expected_answer": to_plain_text(variant.get("expected_answer")),
                    "split_role": to_plain_text(variant.get("split_role") or "single"),
                }
            )
        return variants

    def create_roi_assets(self, problem_id: str, images: Sequence[Image.Image], image_qualities: Sequence[Dict[str, Any]], crop_dir: Path) -> List[Dict[str, Any]]:
        ensure_dir(crop_dir)
        roi_assets: List[Dict[str, Any]] = []
        for index, image in enumerate(images, start=1):
            quality = image_qualities[index - 1]
            bbox = quality.get("roi_bbox")
            if image is None or not bbox:
                continue
            width, height = quality["width"], quality["height"]
            if bbox["width"] * bbox["height"] >= 0.98 * width * height:
                continue
            x1, y1 = bbox["x"], bbox["y"]
            x2, y2 = x1 + bbox["width"], y1 + bbox["height"]
            crop = image.convert("RGB").crop((x1, y1, x2, y2))
            suffix = "primary" if index == 1 else f"aux_{index}"
            crop_path = crop_dir / f"{problem_id}_{suffix}_roi.png"
            crop.save(crop_path, format="PNG")
            crop_bytes = crop_path.read_bytes()
            roi_assets.append(
                {
                    "asset_id": f"asset_{stable_digest([problem_id, f'region_crop_{index}'])}",
                    "problem_id": problem_id,
                    "asset_type": "crop",
                    "asset_role": "region_crop" if index == 1 else f"aux_region_crop_{index}",
                    "source_uri": None,
                    "storage_uri": str(crop_path),
                    "file_format": "png",
                    "file_size_bytes": crop_path.stat().st_size,
                    "width": crop.width,
                    "height": crop.height,
                    "sha256": sha256_bytes(crop_bytes),
                    "perceptual_hash": self.image_analyzer.perceptual_hash(crop),
                    "source_text_snapshot": None,
                    "normalized_text_snapshot": None,
                    "text_completeness_score": None,
                    "blur_score": quality["blur_score"],
                    "readability_score": quality["readability_score"],
                    "noise_score": quality["noise_score"],
                    "cropped_from_asset_id": f"asset_{stable_digest([problem_id, f'primary_image_{index}'])}",
                    "roi_bbox": bbox,
                    "asset_quality_flags": [],
                    "is_usable": True,
                    "discard_reason_codes": [],
                    "created_at": utc_now(),
                    "updated_at": utc_now(),
                }
            )
        return roi_assets

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

    def build_quality_flags(self, raw_question_text: str, raw_answer_text: str, text_completeness: float, image_qualities: Sequence[Dict[str, Any]], requires_image: bool) -> List[str]:
        flags: List[str] = []
        if not raw_question_text:
            flags.append("missing_question_text")
        if not raw_answer_text:
            flags.append("missing_answer")
        if requires_image and not image_qualities:
            flags.append("missing_core_image")
        if requires_image and len(image_qualities) > 1:
            flags.append("multi_image_sample")
        if not requires_image:
            flags.append("text_only_without_visual_need")
        return sorted(set(flags))

    def build_normalized_assets(self, problem_id: str, sample: UnifiedSample, question_norm: Dict[str, Any], answer_norm: Dict[str, Any], image_qualities: Sequence[Dict[str, Any]], text_dominant: bool, cleaning_path: str) -> Dict[str, Any]:
        image_regions = [
            {
                "image_index": index + 1,
                "source_uri": sample.image_sources[index] if index < len(sample.image_sources) else None,
                "roi_bbox": quality.get("roi_bbox"),
                "readability_score": quality.get("readability_score"),
                "contrast_score": quality.get("contrast_score"),
            }
            for index, quality in enumerate(image_qualities)
        ]
        return {
            "normalized_assets_id": f"nassets_{stable_digest([problem_id, self.pipeline_run_id])}",
            "problem_id": problem_id,
            "normalized_question_text": question_norm["normalized_text"],
            "normalized_answer_text": answer_norm["normalized_text"],
            "question_unit_normalization_map": question_norm.get("unit_normalization_map", []),
            "answer_unit_normalization_map": answer_norm.get("unit_normalization_map", []),
            "variable_aliases": question_norm.get("variable_aliases", []),
            "sentence_segments": question_norm.get("sentence_segments", []),
            "image_regions": image_regions,
            "text_dominant": text_dominant,
            "cleaning_path": cleaning_path,
            "created_at": utc_now(),
        }

    def build_clean_problem_record(self, problem_id: str, sample: UnifiedSample, normalized_assets: Dict[str, Any], text_structure: Dict[str, Any], alignment_record: Dict[str, Any], solvability_report: Dict[str, Any], gate: Dict[str, Any], open_variants: Sequence[Dict[str, Any]], requires_image: bool, cleaning_path: str) -> Dict[str, Any]:
        return {
            "clean_problem_record_id": f"cleanprob_{stable_digest([problem_id, self.pipeline_run_id])}",
            "problem_id": problem_id,
            "source_dataset": sample.dataset_display_name,
            "source_problem_id": sample.source_problem_id,
            "normalized_question_text": normalized_assets["normalized_question_text"],
            "normalized_answer_text": normalized_assets["normalized_answer_text"],
            "image_count": len(sample.images),
            "has_multiple_images": len(sample.images) > 1,
            "requires_image": requires_image,
            "text_dominant": normalized_assets["text_dominant"],
            "cleaning_path": cleaning_path,
            "question_type": text_structure.get("question_type"),
            "open_variant_count": len(open_variants),
            "alignment_status": alignment_record.get("alignment_status"),
            "solvability_score": solvability_report.get("solvability_score"),
            "solvability_path_mode": solvability_report.get("path_mode"),
            "clean_decision": gate["decision"],
            "decision_reason_codes": gate["decision_reason_codes"],
            "created_at": utc_now(),
        }

    def build_alignment_record(self, problem_id: str, normalized_question_text: str, requires_image: bool, text_structure: Dict[str, Any], visual_structures: Sequence[Dict[str, Any]], image_qualities: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
        record = self.alignment_engine.align(problem_id, requires_image, text_structure, visual_structures, image_qualities, normalized_question_text)
        record["alignment_id"] = f"align_{stable_digest([problem_id, self.pipeline_run_id])}"
        return record

    def clean_gate(self, dataset_name: str, raw_question_text: str, raw_answer_text: str, text_completeness: float, requires_image: bool, image_qualities: Sequence[Dict[str, Any]], alignment_record: Dict[str, Any], potential_scores: Dict[str, Any], quality_flags: List[str], rewrite_report: Dict[str, Any], open_variants: List[Dict[str, Any]], text_structure: Dict[str, Any], solvability_report: Dict[str, Any], sample_understanding: Dict[str, Any]) -> Dict[str, Any]:
        best_readability = max((quality.get("readability_score", 0.0) for quality in image_qualities), default=1.0 if not requires_image else 0.0)
        completeness_score = {"complete": 1.0, "partial": 0.65, "broken": 0.2}.get(sample_understanding.get("completeness_status"), 0.65)
        joint_understanding_score = {"understandable": 1.0, "partially_understandable": 0.65, "not_understandable": 0.15}.get(sample_understanding.get("joint_understanding_status"), 0.65)
        image_support_score = {"not_needed": 1.0, "clear_enough": 0.95, "uncertain_but_usable": 0.7, "missing_or_unusable": 0.15}.get(sample_understanding.get("image_support_status"), 0.7)
        quality_components = {
            "text_completeness": text_completeness,
            "image_readability": best_readability if requires_image else 1.0,
            "alignment_consistency": alignment_record["consistency_score"] if requires_image else 1.0,
            "multimodal_strength": potential_scores["multimodal_strength_score"],
            "verifiability": potential_scores["verifiability_score"],
            "rewrite_quality": 0.0 if rewrite_report.get("strategy") == "drop_image_index" else 0.9 if open_variants else 0.2,
            "solvability": solvability_report.get("solvability_score", 0.0),
            "text_structure_quality": text_structure.get("parser_confidence", 0.0),
            "sample_completeness": completeness_score,
            "joint_understanding": joint_understanding_score,
            "image_support": image_support_score,
        }
        clean_score = round(
            clamp(
                0.12 * quality_components["text_completeness"]
                + 0.08 * quality_components["image_readability"]
                + 0.10 * quality_components["alignment_consistency"]
                + 0.12 * quality_components["multimodal_strength"]
                + 0.10 * quality_components["verifiability"]
                + 0.10 * quality_components["rewrite_quality"]
                + 0.10 * quality_components["solvability"]
                + 0.06 * quality_components["text_structure_quality"]
                + 0.12 * quality_components["sample_completeness"]
                + 0.10 * quality_components["joint_understanding"]
                + 0.10 * quality_components["image_support"]
            ),
            4,
        )
        agent_decision = self.agentic_orchestrator.decide_gate(
            dataset_name=dataset_name,
            raw_question_text=raw_question_text,
            raw_answer_text=raw_answer_text,
            quality_components=quality_components,
            sample_understanding=sample_understanding,
            rewrite_report=rewrite_report,
            open_variants=open_variants,
            alignment_record=alignment_record,
            solvability_report=solvability_report,
            quality_flags=quality_flags,
            text_structure=text_structure,
        )
        decision = agent_decision["decision"]
        return {
            "decision": decision,
            "decision_reason_codes": sorted(set(agent_decision.get("reason_codes", []))),
            "rationale": agent_decision.get("rationale", ""),
            "llm_used": bool(agent_decision.get("llm_used")),
            "clean_score": clean_score,
            "score_breakdown": quality_components,
            "suggested_next_action": {"pass": "send_to_annotation", "review": "manual_review", "reject": "archive_reject_record"}[decision],
            "review_required": bool(agent_decision.get("review_required", decision == "review")),
        }

    def build_asset_records(self, spec: DatasetSpec, problem_id: str, sample: UnifiedSample, image_paths: Sequence[Path], image_bytes_list: Sequence[bytes], normalized_question_text: str, normalized_answer_text: str, question_norm: Dict[str, Any], answer_norm: Dict[str, Any], text_completeness: float, image_qualities: Sequence[Dict[str, Any]], quality_flags: List[str], roi_assets: List[Dict[str, Any]], open_variants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        created_at = utc_now()
        assets = [
            {
                "asset_id": f"asset_{stable_digest([problem_id, 'question_text_source'])}",
                "problem_id": problem_id,
                "asset_type": "text",
                "asset_role": "question_text_source",
                "source_uri": f"source://{spec.key}/{sample.source_split}/{sample.source_problem_id}/question",
                "storage_uri": f"inline://{problem_id}/question_source",
                "file_format": "txt",
                "file_size_bytes": len(sample.raw_question_text.encode('utf-8')),
                "width": None,
                "height": None,
                "sha256": sha256_bytes(sample.raw_question_text.encode('utf-8')),
                "perceptual_hash": None,
                "source_text_snapshot": sample.raw_question_text,
                "normalized_text_snapshot": None,
                "text_completeness_score": text_completeness,
                "blur_score": None,
                "readability_score": None,
                "noise_score": None,
                "cropped_from_asset_id": None,
                "roi_bbox": None,
                "unit_normalization_map": question_norm.get("unit_normalization_map", []),
                "variable_aliases": question_norm.get("variable_aliases", []),
                "asset_quality_flags": [],
                "is_usable": bool(sample.raw_question_text),
                "discard_reason_codes": [],
                "created_at": created_at,
                "updated_at": created_at,
            },
            {
                "asset_id": f"asset_{stable_digest([problem_id, 'question_text_normalized'])}",
                "problem_id": problem_id,
                "asset_type": "text",
                "asset_role": "question_text_normalized",
                "source_uri": None,
                "storage_uri": f"inline://{problem_id}/question_normalized",
                "file_format": "txt",
                "file_size_bytes": len(normalized_question_text.encode('utf-8')),
                "width": None,
                "height": None,
                "sha256": sha256_bytes(normalized_question_text.encode('utf-8')),
                "perceptual_hash": None,
                "source_text_snapshot": sample.raw_question_text,
                "normalized_text_snapshot": normalized_question_text,
                "text_completeness_score": text_completeness,
                "blur_score": None,
                "readability_score": None,
                "noise_score": None,
                "cropped_from_asset_id": None,
                "roi_bbox": None,
                "unit_normalization_map": question_norm.get("unit_normalization_map", []),
                "variable_aliases": question_norm.get("variable_aliases", []),
                "asset_quality_flags": [],
                "is_usable": bool(normalized_question_text),
                "discard_reason_codes": [],
                "created_at": created_at,
                "updated_at": created_at,
            },
            {
                "asset_id": f"asset_{stable_digest([problem_id, 'answer_raw'])}",
                "problem_id": problem_id,
                "asset_type": "answer",
                "asset_role": "answer_raw",
                "source_uri": f"source://{spec.key}/{sample.source_split}/{sample.source_problem_id}/answer",
                "storage_uri": f"inline://{problem_id}/answer_raw",
                "file_format": "txt",
                "file_size_bytes": len(sample.raw_answer_text.encode('utf-8')),
                "width": None,
                "height": None,
                "sha256": sha256_bytes(sample.raw_answer_text.encode('utf-8')),
                "perceptual_hash": None,
                "source_text_snapshot": sample.raw_answer_text,
                "normalized_text_snapshot": None,
                "text_completeness_score": 1.0 if sample.raw_answer_text else 0.0,
                "blur_score": None,
                "readability_score": None,
                "noise_score": None,
                "cropped_from_asset_id": None,
                "roi_bbox": None,
                "unit_normalization_map": answer_norm.get("unit_normalization_map", []),
                "variable_aliases": answer_norm.get("variable_aliases", []),
                "asset_quality_flags": [],
                "is_usable": bool(sample.raw_answer_text),
                "discard_reason_codes": [],
                "created_at": created_at,
                "updated_at": created_at,
            },
            {
                "asset_id": f"asset_{stable_digest([problem_id, 'answer_normalized'])}",
                "problem_id": problem_id,
                "asset_type": "answer",
                "asset_role": "answer_normalized",
                "source_uri": None,
                "storage_uri": f"inline://{problem_id}/answer_normalized",
                "file_format": "txt",
                "file_size_bytes": len(normalized_answer_text.encode('utf-8')),
                "width": None,
                "height": None,
                "sha256": sha256_bytes(normalized_answer_text.encode('utf-8')),
                "perceptual_hash": None,
                "source_text_snapshot": sample.raw_answer_text,
                "normalized_text_snapshot": normalized_answer_text,
                "text_completeness_score": 1.0 if normalized_answer_text else 0.0,
                "blur_score": None,
                "readability_score": None,
                "noise_score": None,
                "cropped_from_asset_id": None,
                "roi_bbox": None,
                "unit_normalization_map": answer_norm.get("unit_normalization_map", []),
                "variable_aliases": answer_norm.get("variable_aliases", []),
                "asset_quality_flags": [],
                "is_usable": bool(normalized_answer_text),
                "discard_reason_codes": [],
                "created_at": created_at,
                "updated_at": created_at,
            },
        ]
        for index, image_path in enumerate(image_paths, start=1):
            quality = image_qualities[index - 1]
            image_bytes = image_bytes_list[index - 1]
            role = "primary_image" if index == 1 else f"aux_image_{index}"
            assets.append(
                {
                    "asset_id": f"asset_{stable_digest([problem_id, f'primary_image_{index}'])}",
                    "problem_id": problem_id,
                    "asset_type": "image",
                    "asset_role": role,
                    "source_uri": sample.image_sources[index - 1] if index - 1 < len(sample.image_sources) else None,
                    "storage_uri": str(image_path),
                    "file_format": image_path.suffix.lstrip('.') or 'png',
                    "file_size_bytes": len(image_bytes),
                    "width": quality["width"],
                    "height": quality["height"],
                    "sha256": sha256_bytes(image_bytes),
                    "perceptual_hash": quality["perceptual_hash"],
                    "source_text_snapshot": None,
                    "normalized_text_snapshot": None,
                    "text_completeness_score": None,
                    "blur_score": quality["blur_score"],
                    "readability_score": quality["readability_score"],
                    "noise_score": quality["noise_score"],
                    "cropped_from_asset_id": None,
                    "roi_bbox": quality["roi_bbox"],
                    "unit_normalization_map": [],
                    "variable_aliases": [],
                    "asset_quality_flags": quality_flags,
                    "is_usable": True,
                    "discard_reason_codes": [],
                    "created_at": created_at,
                    "updated_at": created_at,
                }
            )
        assets.extend(roi_assets)
        for variant in open_variants:
            assets.append(
                {
                    "asset_id": f"asset_{stable_digest([variant['open_variant_id'], 'open_text'])}",
                    "problem_id": problem_id,
                    "asset_type": "text",
                    "asset_role": "question_text_open_variant",
                    "source_uri": None,
                    "storage_uri": f"inline://{variant['open_variant_id']}",
                    "file_format": "txt",
                    "file_size_bytes": len(variant['rewritten_question_text'].encode('utf-8')),
                    "width": None,
                    "height": None,
                    "sha256": sha256_bytes(variant['rewritten_question_text'].encode('utf-8')),
                    "perceptual_hash": None,
                    "source_text_snapshot": sample.raw_question_text,
                    "normalized_text_snapshot": variant['rewritten_question_text'],
                    "text_completeness_score": text_completeness,
                    "blur_score": None,
                    "readability_score": None,
                    "noise_score": None,
                    "cropped_from_asset_id": None,
                    "roi_bbox": None,
                    "unit_normalization_map": question_norm.get("unit_normalization_map", []),
                    "variable_aliases": question_norm.get("variable_aliases", []),
                    "asset_quality_flags": [],
                    "is_usable": True,
                    "discard_reason_codes": [],
                    "created_at": created_at,
                    "updated_at": created_at,
                }
            )
        return assets

    def build_text_structure_record(self, problem_id: str, text_structure: Dict[str, Any], question_norm: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "text_structure_id": text_structure["text_structure_id"],
            "problem_id": problem_id,
            "question_type": text_structure["question_type"],
            "conditions": text_structure["conditions"],
            "targets": text_structure["targets"],
            "answer_slots": text_structure["answer_slots"],
            "entity_mentions": text_structure["entity_mentions"],
            "variable_aliases": text_structure["variable_aliases"],
            "unit_mentions": text_structure["unit_mentions"],
            "sentence_segments": question_norm.get("sentence_segments", []),
            "requires_visual_grounding": text_structure["requires_visual_grounding"],
            "text_structure_status": text_structure["text_structure_status"],
            "parser_confidence": text_structure["parser_confidence"],
            "created_at": text_structure["created_at"],
        }

    def build_node_records(self, problem_id: str, normalized_question_text: str, normalized_answer_text: str, original_answer_type: str, quality_flags: List[str], text_structure: Dict[str, Any], visual_structures: Sequence[Dict[str, Any]], open_variants: List[Dict[str, Any]], gate: Dict[str, Any], solvability_report: Dict[str, Any]) -> List[Dict[str, Any]]:
        created_at = utc_now()
        nodes: List[Dict[str, Any]] = []
        for condition in text_structure.get("conditions", []):
            nodes.append(
                {
                    "node_id": f"node_{stable_digest([problem_id, 'condition', str(condition['segment_index'])])}",
                    "problem_id": problem_id,
                    "node_type": "text_fact",
                    "canonical_value": condition["text"],
                    "surface_forms": [condition["text"]],
                    "origin_kind": "text",
                    "cognitive_level": "objective",
                    "source_refs": [f"asset_{stable_digest([problem_id, 'question_text_normalized'])}"],
                    "evidence_refs": [f"asset_{stable_digest([problem_id, 'question_text_normalized'])}"],
                    "upstream_node_ids": [],
                    "value_type": "condition",
                    "normalized_value": condition,
                    "unit": ",".join(condition.get("unit_mentions", [])) or None,
                    "confidence": 0.92,
                    "verifiability": "high",
                    "ambiguity_level": "low",
                    "is_direct_from_source": True,
                    "is_generated_by_system": False,
                    "is_reviewed_by_human": False,
                    "stage_created": "cleaning",
                    "status": "active",
                    "version": 1,
                    "created_at": created_at,
                    "updated_at": created_at,
                }
            )
        for slot in text_structure.get("answer_slots", []):
            nodes.append(
                {
                    "node_id": f"node_{stable_digest([problem_id, slot['slot_id'], 'target'])}",
                    "problem_id": problem_id,
                    "node_type": "target_slot",
                    "canonical_value": slot["target_text"],
                    "surface_forms": [slot["target_text"]],
                    "origin_kind": "text_structure",
                    "cognitive_level": "computed",
                    "source_refs": [f"asset_{stable_digest([problem_id, 'question_text_normalized'])}"],
                    "evidence_refs": [f"asset_{stable_digest([problem_id, 'question_text_normalized'])}"],
                    "upstream_node_ids": [],
                    "value_type": slot["slot_type"],
                    "normalized_value": slot,
                    "unit": None,
                    "confidence": text_structure.get("parser_confidence", 0.8),
                    "verifiability": "high" if slot.get("expected_answer") else "medium",
                    "ambiguity_level": "low" if len(slot["target_text"]) >= 3 else "high",
                    "is_direct_from_source": False,
                    "is_generated_by_system": True,
                    "is_reviewed_by_human": False,
                    "stage_created": "cleaning",
                    "status": "active",
                    "version": 1,
                    "created_at": created_at,
                    "updated_at": created_at,
                }
            )
        nodes.append(
            {
                "node_id": f"node_{stable_digest([problem_id, 'answer_claim'])}",
                "problem_id": problem_id,
                "node_type": "answer_claim",
                "canonical_value": normalized_answer_text,
                "surface_forms": [normalized_answer_text],
                "origin_kind": "text",
                "cognitive_level": "objective",
                "source_refs": [f"asset_{stable_digest([problem_id, 'answer_normalized'])}"],
                "evidence_refs": [f"asset_{stable_digest([problem_id, 'answer_normalized'])}"],
                "upstream_node_ids": [],
                "value_type": original_answer_type,
                "normalized_value": {"answer": normalized_answer_text},
                "unit": None,
                "confidence": 0.98 if normalized_answer_text else 0.0,
                "verifiability": "high" if normalized_answer_text else "unverifiable",
                "ambiguity_level": "none" if normalized_answer_text else "high",
                "is_direct_from_source": True,
                "is_generated_by_system": False,
                "is_reviewed_by_human": False,
                "stage_created": "cleaning",
                "status": "active",
                "version": 1,
                "created_at": created_at,
                "updated_at": created_at,
            }
        )
        for visual in visual_structures:
            for entity in visual.get("visual_entities", [])[:8]:
                nodes.append(
                    {
                        "node_id": f"node_{stable_digest([problem_id, visual['visual_structure_id'], entity['entity_id']])}",
                        "problem_id": problem_id,
                        "node_type": "perception_fact",
                        "canonical_value": f"{visual['image_asset_role']}::{entity['entity_type']}::{entity['entity_id']}",
                        "surface_forms": [entity['entity_id']],
                        "origin_kind": "vision",
                        "cognitive_level": "objective",
                        "source_refs": [visual['visual_structure_id']],
                        "evidence_refs": [visual['visual_structure_id']],
                        "upstream_node_ids": [],
                        "value_type": entity['entity_type'],
                        "normalized_value": entity,
                        "unit": None,
                        "confidence": visual.get("parser_confidence", 0.7),
                        "verifiability": "medium",
                        "ambiguity_level": "low",
                        "is_direct_from_source": False,
                        "is_generated_by_system": True,
                        "is_reviewed_by_human": False,
                        "stage_created": "cleaning",
                        "status": "active",
                        "version": 1,
                        "created_at": created_at,
                        "updated_at": created_at,
                    }
                )
        for idx, variant in enumerate(open_variants):
            nodes.append(
                {
                    "node_id": f"node_{stable_digest([variant['open_variant_id'], 'open_variant'])}",
                    "problem_id": problem_id,
                    "node_type": "text_fact",
                    "canonical_value": variant["rewritten_question_text"],
                    "surface_forms": [variant["rewritten_question_text"]],
                    "origin_kind": "reasoning",
                    "cognitive_level": "computed",
                    "source_refs": [f"asset_{stable_digest([variant['open_variant_id'], 'open_text'])}"],
                    "evidence_refs": [f"asset_{stable_digest([variant['open_variant_id'], 'open_text'])}"],
                    "upstream_node_ids": [],
                    "value_type": "text",
                    "normalized_value": variant,
                    "unit": None,
                    "confidence": 0.88,
                    "verifiability": "medium",
                    "ambiguity_level": "low",
                    "is_direct_from_source": False,
                    "is_generated_by_system": True,
                    "is_reviewed_by_human": False,
                    "stage_created": "cleaning",
                    "status": "active",
                    "version": 1,
                    "created_at": created_at,
                    "updated_at": created_at,
                }
            )
        for idx, flag in enumerate(quality_flags):
            nodes.append(
                {
                    "node_id": f"node_{stable_digest([problem_id, 'quality_flag', str(idx)])}",
                    "problem_id": problem_id,
                    "node_type": "quality_signal",
                    "canonical_value": flag,
                    "surface_forms": [flag],
                    "origin_kind": "system_quality",
                    "cognitive_level": "computed",
                    "source_refs": [],
                    "evidence_refs": [],
                    "upstream_node_ids": [],
                    "value_type": "text",
                    "normalized_value": {"flag": flag},
                    "unit": None,
                    "confidence": 1.0,
                    "verifiability": "high",
                    "ambiguity_level": "none",
                    "is_direct_from_source": False,
                    "is_generated_by_system": True,
                    "is_reviewed_by_human": False,
                    "stage_created": "cleaning",
                    "status": "active",
                    "version": 1,
                    "created_at": created_at,
                    "updated_at": created_at,
                }
            )
        nodes.append(
            {
                "node_id": f"node_{stable_digest([problem_id, 'solvability'])}",
                "problem_id": problem_id,
                "node_type": "quality_signal",
                "canonical_value": f"solvability={solvability_report['decision_hint']}",
                "surface_forms": [solvability_report["decision_hint"]],
                "origin_kind": "system_quality",
                "cognitive_level": "computed",
                "source_refs": [],
                "evidence_refs": [],
                "upstream_node_ids": [],
                "value_type": "text",
                "normalized_value": solvability_report,
                "unit": None,
                "confidence": 1.0,
                "verifiability": "high",
                "ambiguity_level": "none",
                "is_direct_from_source": False,
                "is_generated_by_system": True,
                "is_reviewed_by_human": False,
                "stage_created": "cleaning",
                "status": "active",
                "version": 1,
                "created_at": created_at,
                "updated_at": created_at,
            }
        )
        nodes.append(
            {
                "node_id": f"node_{stable_digest([problem_id, 'clean_decision'])}",
                "problem_id": problem_id,
                "node_type": "quality_signal",
                "canonical_value": f"clean_decision={gate['decision']}",
                "surface_forms": [gate["decision"]],
                "origin_kind": "system_quality",
                "cognitive_level": "computed",
                "source_refs": [],
                "evidence_refs": [],
                "upstream_node_ids": [],
                "value_type": "text",
                "normalized_value": {"decision": gate["decision"], "reasons": gate["decision_reason_codes"]},
                "unit": None,
                "confidence": 1.0,
                "verifiability": "high",
                "ambiguity_level": "none",
                "is_direct_from_source": False,
                "is_generated_by_system": True,
                "is_reviewed_by_human": False,
                "stage_created": "cleaning",
                "status": "active",
                "version": 1,
                "created_at": created_at,
                "updated_at": created_at,
            }
        )
        return nodes

    def build_field_audit_records(self, problem_id: str, raw_question_text: str, normalized_question_text: str, raw_answer_text: str, normalized_answer_text: str, rewrite_report: Dict[str, Any], gate: Dict[str, Any], question_norm: Dict[str, Any], answer_norm: Dict[str, Any]) -> List[Dict[str, Any]]:
        timestamp = utc_now()
        records = [
            {
                "audit_id": f"audit_{stable_digest([problem_id, 'normalized_question_text'])}",
                "problem_id": problem_id,
                "record_type": "problem_main_record",
                "field_name": "normalized_question_text",
                "before_value": raw_question_text,
                "after_value": normalized_question_text,
                "change_type": "text_normalized",
                "trigger": "NormalizationAgent",
                "operator_type": "system",
                "created_at": timestamp,
            },
            {
                "audit_id": f"audit_{stable_digest([problem_id, 'normalized_answer_text'])}",
                "problem_id": problem_id,
                "record_type": "problem_main_record",
                "field_name": "normalized_answer_text",
                "before_value": raw_answer_text,
                "after_value": normalized_answer_text,
                "change_type": "answer_canonicalized",
                "trigger": "NormalizationAgent",
                "operator_type": "system",
                "created_at": timestamp,
            },
            {
                "audit_id": f"audit_{stable_digest([problem_id, 'rewrite_strategy'])}",
                "problem_id": problem_id,
                "record_type": "rewrite_report",
                "field_name": "rewrite_strategy",
                "before_value": None,
                "after_value": rewrite_report.get("strategy"),
                "change_type": "question_rewritten",
                "trigger": "QuestionRewriteAgent",
                "operator_type": "system",
                "created_at": timestamp,
            },
            {
                "audit_id": f"audit_{stable_digest([problem_id, 'clean_decision'])}",
                "problem_id": problem_id,
                "record_type": "cleaning_record",
                "field_name": "decision",
                "before_value": None,
                "after_value": gate.get("decision"),
                "change_type": "gate_decision",
                "trigger": "CleanGateAgent",
                "operator_type": "system",
                "created_at": timestamp,
            },
        ]
        if question_norm.get("unit_normalization_map"):
            records.append(
                {
                    "audit_id": f"audit_{stable_digest([problem_id, 'question_unit_map'])}",
                    "problem_id": problem_id,
                    "record_type": "normalized_assets",
                    "field_name": "question_unit_normalization_map",
                    "before_value": raw_question_text,
                    "after_value": question_norm.get("unit_normalization_map"),
                    "change_type": "unit_normalized",
                    "trigger": "NormalizationAgent",
                    "operator_type": "system",
                    "created_at": timestamp,
                }
            )
        if answer_norm.get("unit_normalization_map"):
            records.append(
                {
                    "audit_id": f"audit_{stable_digest([problem_id, 'answer_unit_map'])}",
                    "problem_id": problem_id,
                    "record_type": "normalized_assets",
                    "field_name": "answer_unit_normalization_map",
                    "before_value": raw_answer_text,
                    "after_value": answer_norm.get("unit_normalization_map"),
                    "change_type": "unit_normalized",
                    "trigger": "NormalizationAgent",
                    "operator_type": "system",
                    "created_at": timestamp,
                }
            )
        if question_norm.get("variable_aliases"):
            records.append(
                {
                    "audit_id": f"audit_{stable_digest([problem_id, 'variable_aliases'])}",
                    "problem_id": problem_id,
                    "record_type": "normalized_assets",
                    "field_name": "variable_aliases",
                    "before_value": None,
                    "after_value": question_norm.get("variable_aliases"),
                    "change_type": "variable_canonicalized",
                    "trigger": "NormalizationAgent",
                    "operator_type": "system",
                    "created_at": timestamp,
                }
            )
        return records

    def build_rewrite_record(self, problem_id: str, sample: UnifiedSample, rewrite_report: Dict[str, Any], open_variants: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "rewrite_id": f"rewrite_{stable_digest([problem_id, self.pipeline_run_id])}",
            "problem_id": problem_id,
            "source_problem_id": sample.source_problem_id,
            "strategy": rewrite_report.get("strategy"),
            "rationale": rewrite_report.get("rationale"),
            "discard_reason_codes": rewrite_report.get("discard_reason_codes", []),
            "variant_count": len(open_variants),
            "variants": open_variants,
            "created_at": utc_now(),
        }

    def build_cleaning_record(self, problem_id: str, spec: DatasetSpec, asset_records: List[Dict[str, Any]], alignment_record: Dict[str, Any], quality_flags: List[str], gate: Dict[str, Any], rewrite_report: Dict[str, Any], open_variants: List[Dict[str, Any]], question_norm: Dict[str, Any], answer_norm: Dict[str, Any], image_qualities: Sequence[Dict[str, Any]], text_structure: Dict[str, Any], solvability_report: Dict[str, Any], sample_understanding: Dict[str, Any]) -> Dict[str, Any]:
        combined_risk_flags = sorted(set(list(quality_flags) + list(sample_understanding.get("risk_flags", []))))
        image_quality_checks = [
            {
                "check": f"image_observation_{index + 1}",
                "result": quality,
                "passed": sample_understanding.get("image_support_status") != "missing_or_unusable",
                "judged_by": "SampleUnderstandingAgent",
            }
            for index, quality in enumerate(image_qualities)
        ]
        if not image_quality_checks:
            image_quality_checks = [{"check": "image_observation", "result": None, "passed": True, "judged_by": "SampleUnderstandingAgent"}]
        return {
            "cleaning_id": f"clean_{stable_digest([problem_id, self.pipeline_run_id])}",
            "problem_id": problem_id,
            "cleaning_version": self.config.cleaning_version,
            "pipeline_run_id": self.pipeline_run_id,
            "dataset_name": spec.display_name,
            "input_asset_ids": [asset["asset_id"] for asset in asset_records],
            "normalization_actions": [
                {"action_type": "text_normalized", "trigger": "NormalizationAgent", "confidence": len(question_norm.get("sentence_segments", [])) / max(len(question_norm.get("sentence_segments", [])), 1), "human_confirmed": False},
                {"action_type": "answer_canonicalized", "trigger": "NormalizationAgent", "confidence": 0.98, "human_confirmed": False},
                {"action_type": "unit_normalized", "trigger": "NormalizationAgent", "confidence": 0.92, "human_confirmed": False, "question_unit_count": len(question_norm.get("unit_normalization_map", [])), "answer_unit_count": len(answer_norm.get("unit_normalization_map", []))},
                {"action_type": "variable_canonicalized", "trigger": "NormalizationAgent", "confidence": 0.88, "human_confirmed": False, "variable_alias_count": len(question_norm.get("variable_aliases", []))},
                {"action_type": "question_rewritten", "trigger": "QuestionRewriteAgent", "confidence": 0.85, "human_confirmed": False},
                {"action_type": "sample_understood", "trigger": "SampleUnderstandingAgent", "confidence": sample_understanding.get("confidence", 0.0), "human_confirmed": False},
                {"action_type": "gate_decided", "trigger": "DecisionAgent", "confidence": 1.0 if gate.get("llm_used") else 0.6, "human_confirmed": False},
            ],
            "quality_checks": image_quality_checks,
            "alignment_summary": {
                "alignment_id": alignment_record["alignment_id"],
                "coverage_score": alignment_record["coverage_score"],
                "consistency_score": alignment_record["consistency_score"],
                "alignment_status": alignment_record["alignment_status"],
                "conflict_count": len(alignment_record.get("conflict_pairs", [])),
            },
            "text_structure_summary": {
                "text_structure_id": text_structure["text_structure_id"],
                "question_type": text_structure["question_type"],
                "condition_count": len(text_structure.get("conditions", [])),
                "target_count": len(text_structure.get("targets", [])),
                "answer_slot_count": len(text_structure.get("answer_slots", [])),
                "status": text_structure.get("text_structure_status"),
            },
            "solvability_summary": {
                "solvability_id": solvability_report["solvability_id"],
                "solvability_score": solvability_report["solvability_score"],
                "reasoning_path_exists": solvability_report["reasoning_path_exists"],
                "decision_hint": solvability_report["decision_hint"],
                "failure_codes": solvability_report.get("failure_codes", []),
            },
            "rewrite_summary": {"strategy": rewrite_report.get("strategy"), "variant_count": len(open_variants), "discard_reason_codes": rewrite_report.get("discard_reason_codes", [])},
            "agent_assessment": {
                "completeness_status": sample_understanding.get("completeness_status"),
                "image_support_status": sample_understanding.get("image_support_status"),
                "joint_understanding_status": sample_understanding.get("joint_understanding_status"),
                "reason_codes": sample_understanding.get("reason_codes", []),
                "rationale": sample_understanding.get("rationale"),
                "llm_used": sample_understanding.get("llm_used", False),
            },
            "missing_field_summary": {
                "missing_question_text": not bool(question_norm["normalized_text"]),
                "missing_answer_text": not bool(answer_norm["normalized_text"]),
                "missing_image_count": 0 if image_qualities else (1 if "missing_core_image" in quality_flags else 0),
            },
            "risk_flags": combined_risk_flags,
            "clean_score": gate["clean_score"],
            "decision": gate["decision"],
            "decision_reason_codes": gate["decision_reason_codes"],
            "decision_rationale": gate.get("rationale", ""),
            "review_ticket_id": f"review_{problem_id}" if gate["decision"] == "review" else None,
            "operator_type": "system",
            "started_at": utc_now(),
            "finished_at": utc_now(),
        }

    def build_reject_record(self, problem_id: str, gate: Dict[str, Any], quality_flags: List[str], rewrite_report: Dict[str, Any], alignment_record: Dict[str, Any], solvability_report: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if gate["decision"] != "reject":
            return None
        return {
            "reject_id": f"reject_{stable_digest([problem_id, self.pipeline_run_id])}",
            "problem_id": problem_id,
            "stage": "cleaning",
            "reject_level": "problem",
            "reject_reason_codes": gate["decision_reason_codes"],
            "reject_reason_detail": gate.get("rationale") or rewrite_report.get("rationale") or "Rejected by cleaning gate.",
            "blocking_fields": quality_flags,
            "evidence_refs": [alignment_record["alignment_id"], solvability_report["solvability_id"]],
            "recoverable": False,
            "recommended_action": "drop",
            "reviewed_by": None,
            "created_at": utc_now(),
        }

    def build_problem_main_record(self, problem_id: str, sample: UnifiedSample, language: str, normalized_question_text: str, normalized_answer_text: str, answer_type: str, image_count: int, requires_image: bool, potential_scores: Dict[str, Any], quality_flags: List[str], gate: Dict[str, Any], rewrite_report: Dict[str, Any], open_variants: List[Dict[str, Any]], normalized_assets: Dict[str, Any], alignment_record: Dict[str, Any], solvability_report: Dict[str, Any], sample_understanding: Dict[str, Any], created_at: str) -> Dict[str, Any]:
        combined_risk_flags = sorted(set(list(quality_flags) + list(sample_understanding.get("risk_flags", []))))
        return {
            "problem_id": problem_id,
            "source_dataset": sample.dataset_display_name,
            "source_split": sample.source_split,
            "source_problem_id": sample.source_problem_id,
            "ingest_batch_id": self.ingest_batch_id,
            "problem_type": "multimodal_reasoning",
            "domain_tags": [sample.subject],
            "language": language,
            "raw_question_text": sample.raw_question_text,
            "normalized_question_text": normalized_question_text,
            "raw_answer_text": sample.raw_answer_text,
            "normalized_answer_text": normalized_answer_text,
            "answer_type": answer_type,
            "has_reasoning_chain": bool(normalize_whitespace(to_plain_text(sample.metadata.get("reasoning_chain", "")))),
            "reasoning_chain": normalize_whitespace(to_plain_text(sample.metadata.get("reasoning_chain", ""))),
            "image_count": image_count,
            "has_multiple_images": image_count > 1,
            "requires_image": requires_image,
            "multimodal_strength_score": potential_scores["multimodal_strength_score"],
            "multi_step_score": potential_scores["multi_step_score"],
            "verifiability_score": potential_scores["verifiability_score"],
            "quality_risk_flags": combined_risk_flags,
            "current_status": {"pass": "clean_passed", "review": "cleaning_review", "reject": "clean_rejected"}[gate["decision"]],
            "clean_decision": gate["decision"],
            "clean_decision_reason_codes": gate["decision_reason_codes"],
            "clean_decision_rationale": gate.get("rationale", ""),
            "review_priority": potential_scores["review_priority"],
            "annotation_ready": gate["decision"] == "pass",
            "qa_precheck_ready": bool(open_variants) and gate["decision"] != "reject",
            "release_reserved": {},
            "rewrite_strategy": rewrite_report.get("strategy"),
            "open_variant_count": len(open_variants),
            "candidate_id": None,
            "text_dominant": normalized_assets["text_dominant"],
            "cleaning_path": normalized_assets["cleaning_path"],
            "alignment_status": alignment_record["alignment_status"],
            "solvability_score": solvability_report["solvability_score"],
            "solvability_decision_hint": solvability_report["decision_hint"],
            "agent_completeness_status": sample_understanding.get("completeness_status"),
            "agent_image_support_status": sample_understanding.get("image_support_status"),
            "agent_joint_understanding_status": sample_understanding.get("joint_understanding_status"),
            "agent_decision_source": "llm" if gate.get("llm_used") else "fallback",
            "created_at": created_at,
            "updated_at": utc_now(),
        }

    def process_sample(self, spec: DatasetSpec, sample: UnifiedSample, image_dir: Path, crop_dir: Path) -> Dict[str, Any]:
        created_at = utc_now()
        raw_question_text = sample.raw_question_text
        raw_answer_text = "" if is_null_like_text(sample.raw_answer_text) else sample.raw_answer_text
        raw_answer_text = resolve_multiple_choice_answer_text(
            raw_answer_text,
            dict(sample.choice_map),
            spec.answer_index_base,
        )
        sample.raw_answer_text = raw_answer_text
        digest_seed = [
            spec.key,
            sample.source_split or "unknown",
            sample.source_problem_id or raw_question_text or "empty",
            "||".join(sample.image_sources) if sample.image_sources else str(len(sample.images)),
        ]
        candidate_id = f"cand_{stable_digest(digest_seed)}"
        problem_id = f"prob_{stable_digest(digest_seed)}"
        image_paths, image_bytes_list, image_qualities = self.persist_images(problem_id=problem_id, images=sample.images, image_dir=image_dir)
        image_count = len(sample.images)
        if not image_paths:
            image_qualities = []

        normalization_result = self.normalization_agent.process(
            dataset_name=spec.display_name,
            raw_question_text=raw_question_text,
            raw_answer_text=raw_answer_text,
            choice_map=dict(sample.choice_map),
            force_requires_image=sample.force_requires_image,
            images=sample.images,
            image_qualities=image_qualities,
        )
        normalized_question_text = normalization_result["normalized_question_text"]
        normalized_answer_text = normalization_result["normalized_answer_text"]
        choices = dict(normalization_result.get("normalized_choice_map") or {})
        if not choices:
            choices = dict(sample.choice_map)
        if not choices:
            choices = self.text_normalizer.extract_choice_map(normalized_question_text)
        normalized_answer_text = resolve_multiple_choice_answer_text(
            normalized_answer_text,
            choices,
            spec.answer_index_base,
        )
        text_dominant = bool(normalization_result.get("text_dominant", False))
        cleaning_path = to_plain_text(
            normalization_result.get("cleaning_path") or ("text_lightweight" if text_dominant else "multimodal_full")
        ).strip()
        if cleaning_path not in {"text_lightweight", "multimodal_full"}:
            cleaning_path = "text_lightweight" if text_dominant else "multimodal_full"
        if cleaning_path == "text_lightweight":
            text_dominant = True
            requires_image = False
        else:
            text_dominant = False
            requires_image = True

        question_norm = normalize_structured_text(normalized_question_text)
        answer_norm = normalize_structured_text(normalized_answer_text)
        language = self.text_normalizer.detect_language(normalized_question_text)
        original_answer_type = self.text_normalizer.infer_answer_type(normalized_answer_text)
        text_completeness = self.text_normalizer.text_completeness_score(raw_question_text, normalized_question_text)

        source_intake_record = {
            "source_intake_id": f"sintake_{stable_digest([problem_id, self.pipeline_run_id])}",
            "candidate_id": candidate_id,
            "problem_id": problem_id,
            "dataset_name": spec.display_name,
            "source_problem_id": sample.source_problem_id,
            "raw_question_text": raw_question_text,
            "raw_answer_text": raw_answer_text,
            "choice_map": dict(sample.choice_map),
            "image_paths": list(sample.metadata.get("image_paths", [])),
            "force_requires_image": sample.force_requires_image,
            "question_field": sample.metadata.get("question_field"),
            "answer_field": sample.metadata.get("answer_field"),
            "image_field": sample.metadata.get("image_field"),
            "choice_field": sample.metadata.get("choice_field"),
            "extraction_notes": list(sample.metadata.get("extraction_notes", [])),
            "created_at": created_at,
        }
        asset_registry_record = self.asset_registry_agent.process(
            problem_id=problem_id,
            question_text=raw_question_text,
            answer_text=raw_answer_text,
            image_sources=[str(path) for path in image_paths] if image_paths else list(sample.image_sources),
            image_qualities=image_qualities,
            metadata=sample.metadata,
            requires_image=requires_image,
            choice_count=len(choices),
        )
        asset_registry_record.update(
            {
                "asset_registry_id": f"areg_{stable_digest([problem_id, self.pipeline_run_id])}",
                "candidate_id": candidate_id,
                "dataset_name": spec.display_name,
                "source_problem_id": sample.source_problem_id,
                "created_at": created_at,
            }
        )

        multi_solution_policy = self.determine_multi_solution_policy(spec)
        fallback_initial_scores = self.compute_initial_collection_scores(
            normalized_question_text,
            normalized_answer_text,
            original_answer_type,
            requires_image,
            text_dominant,
            image_qualities,
            choices,
            multi_solution_policy,
        )
        initial_scoring_record = self.potential_scorer_agent.process(
            problem_id=problem_id,
            normalized_question_text=normalized_question_text,
            normalized_answer_text=normalized_answer_text,
            answer_type=original_answer_type,
            requires_image=requires_image,
            text_dominant=text_dominant,
            image_qualities=image_qualities,
            choices=choices,
            multi_solution_policy=multi_solution_policy,
            asset_registry_record=asset_registry_record,
            fallback_scores=fallback_initial_scores,
        )
        initial_scoring_record.update(
            {
                "initial_scoring_id": f"iscore_{stable_digest([problem_id, self.pipeline_run_id])}",
                "candidate_id": candidate_id,
                "dataset_name": spec.display_name,
                "source_problem_id": sample.source_problem_id,
                "created_at": created_at,
            }
        )
        initial_scores = {
            "initial_image_dependency_score": initial_scoring_record["image_dependency_score"],
            "initial_multi_solution_score": initial_scoring_record["multi_step_score"],
            "initial_verifiability_score": initial_scoring_record["verifiability_score"],
        }

        candidate_registration_record = self.candidate_registrar_agent.process(
            problem_id=problem_id,
            asset_registry_record=asset_registry_record,
            initial_scoring_record=initial_scoring_record,
        )
        candidate_registration_record.update(
            {
                "candidate_registration_id": f"creg_{stable_digest([problem_id, self.pipeline_run_id])}",
                "candidate_id": candidate_id,
                "dataset_name": spec.display_name,
                "source_problem_id": sample.source_problem_id,
                "created_at": created_at,
            }
        )
        normalization_record = {
            "normalization_id": f"norm_{stable_digest([problem_id, self.pipeline_run_id])}",
            "candidate_id": candidate_id,
            "problem_id": problem_id,
            "dataset_name": spec.display_name,
            "normalized_question_text": normalized_question_text,
            "normalized_answer_text": normalized_answer_text,
            "normalized_choice_map": choices,
            "requires_image": requires_image,
            "text_dominant": text_dominant,
            "cleaning_path": cleaning_path,
            "normalization_notes": list(normalization_result.get("normalization_notes", [])),
            "llm_used": bool(normalization_result.get("llm_used")),
            "created_at": created_at,
        }

        rewrite_report = self.rewrite_agent.rewrite(spec.display_name, normalized_question_text, normalized_answer_text, original_answer_type, choices)
        open_variants = self.build_open_variants(problem_id, rewrite_report)
        rewrite_consistency_flags = rewrite_answer_consistency_flags(normalized_answer_text, rewrite_report, open_variants)
        rewrite_question_flags = rewrite_question_residual_flags(rewrite_report, open_variants)
        rewrite_report["consistency_check_passed"] = not rewrite_consistency_flags
        rewrite_report["consistency_issue_codes"] = list(rewrite_consistency_flags)
        rewrite_report["question_check_passed"] = not rewrite_question_flags
        rewrite_report["question_issue_codes"] = list(rewrite_question_flags)
        text_structure = self.text_parser.parse(problem_id, normalized_question_text, open_variants, requires_image, question_norm, answer_norm, choices)
        visual_structures = [] if text_dominant else self.visual_parser.parse_many(problem_id, sample.images, image_qualities, normalized_question_text)
        alignment_record = self.build_alignment_record(problem_id, normalized_question_text, requires_image, text_structure, visual_structures, image_qualities)
        quality_flags = sorted(
            set(
                self.build_quality_flags(raw_question_text, raw_answer_text, text_completeness, image_qualities, requires_image)
                + (["asset_registry_failed"] if not asset_registry_record.get("registry_passed", True) else [])
                + list(asset_registry_record.get("issues", []))
                + list(rewrite_consistency_flags)
                + list(rewrite_question_flags)
            )
        )
        sample_understanding = self.agentic_orchestrator.assess_sample(
            dataset_name=spec.display_name,
            normalized_question_text=normalized_question_text,
            normalized_answer_text=normalized_answer_text,
            answer_type=original_answer_type,
            choices=choices,
            requires_image=requires_image,
            images=sample.images,
            image_qualities=image_qualities,
            quality_flags=quality_flags,
        )
        combined_quality_flags = sorted(set(quality_flags + sample_understanding.get("risk_flags", [])))
        solvability_report = self.solvability_checker.evaluate(problem_id, normalized_answer_text, original_answer_type, requires_image, open_variants, text_structure, visual_structures, alignment_record, combined_quality_flags)
        potential_scores = self.compute_potential_scores(normalized_question_text, normalized_answer_text, original_answer_type, requires_image, image_qualities, choices, len(open_variants), text_structure, alignment_record, solvability_report)
        gate = self.clean_gate(spec.display_name, raw_question_text, raw_answer_text, text_completeness, requires_image, image_qualities, alignment_record, potential_scores, combined_quality_flags, rewrite_report, open_variants, text_structure, solvability_report, sample_understanding)
        normalized_assets = self.build_normalized_assets(problem_id, sample, question_norm, answer_norm, image_qualities, text_dominant, cleaning_path)
        normalized_assets.update(
            {
                "normalization_notes": normalization_record["normalization_notes"],
                "normalization_llm_used": normalization_record["llm_used"],
            }
        )
        clean_problem_record = self.build_clean_problem_record(problem_id, sample, normalized_assets, text_structure, alignment_record, solvability_report, gate, open_variants, requires_image, cleaning_path)
        roi_assets = self.create_roi_assets(problem_id, sample.images, image_qualities, crop_dir)
        asset_records = self.build_asset_records(spec, problem_id, sample, image_paths, image_bytes_list, normalized_question_text, normalized_answer_text, question_norm, answer_norm, text_completeness, image_qualities, combined_quality_flags, roi_assets, open_variants)
        node_records = self.build_node_records(problem_id, normalized_question_text, normalized_answer_text, original_answer_type, combined_quality_flags, text_structure, visual_structures, open_variants, gate, solvability_report)
        field_audits = self.build_field_audit_records(problem_id, raw_question_text, normalized_question_text, raw_answer_text, normalized_answer_text, rewrite_report, gate, question_norm, answer_norm)
        cleaning_record = self.build_cleaning_record(problem_id, spec, asset_records, alignment_record, combined_quality_flags, gate, rewrite_report, open_variants, question_norm, answer_norm, image_qualities, text_structure, solvability_report, sample_understanding)
        reject_record = self.build_reject_record(problem_id, gate, combined_quality_flags, rewrite_report, alignment_record, solvability_report)
        problem_main_record = self.build_problem_main_record(problem_id, sample, language, normalized_question_text, normalized_answer_text, original_answer_type, image_count, requires_image, potential_scores, combined_quality_flags, gate, rewrite_report, open_variants, normalized_assets, alignment_record, solvability_report, sample_understanding, created_at)
        problem_main_record.update(
            {
                "candidate_id": candidate_id,
                "initial_image_dependency_score": initial_scores["initial_image_dependency_score"],
                "initial_multi_solution_score": initial_scores["initial_multi_solution_score"],
                "initial_verifiability_score": initial_scores["initial_verifiability_score"],
                "multi_solution_mining_policy": multi_solution_policy["mode"],
                "collection_priority_score": candidate_registration_record["priority"],
                "collection_decision": candidate_registration_record["decision"],
                "collection_decision_reasons": candidate_registration_record["decision_reasons"],
            }
        )
        candidate_problem_record = self.build_candidate_problem_record(candidate_id, sample, initial_scores, requires_image, text_dominant, cleaning_path, multi_solution_policy)
        candidate_problem_record.update(
            {
                "asset_registry_passed": asset_registry_record.get("registry_passed", True),
                "collection_priority_score": candidate_registration_record["priority"],
                "collection_decision": candidate_registration_record["decision"],
                "collection_decision_reasons": candidate_registration_record["decision_reasons"],
                "collection_risk_flags": initial_scoring_record.get("risk_flags", []),
            }
        )
        raw_asset_bundle = self.build_raw_asset_bundle(candidate_id, problem_id, sample, image_qualities, initial_scores)
        raw_asset_bundle.update(
            {
                "asset_registry_passed": asset_registry_record.get("registry_passed", True),
                "asset_registry_issues": asset_registry_record.get("issues", []),
            }
        )
        candidate_pool_entry = self.build_candidate_pool_entry(candidate_id, sample, initial_scores, cleaning_path, multi_solution_policy)
        candidate_pool_entry.update(
            {
                "candidate_status": "collection_rejected" if candidate_registration_record["decision"] == "reject" else "ready_for_cleaning",
                "priority_score": candidate_registration_record["priority"],
                "priority_tier": "high" if candidate_registration_record["priority"] >= 0.72 else "normal" if candidate_registration_record["priority"] >= 0.4 else "low",
                "registration_decision": candidate_registration_record["decision"],
                "registration_decision_reasons": candidate_registration_record["decision_reasons"],
            }
        )
        clean_pool_entry = None if gate["decision"] == "reject" else {
            "clean_pool_entry_id": f"cleanpool_{stable_digest([problem_id, self.pipeline_run_id])}",
            "candidate_id": candidate_id,
            "problem_id": problem_id,
            "dataset_name": spec.display_name,
            "pool_status": "ready_for_annotation" if gate["decision"] == "pass" else "manual_review",
            "clean_decision": gate["decision"],
            "review_required": gate["review_required"],
            "rewrite_strategy": rewrite_report.get("strategy"),
            "open_variant_count": len(open_variants),
            "text_dominant": text_dominant,
            "cleaning_path": cleaning_path,
            "created_at": utc_now(),
        }
        cleaning_record.update({"candidate_id": candidate_id, "cleaning_path": cleaning_path, "text_dominant": text_dominant})
        alignment_record.update({"cleaning_path": cleaning_path, "text_dominant": text_dominant})
        return {
            "source_intake_record": source_intake_record,
            "asset_registry_record": asset_registry_record,
            "initial_scoring_record": initial_scoring_record,
            "candidate_registration_record": candidate_registration_record,
            "normalization_record": normalization_record,
            "candidate_problem_record": candidate_problem_record,
            "raw_asset_bundle": raw_asset_bundle,
            "candidate_pool_entry": candidate_pool_entry,
            "clean_pool_entries": [clean_pool_entry] if clean_pool_entry else [],
            "clean_problem_record": clean_problem_record,
            "normalized_assets": normalized_assets,
            "problem_main_record": problem_main_record,
            "asset_records": asset_records,
            "text_structure_records": [self.build_text_structure_record(problem_id, text_structure, question_norm)],
            "visual_structure_records": list(visual_structures),
            "solvability_reports": [solvability_report],
            "node_records": node_records,
            "cleaning_records": [cleaning_record],
            "reject_records": [reject_record] if reject_record else [],
            "alignment_records": [alignment_record],
            "field_audit_records": field_audits,
            "rewrite_reports": [self.build_rewrite_record(problem_id, sample, rewrite_report, open_variants)],
            "open_ended_problem_variants": open_variants,
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="多数据集采集与清洗智能体流水线")
    parser.add_argument("--config", type=str, default=None, help="YAML 配置文件路径")
    parser.add_argument("--output-dir", type=str, default=None, help="输出目录")
    parser.add_argument("--sample-per-dataset", type=int, default=None, help="每个数据集抽样数")
    parser.add_argument("--sample-strategy", type=str, choices=["head", "random"], default=None, help="抽样策略")
    parser.add_argument("--sample-concurrency", type=int, default=None, help="样本并发数")
    parser.add_argument("--seed", type=int, default=None, help="随机种子")
    parser.add_argument("--disable-llm", action="store_true", help="禁用 LLM Agent，仅使用规则回退")
    parser.add_argument("--base-url", type=str, default=None, help="OpenAI 兼容接口 base url")
    parser.add_argument("--api-key", type=str, default=None, help="OpenAI 兼容接口 key")
    parser.add_argument("--model", type=str, default=None, help="模型名称")
    parser.add_argument("--reasoning-effort", type=str, default=None, help="推理强度，如 xhigh")
    return parser.parse_args()


def merge_cli_overrides(config: PipelineConfig, args: argparse.Namespace) -> PipelineConfig:
    if args.output_dir:
        config.output_root = args.output_dir
    if args.sample_per_dataset is not None:
        config.sample_per_dataset = args.sample_per_dataset
    if args.sample_strategy:
        config.sample_strategy = args.sample_strategy
    if args.sample_concurrency is not None:
        config.sample_concurrency = max(1, args.sample_concurrency)
    if args.seed is not None:
        config.shuffle_seed = args.seed
    if args.disable_llm:
        config.model.enabled = False
    if args.base_url:
        config.model.base_url = args.base_url
    if args.api_key:
        config.model.api_key = args.api_key
    if args.model:
        config.model.model = args.model
    if args.reasoning_effort:
        config.model.reasoning_effort = args.reasoning_effort
    return config


def main() -> None:
    args = parse_args()
    config = PipelineConfig.from_yaml(args.config)
    config = merge_cli_overrides(config, args)
    ensure_dir(Path(config.output_root))
    pipeline = MultiDatasetCleaningPipeline(config)
    summary = pipeline.run()
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
