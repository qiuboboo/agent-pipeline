#!/usr/bin/env python3
"""采集/清洗阶段的语义解析与对齐组件。"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
from PIL import Image


VISUAL_REFERENCE_PATTERN = re.compile(
    r"\b(figure|fig\.?|diagram|graph|chart|plot|curve|waveform|circuit|schematic|table|image|shown below|shown in the figure)\b",
    re.IGNORECASE,
)
TARGET_VERB_PATTERN = re.compile(
    r"\b(find|determine|calculate|compute|derive|prove|what|which|write|state|identify|select|求|计算|判断|写出|给出|确定|求解)\b",
    re.IGNORECASE,
)
GENERIC_BAD_VARIANT_PATTERN = re.compile(r"^(text|bar|figure|diagram|graph|image|chart)\.?$", re.IGNORECASE)
ENTITY_LABEL_PATTERN = re.compile(r"\b[A-Z]{1,3}\d*\b")
NUMERIC_TOKEN_PATTERN = re.compile(r"[+-]?(?:\d+(?:\.\d+)?|\.\d+)")

UNIT_PATTERNS: Sequence[Tuple[str, re.Pattern[str]]] = (
    ("Ω", re.compile(r"(?<![A-Za-z])(?:ohms?|欧姆)(?![A-Za-z])", re.IGNORECASE)),
    ("V", re.compile(r"(?<![A-Za-z])(?:volts?|伏特)(?![A-Za-z])", re.IGNORECASE)),
    ("A", re.compile(r"(?<![A-Za-z])(?:amps?|amperes?|安培)(?![A-Za-z])", re.IGNORECASE)),
    ("W", re.compile(r"(?<![A-Za-z])(?:watts?|瓦特)(?![A-Za-z])", re.IGNORECASE)),
    ("Hz", re.compile(r"(?<![A-Za-z])(?:hertz|赫兹)(?![A-Za-z])", re.IGNORECASE)),
    ("N", re.compile(r"(?<![A-Za-z])(?:newtons?|牛顿)(?![A-Za-z])", re.IGNORECASE)),
    ("J", re.compile(r"(?<![A-Za-z])(?:joules?|焦耳)(?![A-Za-z])", re.IGNORECASE)),
    ("m", re.compile(r"(?<=\d)\s*(?:meters?|metres?|米)(?![A-Za-z])", re.IGNORECASE)),
    ("cm", re.compile(r"(?<=\d)\s*(?:centimeters?|centimetres?|厘米)(?![A-Za-z])", re.IGNORECASE)),
    ("mm", re.compile(r"(?<=\d)\s*(?:millimeters?|millimetres?|毫米)(?![A-Za-z])", re.IGNORECASE)),
    ("kg", re.compile(r"(?<=\d)\s*(?:kilograms?|公斤|千克)(?![A-Za-z])", re.IGNORECASE)),
    ("g", re.compile(r"(?<=\d)\s*(?:grams?|克)(?![A-Za-z])", re.IGNORECASE)),
    ("s", re.compile(r"(?<=\d)\s*(?:seconds?|sec|秒)(?![A-Za-z])", re.IGNORECASE)),
    ("min", re.compile(r"(?<=\d)\s*(?:minutes?|mins?|分钟)(?![A-Za-z])", re.IGNORECASE)),
    ("h", re.compile(r"(?<=\d)\s*(?:hours?|hrs?|小时)(?![A-Za-z])", re.IGNORECASE)),
    ("°", re.compile(r"(?<=\d)\s*(?:degrees?|degree|°|度)(?![A-Za-z])", re.IGNORECASE)),
)

VISUAL_KEYWORDS = {
    "figure": "figure",
    "diagram": "diagram",
    "graph": "graph",
    "chart": "chart",
    "plot": "graph",
    "curve": "curve",
    "waveform": "waveform",
    "circuit": "circuit",
    "schematic": "circuit",
    "table": "table",
    "image": "image",
    "point": "point",
    "line": "line",
    "angle": "angle",
    "triangle": "shape",
    "circle": "shape",
    "resistor": "component",
    "switch": "component",
    "battery": "component",
    "axis": "axis",
    "bar": "bar",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def normalize_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_sentences(text: str) -> List[str]:
    if not text:
        return []
    chunks = re.split(r"(?<=[。！？!?\.])\s+|\n+|;\s+|；\s*", text)
    return [normalize_whitespace(chunk) for chunk in chunks if normalize_whitespace(chunk)]


def normalize_units(text: str) -> Tuple[str, List[Dict[str, Any]]]:
    normalized = text
    operations: List[Dict[str, Any]] = []
    for canonical, pattern in UNIT_PATTERNS:
        matches = pattern.findall(normalized)
        if not matches:
            continue
        normalized = pattern.sub(lambda match: canonical if match.group(0).strip().startswith(tuple("0123456789")) else canonical, normalized)
        operations.append(
            {
                "canonical_unit": canonical,
                "match_count": len(matches),
                "matched_examples": sorted({str(item) for item in matches})[:5],
            }
        )
    normalized = re.sub(r"(?<=\d)\s+(?=(?:Ω|V|A|W|Hz|N|J|m|cm|mm|kg|g|s|min|h|°)\b)", "", normalized)
    return normalize_whitespace(normalized), operations


def extract_variable_aliases(text: str) -> List[Dict[str, str]]:
    aliases: Dict[str, Dict[str, str]] = {}
    for match in re.finditer(r"\b([a-zA-Z][a-zA-Z0-9_]*)\b", text):
        token = match.group(1)
        if token.lower() in {
            "find",
            "determine",
            "calculate",
            "compute",
            "prove",
            "what",
            "which",
            "write",
            "state",
            "diagram",
            "figure",
            "graph",
            "image",
            "table",
            "question",
            "answer",
            "shown",
            "below",
        }:
            continue
        if len(token) <= 4 and (token.isalpha() or re.fullmatch(r"[A-Za-z]{1,3}\d+", token)):
            canonical = token.replace(" ", "")
            aliases[token] = {
                "original": token,
                "canonical": canonical,
                "variable_type": "symbol" if len(token) == 1 else "label",
            }
    return list(aliases.values())


def extract_unit_mentions(text: str) -> List[str]:
    mentions: List[str] = []
    for canonical, pattern in UNIT_PATTERNS:
        if canonical in text or pattern.search(text):
            mentions.append(canonical)
    return sorted(set(mentions))


def normalize_structured_text(text: str) -> Dict[str, Any]:
    normalized_text, unit_map = normalize_units(text)
    variable_aliases = extract_variable_aliases(normalized_text)
    sentences = split_sentences(normalized_text)
    return {
        "normalized_text": normalized_text,
        "unit_normalization_map": unit_map,
        "variable_aliases": variable_aliases,
        "unit_mentions": extract_unit_mentions(normalized_text),
        "sentence_segments": [
            {"segment_index": index + 1, "text": sentence} for index, sentence in enumerate(sentences)
        ],
    }


class TextContextParser:
    """把题干解析成条件、目标、回答槽位与文本实体。"""

    def classify_question_type(self, text: str, choices: Optional[Dict[str, str]] = None) -> str:
        lowered = text.lower()
        if choices:
            return "multiple_choice"
        if any(token in lowered for token in ["prove", "证明"]):
            return "proof"
        if any(token in lowered for token in ["describe", "state", "写出", "说明"]):
            return "descriptive"
        if any(token in lowered for token in ["find", "determine", "calculate", "compute", "求", "计算"]):
            return "calculation"
        return "open"

    def extract_entity_mentions(self, text: str) -> List[Dict[str, Any]]:
        mentions: List[Dict[str, Any]] = []
        seen = set()
        lowered = text.lower()
        for token, category in VISUAL_KEYWORDS.items():
            if token in lowered and token not in seen:
                mentions.append(
                    {
                        "mention": token,
                        "entity_category": category,
                        "requires_visual_grounding": category in {"figure", "diagram", "graph", "curve", "waveform", "circuit", "table", "image", "component", "axis", "bar", "point", "line", "angle", "shape"},
                    }
                )
                seen.add(token)
        for match in ENTITY_LABEL_PATTERN.finditer(text):
            token = match.group(0)
            if token not in seen:
                mentions.append(
                    {
                        "mention": token,
                        "entity_category": "label",
                        "requires_visual_grounding": token.isupper(),
                    }
                )
                seen.add(token)
        return mentions

    def _build_slot(self, problem_id: str, variant_index: int, variant: Dict[str, Any]) -> Dict[str, Any]:
        rewritten = normalize_whitespace(str(variant.get("rewritten_question_text") or ""))
        expected_answer_type = str(variant.get("expected_answer_type") or "unknown")
        target_text = rewritten
        sentences = split_sentences(rewritten)
        if sentences:
            candidate_targets = [item for item in sentences if TARGET_VERB_PATTERN.search(item)]
            if candidate_targets:
                target_text = candidate_targets[-1]
            else:
                target_text = sentences[-1]
        return {
            "slot_id": f"slot_{problem_id}_{variant_index}",
            "variant_index": variant_index,
            "split_role": str(variant.get("split_role") or "single"),
            "slot_type": expected_answer_type,
            "target_text": target_text,
            "expected_answer_type": expected_answer_type,
            "expected_answer": str(variant.get("expected_answer") or ""),
            "requires_visual_grounding": bool(VISUAL_REFERENCE_PATTERN.search(rewritten)),
        }

    def parse(
        self,
        problem_id: str,
        normalized_question_text: str,
        open_variants: List[Dict[str, Any]],
        requires_image: bool,
        question_normalization: Dict[str, Any],
        answer_normalization: Dict[str, Any],
        choices: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        sentences = question_normalization.get("sentence_segments") or [
            {"segment_index": 1, "text": normalized_question_text}
        ]
        conditions: List[Dict[str, Any]] = []
        targets: List[Dict[str, Any]] = []
        for item in sentences:
            sentence = item["text"]
            numeric_tokens = NUMERIC_TOKEN_PATTERN.findall(sentence)
            mentions_visual = bool(VISUAL_REFERENCE_PATTERN.search(sentence))
            entry = {
                "text": sentence,
                "segment_index": item["segment_index"],
                "mentions_visual": mentions_visual,
                "numeric_tokens": numeric_tokens,
                "unit_mentions": extract_unit_mentions(sentence),
            }
            if TARGET_VERB_PATTERN.search(sentence) or sentence.endswith("?"):
                entry["target_role"] = "primary"
                targets.append(entry)
            elif numeric_tokens or "=" in sentence or mentions_visual or any(
                token in sentence.lower() for token in ["given", "if", "已知", "如图", "after", "when"]
            ):
                entry["condition_role"] = "explicit"
                conditions.append(entry)
        if not targets and normalized_question_text:
            targets.append(
                {
                    "text": normalized_question_text,
                    "segment_index": len(sentences),
                    "mentions_visual": bool(VISUAL_REFERENCE_PATTERN.search(normalized_question_text)),
                    "numeric_tokens": NUMERIC_TOKEN_PATTERN.findall(normalized_question_text),
                    "unit_mentions": extract_unit_mentions(normalized_question_text),
                    "target_role": "fallback",
                }
            )
        answer_slots = [self._build_slot(problem_id, index, variant) for index, variant in enumerate(open_variants, start=1)]
        if not answer_slots:
            answer_slots = [
                {
                    "slot_id": f"slot_{problem_id}_1",
                    "variant_index": 1,
                    "split_role": "single",
                    "slot_type": "unknown",
                    "target_text": targets[0]["text"] if targets else normalized_question_text,
                    "expected_answer_type": "unknown",
                    "expected_answer": answer_normalization.get("normalized_text") or "",
                    "requires_visual_grounding": requires_image,
                }
            ]
        entity_mentions = self.extract_entity_mentions(normalized_question_text)
        requires_visual_grounding = requires_image or any(
            item.get("requires_visual_grounding") for item in entity_mentions + answer_slots
        )
        status = "complete"
        if not targets or not answer_slots:
            status = "underspecified"
        elif not conditions and len(normalized_question_text) < 12:
            status = "partial"
        parser_confidence = 0.92
        if status == "partial":
            parser_confidence = 0.74
        elif status == "underspecified":
            parser_confidence = 0.52
        return {
            "text_structure_id": f"text_{problem_id}",
            "problem_id": problem_id,
            "question_type": self.classify_question_type(normalized_question_text, choices),
            "conditions": conditions,
            "targets": targets,
            "answer_slots": answer_slots,
            "entity_mentions": entity_mentions,
            "variable_aliases": question_normalization.get("variable_aliases", []),
            "unit_mentions": sorted(
                set(question_normalization.get("unit_mentions", [])) | set(answer_normalization.get("unit_mentions", []))
            ),
            "requires_visual_grounding": requires_visual_grounding,
            "text_structure_status": status,
            "parser_confidence": round(parser_confidence, 4),
            "created_at": utc_now(),
        }


class VisualParser:
    """对图像做轻量级结构化解析，不依赖 OCR。"""

    def _dark_ratio(self, gray: np.ndarray) -> float:
        return float(((gray / 255.0) < 0.92).mean())

    def _infer_visual_kind(self, question_text: str, dark_ratio: float, aspect_ratio: float) -> str:
        lowered = question_text.lower()
        if any(token in lowered for token in ["circuit", "switch", "resistor", "voltage", "current"]):
            return "circuit_diagram"
        if any(token in lowered for token in ["graph", "plot", "curve", "waveform", "axis", "chart"]):
            return "chart_like"
        if any(token in lowered for token in ["triangle", "circle", "angle", "geometry", "point"]):
            return "geometry_diagram"
        if aspect_ratio > 1.6:
            return "wide_diagram"
        if dark_ratio > 0.30:
            return "dense_diagram"
        return "generic_visual"

    def _collect_regions(self, gray: np.ndarray, roi_bbox: Optional[Dict[str, int]]) -> List[Dict[str, Any]]:
        height, width = gray.shape
        regions: List[Dict[str, Any]] = [
            {
                "entity_id": "canvas",
                "entity_type": "full_canvas",
                "bbox": {"x": 0, "y": 0, "width": int(width), "height": int(height)},
                "salience": 1.0,
            }
        ]
        if roi_bbox:
            regions.append(
                {
                    "entity_id": "roi",
                    "entity_type": "content_region",
                    "bbox": roi_bbox,
                    "salience": 0.95,
                }
            )
            x, y = roi_bbox["x"], roi_bbox["y"]
            w, h = roi_bbox["width"], roi_bbox["height"]
            if w >= 64 and h >= 64:
                quadrants = [
                    ("roi_top_left", x, y, w // 2, h // 2),
                    ("roi_top_right", x + w // 2, y, w - w // 2, h // 2),
                    ("roi_bottom_left", x, y + h // 2, w // 2, h - h // 2),
                    ("roi_bottom_right", x + w // 2, y + h // 2, w - w // 2, h - h // 2),
                ]
                for name, qx, qy, qw, qh in quadrants:
                    if qw <= 0 or qh <= 0:
                        continue
                    patch = gray[qy : qy + qh, qx : qx + qw]
                    if patch.size == 0:
                        continue
                    density = self._dark_ratio(patch)
                    if density >= 0.04:
                        regions.append(
                            {
                                "entity_id": name,
                                "entity_type": "subregion",
                                "bbox": {"x": int(qx), "y": int(qy), "width": int(qw), "height": int(qh)},
                                "salience": round(clamp(0.35 + density), 4),
                            }
                        )
        return regions

    def parse_many(
        self,
        problem_id: str,
        images: Sequence[Image.Image],
        image_qualities: Sequence[Dict[str, Any]],
        question_text: str,
    ) -> List[Dict[str, Any]]:
        records: List[Dict[str, Any]] = []
        for index, image in enumerate(images):
            rgb = image.convert("RGB")
            gray = np.asarray(rgb.convert("L"), dtype=np.float32)
            height, width = gray.shape
            quality = image_qualities[index] if index < len(image_qualities) else {}
            dark_ratio = self._dark_ratio(gray)
            aspect_ratio = float(width) / float(max(height, 1))
            visual_kind = self._infer_visual_kind(question_text, dark_ratio, aspect_ratio)
            entities = self._collect_regions(gray, quality.get("roi_bbox"))
            relations: List[Dict[str, Any]] = []
            for entity in entities:
                if entity["entity_id"] != "canvas":
                    relations.append({
                        "source_entity_id": entity["entity_id"],
                        "target_entity_id": "canvas",
                        "relation": "inside",
                    })
            regions_without_canvas = [item for item in entities if item["entity_id"] != "canvas"]
            for left, right in zip(regions_without_canvas, regions_without_canvas[1:]):
                relations.append(
                    {
                        "source_entity_id": left["entity_id"],
                        "target_entity_id": right["entity_id"],
                        "relation": "left_of" if left["bbox"]["x"] <= right["bbox"]["x"] else "right_of",
                    }
                )
            records.append(
                {
                    "visual_structure_id": f"visual_{problem_id}_{index + 1}",
                    "problem_id": problem_id,
                    "image_index": index + 1,
                    "image_asset_role": "primary_image" if index == 0 else f"aux_image_{index + 1}",
                    "global_attributes": {
                        "visual_kind": visual_kind,
                        "aspect_ratio": round(aspect_ratio, 4),
                        "dark_pixel_ratio": round(dark_ratio, 4),
                        "readability_score": quality.get("readability_score", 0.0),
                        "has_roi": bool(quality.get("roi_bbox")),
                    },
                    "visual_entities": entities,
                    "visual_relations": relations,
                    "parser_confidence": round(clamp(0.45 + 0.4 * quality.get("readability_score", 0.0) + 0.15 * min(len(entities), 5) / 5.0), 4),
                    "created_at": utc_now(),
                }
            )
        return records


class AlignmentEngine:
    """对齐文本结构与视觉结构。"""

    def align(
        self,
        problem_id: str,
        requires_image: bool,
        text_structure: Dict[str, Any],
        visual_structures: Sequence[Dict[str, Any]],
        image_qualities: Sequence[Dict[str, Any]],
        normalized_question_text: str,
    ) -> Dict[str, Any]:
        alignment_pairs: List[Dict[str, Any]] = []
        conflict_pairs: List[Dict[str, Any]] = []
        text_refs = [f"asset_{problem_id}_question_text_normalized"]
        image_entity_refs: List[str] = []
        referenced_visual_mentions = [item for item in text_structure.get("entity_mentions", []) if item.get("requires_visual_grounding")]
        slot_visual_mentions = [item for item in text_structure.get("answer_slots", []) if item.get("requires_visual_grounding")]
        expected_visual_anchors = len(referenced_visual_mentions) + len(slot_visual_mentions)
        available_entities = 0
        for visual in visual_structures:
            entities = visual.get("visual_entities", [])
            available_entities += len([item for item in entities if item.get("entity_id") != "canvas"])
            image_entity_refs.extend(
                [f"{visual['visual_structure_id']}::{entity['entity_id']}" for entity in entities if entity.get("entity_id") != "canvas"]
            )
        if requires_image and not visual_structures:
            conflict_pairs.append(
                {
                    "type": "missing_visual_structure",
                    "detail": "题目需要图像，但没有可用的视觉结构。",
                    "severity": "critical",
                    "confidence": 0.99,
                }
            )
        for visual in visual_structures:
            primary_region = next(
                (entity for entity in visual.get("visual_entities", []) if entity.get("entity_type") == "content_region"),
                None,
            ) or next(
                (entity for entity in visual.get("visual_entities", []) if entity.get("entity_id") != "canvas"),
                None,
            )
            if primary_region is None:
                continue
            for mention in referenced_visual_mentions:
                alignment_pairs.append(
                    {
                        "text_ref": mention["mention"],
                        "image_ref": f"{visual['visual_structure_id']}::{primary_region['entity_id']}",
                        "relation": f"grounds_{mention['entity_category']}",
                        "confidence": round(clamp(0.55 + 0.25 * visual.get("parser_confidence", 0.0)), 4),
                    }
                )
            for slot in slot_visual_mentions:
                alignment_pairs.append(
                    {
                        "text_ref": slot["slot_id"],
                        "image_ref": f"{visual['visual_structure_id']}::{primary_region['entity_id']}",
                        "relation": "slot_grounding",
                        "confidence": round(clamp(0.58 + 0.22 * visual.get("parser_confidence", 0.0)), 4),
                    }
                )
        if requires_image:
            low_readability_indices = [
                index + 1
                for index, quality in enumerate(image_qualities)
                if quality.get("readability_score", 0.0) < 0.4
            ]
            if low_readability_indices:
                conflict_pairs.append(
                    {
                        "type": "visual_readability_risk",
                        "detail": f"图像 {low_readability_indices} 可读性偏低。",
                        "severity": "major",
                        "confidence": 0.9,
                    }
                )
            if expected_visual_anchors > 0 and available_entities == 0:
                conflict_pairs.append(
                    {
                        "type": "ungrounded_visual_reference",
                        "detail": "文本显式引用了图像对象，但视觉结构中没有可对齐区域。",
                        "severity": "critical",
                        "confidence": 0.96,
                    }
                )
            elif expected_visual_anchors > max(available_entities, 1) * 2:
                conflict_pairs.append(
                    {
                        "type": "visual_reference_density_mismatch",
                        "detail": "文本中的视觉锚点明显多于可识别视觉区域。",
                        "severity": "major",
                        "confidence": 0.72,
                    }
                )
        if requires_image and not VISUAL_REFERENCE_PATTERN.search(normalized_question_text) and text_structure.get("requires_visual_grounding"):
            conflict_pairs.append(
                {
                    "type": "implicit_visual_dependency",
                    "detail": "题目依赖图像，但题干中视觉锚点表达较弱。",
                    "severity": "minor",
                    "confidence": 0.61,
                }
            )
        matched_anchor_count = len(alignment_pairs)
        expected_count = expected_visual_anchors if requires_image else 1
        coverage_score = 1.0
        if requires_image:
            coverage_score = clamp(0.18 + 0.72 * min(matched_anchor_count, max(expected_count, 1)) / max(expected_count, 1))
        penalty = 0.0
        for conflict in conflict_pairs:
            severity = conflict.get("severity")
            if severity == "critical":
                penalty += 0.28
            elif severity == "major":
                penalty += 0.16
            else:
                penalty += 0.08
        consistency_score = clamp(coverage_score - penalty + (0.08 if matched_anchor_count else 0.0))
        status = "good"
        if consistency_score < 0.55:
            status = "bad"
        elif consistency_score < 0.72 or penalty > 0.12:
            status = "risky"
        return {
            "alignment_id": f"align_{problem_id}",
            "problem_id": problem_id,
            "image_entity_refs": image_entity_refs,
            "text_span_refs": text_refs,
            "alignment_pairs": alignment_pairs,
            "conflict_pairs": conflict_pairs,
            "coverage_score": round(coverage_score, 4),
            "consistency_score": round(consistency_score, 4),
            "alignment_status": status,
            "created_at": utc_now(),
        }


class SolvabilityChecker:
    """判断样本是否具备进入标注的最低可解性。"""

    def evaluate(
        self,
        problem_id: str,
        normalized_answer_text: str,
        answer_type: str,
        requires_image: bool,
        open_variants: Sequence[Dict[str, Any]],
        text_structure: Dict[str, Any],
        visual_structures: Sequence[Dict[str, Any]],
        alignment_record: Dict[str, Any],
        quality_flags: Sequence[str],
    ) -> Dict[str, Any]:
        failure_codes: List[str] = []
        answer_verifiable = bool(normalized_answer_text) and answer_type in {"numeric", "option", "short_text", "text", "set"}
        target_clear = bool(text_structure.get("answer_slots")) and all(
            len(normalize_whitespace(str(slot.get("target_text") or ""))) >= 3
            and not GENERIC_BAD_VARIANT_PATTERN.fullmatch(normalize_whitespace(str(slot.get("target_text") or "")))
            for slot in text_structure.get("answer_slots", [])
        )
        rewrite_complete = bool(open_variants) and all(
            normalize_whitespace(str(variant.get("rewritten_question_text") or ""))
            and not GENERIC_BAD_VARIANT_PATTERN.fullmatch(normalize_whitespace(str(variant.get("rewritten_question_text") or "")))
            for variant in open_variants
        )
        text_sufficient = bool(text_structure.get("conditions")) or len(text_structure.get("targets", [])) >= 1
        visual_grounding_available = (not requires_image) or (
            bool(visual_structures)
            and alignment_record.get("alignment_status") != "bad"
            and alignment_record.get("coverage_score", 0.0) >= 0.4
        )
        reasoning_path_exists = answer_verifiable and target_clear and rewrite_complete and text_sufficient and visual_grounding_available
        if not answer_verifiable:
            failure_codes.append("answer_not_verifiable")
        if not target_clear:
            failure_codes.append("target_underspecified")
        if not rewrite_complete:
            failure_codes.append("rewrite_variant_invalid")
        if not text_sufficient:
            failure_codes.append("insufficient_text_conditions")
        if requires_image and not visual_grounding_available:
            failure_codes.append("missing_grounded_visual_path")
        if any(flag in {"missing_answer", "missing_core_image"} for flag in quality_flags):
            failure_codes.append("missing_core_field")
        score_breakdown = {
            "answer_verifiable": 1.0 if answer_verifiable else 0.0,
            "target_clear": 1.0 if target_clear else 0.0,
            "rewrite_complete": 1.0 if rewrite_complete else 0.0,
            "text_sufficient": 1.0 if text_sufficient else 0.0,
            "visual_grounding": 1.0 if visual_grounding_available else 0.0,
        }
        solvability_score = round(
            clamp(
                0.22 * score_breakdown["answer_verifiable"]
                + 0.22 * score_breakdown["target_clear"]
                + 0.18 * score_breakdown["rewrite_complete"]
                + 0.18 * score_breakdown["text_sufficient"]
                + 0.20 * score_breakdown["visual_grounding"]
            ),
            4,
        )
        decision_hint = "pass"
        if failure_codes:
            if any(code in {"missing_grounded_visual_path", "missing_core_field", "rewrite_variant_invalid"} for code in failure_codes):
                decision_hint = "reject"
            else:
                decision_hint = "review"
        elif solvability_score < 0.7:
            decision_hint = "review"
        return {
            "solvability_id": f"solv_{problem_id}",
            "problem_id": problem_id,
            "answer_verifiable": answer_verifiable,
            "target_clear": target_clear,
            "rewrite_complete": rewrite_complete,
            "text_sufficient": text_sufficient,
            "visual_grounding_available": visual_grounding_available,
            "reasoning_path_exists": reasoning_path_exists,
            "path_mode": "multimodal" if requires_image else "text_only",
            "failure_codes": failure_codes,
            "score_breakdown": score_breakdown,
            "solvability_score": solvability_score,
            "decision_hint": decision_hint,
            "created_at": utc_now(),
        }
