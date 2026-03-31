#!/usr/bin/env python3
"""PhyX dataset connector."""

from __future__ import annotations

import base64
import io
import re
from typing import Any, Dict, List, Tuple

from PIL import Image

try:
    from .pipeline import (
        HuggingFaceConnector,
        UnifiedSample,
        is_null_like_text,
        normalize_whitespace,
        resolve_multiple_choice_answer_text,
        to_plain_text,
    )
except ImportError:  # pragma: no cover
    from pipeline import (  # type: ignore
        HuggingFaceConnector,
        UnifiedSample,
        is_null_like_text,
        normalize_whitespace,
        resolve_multiple_choice_answer_text,
        to_plain_text,
    )


class PhyXConnector(HuggingFaceConnector):
    OPTION_SECTION_PATTERN = re.compile(r"(?i)\boption\s*:\s*(.*)$", flags=re.DOTALL)
    OPTION_PAIR_PATTERN = re.compile(r"([A-H])\s*:\s*(.*?)(?=\s+[A-H]\s*:|$)", flags=re.IGNORECASE | re.DOTALL)
    ANSWER_INSTRUCTION_PATTERN = re.compile(r"(?i)\s*please\s+directly\s+answer.*$")

    def extract_choice_map_from_question(self, question_text: str) -> Dict[str, str]:
        if not question_text:
            return {}
        match = self.OPTION_SECTION_PATTERN.search(question_text)
        if not match:
            return {}
        choice_block = normalize_whitespace(match.group(1))
        choices: Dict[str, str] = {}
        for item in self.OPTION_PAIR_PATTERN.finditer(choice_block):
            label = item.group(1).upper().strip()
            text = normalize_whitespace(item.group(2))
            if label and text and not is_null_like_text(text):
                choices[label] = text
        return choices

    def strip_embedded_choice_suffix(self, question_text: str) -> str:
        if not question_text:
            return ""
        stripped = self.ANSWER_INSTRUCTION_PATTERN.sub("", question_text).strip()
        if stripped != question_text.strip():
            return normalize_whitespace(stripped)
        option_match = self.OPTION_SECTION_PATTERN.search(question_text)
        if option_match:
            return normalize_whitespace(question_text[: option_match.start()])
        return normalize_whitespace(question_text)

    def decode_base64_image(self, value: Any, sample_id: str) -> Tuple[List[Image.Image], List[str]]:
        payload = to_plain_text(value).strip()
        if not payload or is_null_like_text(payload):
            return [], []
        if payload.lower().startswith("data:image") and "," in payload:
            payload = payload.split(",", 1)[1]
        payload = re.sub(r"\s+", "", payload)
        if not payload:
            return [], []
        padding = (-len(payload)) % 4
        if padding:
            payload += "=" * padding
        try:
            image_bytes = base64.b64decode(payload, validate=False)
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            return [image], [f"inline://phyx_image_{sample_id}"]
        except Exception:
            return [], []

    def sample(self):
        dataset, detail = self.load_dataset_any()
        if dataset is None:
            return "source_unavailable", [], detail or "load_dataset failed"
        offset = max(0, int(self.spec.sample_offset or 0))
        if self.config.sample_strategy == "random":
            dataset = dataset.shuffle(seed=self.config.shuffle_seed)
        if offset >= len(dataset):
            return "available", [], detail
        end_index = min(offset + self.config.sample_per_dataset, len(dataset))
        rows = dataset.select(range(offset, end_index))
        samples: List[UnifiedSample] = []
        for index, row in enumerate(rows):
            row = dict(row)
            source_problem_id = str(row.get("index", row.get("id", row.get("problem_id", index))))
            raw_question_full = normalize_whitespace(to_plain_text(row.get("question")))
            choice_map = self.extract_choice_map_from_question(raw_question_full)
            raw_question = self.strip_embedded_choice_suffix(raw_question_full)
            raw_answer = resolve_multiple_choice_answer_text(
                self.resolve_answer_text(row.get("answer")),
                choice_map,
                self.spec.answer_index_base,
            )
            images, image_sources = self.decode_base64_image(row.get("image"), source_problem_id)
            if not raw_question and not images:
                continue
            samples.append(
                UnifiedSample(
                    dataset_key=self.spec.key,
                    dataset_display_name=self.spec.display_name,
                    subject=self.spec.subject,
                    source_dataset=self.spec.display_name,
                    source_split=detail or self.spec.split or "unknown",
                    source_problem_id=source_problem_id,
                    raw_question_text=raw_question,
                    raw_answer_text=raw_answer,
                    images=images,
                    image_sources=image_sources,
                    raw_record=row,
                    metadata={
                        "row_index": index,
                        "image_paths": list(image_sources),
                        "extraction_notes": [
                            "phyx_connector",
                            "phyx_base64_image",
                            "phyx_options_embedded_in_question",
                        ],
                        "question_field": "question",
                        "answer_field": "answer",
                        "image_field": "image",
                        "choice_field": "question_embedded_options",
                        "category": row.get("category"),
                        "subfield": row.get("subfield"),
                        "reasoning_type": row.get("reasoning_type"),
                    },
                    choice_map=choice_map,
                    force_requires_image=True,
                )
            )
        return "available", samples, None
