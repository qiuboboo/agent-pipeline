#!/usr/bin/env python3
"""EEE-Bench 数据采集与清洗自动化流水线。

本实现严格围绕 plans/数据采集与清洗自动化搭建文档.md 中的采集与清洗要求，
提供以下能力：
1. Hugging Face 数据集接入与统一映射
2. problem_main_record / asset_record / node_record / cleaning_record / reject_record
   / alignment_record / field_audit_record 的结构化产出
3. 原始字段保留、规范化字段派生、字段审计与可追溯日志
4. 图像质量检测（分辨率、模糊度、对比度、可读性、内容区域）
5. 缺失字段处理、规则门控、通过/复核/淘汰决策
6. 小批量验证与统计汇总输出
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import re
import shutil
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
import yaml
from datasets import Dataset, load_dataset
from PIL import Image


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def json_default(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, np.generic):
        return value.item()
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
    if isinstance(value, (list, tuple)):
        return "\n".join(to_plain_text(item) for item in value)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def normalize_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


class TextNormalizer:
    IMAGE_HINT_PATTERN = re.compile(
        r"\b(figure|fig\.?|diagram|graph|chart|circuit|schematic|shown in the figure|shown below|waveform|table)\b",
        re.IGNORECASE,
    )
    OPTION_PATTERN = re.compile(r"(?:^|\n)\s*(?:[A-H][\.:\)]\s*|\*\*Choices:\*\*)", re.IGNORECASE)
    NUMERIC_PATTERN = re.compile(r"^[+-]?(?:\d+(?:\.\d+)?|\.\d+)$")

    def normalize_text(self, text: Any) -> str:
        value = unicodedata.normalize("NFKC", to_plain_text(text))
        value = value.replace("\u00a0", " ")
        value = normalize_whitespace(value)
        return value

    def normalize_answer(self, answer: Any) -> str:
        value = self.normalize_text(answer)
        value = value.strip(". ")
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

    def extract_question_body(self, text: str) -> str:
        match = re.search(r"Question\s*:\s*(.*)", text, flags=re.IGNORECASE | re.DOTALL)
        if match:
            return normalize_whitespace(match.group(1))
        return text

    def extract_choices(self, text: str) -> List[str]:
        choices: List[str] = []
        for line in text.splitlines():
            line = line.strip()
            if re.match(r"^[A-H][\.:\)]\s*", line):
                choices.append(line)
        return choices

    def infer_requires_image(self, question_text: str, image_count: int) -> bool:
        if image_count <= 0:
            return False
        return bool(self.IMAGE_HINT_PATTERN.search(question_text))

    def text_completeness_score(self, raw_text: str, normalized_text: str) -> float:
        if not raw_text:
            return 0.0
        length_score = clamp(min(len(normalized_text), 400) / 220.0)
        question_bonus = 0.15 if "question:" in normalized_text.lower() else 0.0
        answer_hint_bonus = 0.1 if "hint:" in normalized_text.lower() else 0.0
        return round(clamp(0.55 + 0.25 * length_score + question_bonus + answer_hint_bonus), 4)


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
        lap = (
            padded[:-2, 1:-1]
            + padded[2:, 1:-1]
            + padded[1:-1, :-2]
            + padded[1:-1, 2:]
            - 4.0 * center
        )
        return float(np.var(lap))

    def contrast_score(self, gray: np.ndarray) -> float:
        return float(np.std(gray))

    def noise_score(self, gray: np.ndarray) -> float:
        coarse = np.asarray(
            Image.fromarray(gray.clip(0, 255).astype(np.uint8)).resize(
                (max(1, gray.shape[1] // 4), max(1, gray.shape[0] // 4)),
                Image.Resampling.BILINEAR,
            ).resize((gray.shape[1], gray.shape[0]), Image.Resampling.BILINEAR),
            dtype=np.float32,
        )
        residual = gray - coarse
        return float(np.std(residual))

    def detect_content_bbox(self, gray: np.ndarray) -> Optional[Dict[str, int]]:
        normalized = gray / 255.0
        mask = normalized < 0.97
        if mask.sum() == 0:
            return None
        ys, xs = np.where(mask)
        x1, x2 = int(xs.min()), int(xs.max())
        y1, y2 = int(ys.min()), int(ys.max())
        width = int(x2 - x1 + 1)
        height = int(y2 - y1 + 1)
        return {"x": x1, "y": y1, "width": width, "height": height}

    def crop_integrity_score(self, bbox: Optional[Dict[str, int]], width: int, height: int) -> float:
        if bbox is None:
            return 0.0
        left_margin = bbox["x"]
        top_margin = bbox["y"]
        right_margin = width - (bbox["x"] + bbox["width"])
        bottom_margin = height - (bbox["y"] + bbox["height"])
        clipped_edges = sum(margin <= 1 for margin in [left_margin, top_margin, right_margin, bottom_margin])
        return round(clamp(1.0 - 0.22 * clipped_edges), 4)

    def readability_score(
        self,
        blur_score: float,
        contrast_score: float,
        width: int,
        height: int,
        crop_integrity: float,
    ) -> float:
        sharpness = clamp(math.log1p(max(blur_score, 0.0)) / 8.0)
        contrast = clamp(contrast_score / 64.0)
        resolution = clamp(min(width / 512.0, height / 512.0))
        score = 0.4 * sharpness + 0.25 * contrast + 0.2 * resolution + 0.15 * crop_integrity
        return round(clamp(score), 4)

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


@dataclass
class PipelineConfig:
    dataset_name: str = "afdsafas/EEE-Bench"
    split: str = "test"
    sample_limit: int = 200
    sample_strategy: str = "head"
    shuffle_seed: int = 42
    output_root: str = "outputs/eee_pipeline"
    cleaning_version: str = "v1.0.0"
    batch_id_prefix: str = "eee-bench"
    min_width: int = 256
    min_height: int = 256
    min_sharpness_score: float = 0.22
    min_readability_score: float = 0.35
    min_contrast_score: float = 18.0
    reject_clean_score_below: float = 0.45
    review_clean_score_below: float = 0.62
    min_text_completeness_score: float = 0.60
    min_alignment_consistency: float = 0.55
    save_sample_bundle: bool = True

    @classmethod
    def from_yaml(cls, path: Optional[str]) -> "PipelineConfig":
        if not path:
            return cls()
        with open(path, "r", encoding="utf-8") as file:
            raw = yaml.safe_load(file) or {}
        dataset = raw.get("dataset", {})
        storage = raw.get("storage", {})
        cleaning = raw.get("cleaning", {})
        thresholds = raw.get("thresholds", {})
        runtime = raw.get("runtime", {})
        return cls(
            dataset_name=dataset.get("name", cls.dataset_name),
            split=dataset.get("split", cls.split),
            sample_limit=dataset.get("sample_limit", cls.sample_limit),
            sample_strategy=dataset.get("sample_strategy", cls.sample_strategy),
            shuffle_seed=dataset.get("shuffle_seed", cls.shuffle_seed),
            output_root=storage.get("output_root", cls.output_root),
            cleaning_version=cleaning.get("version", cls.cleaning_version),
            batch_id_prefix=runtime.get("batch_id_prefix", cls.batch_id_prefix),
            min_width=thresholds.get("min_width", cls.min_width),
            min_height=thresholds.get("min_height", cls.min_height),
            min_sharpness_score=thresholds.get("min_sharpness_score", cls.min_sharpness_score),
            min_readability_score=thresholds.get("min_readability_score", cls.min_readability_score),
            min_contrast_score=thresholds.get("min_contrast_score", cls.min_contrast_score),
            reject_clean_score_below=thresholds.get("reject_clean_score_below", cls.reject_clean_score_below),
            review_clean_score_below=thresholds.get("review_clean_score_below", cls.review_clean_score_below),
            min_text_completeness_score=thresholds.get(
                "min_text_completeness_score", cls.min_text_completeness_score
            ),
            min_alignment_consistency=thresholds.get(
                "min_alignment_consistency", cls.min_alignment_consistency
            ),
            save_sample_bundle=runtime.get("save_sample_bundle", cls.save_sample_bundle),
        )


class EEEPipeline:
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.text_normalizer = TextNormalizer()
        self.image_analyzer = ImageQualityAnalyzer()
        self.pipeline_run_id = f"run_{stable_digest([utc_now(), config.dataset_name, config.split], 16)}"
        self.ingest_batch_id = f"{config.batch_id_prefix}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
        self.output_root = Path(config.output_root)
        self.run_dir = self.output_root / self.pipeline_run_id
        self.artifact_dir = self.run_dir / "artifacts"
        self.image_dir = self.artifact_dir / "images"
        self.crop_dir = self.artifact_dir / "crops"
        self.sample_dir = self.run_dir / "samples"
        self.records_dir = self.run_dir / "records"
        self.problems: List[Dict[str, Any]] = []
        self.assets: List[Dict[str, Any]] = []
        self.nodes: List[Dict[str, Any]] = []
        self.cleanings: List[Dict[str, Any]] = []
        self.rejects: List[Dict[str, Any]] = []
        self.alignments: List[Dict[str, Any]] = []
        self.field_audits: List[Dict[str, Any]] = []
        ensure_dir(self.image_dir)
        ensure_dir(self.crop_dir)
        ensure_dir(self.sample_dir)
        ensure_dir(self.records_dir)

    def load_source_dataset(self) -> Dataset:
        dataset = load_dataset(self.config.dataset_name, split=self.config.split)
        if self.config.sample_strategy == "random":
            dataset = dataset.shuffle(seed=self.config.shuffle_seed)
        if self.config.sample_limit > 0:
            dataset = dataset.select(range(min(self.config.sample_limit, len(dataset))))
        return dataset

    def export_outputs(self) -> Dict[str, Path]:
        files = {
            "problems": self.records_dir / "problem_main_records.jsonl",
            "assets": self.records_dir / "asset_records.jsonl",
            "nodes": self.records_dir / "node_records.jsonl",
            "cleanings": self.records_dir / "cleaning_records.jsonl",
            "rejects": self.records_dir / "reject_records.jsonl",
            "alignments": self.records_dir / "alignment_records.jsonl",
            "field_audits": self.records_dir / "field_audit_records.jsonl",
        }
        write_jsonl(files["problems"], self.problems)
        write_jsonl(files["assets"], self.assets)
        write_jsonl(files["nodes"], self.nodes)
        write_jsonl(files["cleanings"], self.cleanings)
        write_jsonl(files["rejects"], self.rejects)
        write_jsonl(files["alignments"], self.alignments)
        write_jsonl(files["field_audits"], self.field_audits)
        return files

    def run(self) -> Dict[str, Any]:
        dataset = self.load_source_dataset()
        for index, row in enumerate(dataset):
            result = self.process_row(index=index, row=row)
            self.problems.append(result["problem_main_record"])
            self.assets.extend(result["asset_records"])
            self.nodes.extend(result["node_records"])
            self.cleanings.append(result["cleaning_record"])
            self.alignments.append(result["alignment_record"])
            self.field_audits.extend(result["field_audit_records"])
            if result["reject_record"] is not None:
                self.rejects.append(result["reject_record"])
            if self.config.save_sample_bundle:
                sample_path = self.sample_dir / f"{result['problem_main_record']['problem_id']}.json"
                write_json(sample_path, result)
        exported = self.export_outputs()
        summary = self.build_summary(dataset_size=len(dataset), exported_files=exported)
        write_json(self.run_dir / "summary.json", summary)
        return summary

    def process_row(self, index: int, row: Dict[str, Any]) -> Dict[str, Any]:
        started_at = utc_now()
        raw_question_text = to_plain_text(row.get("problem"))
        raw_answer_text = to_plain_text(row.get("solution"))
        image = row.get("image")
        if image is None:
            raise ValueError(f"Row {index} is missing image field")
        image_bytes = self.image_analyzer.pil_to_png_bytes(image)
        image_sha = sha256_bytes(image_bytes)
        source_problem_id = str(index)
        problem_id = f"prob_{stable_digest([self.config.dataset_name, self.config.split, source_problem_id, image_sha])}"
        created_at = utc_now()

        raw_text_normalized = self.text_normalizer.normalize_text(raw_question_text)
        normalized_question_text = raw_text_normalized
        normalized_answer_text = self.text_normalizer.normalize_answer(raw_answer_text)
        language = self.text_normalizer.detect_language(normalized_question_text)
        answer_type = self.text_normalizer.infer_answer_type(normalized_answer_text)
        question_body = self.text_normalizer.extract_question_body(normalized_question_text)
        choices = self.text_normalizer.extract_choices(normalized_question_text)
        image_count = 1
        requires_image = self.text_normalizer.infer_requires_image(normalized_question_text, image_count)
        text_completeness = self.text_normalizer.text_completeness_score(raw_question_text, normalized_question_text)

        image_path = self.image_dir / f"{problem_id}_primary.png"
        ensure_dir(image_path.parent)
        with image_path.open("wb") as file:
            file.write(image_bytes)

        image_quality = self.image_analyzer.analyze(image)
        roi_asset, roi_bbox = self.create_roi_asset(problem_id, image, image_quality)
        potential_scores = self.compute_potential_scores(
            normalized_question_text=normalized_question_text,
            normalized_answer_text=normalized_answer_text,
            answer_type=answer_type,
            requires_image=requires_image,
            image_quality=image_quality,
            choices=choices,
        )

        missing_field_summary = self.build_missing_field_summary(
            raw_question_text=raw_question_text,
            raw_answer_text=raw_answer_text,
            normalized_question_text=normalized_question_text,
            normalized_answer_text=normalized_answer_text,
            blur_score=image_quality["blur_score"],
        )
        quality_flags = self.build_quality_flags(
            raw_question_text=raw_question_text,
            raw_answer_text=raw_answer_text,
            text_completeness_score=text_completeness,
            image_quality=image_quality,
        )

        asset_records = self.build_asset_records(
            problem_id=problem_id,
            source_problem_id=source_problem_id,
            image_sha=image_sha,
            image_path=image_path,
            raw_question_text=raw_question_text,
            normalized_question_text=normalized_question_text,
            raw_answer_text=raw_answer_text,
            normalized_answer_text=normalized_answer_text,
            text_completeness=text_completeness,
            image_quality=image_quality,
            quality_flags=quality_flags,
            roi_asset=roi_asset,
        )
        alignment_record = self.build_alignment_record(
            problem_id=problem_id,
            normalized_question_text=normalized_question_text,
            asset_records=asset_records,
            image_quality=image_quality,
            requires_image=requires_image,
        )
        gate = self.clean_gate(
            requires_image=requires_image,
            raw_question_text=raw_question_text,
            raw_answer_text=raw_answer_text,
            normalized_question_text=normalized_question_text,
            normalized_answer_text=normalized_answer_text,
            text_completeness=text_completeness,
            image_quality=image_quality,
            alignment_record=alignment_record,
            potential_scores=potential_scores,
            quality_flags=quality_flags,
        )
        field_audit_records = self.build_field_audit_records(
            problem_id=problem_id,
            raw_question_text=raw_question_text,
            normalized_question_text=normalized_question_text,
            raw_answer_text=raw_answer_text,
            normalized_answer_text=normalized_answer_text,
            image_quality=image_quality,
            gate=gate,
        )
        node_records = self.build_node_records(
            problem_id=problem_id,
            normalized_question_text=normalized_question_text,
            normalized_answer_text=normalized_answer_text,
            answer_type=answer_type,
            quality_flags=quality_flags,
            image_quality=image_quality,
            asset_records=asset_records,
            choices=choices,
            gate=gate,
            question_body=question_body,
            roi_bbox=roi_bbox,
        )
        problem_main_record = self.build_problem_main_record(
            problem_id=problem_id,
            source_problem_id=source_problem_id,
            created_at=created_at,
            raw_question_text=raw_question_text,
            normalized_question_text=normalized_question_text,
            raw_answer_text=raw_answer_text,
            normalized_answer_text=normalized_answer_text,
            language=language,
            answer_type=answer_type,
            image_count=image_count,
            requires_image=requires_image,
            potential_scores=potential_scores,
            quality_flags=quality_flags,
            gate=gate,
            text_completeness=text_completeness,
            alignment_record=alignment_record,
        )
        cleaning_record = self.build_cleaning_record(
            problem_id=problem_id,
            started_at=started_at,
            finished_at=utc_now(),
            asset_records=asset_records,
            missing_field_summary=missing_field_summary,
            alignment_record=alignment_record,
            image_quality=image_quality,
            quality_flags=quality_flags,
            gate=gate,
            raw_question_text=raw_question_text,
            normalized_question_text=normalized_question_text,
            raw_answer_text=raw_answer_text,
            normalized_answer_text=normalized_answer_text,
        )
        reject_record = self.build_reject_record(
            problem_id=problem_id,
            gate=gate,
            quality_flags=quality_flags,
            alignment_record=alignment_record,
        )
        return {
            "problem_main_record": problem_main_record,
            "asset_records": asset_records,
            "node_records": node_records,
            "cleaning_record": cleaning_record,
            "reject_record": reject_record,
            "alignment_record": alignment_record,
            "field_audit_records": field_audit_records,
        }

    def build_missing_field_summary(
        self,
        raw_question_text: str,
        raw_answer_text: str,
        normalized_question_text: str,
        normalized_answer_text: str,
        blur_score: float,
    ) -> Dict[str, Any]:
        summary = {"missing_fields": [], "actions": [], "blocking_fields": []}
        if not raw_question_text:
            summary["missing_fields"].append("raw_question_text")
            summary["actions"].append({"field": "raw_question_text", "action": "manual_review", "priority": "P0"})
            summary["blocking_fields"].append("raw_question_text")
        if not raw_answer_text:
            summary["missing_fields"].append("raw_answer_text")
            summary["actions"].append({"field": "raw_answer_text", "action": "hard_reject", "priority": "P0"})
            summary["blocking_fields"].append("raw_answer_text")
        if raw_question_text and not normalized_question_text:
            summary["missing_fields"].append("normalized_question_text")
            summary["actions"].append(
                {"field": "normalized_question_text", "action": "generate_by_model", "priority": "P1"}
            )
        if raw_answer_text and not normalized_answer_text:
            summary["missing_fields"].append("normalized_answer_text")
            summary["actions"].append(
                {"field": "normalized_answer_text", "action": "generate_by_model", "priority": "P1"}
            )
        if blur_score <= 0:
            summary["missing_fields"].append("blur_score")
            summary["actions"].append({"field": "blur_score", "action": "derive_by_rule", "priority": "P1"})
        return summary

    def build_quality_flags(
        self,
        raw_question_text: str,
        raw_answer_text: str,
        text_completeness_score: float,
        image_quality: Dict[str, Any],
    ) -> List[str]:
        flags: List[str] = []
        if not raw_question_text:
            flags.append("missing_question_text")
        if not raw_answer_text:
            flags.append("missing_answer")
        if image_quality["width"] < self.config.min_width or image_quality["height"] < self.config.min_height:
            flags.append("low_resolution")
        sharpness_score = clamp(math.log1p(max(image_quality["blur_score"], 0.0)) / 8.0)
        if sharpness_score < self.config.min_sharpness_score:
            flags.append("severe_global_blur")
        if image_quality["readability_score"] < self.config.min_readability_score:
            flags.append("key_text_unreadable")
        if image_quality["contrast_score"] < self.config.min_contrast_score:
            flags.append("contrast_too_low")
        if image_quality["crop_integrity_score"] < 0.45:
            flags.append("severe_crop_loss")
        if text_completeness_score < self.config.min_text_completeness_score:
            flags.append("low_text_completeness")
        return sorted(set(flags))

    def build_asset_records(
        self,
        problem_id: str,
        source_problem_id: str,
        image_sha: str,
        image_path: Path,
        raw_question_text: str,
        normalized_question_text: str,
        raw_answer_text: str,
        normalized_answer_text: str,
        text_completeness: float,
        image_quality: Dict[str, Any],
        quality_flags: List[str],
        roi_asset: Optional[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        created_at = utc_now()
        primary_image_asset_id = f"asset_{stable_digest([problem_id, 'primary_image'])}"
        question_asset_id = f"asset_{stable_digest([problem_id, 'question_source'])}"
        question_norm_asset_id = f"asset_{stable_digest([problem_id, 'question_normalized'])}"
        answer_asset_id = f"asset_{stable_digest([problem_id, 'answer_raw'])}"
        answer_norm_asset_id = f"asset_{stable_digest([problem_id, 'answer_normalized'])}"
        assets = [
            {
                "asset_id": primary_image_asset_id,
                "problem_id": problem_id,
                "asset_type": "image",
                "asset_role": "primary_image",
                "source_uri": f"hf://{self.config.dataset_name}/{self.config.split}/{source_problem_id}/image",
                "storage_uri": str(image_path.relative_to(self.run_dir)),
                "file_format": "png",
                "file_size_bytes": image_path.stat().st_size,
                "width": image_quality["width"],
                "height": image_quality["height"],
                "sha256": image_sha,
                "perceptual_hash": image_quality["perceptual_hash"],
                "source_text_snapshot": None,
                "normalized_text_snapshot": None,
                "text_completeness_score": None,
                "blur_score": image_quality["blur_score"],
                "readability_score": image_quality["readability_score"],
                "noise_score": image_quality["noise_score"],
                "cropped_from_asset_id": None,
                "roi_bbox": image_quality["roi_bbox"],
                "asset_quality_flags": quality_flags,
                "is_usable": not any(flag in quality_flags for flag in ["severe_global_blur", "low_resolution"]),
                "discard_reason_codes": [
                    flag for flag in quality_flags if flag in ["severe_global_blur", "key_text_unreadable", "low_resolution"]
                ],
                "created_at": created_at,
                "updated_at": created_at,
            },
            {
                "asset_id": question_asset_id,
                "problem_id": problem_id,
                "asset_type": "text",
                "asset_role": "question_text_source",
                "source_uri": f"hf://{self.config.dataset_name}/{self.config.split}/{source_problem_id}/problem",
                "storage_uri": f"inline://{question_asset_id}",
                "file_format": "txt",
                "file_size_bytes": len(raw_question_text.encode("utf-8")),
                "width": None,
                "height": None,
                "sha256": sha256_bytes(raw_question_text.encode("utf-8")),
                "perceptual_hash": None,
                "source_text_snapshot": raw_question_text,
                "normalized_text_snapshot": None,
                "text_completeness_score": text_completeness,
                "blur_score": None,
                "readability_score": None,
                "noise_score": None,
                "cropped_from_asset_id": None,
                "roi_bbox": None,
                "asset_quality_flags": ["missing_question_text"] if not raw_question_text else [],
                "is_usable": bool(raw_question_text),
                "discard_reason_codes": ["missing_question_text"] if not raw_question_text else [],
                "created_at": created_at,
                "updated_at": created_at,
            },
            {
                "asset_id": question_norm_asset_id,
                "problem_id": problem_id,
                "asset_type": "text",
                "asset_role": "question_text_normalized",
                "source_uri": None,
                "storage_uri": f"inline://{question_norm_asset_id}",
                "file_format": "txt",
                "file_size_bytes": len(normalized_question_text.encode("utf-8")),
                "width": None,
                "height": None,
                "sha256": sha256_bytes(normalized_question_text.encode("utf-8")),
                "perceptual_hash": None,
                "source_text_snapshot": raw_question_text,
                "normalized_text_snapshot": normalized_question_text,
                "text_completeness_score": text_completeness,
                "blur_score": None,
                "readability_score": None,
                "noise_score": None,
                "cropped_from_asset_id": None,
                "roi_bbox": None,
                "asset_quality_flags": [],
                "is_usable": bool(normalized_question_text),
                "discard_reason_codes": [],
                "created_at": created_at,
                "updated_at": created_at,
            },
            {
                "asset_id": answer_asset_id,
                "problem_id": problem_id,
                "asset_type": "answer",
                "asset_role": "answer_raw",
                "source_uri": f"hf://{self.config.dataset_name}/{self.config.split}/{source_problem_id}/solution",
                "storage_uri": f"inline://{answer_asset_id}",
                "file_format": "txt",
                "file_size_bytes": len(raw_answer_text.encode("utf-8")),
                "width": None,
                "height": None,
                "sha256": sha256_bytes(raw_answer_text.encode("utf-8")),
                "perceptual_hash": None,
                "source_text_snapshot": raw_answer_text,
                "normalized_text_snapshot": None,
                "text_completeness_score": 1.0 if raw_answer_text else 0.0,
                "blur_score": None,
                "readability_score": None,
                "noise_score": None,
                "cropped_from_asset_id": None,
                "roi_bbox": None,
                "asset_quality_flags": ["missing_answer"] if not raw_answer_text else [],
                "is_usable": bool(raw_answer_text),
                "discard_reason_codes": ["missing_answer"] if not raw_answer_text else [],
                "created_at": created_at,
                "updated_at": created_at,
            },
            {
                "asset_id": answer_norm_asset_id,
                "problem_id": problem_id,
                "asset_type": "answer",
                "asset_role": "answer_normalized",
                "source_uri": None,
                "storage_uri": f"inline://{answer_norm_asset_id}",
                "file_format": "txt",
                "file_size_bytes": len(normalized_answer_text.encode("utf-8")),
                "width": None,
                "height": None,
                "sha256": sha256_bytes(normalized_answer_text.encode("utf-8")),
                "perceptual_hash": None,
                "source_text_snapshot": raw_answer_text,
                "normalized_text_snapshot": normalized_answer_text,
                "text_completeness_score": 1.0 if normalized_answer_text else 0.0,
                "blur_score": None,
                "readability_score": None,
                "noise_score": None,
                "cropped_from_asset_id": None,
                "roi_bbox": None,
                "asset_quality_flags": [],
                "is_usable": bool(normalized_answer_text),
                "discard_reason_codes": [],
                "created_at": created_at,
                "updated_at": created_at,
            },
        ]
        if roi_asset is not None:
            assets.append(roi_asset)
        return assets

    def create_roi_asset(
        self,
        problem_id: str,
        image: Image.Image,
        image_quality: Dict[str, Any],
    ) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, int]]]:
        bbox = image_quality.get("roi_bbox")
        if not bbox:
            return None, None
        width, height = image_quality["width"], image_quality["height"]
        area_ratio = (bbox["width"] * bbox["height"]) / max(width * height, 1)
        if area_ratio > 0.98:
            return None, bbox
        x1, y1 = bbox["x"], bbox["y"]
        x2 = x1 + bbox["width"]
        y2 = y1 + bbox["height"]
        crop = image.convert("RGB").crop((x1, y1, x2, y2))
        crop_path = self.crop_dir / f"{problem_id}_roi.png"
        crop.save(crop_path, format="PNG")
        crop_bytes = crop_path.read_bytes()
        asset = {
            "asset_id": f"asset_{stable_digest([problem_id, 'region_crop'])}",
            "problem_id": problem_id,
            "asset_type": "crop",
            "asset_role": "region_crop",
            "source_uri": None,
            "storage_uri": str(crop_path.relative_to(self.run_dir)),
            "file_format": "png",
            "file_size_bytes": crop_path.stat().st_size,
            "width": crop.width,
            "height": crop.height,
            "sha256": sha256_bytes(crop_bytes),
            "perceptual_hash": self.image_analyzer.perceptual_hash(crop),
            "source_text_snapshot": None,
            "normalized_text_snapshot": None,
            "text_completeness_score": None,
            "blur_score": image_quality["blur_score"],
            "readability_score": image_quality["readability_score"],
            "noise_score": image_quality["noise_score"],
            "cropped_from_asset_id": f"asset_{stable_digest([problem_id, 'primary_image'])}",
            "roi_bbox": bbox,
            "asset_quality_flags": [],
            "is_usable": True,
            "discard_reason_codes": [],
            "created_at": utc_now(),
            "updated_at": utc_now(),
        }
        return asset, bbox

    def compute_potential_scores(
        self,
        normalized_question_text: str,
        normalized_answer_text: str,
        answer_type: str,
        requires_image: bool,
        image_quality: Dict[str, Any],
        choices: List[str],
    ) -> Dict[str, Any]:
        keyword_hits = len(
            re.findall(
                r"\b(calculate|determine|equivalent|frequency|voltage|current|impedance|find|which|what|if)\b",
                normalized_question_text,
                flags=re.IGNORECASE,
            )
        )
        math_hits = len(re.findall(r"[=+\-*/^()]", normalized_question_text))
        multimodal_strength = 0.25
        if requires_image:
            multimodal_strength += 0.45
        if choices:
            multimodal_strength += 0.08
        multimodal_strength += 0.15 * clamp(image_quality["readability_score"])
        multimodal_strength += 0.07 * clamp(keyword_hits / 4.0)
        multi_step = 0.2 + 0.2 * clamp(keyword_hits / 4.0) + 0.25 * clamp(math_hits / 20.0)
        if len(normalized_question_text) > 120:
            multi_step += 0.15
        if answer_type in {"numeric", "option"}:
            multi_step += 0.1
        verifiability = 0.25
        if answer_type == "option":
            verifiability += 0.4
        elif answer_type == "numeric":
            verifiability += 0.35
        elif answer_type == "short_text":
            verifiability += 0.2
        verifiability += 0.15 * clamp(image_quality["readability_score"])
        verifiability += 0.1 if normalized_answer_text else -0.2
        review_priority = "normal"
        if multimodal_strength >= 0.72 and multi_step >= 0.62:
            review_priority = "high"
        if image_quality["readability_score"] < 0.45:
            review_priority = "high"
        return {
            "requires_image": requires_image,
            "multimodal_strength_score": round(clamp(multimodal_strength), 4),
            "multi_step_score": round(clamp(multi_step), 4),
            "verifiability_score": round(clamp(verifiability), 4),
            "review_priority": review_priority,
        }

    def build_alignment_record(
        self,
        problem_id: str,
        normalized_question_text: str,
        asset_records: List[Dict[str, Any]],
        image_quality: Dict[str, Any],
        requires_image: bool,
    ) -> Dict[str, Any]:
        image_asset_ids = [asset["asset_id"] for asset in asset_records if asset["asset_role"] == "primary_image"]
        text_asset_ids = [asset["asset_id"] for asset in asset_records if asset["asset_role"] == "question_text_normalized"]
        alignment_pairs: List[Dict[str, Any]] = []
        conflict_pairs: List[Dict[str, Any]] = []
        if requires_image and image_asset_ids and text_asset_ids:
            alignment_pairs.append(
                {
                    "text_ref": text_asset_ids[0],
                    "image_ref": image_asset_ids[0],
                    "relation": "global_figure_reference",
                    "confidence": 0.88,
                }
            )
        coverage_score = 0.9 if requires_image else 0.7
        if image_quality["readability_score"] < 0.4:
            coverage_score -= 0.18
            conflict_pairs.append(
                {
                    "type": "visual_readability_risk",
                    "detail": "image readability below threshold",
                    "confidence": 0.85,
                }
            )
        consistency_score = 0.88 if requires_image else 0.74
        if "figure" not in normalized_question_text.lower() and requires_image:
            consistency_score -= 0.08
        if image_quality["readability_score"] < 0.4:
            consistency_score -= 0.2
        coverage_score = round(clamp(coverage_score), 4)
        consistency_score = round(clamp(consistency_score), 4)
        status = "good"
        if consistency_score < self.config.min_alignment_consistency:
            status = "bad"
        elif consistency_score < self.config.min_alignment_consistency + 0.15:
            status = "risky"
        return {
            "alignment_id": f"align_{stable_digest([problem_id, self.pipeline_run_id])}",
            "problem_id": problem_id,
            "image_entity_refs": image_asset_ids,
            "text_span_refs": text_asset_ids,
            "alignment_pairs": alignment_pairs,
            "conflict_pairs": conflict_pairs,
            "coverage_score": coverage_score,
            "consistency_score": consistency_score,
            "alignment_status": status,
            "created_at": utc_now(),
        }

    def clean_gate(
        self,
        requires_image: bool,
        raw_question_text: str,
        raw_answer_text: str,
        normalized_question_text: str,
        normalized_answer_text: str,
        text_completeness: float,
        image_quality: Dict[str, Any],
        alignment_record: Dict[str, Any],
        potential_scores: Dict[str, Any],
        quality_flags: List[str],
    ) -> Dict[str, Any]:
        reason_codes: List[str] = []
        hard_reject_codes: List[str] = []
        if not raw_answer_text:
            hard_reject_codes.append("missing_answer")
        if requires_image and (image_quality["width"] < self.config.min_width or image_quality["height"] < self.config.min_height):
            hard_reject_codes.append("low_resolution")
        if requires_image and "severe_global_blur" in quality_flags:
            hard_reject_codes.append("severe_blur")
        if requires_image and "key_text_unreadable" in quality_flags:
            hard_reject_codes.append("image_unreadable")
        if not raw_question_text and not requires_image:
            hard_reject_codes.append("missing_question_text")
        if alignment_record["alignment_status"] == "bad":
            hard_reject_codes.append("text_image_misaligned")

        quality_components = {
            "text_completeness": text_completeness,
            "image_readability": image_quality["readability_score"],
            "alignment_consistency": alignment_record["consistency_score"],
            "multimodal_strength": potential_scores["multimodal_strength_score"],
            "verifiability": potential_scores["verifiability_score"],
        }
        clean_score = round(
            clamp(
                0.24 * quality_components["text_completeness"]
                + 0.25 * quality_components["image_readability"]
                + 0.18 * quality_components["alignment_consistency"]
                + 0.15 * quality_components["multimodal_strength"]
                + 0.18 * quality_components["verifiability"]
            ),
            4,
        )

        if hard_reject_codes:
            decision = "reject"
            reason_codes.extend(sorted(set(hard_reject_codes)))
        elif clean_score < self.config.reject_clean_score_below:
            decision = "reject"
            reason_codes.append("low_clean_score")
        elif (
            clean_score < self.config.review_clean_score_below
            or text_completeness < self.config.min_text_completeness_score
            or alignment_record["alignment_status"] == "risky"
            or "contrast_too_low" in quality_flags
        ):
            decision = "review"
            if clean_score < self.config.review_clean_score_below:
                reason_codes.append("borderline_clean_score")
            if text_completeness < self.config.min_text_completeness_score:
                reason_codes.append("normalized_question_incomplete")
            if alignment_record["alignment_status"] == "risky":
                reason_codes.append("alignment_risky")
            if "contrast_too_low" in quality_flags:
                reason_codes.append("contrast_too_low")
        else:
            decision = "pass"
            reason_codes.append("meets_cleaning_requirements")

        return {
            "decision": decision,
            "decision_reason_codes": sorted(set(reason_codes)),
            "clean_score": clean_score,
            "score_breakdown": quality_components,
            "suggested_next_action": {
                "pass": "send_to_annotation",
                "review": "manual_review",
                "reject": "archive_reject_record",
            }[decision],
            "review_required": decision == "review",
        }

    def build_field_audit_records(
        self,
        problem_id: str,
        raw_question_text: str,
        normalized_question_text: str,
        raw_answer_text: str,
        normalized_answer_text: str,
        image_quality: Dict[str, Any],
        gate: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        timestamp = utc_now()
        audits = [
            {
                "audit_id": f"audit_{stable_digest([problem_id, 'raw_question_text'])}",
                "problem_id": problem_id,
                "record_type": "problem_main_record",
                "field_name": "normalized_question_text",
                "before_value": raw_question_text,
                "after_value": normalized_question_text,
                "change_type": "text_normalized",
                "trigger": "rule_generated",
                "operator_type": "system",
                "created_at": timestamp,
            },
            {
                "audit_id": f"audit_{stable_digest([problem_id, 'raw_answer_text'])}",
                "problem_id": problem_id,
                "record_type": "problem_main_record",
                "field_name": "normalized_answer_text",
                "before_value": raw_answer_text,
                "after_value": normalized_answer_text,
                "change_type": "answer_canonicalized",
                "trigger": "rule_generated",
                "operator_type": "system",
                "created_at": timestamp,
            },
            {
                "audit_id": f"audit_{stable_digest([problem_id, 'decision'])}",
                "problem_id": problem_id,
                "record_type": "cleaning_record",
                "field_name": "decision",
                "before_value": None,
                "after_value": gate["decision"],
                "change_type": "gate_decision",
                "trigger": "rule_engine",
                "operator_type": "system",
                "created_at": timestamp,
            },
            {
                "audit_id": f"audit_{stable_digest([problem_id, 'blur_score'])}",
                "problem_id": problem_id,
                "record_type": "asset_record",
                "field_name": "blur_score",
                "before_value": None,
                "after_value": image_quality["blur_score"],
                "change_type": "quality_derived",
                "trigger": "image_quality_analyzer",
                "operator_type": "system",
                "created_at": timestamp,
            },
        ]
        return audits

    def build_node_records(
        self,
        problem_id: str,
        normalized_question_text: str,
        normalized_answer_text: str,
        answer_type: str,
        quality_flags: List[str],
        image_quality: Dict[str, Any],
        asset_records: List[Dict[str, Any]],
        choices: List[str],
        gate: Dict[str, Any],
        question_body: str,
        roi_bbox: Optional[Dict[str, int]],
    ) -> List[Dict[str, Any]]:
        created_at = utc_now()
        primary_image_refs = [asset["asset_id"] for asset in asset_records if asset["asset_role"] == "primary_image"]
        question_refs = [asset["asset_id"] for asset in asset_records if asset["asset_role"] == "question_text_normalized"]
        answer_refs = [asset["asset_id"] for asset in asset_records if asset["asset_role"] == "answer_normalized"]
        nodes: List[Dict[str, Any]] = []

        text_snippets = [snippet.strip() for snippet in re.split(r"(?<=[.!?])\s+|\n+", question_body) if snippet.strip()]
        for idx, snippet in enumerate(text_snippets[:6]):
            nodes.append(
                self.make_node(
                    problem_id=problem_id,
                    node_type="text_fact",
                    canonical_value=snippet,
                    surface_forms=[snippet],
                    origin_kind="text",
                    cognitive_level="objective",
                    source_refs=question_refs,
                    evidence_refs=question_refs,
                    value_type="text",
                    normalized_value={"text": snippet},
                    unit=None,
                    confidence=0.92,
                    verifiability="high",
                    ambiguity_level="low",
                    is_direct_from_source=True,
                    is_generated_by_system=False,
                    stage_created="cleaning",
                    created_at=created_at,
                    version=1,
                    suffix=f"text_fact_{idx}",
                )
            )
        for idx, choice in enumerate(choices[:6]):
            nodes.append(
                self.make_node(
                    problem_id=problem_id,
                    node_type="text_fact",
                    canonical_value=choice,
                    surface_forms=[choice],
                    origin_kind="text",
                    cognitive_level="objective",
                    source_refs=question_refs,
                    evidence_refs=question_refs,
                    value_type="option",
                    normalized_value={"option": choice[:1], "text": choice},
                    unit=None,
                    confidence=0.95,
                    verifiability="high",
                    ambiguity_level="none",
                    is_direct_from_source=True,
                    is_generated_by_system=False,
                    stage_created="cleaning",
                    created_at=created_at,
                    version=1,
                    suffix=f"choice_{idx}",
                )
            )
        nodes.extend(
            [
                self.make_node(
                    problem_id=problem_id,
                    node_type="answer_claim",
                    canonical_value=normalized_answer_text,
                    surface_forms=[normalized_answer_text],
                    origin_kind="text",
                    cognitive_level="objective",
                    source_refs=answer_refs,
                    evidence_refs=answer_refs,
                    value_type=answer_type,
                    normalized_value={"answer": normalized_answer_text},
                    unit=None,
                    confidence=0.98 if normalized_answer_text else 0.0,
                    verifiability="high" if normalized_answer_text else "unverifiable",
                    ambiguity_level="none" if normalized_answer_text else "high",
                    is_direct_from_source=True,
                    is_generated_by_system=False,
                    stage_created="cleaning",
                    created_at=created_at,
                    version=1,
                    suffix="answer_claim",
                ),
                self.make_node(
                    problem_id=problem_id,
                    node_type="derived_value",
                    canonical_value=f"image_width={image_quality['width']} px",
                    surface_forms=[str(image_quality["width"])],
                    origin_kind="calculation",
                    cognitive_level="computed",
                    source_refs=primary_image_refs,
                    evidence_refs=primary_image_refs,
                    value_type="number",
                    normalized_value={"name": "image_width", "value": image_quality["width"]},
                    unit="px",
                    confidence=1.0,
                    verifiability="high",
                    ambiguity_level="none",
                    is_direct_from_source=False,
                    is_generated_by_system=True,
                    stage_created="cleaning",
                    created_at=created_at,
                    version=1,
                    suffix="image_width",
                ),
                self.make_node(
                    problem_id=problem_id,
                    node_type="derived_value",
                    canonical_value=f"blur_score={image_quality['blur_score']}",
                    surface_forms=[str(image_quality["blur_score"])],
                    origin_kind="calculation",
                    cognitive_level="computed",
                    source_refs=primary_image_refs,
                    evidence_refs=primary_image_refs,
                    value_type="number",
                    normalized_value={"name": "blur_score", "value": image_quality["blur_score"]},
                    unit=None,
                    confidence=1.0,
                    verifiability="high",
                    ambiguity_level="none",
                    is_direct_from_source=False,
                    is_generated_by_system=True,
                    stage_created="cleaning",
                    created_at=created_at,
                    version=1,
                    suffix="blur_score",
                ),
                self.make_node(
                    problem_id=problem_id,
                    node_type="perception_fact",
                    canonical_value="primary image contains a visible diagram region",
                    surface_forms=["visible diagram region"],
                    origin_kind="image",
                    cognitive_level="perceived",
                    source_refs=primary_image_refs,
                    evidence_refs=primary_image_refs,
                    value_type="object",
                    normalized_value={"roi_bbox": roi_bbox or image_quality["roi_bbox"]},
                    unit=None,
                    confidence=0.78 if (roi_bbox or image_quality["roi_bbox"]) else 0.55,
                    verifiability="medium",
                    ambiguity_level="low",
                    is_direct_from_source=False,
                    is_generated_by_system=True,
                    stage_created="cleaning",
                    created_at=created_at,
                    version=1,
                    suffix="perception_region",
                ),
                self.make_node(
                    problem_id=problem_id,
                    node_type="quality_signal",
                    canonical_value=f"clean_decision={gate['decision']}",
                    surface_forms=[gate["decision"]],
                    origin_kind="system_quality",
                    cognitive_level="computed",
                    source_refs=[],
                    evidence_refs=primary_image_refs + question_refs + answer_refs,
                    value_type="text",
                    normalized_value={"decision": gate["decision"], "reasons": gate["decision_reason_codes"]},
                    unit=None,
                    confidence=1.0,
                    verifiability="high",
                    ambiguity_level="none",
                    is_direct_from_source=False,
                    is_generated_by_system=True,
                    stage_created="cleaning",
                    created_at=created_at,
                    version=1,
                    suffix="clean_decision",
                ),
            ]
        )
        for idx, flag in enumerate(quality_flags):
            nodes.append(
                self.make_node(
                    problem_id=problem_id,
                    node_type="quality_signal",
                    canonical_value=flag,
                    surface_forms=[flag],
                    origin_kind="system_quality",
                    cognitive_level="computed",
                    source_refs=primary_image_refs,
                    evidence_refs=primary_image_refs,
                    value_type="text",
                    normalized_value={"flag": flag},
                    unit=None,
                    confidence=1.0,
                    verifiability="high",
                    ambiguity_level="none",
                    is_direct_from_source=False,
                    is_generated_by_system=True,
                    stage_created="cleaning",
                    created_at=created_at,
                    version=1,
                    suffix=f"quality_flag_{idx}",
                )
            )
        return nodes

    def make_node(
        self,
        problem_id: str,
        node_type: str,
        canonical_value: str,
        surface_forms: List[str],
        origin_kind: str,
        cognitive_level: str,
        source_refs: List[str],
        evidence_refs: List[str],
        value_type: str,
        normalized_value: Dict[str, Any],
        unit: Optional[str],
        confidence: float,
        verifiability: str,
        ambiguity_level: str,
        is_direct_from_source: bool,
        is_generated_by_system: bool,
        stage_created: str,
        created_at: str,
        version: int,
        suffix: str,
    ) -> Dict[str, Any]:
        return {
            "node_id": f"node_{stable_digest([problem_id, suffix])}",
            "problem_id": problem_id,
            "node_type": node_type,
            "canonical_value": canonical_value,
            "surface_forms": surface_forms,
            "origin_kind": origin_kind,
            "cognitive_level": cognitive_level,
            "source_refs": source_refs,
            "evidence_refs": evidence_refs,
            "upstream_node_ids": [],
            "value_type": value_type,
            "normalized_value": normalized_value,
            "unit": unit,
            "confidence": round(confidence, 4),
            "verifiability": verifiability,
            "ambiguity_level": ambiguity_level,
            "is_direct_from_source": is_direct_from_source,
            "is_generated_by_system": is_generated_by_system,
            "is_reviewed_by_human": False,
            "stage_created": stage_created,
            "status": "active",
            "version": version,
            "created_at": created_at,
            "updated_at": created_at,
        }

    def build_problem_main_record(
        self,
        problem_id: str,
        source_problem_id: str,
        created_at: str,
        raw_question_text: str,
        normalized_question_text: str,
        raw_answer_text: str,
        normalized_answer_text: str,
        language: str,
        answer_type: str,
        image_count: int,
        requires_image: bool,
        potential_scores: Dict[str, Any],
        quality_flags: List[str],
        gate: Dict[str, Any],
        text_completeness: float,
        alignment_record: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "problem_id": problem_id,
            "source_dataset": self.config.dataset_name,
            "source_split": self.config.split,
            "source_problem_id": source_problem_id,
            "ingest_batch_id": self.ingest_batch_id,
            "problem_type": "circuit_reasoning",
            "domain_tags": ["electronics", "multimodal_reasoning"],
            "language": language,
            "raw_question_text": raw_question_text,
            "normalized_question_text": normalized_question_text,
            "raw_answer_text": raw_answer_text,
            "normalized_answer_text": normalized_answer_text,
            "answer_type": answer_type,
            "image_count": image_count,
            "has_multiple_images": image_count > 1,
            "requires_image": requires_image,
            "multimodal_strength_score": potential_scores["multimodal_strength_score"],
            "multi_step_score": potential_scores["multi_step_score"],
            "verifiability_score": potential_scores["verifiability_score"],
            "quality_risk_flags": quality_flags,
            "current_status": {
                "pass": "clean_passed",
                "review": "cleaning_review",
                "reject": "clean_rejected",
            }[gate["decision"]],
            "clean_decision": gate["decision"],
            "clean_decision_reason_codes": gate["decision_reason_codes"],
            "review_priority": potential_scores["review_priority"],
            "annotation_ready": gate["decision"] == "pass",
            "qa_precheck_ready": bool(
                normalized_question_text and normalized_answer_text and alignment_record["alignment_status"] != "bad"
            ),
            "release_reserved": {},
            "created_at": created_at,
            "updated_at": utc_now(),
            "field_provenance": {
                "source_dataset": {"field_origin": "source_provided", "confidence": 1.0},
                "source_split": {"field_origin": "source_derived", "confidence": 1.0},
                "source_problem_id": {"field_origin": "source_derived", "confidence": 1.0},
                "raw_question_text": {"field_origin": "source_provided", "confidence": 1.0},
                "normalized_question_text": {
                    "field_origin": "rule_generated",
                    "confidence": round(text_completeness, 4),
                },
                "raw_answer_text": {"field_origin": "source_provided", "confidence": 1.0},
                "normalized_answer_text": {"field_origin": "rule_generated", "confidence": 0.98},
                "language": {"field_origin": "model_generated", "confidence": 0.9},
                "answer_type": {"field_origin": "rule_generated", "confidence": 0.95},
                "requires_image": {
                    "field_origin": "rule_generated",
                    "confidence": potential_scores["multimodal_strength_score"],
                },
                "multimodal_strength_score": {"field_origin": "rule_generated", "confidence": 0.82},
                "multi_step_score": {"field_origin": "rule_generated", "confidence": 0.78},
                "verifiability_score": {"field_origin": "rule_generated", "confidence": 0.86},
                "quality_risk_flags": {"field_origin": "rule_generated", "confidence": 1.0},
                "clean_decision": {"field_origin": "rule_generated", "confidence": 1.0},
            },
        }

    def build_cleaning_record(
        self,
        problem_id: str,
        started_at: str,
        finished_at: str,
        asset_records: List[Dict[str, Any]],
        missing_field_summary: Dict[str, Any],
        alignment_record: Dict[str, Any],
        image_quality: Dict[str, Any],
        quality_flags: List[str],
        gate: Dict[str, Any],
        raw_question_text: str,
        normalized_question_text: str,
        raw_answer_text: str,
        normalized_answer_text: str,
    ) -> Dict[str, Any]:
        return {
            "cleaning_id": f"clean_{stable_digest([problem_id, self.pipeline_run_id])}",
            "problem_id": problem_id,
            "cleaning_version": self.config.cleaning_version,
            "pipeline_run_id": self.pipeline_run_id,
            "input_asset_ids": [asset["asset_id"] for asset in asset_records],
            "normalization_actions": [
                {
                    "action_type": "text_normalized",
                    "before": raw_question_text,
                    "after": normalized_question_text,
                    "trigger": "unicode_whitespace_normalizer",
                    "confidence": 0.96,
                    "human_confirmed": False,
                },
                {
                    "action_type": "answer_canonicalized",
                    "before": raw_answer_text,
                    "after": normalized_answer_text,
                    "trigger": "answer_normalizer",
                    "confidence": 0.98,
                    "human_confirmed": False,
                },
            ],
            "quality_checks": [
                {
                    "check": "image_quality",
                    "result": {
                        "blur_score": image_quality["blur_score"],
                        "readability_score": image_quality["readability_score"],
                        "contrast_score": image_quality["contrast_score"],
                        "noise_score": image_quality["noise_score"],
                        "roi_bbox": image_quality["roi_bbox"],
                    },
                    "passed": gate["decision"] != "reject",
                }
            ],
            "alignment_summary": {
                "alignment_id": alignment_record["alignment_id"],
                "coverage_score": alignment_record["coverage_score"],
                "consistency_score": alignment_record["consistency_score"],
                "alignment_status": alignment_record["alignment_status"],
            },
            "missing_field_summary": missing_field_summary,
            "risk_flags": quality_flags,
            "clean_score": gate["clean_score"],
            "decision": gate["decision"],
            "decision_reason_codes": gate["decision_reason_codes"],
            "review_ticket_id": f"review_{problem_id}" if gate["decision"] == "review" else None,
            "operator_type": "system",
            "started_at": started_at,
            "finished_at": finished_at,
        }

    def build_reject_record(
        self,
        problem_id: str,
        gate: Dict[str, Any],
        quality_flags: List[str],
        alignment_record: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        if gate["decision"] != "reject":
            return None
        return {
            "reject_id": f"reject_{stable_digest([problem_id, self.pipeline_run_id])}",
            "problem_id": problem_id,
            "stage": "cleaning",
            "reject_level": "problem",
            "reject_reason_codes": gate["decision_reason_codes"],
            "reject_reason_detail": "Rejected by hard blocking rules or clean score threshold.",
            "blocking_fields": quality_flags,
            "evidence_refs": [alignment_record["alignment_id"]],
            "recoverable": False,
            "recommended_action": "drop",
            "reviewed_by": None,
            "created_at": utc_now(),
        }

    def build_summary(self, dataset_size: int, exported_files: Dict[str, Path]) -> Dict[str, Any]:
        decision_counts = {"pass": 0, "review": 0, "reject": 0}
        reason_counter: Dict[str, int] = {}
        for record in self.problems:
            decision = record["clean_decision"]
            decision_counts[decision] += 1
            for reason in record["clean_decision_reason_codes"]:
                reason_counter[reason] = reason_counter.get(reason, 0) + 1
        avg_clean_score = round(
            sum(cleaning["clean_score"] for cleaning in self.cleanings) / max(len(self.cleanings), 1),
            4,
        )
        summary = {
            "pipeline_run_id": self.pipeline_run_id,
            "dataset_name": self.config.dataset_name,
            "split": self.config.split,
            "sample_limit": self.config.sample_limit,
            "processed_samples": dataset_size,
            "decision_counts": decision_counts,
            "average_clean_score": avg_clean_score,
            "top_reason_codes": sorted(reason_counter.items(), key=lambda item: (-item[1], item[0]))[:10],
            "exported_files": {name: str(path.relative_to(self.run_dir)) for name, path in exported_files.items()},
            "artifacts_root": str(self.artifact_dir.relative_to(self.run_dir)),
            "created_at": utc_now(),
        }
        return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="EEE-Bench 数据采集与清洗自动化流水线")
    parser.add_argument("--config", type=str, default=None, help="YAML 配置文件路径")
    parser.add_argument("--dataset", type=str, default=None, help="Hugging Face 数据集名称")
    parser.add_argument("--split", type=str, default=None, help="数据集 split，例如 test 或 testmini")
    parser.add_argument("--limit", type=int, default=None, help="处理样本数")
    parser.add_argument("--output-dir", type=str, default=None, help="输出目录")
    parser.add_argument("--sample-strategy", type=str, choices=["head", "random"], default=None, help="抽样策略")
    parser.add_argument("--seed", type=int, default=None, help="随机抽样种子")
    parser.add_argument("--cleaning-version", type=str, default=None, help="清洗版本号")
    parser.add_argument(
        "--keep-existing-output",
        action="store_true",
        help="默认会保留历史 run；该参数仅用于显式表达不清理输出目录。",
    )
    return parser.parse_args()


def merge_cli_overrides(config: PipelineConfig, args: argparse.Namespace) -> PipelineConfig:
    if args.dataset:
        config.dataset_name = args.dataset
    if args.split:
        config.split = args.split
    if args.limit is not None:
        config.sample_limit = args.limit
    if args.output_dir:
        config.output_root = args.output_dir
    if args.sample_strategy:
        config.sample_strategy = args.sample_strategy
    if args.seed is not None:
        config.shuffle_seed = args.seed
    if args.cleaning_version:
        config.cleaning_version = args.cleaning_version
    return config


def main() -> None:
    args = parse_args()
    config = PipelineConfig.from_yaml(args.config)
    config = merge_cli_overrides(config, args)
    output_root = Path(config.output_root)
    ensure_dir(output_root)
    pipeline = EEEPipeline(config)
    summary = pipeline.run()
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
