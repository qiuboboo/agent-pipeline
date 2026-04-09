#!/usr/bin/env python3
"""多数据集数据采集与清洗智能体流水线。"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from .pipeline_clients import OpenAICompatibleClient
    from .pipeline_extraction import read_prompt
    from .pipeline_normalization import TextNormalizer
    from .pipeline_types import RewriteReport, RewriteVariant
    from .pipeline_utils import normalize_whitespace, to_plain_text
except ImportError:
    from pipeline_clients import OpenAICompatibleClient
    from pipeline_extraction import read_prompt
    from pipeline_normalization import TextNormalizer
    from pipeline_types import RewriteReport, RewriteVariant
    from pipeline_utils import normalize_whitespace, to_plain_text


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROMPT_ROOT = PROJECT_ROOT / "prompts"
REWRITE_AGENT_PROMPT_PATH = PROMPT_ROOT / "cleaning" / "rewrite_agent.md"


def build_rewrite_result(
    *,
    strategy: str,
    rationale: str,
    variants: List[Dict[str, Any]],
    discard_reason_codes: List[str],
    llm_used: bool,
    fallback_used: bool,
    fallback_reason: Optional[str],
    schema_valid: bool,
    normalization_warnings: List[str],
) -> RewriteReport:
    return {
        "strategy": strategy,
        "rationale": rationale,
        "variants": variants,
        "discard_reason_codes": discard_reason_codes,
        "llm_used": llm_used,
        "fallback_used": fallback_used,
        "fallback_reason": fallback_reason,
        "schema_valid": schema_valid,
        "normalization_warnings": normalization_warnings,
    }


ALLOWED_REWRITE_STRATEGIES = {"keep_open", "blank_open", "split_open", "drop_image_index"}


class BaseStructuredAgent:
    def __init__(self, client: OpenAICompatibleClient, prompt_path: Path, fallback_system_prompt: str):
        self.client = client
        self.prompt_path = prompt_path
        self.system_prompt = read_prompt(prompt_path) if prompt_path.exists() else fallback_system_prompt

    def call_json(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        user_prompt = json.dumps(payload, ensure_ascii=False, indent=2)
        result = self.client.chat_json(self.system_prompt, user_prompt, caller=self.__class__.__name__.lower())
        if not isinstance(result, dict):
            return None
        return result

    def normalize_list_field(self, result: Dict[str, Any], field_name: str) -> Dict[str, Any]:
        field_value = result.get(field_name)
        if field_value is not None and not isinstance(field_value, list):
            result[field_name] = []
        return result


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
    if mixed_match:
        answer = mixed_match.group(2).strip()
    return normalize_whitespace(answer)


def normalize_rewrite_variants_temp(
    normalizer: TextNormalizer,
    dataset_name: str,
    normalized_question_text: str,
    normalized_answer_text: str,
    answer_type: str,
    choices: Dict[str, str],
    variants: List[Dict[str, Any]],
) -> Tuple[List[RewriteVariant], List[str]]:
    normalized_variants: List[RewriteVariant] = []
    warnings: List[str] = []
    seen_variant_keys = set()
    fallback_answer = choices.get(normalized_answer_text, normalized_answer_text)
    answer_index_base = 0 if dataset_name.strip().lower() == "scemqa" else None
    for idx, variant in enumerate(variants, start=1):
        if not isinstance(variant, dict):
            warnings.append(f"variant_{idx}_not_object")
            continue
        expected_answer = normalize_whitespace(to_plain_text(variant.get("expected_answer")))
        if expected_answer:
            expected_answer = resolve_multiple_choice_answer_text(expected_answer, choices, answer_index_base)
        if not expected_answer:
            expected_answer = fallback_answer
            warnings.append(f"variant_{idx}_missing_expected_answer")
        expected_answer_type = to_plain_text(variant.get("expected_answer_type")).strip() or answer_type
        inferred_type = normalizer.infer_answer_type(normalizer.normalize_answer(expected_answer)) if expected_answer else expected_answer_type
        if inferred_type == "option":
            inferred_type = "short_text"
        rewritten_question_text = to_plain_text(variant.get("rewritten_question_text")) or normalized_question_text
        if not to_plain_text(variant.get("rewritten_question_text")).strip():
            warnings.append(f"variant_{idx}_missing_question_text")
        normalized_variant: RewriteVariant = {
            "variant_id": to_plain_text(variant.get("variant_id")) or f"open_{idx}",
            "title": to_plain_text(variant.get("title")) or f"{dataset_name} 开放题",
            "rewritten_question_text": rewritten_question_text,
            "expected_answer_type": inferred_type or expected_answer_type or answer_type,
            "expected_answer": expected_answer,
            "split_role": to_plain_text(variant.get("split_role")) or "single",
        }
        dedupe_key = (
            normalized_variant["rewritten_question_text"],
            normalized_variant["expected_answer"],
            normalized_variant["split_role"],
        )
        if dedupe_key in seen_variant_keys:
            warnings.append(f"variant_{idx}_duplicate")
            continue
        seen_variant_keys.add(dedupe_key)
        normalized_variants.append(normalized_variant)
    return normalized_variants, warnings


class RewriteAgent(BaseStructuredAgent):
    def __init__(self, client: OpenAICompatibleClient, normalizer: TextNormalizer, logger: Any = None):
        super().__init__(
            client,
            REWRITE_AGENT_PROMPT_PATH,
            "You are the Question Rewrite Agent in a multimodal dataset cleaning pipeline. Convert multiple-choice questions into open-ended variants and return strict JSON only.",
        )
        self.normalizer = normalizer
        self.logger = logger

    def call_json(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        result = super().call_json(payload)
        if not isinstance(result, dict):
            return None
        result = self.normalize_list_field(result, "variants")
        result = self.normalize_list_field(result, "discard_reason_codes")
        return result

    def fallback_rewrite(self, dataset_name: str, question_text: str, normalized_answer: str, answer_type: str, choices: Dict[str, str]) -> RewriteReport:
        question_only, _ = self.normalizer.split_question_and_choices(question_text)
        question_only = self.normalizer.strip_hint(question_only)
        if not choices:
            if answer_type == "option" and any(token in question_only.lower() for token in ["which picture", "in which picture", "which figure", "which diagram", "which graph", "shown below", "illustrated"]):
                return build_rewrite_result(
                    strategy="blank_open",
                    rationale="Pure-image label selection tasks are in scope, so keep the task and require the answer as the correct option label.",
                    variants=[
                        {
                            "variant_id": "open_1",
                            "title": f"{dataset_name} 图像标签题",
                            "rewritten_question_text": question_only,
                            "expected_answer_type": "short_text",
                            "expected_answer": normalized_answer,
                            "split_role": "single",
                        }
                    ],
                    discard_reason_codes=[],
                    llm_used=False,
                    fallback_used=True,
                    fallback_reason=None,
                    schema_valid=True,
                    normalization_warnings=[],
                )
            return build_rewrite_result(
                strategy="keep_open",
                rationale="Question is already open-ended.",
                variants=[
                    {
                        "variant_id": "open_1",
                        "title": f"{dataset_name} 开放题",
                        "rewritten_question_text": question_only,
                        "expected_answer_type": answer_type,
                        "expected_answer": normalized_answer,
                        "split_role": "single",
                    }
                ],
                discard_reason_codes=[],
                llm_used=False,
                fallback_used=True,
                fallback_reason=None,
                schema_valid=True,
                normalization_warnings=[],
            )
        if self.normalizer.is_pure_image_index_question(question_only, choices):
            resolved_answer = choices.get(normalized_answer, normalized_answer)
            return build_rewrite_result(
                strategy="blank_open",
                rationale="Pure-image choice questions remain valid tasks for this pipeline, so convert them into answer-with-label open questions instead of dropping them.",
                variants=[
                    {
                        "variant_id": "open_1",
                        "title": f"{dataset_name} 图像标签题",
                        "rewritten_question_text": question_only,
                        "expected_answer_type": "short_text",
                        "expected_answer": resolved_answer,
                        "split_role": "single",
                    }
                ],
                discard_reason_codes=[],
                llm_used=False,
                fallback_used=True,
                fallback_reason=None,
                schema_valid=True,
                normalization_warnings=[],
            )
        if self.normalizer.is_compound_answer_question(question_only, choices):
            correct_text = choices.get(normalized_answer, "")
            pieces = [piece.strip() for piece in re.split(r"[;；]", correct_text) if piece.strip()]
            if not pieces:
                pieces = [correct_text] if correct_text else []
            variants: List[RewriteVariant] = []
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
            return build_rewrite_result(
                strategy="split_open",
                rationale="Compound choice answer was split into multiple open-ended targets.",
                variants=variants,
                discard_reason_codes=[],
                llm_used=False,
                fallback_used=True,
                fallback_reason=None,
                schema_valid=True,
                normalization_warnings=[],
            )
        resolved_answer = choices.get(normalized_answer, normalized_answer)
        resolved_answer_type = self.normalizer.infer_answer_type(self.normalizer.normalize_answer(resolved_answer))
        if resolved_answer_type == "option":
            resolved_answer_type = "short_text"
        return build_rewrite_result(
            strategy="blank_open",
            rationale="Converted multiple choice into blank-style open-ended question.",
            variants=[
                {
                    "variant_id": "open_1",
                    "title": f"{dataset_name} 开放题",
                    "rewritten_question_text": question_only,
                    "expected_answer_type": resolved_answer_type,
                    "expected_answer": resolved_answer,
                    "split_role": "single",
                }
            ],
            discard_reason_codes=[],
            llm_used=False,
            fallback_used=True,
            fallback_reason=None,
            schema_valid=True,
            normalization_warnings=[],
        )

    def rewrite(self, dataset_name: str, normalized_question_text: str, normalized_answer_text: str, answer_type: str, choices: Dict[str, str]) -> RewriteReport:
        fallback = self.fallback_rewrite(dataset_name, normalized_question_text, normalized_answer_text, answer_type, choices)
        if not self.client.config.enabled:
            fallback["fallback_reason"] = "llm_disabled"
            return fallback
        if not choices:
            fallback["fallback_reason"] = "question_already_open_or_no_choices"
            return fallback
        llm_result = self.call_json(
            {
                "dataset_name": dataset_name,
                "question_text": normalized_question_text,
                "choices": choices,
                "correct_option_letter": normalized_answer_text if answer_type == "option" else None,
                "correct_option_text": choices.get(normalized_answer_text, normalized_answer_text),
                "answer_type": answer_type,
                "dataset_rules": {
                    "scemqa_answer_index_base": 0 if dataset_name.strip().lower() == "scemqa" else None
                },
                "fallback_result": fallback,
            }
        )
        if not llm_result:
            fallback["fallback_reason"] = "llm_empty_result"
            return fallback
        raw_strategy = to_plain_text(llm_result.get("strategy")).strip()
        strategy = raw_strategy or fallback["strategy"]
        if strategy not in ALLOWED_REWRITE_STRATEGIES:
            fallback["fallback_reason"] = "invalid_strategy"
            fallback["normalization_warnings"] = [f"invalid_strategy:{strategy}"] if strategy else ["missing_strategy"]
            return fallback
        raw_variants = llm_result.get("variants")
        if strategy == "drop_image_index":
            normalized_variants: List[RewriteVariant] = []
            normalization_warnings: List[str] = []
        else:
            if not isinstance(raw_variants, list):
                fallback["fallback_reason"] = "variants_not_list"
                fallback["normalization_warnings"] = ["variants_not_list"]
                return fallback
            normalized_variants, normalization_warnings = normalize_rewrite_variants_temp(
                self.normalizer,
                dataset_name,
                normalized_question_text,
                normalized_answer_text,
                answer_type,
                choices,
                raw_variants,
            )
            if not normalized_variants:
                fallback["fallback_reason"] = "variants_empty_after_normalization"
                fallback["normalization_warnings"] = normalization_warnings or ["variants_empty_after_normalization"]
                return fallback
        discard_reason_codes = llm_result.get("discard_reason_codes")
        if not isinstance(discard_reason_codes, list):
            discard_reason_codes = []
            normalization_warnings = [*normalization_warnings, "discard_reason_codes_not_list"]
        return build_rewrite_result(
            strategy=strategy,
            rationale=to_plain_text(llm_result.get("rationale")) or fallback["rationale"],
            variants=normalized_variants,
            discard_reason_codes=[to_plain_text(code) for code in discard_reason_codes if to_plain_text(code)],
            llm_used=True,
            fallback_used=False,
            fallback_reason=None,
            schema_valid=True,
            normalization_warnings=normalization_warnings,
        )
