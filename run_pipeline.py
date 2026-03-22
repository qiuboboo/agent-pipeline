from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import io
import json
import mimetypes
import os
import re
import shutil
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from openai import OpenAI

PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "outputs" / "multidataset_cleaning"
UNIFIED_PROMPT_PATH = PROJECT_ROOT / "prompts" / "extract_unified_sample.md"
SCORING_PROMPT_PATH = PROJECT_ROOT / "prompts" / "preliminary_value_scoring.md"


@dataclass
class ModelConfig:
    base_url: str = "https://synai996.space/v1"
    api_key: str = os.environ.get("OPENAI_API_KEY_AGENT", "")
    model: str = "gpt-5.4"
    reasoning_effort: str = "xhigh"
    temperature: float = 0.1
    timeout_seconds: int = 180
    enabled: bool = True


@dataclass
class ThresholdConfig:
    pass_score_threshold: float = 14.0
    reject_score_threshold: float = 10.0
    min_alignment_consistency: float = 0.55
    min_alignment_coverage: float = 0.6


@dataclass
class DatasetSpec:
    key: str
    display_name: str
    subject: str
    source_kind: str = "local_file"
    source_locator: str = ""
    split: Optional[str] = None
    note: str = ""
    question_fields: list[str] = field(default_factory=list)
    answer_fields: list[str] = field(default_factory=list)
    image_fields: list[str] = field(default_factory=list)
    choice_fields: list[str] = field(default_factory=list)
    force_requires_image: bool = False


@dataclass
class PipelineConfig:
    output_root: Path = DEFAULT_OUTPUT_ROOT
    cleaning_version: str = "v0.5.0"
    batch_id_prefix: str = "candidate-clean"
    sample_per_dataset: int = 30
    sample_strategy: str = "head"
    shuffle_seed: int = 42
    git_cache_root: Path = PROJECT_ROOT / "outputs" / "repo_cache"
    model: ModelConfig = field(default_factory=ModelConfig)
    thresholds: ThresholdConfig = field(default_factory=ThresholdConfig)
    datasets: list[DatasetSpec] = field(default_factory=list)


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
    image: str | None
    image_source: str | None
    raw_record: dict[str, Any]
    metadata: dict[str, Any]
    choice_map: dict[str, str] = field(default_factory=dict)
    force_requires_image: bool = False


api_key = os.environ.get("OPENAI_API_KEY_AGENT")
model_config = ModelConfig(api_key=api_key or "")
client = OpenAI(api_key=model_config.api_key, base_url=model_config.base_url) if api_key else None


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def stable_digest(parts: list[str], length: int = 24) -> str:
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


def is_missing_value(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    if isinstance(value, (list, dict)) and not value:
        return True
    return False


def read_prompt(prompt_path: Path) -> str:
    return prompt_path.read_text(encoding="utf-8").strip()


def strip_code_fence(text: str) -> str:
    text = text.strip()
    if not text.startswith("```"):
        return text
    lines = text.splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip()


def parse_json_response(text: str) -> dict:
    cleaned = strip_code_fence(text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(cleaned[start : end + 1])
        raise


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def append_jsonl(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def make_problem_id(prefix: str, record: dict, index: int) -> str:
    source_id = record.get("id") or record.get("image_id") or f"{index:06d}"
    return f"{prefix}_{str(source_id).replace('/', '_')}"


def normalize_choice_text(text: str) -> str:
    value = (text or "").strip()
    value = re.sub(r"^\(?[A-Za-z0-9]\)?[\s.、:_-]+", "", value)
    return value.strip()


def normalize_answer_text(text: str) -> str:
    return normalize_whitespace(normalize_choice_text(text))


def infer_answer_type(answer: str) -> str:
    if not answer:
        return "unknown"
    if re.fullmatch(r"[A-Z]", answer):
        return "option"
    if re.fullmatch(r"[+-]?(?:\d+(?:\.\d+)?|\.\d+)", answer):
        return "numeric"
    if len(answer.split()) <= 8:
        return "short_text"
    return "text"


def detect_language(text: str) -> str:
    if re.search(r"[\u4e00-\u9fff]", text):
        return "zh"
    if re.search(r"[A-Za-z]", text):
        return "en"
    return "unknown"


def resolve_choice_map(record: dict, extracted_choice_map: dict | None) -> dict[str, str]:
    if extracted_choice_map and isinstance(extracted_choice_map, dict):
        out = {}
        for key, value in extracted_choice_map.items():
            k = str(key).strip().upper()
            v = str(value).strip()
            if re.fullmatch(r"[A-H]", k) and v:
                out[k] = v
        if out:
            return out
    choices = record.get("choices") or record.get("options")
    if isinstance(choices, list):
        return {chr(ord('A') + i): str(choice).strip() for i, choice in enumerate(choices) if str(choice).strip()}
    if isinstance(choices, dict):
        return {str(k).strip().upper(): str(v).strip() for k, v in choices.items() if str(v).strip()}
    return {}


def resolve_multiple_choice_answer(record: dict, extracted_answer: str, choice_map: dict[str, str] | None = None) -> str:
    answer = (extracted_answer or "").strip()
    effective_choice_map = choice_map or resolve_choice_map(record, None)
    if not effective_choice_map:
        return normalize_answer_text(answer)
    answer_upper = answer.upper().strip()
    letter_match = re.fullmatch(r"\(?([A-Z])\)?", answer_upper)
    if letter_match:
        key = letter_match.group(1)
        if key in effective_choice_map:
            return normalize_answer_text(effective_choice_map[key])
    mixed_match = re.match(r"^\(?([A-Z])\)?[\s.、:_-]+(.+)$", answer, flags=re.I)
    if mixed_match:
        answer = mixed_match.group(2).strip()
    normalized_answer = normalize_answer_text(answer)
    for choice in effective_choice_map.values():
        if normalized_answer == normalize_answer_text(choice):
            return normalize_answer_text(choice)
    return normalized_answer


def encode_image_as_data_url(image_path: Path) -> str:
    mime_type, _ = mimetypes.guess_type(image_path.name)
    mime_type = mime_type or "application/octet-stream"
    data = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{data}"


def build_user_content(user_prompt: str, image_paths: list[str] | None = None, asset_base_dir: Path | None = None):
    if not image_paths:
        return user_prompt
    content_blocks = [{"type": "text", "text": user_prompt}]
    for raw_path in image_paths:
        image_path = Path(raw_path)
        if not image_path.is_absolute() and asset_base_dir is not None:
            image_path = asset_base_dir / image_path
        if not image_path.exists():
            continue
        content_blocks.append({
            "type": "image_url",
            "image_url": {"url": encode_image_as_data_url(image_path)},
        })
    if len(content_blocks) == 1:
        return user_prompt
    return content_blocks


def call_model(system_prompt: str, user_prompt: str, image_paths: list[str] | None = None, asset_base_dir: Path | None = None) -> str:
    if client is None:
        raise RuntimeError("OPENAI_API_KEY_AGENT is not set")
    response = client.chat.completions.create(
        model=model_config.model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": build_user_content(user_prompt, image_paths=image_paths, asset_base_dir=asset_base_dir)},
        ],
    )
    return response.choices[0].message.content or ""


def heuristic_extract_unified_sample(record: dict) -> dict:
    question_text = to_plain_text(record.get("question") or record.get("problem") or record.get("query") or record.get("text") or "").strip()
    answer_raw = to_plain_text(record.get("answer") or record.get("solution") or record.get("label") or "").strip()
    choice_map = resolve_choice_map(record, None)
    answer_text = resolve_multiple_choice_answer(record, answer_raw, choice_map=choice_map)
    raw_images = record.get("images") if record.get("images") is not None else record.get("image")
    image_paths: list[str] = []
    if isinstance(raw_images, str):
        image_paths = [raw_images]
    elif isinstance(raw_images, list):
        image_paths = [str(item) for item in raw_images if str(item).strip()]
    force_requires_image = bool(re.search(r"\b(figure|diagram|graph|chart|image|shown|below|sample)\b", question_text, flags=re.I)) or bool(image_paths)
    return {
        "raw_question_text": question_text,
        "raw_answer_text": answer_text,
        "choice_map": choice_map,
        "image_paths": image_paths,
        "force_requires_image": force_requires_image,
        "extraction_notes": ["heuristic_fallback_used"],
    }


def heuristic_score_sample(sample: dict) -> dict:
    question_text = to_plain_text(sample.get("question_text") or "")
    answer_text = to_plain_text(sample.get("answer_text") or "")
    image_paths = sample.get("image_paths") or []
    multimodal = 4 if image_paths and re.search(r"\b(compare|diagram|graph|chart|image|shown|below|sample|figure)\b", question_text, flags=re.I) else (3 if image_paths else 1)
    decomposability = 4 if re.search(r"\b(compare|why|how|trace|relationship|path|temperature|energy|reaction|derive)\b", question_text, flags=re.I) else 2
    answer_stability = 4 if answer_text else 1
    annotation_payoff = 4 if multimodal >= 3 and decomposability >= 3 else 2
    total = multimodal + decomposability + answer_stability + annotation_payoff
    if multimodal <= 2 or decomposability <= 2:
        value_level = "medium" if total >= 10 else "low"
    elif total >= 17:
        value_level = "very_high"
    elif total >= 14:
        value_level = "high"
    elif total >= 10:
        value_level = "medium"
    else:
        value_level = "low"
    return {
        "preliminary_value_score": total,
        "value_level": value_level,
        "dimension_scores": {
            "multimodal_necessity": multimodal,
            "node_decomposability": decomposability,
            "answer_stability": answer_stability,
            "annotation_payoff": annotation_payoff,
        },
        "short_reason": "启发式评分：有无图像依赖、是否可拆步骤、答案是否稳定。",
    }


def build_unified_extraction_user_prompt(record: dict) -> str:
    record_json = json.dumps(record, ensure_ascii=False, indent=2)
    return f"""下面是一条原始 JSON 记录。
请按照 system prompt 的规则提取 UnifiedSample 所需的关键字段。
只返回 JSON 对象。

原始 JSON:
{record_json}
"""


def build_scoring_user_prompt(sample: dict) -> str:
    sample_json = json.dumps(sample, ensure_ascii=False, indent=2)
    return f"""下面是一个已经抽取出的候选样本，请你根据 system prompt 中的评分标准进行初步价值评分。
如果附带了图片，请结合图片一起判断；如果图片缺失，则仅根据文本保守评分。
只返回 JSON 对象。

候选样本:
{sample_json}
"""


class BaseConnector:
    def __init__(self, spec: DatasetSpec, config: PipelineConfig):
        self.spec = spec
        self.config = config

    def sample(self) -> tuple[str, list[dict[str, Any]], Optional[str], Optional[Path]]:
        raise NotImplementedError


class LocalFileConnector(BaseConnector):
    def iter_records(self, path: Path):
        suffix = path.suffix.lower()
        if suffix == ".jsonl":
            with path.open("r", encoding="utf-8") as fh:
                for _, line in enumerate(fh):
                    line = line.strip()
                    if not line:
                        continue
                    yield json.loads(line)
            return
        if suffix == ".json":
            with path.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, list):
                for record in data:
                    yield record
                return
            if isinstance(data, dict):
                yield data
                return
        raise ValueError(f"Unsupported input format: {path.suffix}")

    def sample(self) -> tuple[str, list[dict[str, Any]], Optional[str], Optional[Path]]:
        path = Path(self.spec.source_locator)
        if not path.exists():
            return "source_unavailable", [], f"Input not found: {path}", None
        rows = list(self.iter_records(path))
        if self.config.sample_strategy == "random":
            import random
            rng = random.Random(self.config.shuffle_seed)
            rng.shuffle(rows)
        rows = rows[: min(self.config.sample_per_dataset, len(rows))]
        return "available", rows, None, path.parent


class GitHubConnector(BaseConnector):
    def ensure_repo(self) -> tuple[Optional[Path], Optional[str]]:
        cache_root = Path(self.config.git_cache_root)
        ensure_dir(cache_root)
        target = cache_root / self.spec.key
        if target.exists() and (target / ".git").exists():
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

    def discover_data_files(self, repo_dir: Path) -> list[Path]:
        scored: list[tuple[int, Path]] = []
        for path in repo_dir.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in {".json", ".jsonl", ".csv", ".tsv"}:
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
                    score += 30
                if rel.endswith("logic_form.json"):
                    score -= 10
            scored.append((score, path))
        scored.sort(key=lambda item: (-item[0], str(item[1])))
        return [path for _, path in scored]

    def load_records(self, path: Path) -> list[dict[str, Any]]:
        if path.suffix.lower() == ".json":
            with path.open("r", encoding="utf-8", errors="ignore") as file:
                data = json.load(file)
            if isinstance(data, list):
                return [item for item in data if isinstance(item, dict)]
            if isinstance(data, dict):
                for key in ["data", "dataset", "datasets", "records", "items", "problems", "questions", "annotations"]:
                    value = data.get(key)
                    if isinstance(value, list) and value and isinstance(value[0], dict):
                        return value
                return [data]
            return []
        if path.suffix.lower() == ".jsonl":
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
        if path.suffix.lower() in {".csv", ".tsv"}:
            delimiter = "," if path.suffix.lower() == ".csv" else "\t"
            with path.open("r", encoding="utf-8", errors="ignore") as file:
                reader = csv.DictReader(file, delimiter=delimiter)
                return [dict(row) for row in reader]
        return []

    def sample(self) -> tuple[str, list[dict[str, Any]], Optional[str], Optional[Path]]:
        repo_dir, detail = self.ensure_repo()
        if repo_dir is None:
            return "source_unavailable", [], detail, None
        files = self.discover_data_files(repo_dir)
        samples: list[dict[str, Any]] = []
        for file in files:
            rows = self.load_records(file)
            for row in rows:
                samples.append(row)
                if len(samples) >= self.config.sample_per_dataset:
                    break
            if len(samples) >= self.config.sample_per_dataset:
                break
        if self.config.sample_strategy == "random":
            import random
            rng = random.Random(self.config.shuffle_seed)
            rng.shuffle(samples)
        return "available", samples[: self.config.sample_per_dataset], detail, repo_dir


class SourceUnavailableConnector(BaseConnector):
    def sample(self) -> tuple[str, list[dict[str, Any]], Optional[str], Optional[Path]]:
        return "source_unavailable", [], self.spec.note or self.spec.source_locator or "source unavailable", None


def score_sample(sample: dict, scoring_prompt_path: Path, asset_base_dir: Path | None = None) -> dict:
    if client is None:
        assessment = heuristic_score_sample(sample)
    else:
        system_prompt = read_prompt(scoring_prompt_path)
        user_prompt = build_scoring_user_prompt(sample)
        response_text = call_model(system_prompt, user_prompt, image_paths=sample.get("image_paths", []), asset_base_dir=asset_base_dir)
        assessment = parse_json_response(response_text)
    return {
        "preliminary_value_score": assessment.get("preliminary_value_score"),
        "preliminary_value_level": assessment.get("value_level", ""),
        "preliminary_value_reason": (assessment.get("short_reason") or "").strip(),
        "preliminary_value_dimensions": assessment.get("dimension_scores") or {},
    }


def build_unified_sample(record: dict, index: int, spec: DatasetSpec, asset_base_dir: Path | None = None, scoring_prompt_path: Path | None = None) -> dict:
    if client is None:
        extracted = heuristic_extract_unified_sample(record)
    else:
        system_prompt = read_prompt(UNIFIED_PROMPT_PATH)
        user_prompt = build_unified_extraction_user_prompt(record)
        response_text = call_model(system_prompt, user_prompt)
        extracted = parse_json_response(response_text)

    choice_map = resolve_choice_map(record, extracted.get("choice_map"))
    raw_answer_text = resolve_multiple_choice_answer(record, (extracted.get("raw_answer_text") or extracted.get("answer_text") or "").strip(), choice_map=choice_map)
    image_paths = extracted.get("image_paths") if isinstance(extracted.get("image_paths"), list) else []
    if not image_paths:
        raw_images = record.get("images") if record.get("images") is not None else record.get("image")
        if isinstance(raw_images, str):
            raw_images = [raw_images]
        if isinstance(raw_images, list):
            image_paths = [str(Path(p)) for p in raw_images if str(p).strip()]
    image_paths = [str(Path(p)) for p in image_paths if str(p).strip()]

    problem_id = make_problem_id(spec.key, record, index)
    raw_question_text = normalize_whitespace((extracted.get("raw_question_text") or extracted.get("question_text") or record.get("question") or record.get("problem") or "").strip())

    unified = UnifiedSample(
        dataset_key=spec.key,
        dataset_display_name=spec.display_name,
        subject=spec.subject,
        source_dataset=spec.display_name,
        source_split=str(spec.split or record.get("split") or "unknown"),
        source_problem_id=str(record.get("id") or record.get("image_id") or index),
        raw_question_text=raw_question_text,
        raw_answer_text=raw_answer_text,
        image=image_paths[0] if image_paths else None,
        image_source=image_paths[0] if image_paths else None,
        raw_record=record,
        metadata={
            "problem_id": problem_id,
            "image_paths": image_paths,
            "extraction_notes": extracted.get("extraction_notes") or [],
        },
        choice_map=choice_map,
        force_requires_image=bool(extracted.get("force_requires_image")) or spec.force_requires_image,
    )

    unified_dict = asdict(unified)
    sample_for_scoring = {
        "problem_id": problem_id,
        "question_text": unified_dict["raw_question_text"],
        "answer_text": unified_dict["raw_answer_text"],
        "image_paths": image_paths,
    }
    if scoring_prompt_path is not None:
        unified_dict["preliminary_scoring"] = score_sample(sample_for_scoring, scoring_prompt_path, asset_base_dir=asset_base_dir)
    return unified_dict


def decide_from_signals(scoring: dict, rewrite_report: dict, requires_image: bool, image_count: int, alignment_record: dict | None, thresholds: ThresholdConfig) -> str:
    score = scoring.get("preliminary_value_score")
    dims = scoring.get("preliminary_value_dimensions") or {}
    multimodal = dims.get("multimodal_necessity")
    decomposability = dims.get("node_decomposability")
    answer_stability = dims.get("answer_stability")

    if rewrite_report.get("strategy") == "drop_image_index":
        return "reject"
    if requires_image and image_count <= 0:
        return "reject"
    alignment_status = (alignment_record or {}).get("alignment_status")
    if alignment_status == "bad":
        return "reject"
    if isinstance(multimodal, (int, float)) and isinstance(decomposability, (int, float)):
        if multimodal >= 4 and decomposability >= 4:
            if isinstance(score, (int, float)) and score >= thresholds.reject_score_threshold:
                if alignment_status == "risky":
                    return "review"
                if isinstance(answer_stability, (int, float)) and answer_stability >= 4:
                    return "pass"
                if isinstance(score, (int, float)) and score >= thresholds.pass_score_threshold:
                    return "pass"
                return "review"
    if isinstance(score, (int, float)):
        if score >= thresholds.pass_score_threshold:
            return "pass"
        if score >= thresholds.reject_score_threshold:
            return "review"
        return "reject"
    return "review"


def build_alignment_record(unified: dict, problem_main_record: dict, pipeline_run_id: str, config: PipelineConfig) -> dict:
    question_text = problem_main_record["normalized_question_text"]
    requires_image = problem_main_record["requires_image"]
    image_count = problem_main_record["image_count"]
    image_hint = bool(re.search(r"\b(figure|diagram|graph|chart|image|shown|below|sample)\b", question_text, flags=re.I))
    coverage_score = 0.9 if requires_image else 1.0
    consistency_score = 0.88 if requires_image else 1.0
    conflict_pairs: list[dict[str, Any]] = []
    if requires_image and image_count <= 0:
        coverage_score -= 0.45
        consistency_score -= 0.45
        conflict_pairs.append({"type": "missing_image", "detail": "Question appears image-dependent but no image asset is present.", "confidence": 0.98})
    if requires_image and not image_hint:
        consistency_score -= 0.08
    if not requires_image and image_count > 0 and image_hint:
        consistency_score -= 0.04
    coverage_score = round(clamp(coverage_score), 4)
    consistency_score = round(clamp(consistency_score), 4)
    status = "good"
    if consistency_score < config.thresholds.min_alignment_consistency:
        status = "bad"
    elif consistency_score < config.thresholds.min_alignment_consistency + 0.15:
        status = "risky"
    alignment_id = f"align_{stable_digest([problem_main_record['problem_id'], pipeline_run_id])}"
    text_ref = f"asset_{stable_digest([problem_main_record['problem_id'], 'question_text_normalized'])}"
    image_ref = f"asset_{stable_digest([problem_main_record['problem_id'], 'primary_image'])}"
    return {
        "alignment_id": alignment_id,
        "problem_id": problem_main_record["problem_id"],
        "image_entity_refs": [image_ref] if image_count > 0 else [],
        "text_span_refs": [text_ref],
        "alignment_pairs": [
            {
                "text_ref": text_ref,
                "image_ref": image_ref,
                "relation": "global_figure_reference",
                "confidence": 0.88,
            }
        ] if image_count > 0 else [],
        "conflict_pairs": conflict_pairs,
        "coverage_score": coverage_score,
        "consistency_score": consistency_score,
        "alignment_status": status,
        "created_at": utc_now(),
    }


def fallback_rewrite(question_text: str, normalized_answer: str, answer_type: str, choices: dict[str, str]) -> dict:
    question_only = question_text.strip()
    lower_q = question_only.lower()
    if not choices:
        return {
            "strategy": "keep_open",
            "rationale": "Question is already open-ended.",
            "variants": [
                {
                    "variant_id": "open_1",
                    "title": "开放题 1",
                    "rewritten_question_text": question_only,
                    "expected_answer_type": answer_type,
                    "expected_answer": normalized_answer,
                    "split_role": "single",
                }
            ],
            "discard_reason_codes": [],
        }
    choice_values = [str(v).strip() for _, v in sorted(choices.items()) if str(v).strip()]
    figure_index_pattern = re.compile(r"^(figure|diagram|graph|waveform|image)\s*[a-z0-9]+$", flags=re.I)
    all_index_choices = bool(choice_values) and all(figure_index_pattern.fullmatch(value) for value in choice_values)
    select_option_question = bool(re.search(r"\b(select|choose|which option|option|figure)\b", lower_q))
    if all_index_choices and select_option_question:
        return {
            "strategy": "drop_image_index",
            "rationale": "Pure image-index multiple-choice question should be dropped.",
            "variants": [],
            "discard_reason_codes": ["pure_image_index_choice"],
        }
    split_pieces = [piece.strip() for piece in re.split(r"[;；]", normalized_answer) if piece.strip()]
    if len(split_pieces) > 1:
        return {
            "strategy": "split_open",
            "rationale": "Compound answer was split into multiple open-ended targets.",
            "variants": [
                {
                    "variant_id": f"open_{idx}",
                    "title": f"开放题 {idx}",
                    "rewritten_question_text": f"{question_only}\n请只回答第 {idx} 个目标。",
                    "expected_answer_type": "short_text",
                    "expected_answer": piece,
                    "split_role": f"part_{idx}",
                }
                for idx, piece in enumerate(split_pieces, start=1)
            ],
            "discard_reason_codes": [],
        }
    return {
        "strategy": "blank_open",
        "rationale": "Converted multiple-choice question into blank-style open-ended question.",
        "variants": [
            {
                "variant_id": "open_1",
                "title": "开放题 1",
                "rewritten_question_text": question_only,
                "expected_answer_type": answer_type if answer_type != "option" else "short_text",
                "expected_answer": normalized_answer,
                "split_role": "single",
            }
        ],
        "discard_reason_codes": [],
    }


def build_open_variants(problem_id: str, rewrite_report: dict) -> list[dict]:
    variants: list[dict] = []
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


def build_rewrite_record(problem_main_record: dict, unified: dict, rewrite_report: dict, open_variants: list[dict], pipeline_run_id: str) -> dict:
    return {
        "rewrite_id": f"rewrite_{stable_digest([problem_main_record['problem_id'], pipeline_run_id])}",
        "problem_id": problem_main_record["problem_id"],
        "source_problem_id": unified["source_problem_id"],
        "strategy": rewrite_report.get("strategy"),
        "rationale": rewrite_report.get("rationale"),
        "discard_reason_codes": rewrite_report.get("discard_reason_codes", []),
        "variant_count": len(open_variants),
        "variants": open_variants,
        "created_at": utc_now(),
    }


def build_problem_main_record(unified: dict, pipeline_run_id: str) -> dict:
    normalized_answer = normalize_answer_text(unified["raw_answer_text"])
    answer_type = infer_answer_type(normalized_answer)
    rewrite_report = fallback_rewrite(unified["raw_question_text"], normalized_answer, answer_type, unified.get("choice_map") or {})
    open_variants = build_open_variants(unified["metadata"]["problem_id"], rewrite_report)
    return {
        "problem_id": unified["metadata"]["problem_id"],
        "source_dataset": unified["dataset_display_name"],
        "source_split": unified["source_split"],
        "source_problem_id": unified["source_problem_id"],
        "ingest_batch_id": pipeline_run_id,
        "problem_type": "multimodal_reasoning",
        "domain_tags": [unified.get("subject") or "unknown"],
        "language": detect_language(unified["raw_question_text"]),
        "raw_question_text": unified["raw_question_text"],
        "normalized_question_text": unified["raw_question_text"],
        "raw_answer_text": unified["raw_answer_text"],
        "normalized_answer_text": normalized_answer,
        "answer_type": answer_type,
        "image_count": len(unified["metadata"].get("image_paths", [])),
        "has_multiple_images": len(unified["metadata"].get("image_paths", [])) > 1,
        "requires_image": bool(unified.get("force_requires_image")) or bool(unified["metadata"].get("image_paths")),
        "multimodal_strength_score": (unified.get("preliminary_scoring", {}).get("preliminary_value_dimensions") or {}).get("multimodal_necessity"),
        "multi_step_score": (unified.get("preliminary_scoring", {}).get("preliminary_value_dimensions") or {}).get("node_decomposability"),
        "verifiability_score": (unified.get("preliminary_scoring", {}).get("preliminary_value_dimensions") or {}).get("answer_stability"),
        "quality_risk_flags": [],
        "current_status": None,
        "clean_decision": None,
        "clean_decision_reason_codes": [],
        "review_priority": (unified.get("preliminary_scoring", {}).get("preliminary_value_dimensions") or {}).get("review_priority") or unified.get("preliminary_scoring", {}).get("preliminary_value_level"),
        "annotation_ready": False,
        "qa_precheck_ready": bool(open_variants),
        "release_reserved": {},
        "rewrite_strategy": rewrite_report.get("strategy"),
        "open_variant_count": len(open_variants),
        "created_at": utc_now(),
        "updated_at": utc_now(),
    }


def build_asset_records(unified: dict, asset_base_dir: Path | None = None) -> list[dict]:
    created_at = utc_now()
    problem_id = unified["metadata"]["problem_id"]
    assets: list[dict] = []
    question_text_asset_id = f"asset_{stable_digest([problem_id, 'question_text_normalized'])}"
    assets.append({
        "asset_id": question_text_asset_id,
        "problem_id": problem_id,
        "asset_type": "text",
        "asset_role": "question_text_normalized",
        "source_uri": None,
        "storage_uri": f"inline://{problem_id}/question_text_normalized",
        "file_format": "txt",
        "file_size_bytes": len(unified["raw_question_text"].encode("utf-8")),
        "width": None,
        "height": None,
        "sha256": None,
        "perceptual_hash": None,
        "source_text_snapshot": unified["raw_question_text"],
        "normalized_text_snapshot": unified["raw_question_text"],
        "text_completeness_score": None,
        "blur_score": None,
        "readability_score": None,
        "noise_score": None,
        "cropped_from_asset_id": None,
        "roi_bbox": None,
        "asset_quality_flags": [],
        "is_usable": bool(unified["raw_question_text"]),
        "discard_reason_codes": [],
        "created_at": created_at,
        "updated_at": created_at,
    })
    answer_text_asset_id = f"asset_{stable_digest([problem_id, 'answer_text_normalized'])}"
    assets.append({
        "asset_id": answer_text_asset_id,
        "problem_id": problem_id,
        "asset_type": "text",
        "asset_role": "answer_text_normalized",
        "source_uri": None,
        "storage_uri": f"inline://{problem_id}/answer_text_normalized",
        "file_format": "txt",
        "file_size_bytes": len(unified["raw_answer_text"].encode("utf-8")),
        "width": None,
        "height": None,
        "sha256": None,
        "perceptual_hash": None,
        "source_text_snapshot": unified["raw_answer_text"],
        "normalized_text_snapshot": normalize_answer_text(unified["raw_answer_text"]),
        "text_completeness_score": None,
        "blur_score": None,
        "readability_score": None,
        "noise_score": None,
        "cropped_from_asset_id": None,
        "roi_bbox": None,
        "asset_quality_flags": [],
        "is_usable": bool(unified["raw_answer_text"]),
        "discard_reason_codes": [],
        "created_at": created_at,
        "updated_at": created_at,
    })
    image_paths = unified["metadata"].get("image_paths") or []
    for idx, image_path_value in enumerate(image_paths, start=1):
        image_path = Path(image_path_value)
        if not image_path.is_absolute() and asset_base_dir is not None:
            image_path = asset_base_dir / image_path
        asset_id = f"asset_{stable_digest([problem_id, 'primary_image' if idx == 1 else f'aux_image_{idx}'])}"
        image_bytes = None
        try:
            if image_path.exists():
                image_bytes = image_path.read_bytes()
        except Exception:
            image_bytes = None
        assets.append({
            "asset_id": asset_id,
            "problem_id": problem_id,
            "asset_type": "image",
            "asset_role": "primary_image" if idx == 1 else f"aux_image_{idx}",
            "source_uri": str(image_path),
            "storage_uri": str(image_path),
            "file_format": image_path.suffix.lstrip(".") or None,
            "file_size_bytes": len(image_bytes) if image_bytes else None,
            "width": None,
            "height": None,
            "sha256": sha256_bytes(image_bytes) if image_bytes else None,
            "perceptual_hash": None,
            "source_text_snapshot": None,
            "normalized_text_snapshot": None,
            "text_completeness_score": None,
            "blur_score": None,
            "readability_score": None,
            "noise_score": None,
            "cropped_from_asset_id": None,
            "roi_bbox": None,
            "asset_quality_flags": [],
            "is_usable": True,
            "discard_reason_codes": [],
            "created_at": created_at,
            "updated_at": created_at,
        })
    return assets


def build_cleaning_record(unified: dict, problem_main_record: dict, asset_records: list[dict], alignment_record: dict, rewrite_report: dict, open_variants: list[dict], pipeline_run_id: str, config: PipelineConfig) -> dict:
    scoring = unified.get("preliminary_scoring") or {}
    decision = problem_main_record["clean_decision"]
    score = scoring.get("preliminary_value_score")
    if decision == "pass":
        reason_codes = ["meets_candidate_threshold"]
    elif decision == "review":
        reason_codes = ["borderline_candidate_score"]
    else:
        reason_codes = ["below_candidate_threshold"]
    return {
        "cleaning_id": f"clean_{stable_digest([unified['metadata']['problem_id'], pipeline_run_id])}",
        "problem_id": unified["metadata"]["problem_id"],
        "cleaning_version": config.cleaning_version,
        "pipeline_run_id": pipeline_run_id,
        "dataset_name": unified["dataset_display_name"],
        "input_asset_ids": [asset["asset_id"] for asset in asset_records],
        "normalization_actions": [
            {"action_type": "text_normalized", "trigger": "NormalizationAgent", "confidence": 0.90, "human_confirmed": False},
            {"action_type": "answer_canonicalized", "trigger": "NormalizationAgent", "confidence": 0.95, "human_confirmed": False},
            {"action_type": "llm_unified_extraction", "trigger": "UnifiedSampleExtractionAgent", "confidence": 0.85, "human_confirmed": False},
            {"action_type": "question_rewritten", "trigger": "QuestionRewriteAgent", "confidence": 0.70, "human_confirmed": False},
        ],
        "quality_checks": [
            {"check": "preliminary_value_scoring", "result": scoring, "passed": decision != "reject"}
        ],
        "alignment_summary": {
            "alignment_id": alignment_record["alignment_id"],
            "coverage_score": alignment_record["coverage_score"],
            "consistency_score": alignment_record["consistency_score"],
            "alignment_status": alignment_record["alignment_status"],
        },
        "rewrite_summary": {
            "strategy": rewrite_report.get("strategy"),
            "variant_count": len(open_variants),
            "discard_reason_codes": rewrite_report.get("discard_reason_codes", []),
        },
        "risk_flags": [],
        "clean_score": score,
        "decision": decision,
        "decision_reason_codes": reason_codes,
        "review_ticket_id": f"review_{unified['metadata']['problem_id']}" if decision == "review" else None,
        "operator_type": "system",
        "started_at": utc_now(),
        "finished_at": utc_now(),
    }


def build_reject_record(problem_main_record: dict, cleaning_record: dict, alignment_record: dict, rewrite_report: dict, pipeline_run_id: str) -> dict | None:
    if problem_main_record["clean_decision"] != "reject":
        return None
    return {
        "reject_id": f"reject_{stable_digest([problem_main_record['problem_id'], pipeline_run_id])}",
        "problem_id": problem_main_record["problem_id"],
        "stage": "cleaning",
        "reject_level": "problem",
        "reject_reason_codes": cleaning_record["decision_reason_codes"],
        "reject_reason_detail": rewrite_report.get("rationale") or "Rejected by cleaning gate.",
        "blocking_fields": cleaning_record.get("risk_flags", []),
        "evidence_refs": [alignment_record["alignment_id"]],
        "recoverable": False,
        "recommended_action": "drop",
        "reviewed_by": None,
        "created_at": utc_now(),
    }


def build_field_audit_records(unified: dict, problem_main_record: dict, cleaning_record: dict, rewrite_report: dict) -> list[dict]:
    timestamp = utc_now()
    problem_id = problem_main_record["problem_id"]
    raw_question = unified["raw_record"].get("question") or unified["raw_record"].get("problem") or ""
    raw_answer = unified["raw_record"].get("answer") or unified["raw_record"].get("solution") or ""
    return [
        {
            "audit_id": f"audit_{problem_id}_normalized_question_text",
            "problem_id": problem_id,
            "record_type": "problem_main_record",
            "field_name": "normalized_question_text",
            "before_value": raw_question,
            "after_value": problem_main_record["normalized_question_text"],
            "change_type": "text_normalized",
            "trigger": "UnifiedSampleExtractionAgent",
            "operator_type": "system",
            "created_at": timestamp,
        },
        {
            "audit_id": f"audit_{problem_id}_normalized_answer_text",
            "problem_id": problem_id,
            "record_type": "problem_main_record",
            "field_name": "normalized_answer_text",
            "before_value": raw_answer,
            "after_value": problem_main_record["normalized_answer_text"],
            "change_type": "answer_canonicalized",
            "trigger": "NormalizationAgent",
            "operator_type": "system",
            "created_at": timestamp,
        },
        {
            "audit_id": f"audit_{problem_id}_rewrite_strategy",
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
            "audit_id": f"audit_{problem_id}_clean_decision",
            "problem_id": problem_id,
            "record_type": "cleaning_record",
            "field_name": "decision",
            "before_value": None,
            "after_value": cleaning_record["decision"],
            "change_type": "gate_decision",
            "trigger": "CandidateCleanGate",
            "operator_type": "system",
            "created_at": timestamp,
        },
    ]


class PromptExtractionPipeline:
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.pipeline_run_id = f"run_{stable_digest([utc_now(), 'multidataset-clean'], 16)}"
        self.ingest_batch_id = f"{config.batch_id_prefix}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
        self.output_root = Path(config.output_root)
        self.run_dir = self.output_root / self.pipeline_run_id
        self.records_dir = self.run_dir / "records"
        self.dataset_root = self.run_dir / "datasets"
        ensure_dir(self.records_dir)
        ensure_dir(self.dataset_root)
        self.aggregate_summary: dict[str, Any] = {
            "pipeline_run_id": self.pipeline_run_id,
            "created_at": utc_now(),
            "datasets": [],
        }

    def connector_for(self, spec: DatasetSpec) -> BaseConnector:
        if spec.source_kind == "github":
            return GitHubConnector(spec, self.config)
        if spec.source_kind == "local_file":
            return LocalFileConnector(spec, self.config)
        return SourceUnavailableConnector(spec, self.config)

    def process_sample(self, spec: DatasetSpec, unified: dict, asset_base_dir: Path | None) -> dict[str, Any]:
        scoring = unified.get("preliminary_scoring") or {}
        problem_main_record = build_problem_main_record(unified, self.ingest_batch_id)
        rewrite_report = fallback_rewrite(
            problem_main_record["normalized_question_text"],
            problem_main_record["normalized_answer_text"],
            problem_main_record["answer_type"],
            unified.get("choice_map") or {},
        )
        open_variants = build_open_variants(problem_main_record["problem_id"], rewrite_report)
        rewrite_record = build_rewrite_record(problem_main_record, unified, rewrite_report, open_variants, self.pipeline_run_id)
        asset_records = build_asset_records(unified, asset_base_dir=asset_base_dir)
        alignment_record = build_alignment_record(unified, problem_main_record, self.pipeline_run_id, self.config)
        final_decision = decide_from_signals(
            scoring=scoring,
            rewrite_report=rewrite_report,
            requires_image=problem_main_record["requires_image"],
            image_count=problem_main_record["image_count"],
            alignment_record=alignment_record,
            thresholds=self.config.thresholds,
        )
        if final_decision == "pass":
            reason_codes = ["meets_candidate_threshold"]
        elif final_decision == "review":
            reason_codes = ["borderline_candidate_score"]
        else:
            reason_codes = ["below_candidate_threshold"]
        problem_main_record["clean_decision"] = final_decision
        problem_main_record["current_status"] = {"pass": "clean_passed", "review": "cleaning_review", "reject": "clean_rejected"}[final_decision]
        problem_main_record["clean_decision_reason_codes"] = reason_codes
        problem_main_record["annotation_ready"] = final_decision == "pass"
        problem_main_record["qa_precheck_ready"] = bool(open_variants) and final_decision != "reject"
        cleaning_record = build_cleaning_record(unified, problem_main_record, asset_records, alignment_record, rewrite_report, open_variants, self.pipeline_run_id, self.config)
        reject_record = build_reject_record(problem_main_record, cleaning_record, alignment_record, rewrite_report, self.pipeline_run_id)
        field_audits = build_field_audit_records(unified, problem_main_record, cleaning_record, rewrite_report)
        return {
            "problem_main_record": problem_main_record,
            "asset_records": asset_records,
            "alignment_record": alignment_record,
            "rewrite_record": rewrite_record,
            "open_variants": open_variants,
            "cleaning_record": cleaning_record,
            "reject_record": reject_record,
            "field_audit_records": field_audits,
            "unified_sample": unified,
        }

    def run_single_dataset(self, spec: DatasetSpec) -> dict[str, Any]:
        connector = self.connector_for(spec)
        source_status, rows, detail, asset_base_dir = connector.sample()
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
            }
            write_json(dataset_dir / "summary.json", summary)
            return summary
        bundle = {
            "unified_samples": [],
            "problem_main_records": [],
            "asset_records": [],
            "alignment_records": [],
            "rewrite_reports": [],
            "open_ended_problem_variants": [],
            "cleaning_records": [],
            "reject_records": [],
            "field_audit_records": [],
        }
        for index, row in enumerate(rows):
            unified = build_unified_sample(row, index, spec, asset_base_dir=asset_base_dir, scoring_prompt_path=SCORING_PROMPT_PATH)
            result = self.process_sample(spec, unified, asset_base_dir)
            bundle["unified_samples"].append(result["unified_sample"])
            bundle["problem_main_records"].append(result["problem_main_record"])
            bundle["asset_records"].extend(result["asset_records"])
            bundle["alignment_records"].append(result["alignment_record"])
            bundle["rewrite_reports"].append(result["rewrite_record"])
            bundle["open_ended_problem_variants"].extend(result["open_variants"])
            bundle["cleaning_records"].append(result["cleaning_record"])
            bundle["field_audit_records"].extend(result["field_audit_records"])
            if result["reject_record"]:
                bundle["reject_records"].append(result["reject_record"])
        records_dir = dataset_dir / "records"
        ensure_dir(records_dir)
        for key, rows_out in bundle.items():
            write_jsonl(records_dir / f"{key}.jsonl", rows_out)
        decision_counts = {"pass": 0, "review": 0, "reject": 0}
        rewrite_strategy_counts: dict[str, int] = {}
        for record in bundle["problem_main_records"]:
            decision_counts[record["clean_decision"]] += 1
            strategy = record.get("rewrite_strategy") or "unknown"
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
        }
        write_json(dataset_dir / "summary.json", summary)
        return summary

    def run(self) -> dict[str, Any]:
        dataset_summaries = []
        for spec in self.config.datasets:
            dataset_summaries.append(self.run_single_dataset(spec))
        self.aggregate_summary["datasets"] = dataset_summaries
        write_json(self.run_dir / "summary.json", self.aggregate_summary)
        return self.aggregate_summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prompt-extraction pipeline with reference-style outputs")
    parser.add_argument("input", type=Path, nargs="?", default=None, help="Path to local JSON/JSONL input")
    parser.add_argument("--prefix", default="sample")
    parser.add_argument("--dataset-key", default="local_dataset")
    parser.add_argument("--dataset-name", default="Local Dataset")
    parser.add_argument("--subject", default="unknown")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--reset-output", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = PipelineConfig()
    if args.limit:
        config.sample_per_dataset = args.limit
    spec = DatasetSpec(
        key=args.dataset_key or args.prefix,
        display_name=args.dataset_name,
        subject=args.subject,
        source_kind="local_file",
        source_locator=str(args.input) if args.input else "",
        split="unknown",
    )
    config.datasets = [spec]
    pipeline = PromptExtractionPipeline(config)
    if args.reset_output and pipeline.output_root.exists():
        shutil.rmtree(pipeline.output_root)
    summary = pipeline.run()
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
