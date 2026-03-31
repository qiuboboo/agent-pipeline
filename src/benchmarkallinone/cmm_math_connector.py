#!/usr/bin/env python3
"""CMM-Math dataset connector with raw image zip support."""

from __future__ import annotations

import ast
import json
import zipfile
from pathlib import Path
from typing import Any, List, Tuple

from PIL import Image

try:
    from huggingface_hub import hf_hub_download
except ImportError:  # pragma: no cover
    hf_hub_download = None  # type: ignore

try:
    from .pipeline import (
        HuggingFaceConnector,
        UnifiedSample,
        ensure_dir,
        normalize_whitespace,
        resolve_multiple_choice_answer_text,
        resolve_answer_source_text,
        to_plain_text,
    )
except ImportError:  # pragma: no cover
    from pipeline import (  # type: ignore
        HuggingFaceConnector,
        UnifiedSample,
        ensure_dir,
        normalize_whitespace,
        resolve_multiple_choice_answer_text,
        resolve_answer_source_text,
        to_plain_text,
    )


class CMMMathConnector(HuggingFaceConnector):
    def resolve_jsonl_filename(self) -> str:
        split = (self.spec.split or "train").strip().lower()
        if split == "test":
            return "test_data.jsonl"
        if split in {"all", "full"}:
            return "all_data.jsonl"
        return "train_data.jsonl"

    def candidate_image_roots(self, extract_root: Path) -> List[Path]:
        split = (self.spec.split or "train").strip().lower()
        roots: List[Path] = []
        if split == "train":
            roots.extend([extract_root / "Train_Images", extract_root / "All_Images"])
        elif split == "test":
            roots.extend([extract_root / "Test_Images", extract_root / "All_Images"])
        else:
            roots.extend([extract_root / "All_Images", extract_root / "Train_Images", extract_root / "Test_Images"])
        return roots

    def ensure_raw_assets(self) -> Tuple[Path, Path]:
        if hf_hub_download is None:
            raise RuntimeError("CMM-Math raw assets require huggingface_hub.")
        jsonl_name = self.resolve_jsonl_filename()
        jsonl_path = Path(hf_hub_download(repo_id=self.spec.source_locator, repo_type="dataset", filename=jsonl_name))
        zip_path = Path(hf_hub_download(repo_id=self.spec.source_locator, repo_type="dataset", filename="images.zip"))
        extract_root = Path(self.config.git_cache_root) / "hf_raw" / "cmm_math"
        marker_dir = extract_root / "All_Images"
        if not marker_dir.exists():
            ensure_dir(extract_root)
            with zipfile.ZipFile(zip_path) as zf:
                zf.extractall(extract_root)
        return jsonl_path, extract_root

    def parse_image_entries(self, value: Any) -> List[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [to_plain_text(item).strip() for item in value if to_plain_text(item).strip()]
        text = to_plain_text(value).strip()
        if not text:
            return []
        try:
            parsed = ast.literal_eval(text)
        except Exception:
            parsed = text
        if isinstance(parsed, list):
            return [to_plain_text(item).strip() for item in parsed if to_plain_text(item).strip()]
        normalized = text.strip("[] ")
        return [normalized] if normalized else []

    def load_image_files(self, image_names: List[str], extract_root: Path) -> Tuple[List[Image.Image], List[str]]:
        images: List[Image.Image] = []
        image_sources: List[str] = []
        if not image_names:
            return images, image_sources
        roots = self.candidate_image_roots(extract_root)
        for image_name in image_names:
            candidate = None
            for root in roots:
                trial = root / image_name
                if trial.exists():
                    candidate = trial
                    break
            if candidate is None:
                continue
            try:
                images.append(Image.open(candidate).convert("RGB"))
                image_sources.append(str(candidate))
            except Exception:
                continue
        return images, image_sources

    def sample(self):
        try:
            jsonl_path, extract_root = self.ensure_raw_assets()
        except Exception as exc:
            return "source_unavailable", [], str(exc)

        rows: List[dict] = []
        with jsonl_path.open("r", encoding="utf-8") as file:
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

        if self.config.sample_strategy == "random":
            import numpy as np
            rng = np.random.default_rng(self.config.shuffle_seed)
            indices = rng.permutation(len(rows)).tolist()
            rows = [rows[i] for i in indices]

        offset = max(0, int(self.spec.sample_offset or 0))
        if offset >= len(rows):
            return "available", [], self.spec.split or self.resolve_jsonl_filename()
        rows = rows[offset : offset + self.config.sample_per_dataset]

        samples: List[UnifiedSample] = []
        for index, row in enumerate(rows):
            extracted = self.extract_record_content(row)
            raw_question = extracted["raw_question_text"]
            raw_answer = resolve_multiple_choice_answer_text(
                self.resolve_answer_text(resolve_answer_source_text(row, extracted)),
                extracted["choice_map"],
                self.spec.answer_index_base,
            )
            image_names = self.parse_image_entries(row.get("image"))
            images, image_sources = self.load_image_files(image_names, extract_root)
            if not raw_question and not images:
                continue
            samples.append(
                UnifiedSample(
                    dataset_key=self.spec.key,
                    dataset_display_name=self.spec.display_name,
                    subject=self.spec.subject,
                    source_dataset=self.spec.display_name,
                    source_split=self.spec.split or self.resolve_jsonl_filename(),
                    source_problem_id=str(row.get("id", row.get("problem_id", offset + index))),
                    raw_question_text=raw_question,
                    raw_answer_text=raw_answer,
                    images=images,
                    image_sources=image_sources,
                    raw_record=row,
                    metadata={
                        "row_index": offset + index,
                        "image_paths": image_sources or image_names,
                        "extraction_notes": list(extracted.get("extraction_notes", [])) + ["hf_raw_cmm_math_fallback"],
                        "question_field": extracted.get("question_field"),
                        "answer_field": extracted.get("answer_field"),
                        "image_field": extracted.get("image_field"),
                        "choice_field": extracted.get("choice_field"),
                        "source_file": str(jsonl_path),
                    },
                    choice_map=extracted["choice_map"],
                    force_requires_image=bool(extracted["force_requires_image"] or self.spec.force_requires_image),
                )
            )
        return "available", samples, self.spec.split or self.resolve_jsonl_filename()
