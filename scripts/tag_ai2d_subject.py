#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
DEFAULT_DATASET_ROOT = PROJECT_ROOT / "ready" / "ai2d"
DEFAULT_PIPELINE2_CONFIG_PATH = SRC_ROOT / "benchmarkallinone" / "pipeline2" / "configs" / "default_pipeline2.yaml"

if SRC_ROOT.exists():
    sys.path.insert(0, str(SRC_ROOT))

try:
    from benchmarkallinone.pipeline2.clients import OpenAICompatibleClient
    from benchmarkallinone.pipeline2.config import ModelEndpointConfig, Pipeline2Config
except Exception:
    OpenAICompatibleClient = None
    ModelEndpointConfig = None
    Pipeline2Config = None

BIOLOGY_PATTERNS: Sequence[Tuple[str, str, int]] = [
    ("food chain", "phrase:food chain", 4),
    ("food web", "phrase:food web", 4),
    ("ecosystem", "token:ecosystem", 3),
    ("habitat", "token:habitat", 3),
    ("population", "token:population", 3),
    ("predator", "token:predator", 3),
    ("prey", "token:prey", 3),
    ("producer", "token:producer", 3),
    ("consumer", "token:consumer", 3),
    ("decomposer", "token:decomposer", 3),
    ("photosynthesis", "token:photosynthesis", 4),
    ("respiration", "token:respiration", 3),
    ("phytoplankton", "token:phytoplankton", 4),
    ("plankton", "token:plankton", 3),
    ("species", "token:species", 3),
    ("organism", "token:organism", 3),
    ("organisms", "token:organisms", 3),
    ("cell", "token:cell", 3),
    ("cells", "token:cells", 3),
    ("tissue", "token:tissue", 3),
    ("organ", "token:organ", 3),
    ("plant", "token:plant", 2),
    ("plants", "token:plants", 2),
    ("animal", "token:animal", 2),
    ("animals", "token:animals", 2),
    ("mammal", "token:mammal", 2),
    ("mammals", "token:mammals", 2),
    ("bird", "token:bird", 2),
    ("birds", "token:birds", 2),
    ("fish", "token:fish", 2),
    ("whale", "token:whale", 3),
    ("whales", "token:whales", 3),
    ("seal", "token:seal", 3),
    ("seals", "token:seals", 3),
    ("elephant seal", "phrase:elephant seal", 4),
    ("insect", "token:insect", 2),
    ("insects", "token:insects", 2),
    ("frog", "token:frog", 2),
    ("bacteria", "token:bacteria", 3),
    ("fungi", "token:fungi", 3),
    ("dna", "token:dna", 3),
    ("gene", "token:gene", 3),
    ("genes", "token:genes", 3),
    ("leaf", "token:leaf", 2),
    ("roots", "token:roots", 2),
    ("flower", "token:flower", 2),
    ("respiratory", "token:respiratory", 3),
    ("digestive", "token:digestive", 3),
    ("circulatory", "token:circulatory", 3),
]

GEOGRAPHY_PATTERNS: Sequence[Tuple[str, str, int]] = [
    ("world map", "phrase:world map", 5),
    ("political map", "phrase:political map", 5),
    ("physical map", "phrase:physical map", 5),
    ("topographic map", "phrase:topographic map", 5),
    ("climate map", "phrase:climate map", 5),
    ("weather map", "phrase:weather map", 5),
    ("water cycle", "phrase:water cycle", 5),
    ("rock cycle", "phrase:rock cycle", 5),
    ("runoff stage", "phrase:runoff stage", 5),
    ("compass rose", "phrase:compass rose", 4),
    ("water current", "phrase:water current", 4),
    ("air current", "phrase:air current", 3),
    ("sedimentary rock", "phrase:sedimentary rock", 4),
    ("metamorphic rock", "phrase:metamorphic rock", 4),
    ("igneous rock", "phrase:igneous rock", 4),
    ("pacific ocean", "phrase:pacific ocean", 5),
    ("latitude", "token:latitude", 4),
    ("longitude", "token:longitude", 4),
    ("equator", "token:equator", 4),
    ("hemisphere", "token:hemisphere", 4),
    ("continent", "token:continent", 4),
    ("continents", "token:continents", 4),
    ("country", "token:country", 4),
    ("countries", "token:countries", 4),
    ("city", "token:city", 3),
    ("cities", "token:cities", 3),
    ("capital", "token:capital", 4),
    ("river", "token:river", 3),
    ("rivers", "token:rivers", 3),
    ("mountain", "token:mountain", 3),
    ("mountains", "token:mountains", 3),
    ("ocean", "token:ocean", 3),
    ("oceans", "token:oceans", 3),
    ("sea", "token:sea", 2),
    ("desert", "token:desert", 3),
    ("island", "token:island", 3),
    ("landform", "token:landform", 3),
    ("landforms", "token:landforms", 3),
    ("climate", "token:climate", 3),
    ("weather", "token:weather", 3),
    ("precipitation", "token:precipitation", 3),
    ("evaporation", "token:evaporation", 3),
    ("condensation", "token:condensation", 3),
    ("erosion", "token:erosion", 4),
    ("weathering", "token:weathering", 4),
    ("deposition", "token:deposition", 4),
    ("sediment", "token:sediment", 3),
    ("sediments", "token:sediments", 3),
    ("sedimentary", "token:sedimentary", 3),
    ("metamorphic", "token:metamorphic", 3),
    ("igneous", "token:igneous", 3),
    ("plateau", "token:plateau", 3),
    ("plain", "token:plain", 2),
    ("valley", "token:valley", 2),
    ("coast", "token:coast", 2),
    ("map", "token:map", 2),
    ("delta", "token:delta", 2),
    ("runoff", "token:runoff", 4),
]

OTHER_HINT_PATTERNS: Sequence[Tuple[str, str, int]] = [
    ("moon", "token:moon", 4),
    ("lunar", "token:lunar", 4),
    ("waxing", "token:waxing", 4),
    ("waning", "token:waning", 4),
    ("gibbous", "token:gibbous", 4),
    ("eclipse", "token:eclipse", 4),
    ("solar system", "phrase:solar system", 5),
    ("planet", "token:planet", 4),
    ("planets", "token:planets", 4),
    ("orbit", "token:orbit", 3),
    ("star", "token:star", 3),
    ("stars", "token:stars", 3),
    ("constellation", "token:constellation", 4),
    ("circuit", "token:circuit", 4),
    ("voltage", "token:voltage", 4),
    ("current", "token:current", 3),
    ("force", "token:force", 3),
    ("velocity", "token:velocity", 3),
]

SUBJECT_FIELDS = [
    "problem_main_record",
    "clean_problem_record",
    "normalization_record",
    "source_intake_record",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rule-based subject tagging for ready/ai2d samples. Defaults to dry-run."
    )
    parser.add_argument("--dataset-root", default=str(DEFAULT_DATASET_ROOT), help="Dataset root containing samples/*.json")
    parser.add_argument("--limit", type=int, default=0, help="Maximum samples to scan (0 = all)")
    parser.add_argument("--preview", type=int, default=12, help="Number of preview rows to print")
    parser.add_argument("--write", action="store_true", help="Actually write subject tags back into sample JSON files")
    parser.add_argument(
        "--set-other",
        action="store_true",
        help="When writing, also write subject=other for non-biology/non-geography samples. Default only writes biology/geography.",
    )
    parser.add_argument(
        "--llm-fallback",
        action="store_true",
        help="When rule classification is uncertain, call an OpenAI-compatible chat JSON model for a second opinion.",
    )
    parser.add_argument(
        "--llm-max-calls",
        type=int,
        default=20,
        help="Maximum fallback LLM calls to make in one run when --llm-fallback is enabled (default: 20).",
    )
    parser.add_argument(
        "--llm-config",
        default=os.environ.get("AI2D_SUBJECT_PIPELINE2_CONFIG", ""),
        help="Optional pipeline2 YAML config to inherit primary model settings from.",
    )
    parser.add_argument("--llm-base-url", default=os.environ.get("AI2D_SUBJECT_BASE_URL", ""))
    parser.add_argument("--llm-api-key", default=os.environ.get("AI2D_SUBJECT_API_KEY", ""))
    parser.add_argument("--llm-model", default=os.environ.get("AI2D_SUBJECT_MODEL", ""))
    parser.add_argument("--llm-reasoning-effort", default=os.environ.get("AI2D_SUBJECT_REASONING_EFFORT", ""))
    parser.add_argument(
        "--llm-temperature",
        type=float,
        default=float(os.environ["AI2D_SUBJECT_TEMPERATURE"]) if "AI2D_SUBJECT_TEMPERATURE" in os.environ else None,
    )
    parser.add_argument(
        "--llm-timeout-seconds",
        type=int,
        default=int(os.environ["AI2D_SUBJECT_TIMEOUT_SECONDS"]) if "AI2D_SUBJECT_TIMEOUT_SECONDS" in os.environ else None,
    )
    return parser.parse_args()


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def pick_first_nonempty(*values: Any) -> str:
    for value in values:
        if value is None:
            continue
        if isinstance(value, str):
            if value.strip():
                return value.strip()
            continue
        if isinstance(value, (int, float)):
            return str(value)
    return ""


def first_present(*values: Any) -> Any:
    for value in values:
        if value is None:
            continue
        if isinstance(value, str):
            if value.strip():
                return value
            continue
        return value
    return None


def resolve_pipeline2_primary_config(config_path: str) -> Tuple[Optional[Any], Optional[str]]:
    if Pipeline2Config is None:
        return None, None
    candidate_paths: List[Path] = []
    if config_path:
        candidate_paths.append(Path(config_path))
    if DEFAULT_PIPELINE2_CONFIG_PATH.exists():
        candidate_paths.append(DEFAULT_PIPELINE2_CONFIG_PATH)
    for candidate in candidate_paths:
        try:
            config = Pipeline2Config.from_yaml(str(candidate))
            return config.models.primary, str(candidate)
        except Exception:
            continue
    return None, None


def resolve_llm_endpoint_settings(args: argparse.Namespace) -> Dict[str, Any]:
    inherited_config, inherited_source = resolve_pipeline2_primary_config(args.llm_config)

    base_url = first_present(
        args.llm_base_url,
        getattr(inherited_config, "base_url", None),
        os.environ.get("ANNOTATION_API_BASE_URL"),
        os.environ.get("PIPELINE2_BASE_URL_PRIMARY"),
        os.environ.get("OPENAI_BASE_URL"),
        "https://synai996.space/v1",
    )
    api_key = first_present(
        args.llm_api_key,
        getattr(inherited_config, "api_key", None),
        os.environ.get("ANNOTATION_API_KEY"),
        os.environ.get("PIPELINE2_API_KEY_PRIMARY"),
        os.environ.get("OPENAI_API_KEY"),
        "",
    )
    model = first_present(
        args.llm_model,
        getattr(inherited_config, "model", None),
        os.environ.get("ANNOTATION_MODEL"),
        "gpt-5.4",
    )
    reasoning_effort = first_present(
        args.llm_reasoning_effort,
        getattr(inherited_config, "reasoning_effort", None),
        os.environ.get("ANNOTATION_REASONING_EFFORT"),
        "low",
    )
    temperature = first_present(
        args.llm_temperature,
        getattr(inherited_config, "temperature", None),
        0.0,
    )
    timeout_seconds = first_present(
        args.llm_timeout_seconds,
        getattr(inherited_config, "timeout_seconds", None),
        180,
    )

    return {
        "base_url": str(base_url),
        "api_key": str(api_key),
        "model": str(model),
        "reasoning_effort": str(reasoning_effort),
        "temperature": float(temperature),
        "timeout_seconds": int(timeout_seconds),
        "config_source": inherited_source or "direct-env-or-defaults",
    }


def append_text(parts: List[str], value: Any) -> None:
    if value is None:
        return
    if isinstance(value, str):
        text = value.strip()
        if text:
            parts.append(text)
        return
    if isinstance(value, dict):
        for nested in value.values():
            append_text(parts, nested)
        return
    if isinstance(value, list):
        for item in value:
            append_text(parts, item)


def gather_sample_texts(sample: Dict[str, Any]) -> List[str]:
    parts: List[str] = []

    for block_name in [
        "problem_main_record",
        "clean_problem_record",
        "normalization_record",
        "source_intake_record",
        "candidate_problem_record",
    ]:
        block = sample.get(block_name) or {}
        append_text(parts, block.get("normalized_question_text"))
        append_text(parts, block.get("raw_question_text"))
        append_text(parts, block.get("normalized_answer_text"))
        append_text(parts, block.get("raw_answer_text"))
        append_text(parts, block.get("choice_map"))

    for record in sample.get("text_structure_records") or []:
        append_text(parts, record.get("targets"))
        append_text(parts, record.get("conditions"))
        append_text(parts, record.get("entity_mentions"))

    for record in sample.get("visual_structure_records") or []:
        append_text(parts, (record.get("global_attributes") or {}).get("visual_kind"))

    return parts


def normalize_text(texts: Iterable[str]) -> str:
    joined = "\n".join(texts)
    joined = joined.lower()
    joined = joined.replace("_", " ")
    joined = re.sub(r"[^a-z0-9\s\-]", " ", joined)
    joined = re.sub(r"\s+", " ", joined)
    return joined.strip()


def score_patterns(text: str, patterns: Sequence[Tuple[str, str, int]]) -> Tuple[int, List[str]]:
    score = 0
    reasons: List[str] = []
    for pattern, reason, weight in patterns:
        escaped = re.escape(pattern)
        regex = rf"(?<![a-z0-9]){escaped}(?![a-z0-9])"
        if re.search(regex, text):
            score += weight
            reasons.append(reason)
    return score, reasons


def rule_classify_sample(sample: Dict[str, Any]) -> Dict[str, Any]:
    text_parts = gather_sample_texts(sample)
    normalized = normalize_text(text_parts)
    biology_score, biology_reasons = score_patterns(normalized, BIOLOGY_PATTERNS)
    geography_score, geography_reasons = score_patterns(normalized, GEOGRAPHY_PATTERNS)
    other_score, other_reasons = score_patterns(normalized, OTHER_HINT_PATTERNS)

    subject = "other"
    confidence = "low"
    reasons: List[str] = []

    if biology_score >= 4 and biology_score >= geography_score + 2 and biology_score >= other_score:
        subject = "biology"
        confidence = "high" if biology_score >= 6 else "medium"
        reasons = biology_reasons
    elif geography_score >= 4 and geography_score >= biology_score + 2 and geography_score >= other_score:
        subject = "geography"
        confidence = "high" if geography_score >= 6 else "medium"
        reasons = geography_reasons
    elif max(biology_score, geography_score) >= 3 and abs(biology_score - geography_score) >= 2 and max(biology_score, geography_score) > other_score:
        if biology_score > geography_score:
            subject = "biology"
            confidence = "medium"
            reasons = biology_reasons
        else:
            subject = "geography"
            confidence = "medium"
            reasons = geography_reasons
    else:
        subject = "other"
        confidence = "low" if other_score == 0 else "medium"
        reasons = other_reasons or ["fallback:non-bio-geo"]

    return {
        "subject": subject,
        "confidence": confidence,
        "scores": {
            "biology": biology_score,
            "geography": geography_score,
            "other": other_score,
        },
        "reasons": reasons[:8],
        "text_excerpt": normalized[:240],
        "normalized_text": normalized,
        "route": "rules",
    }


def should_use_llm_fallback(rule_metadata: Dict[str, Any]) -> bool:
    scores = rule_metadata.get("scores") or {}
    biology_score = int(scores.get("biology", 0) or 0)
    geography_score = int(scores.get("geography", 0) or 0)
    other_score = int(scores.get("other", 0) or 0)
    subject = rule_metadata.get("subject")
    confidence = rule_metadata.get("confidence")
    reasons = rule_metadata.get("reasons") or []

    if confidence == "low":
        return True
    if subject == "other":
        return True
    if "fallback:non-bio-geo" in reasons:
        return True
    if abs(biology_score - geography_score) <= 1 and max(biology_score, geography_score) >= 2:
        return True
    if other_score >= max(biology_score, geography_score) and max(biology_score, geography_score) >= 2:
        return True
    return False


def build_llm_user_prompt(sample: Dict[str, Any], rule_metadata: Dict[str, Any]) -> str:
    question = pick_first_nonempty(
        ((sample.get("clean_problem_record") or {}).get("normalized_question_text")),
        ((sample.get("problem_main_record") or {}).get("normalized_question_text")),
        ((sample.get("source_intake_record") or {}).get("raw_question_text")),
    )
    answer = pick_first_nonempty(
        ((sample.get("clean_problem_record") or {}).get("normalized_answer_text")),
        ((sample.get("problem_main_record") or {}).get("normalized_answer_text")),
        ((sample.get("source_intake_record") or {}).get("raw_answer_text")),
    )
    choice_map = (
        ((sample.get("clean_problem_record") or {}).get("choice_map"))
        or ((sample.get("problem_main_record") or {}).get("choice_map"))
        or ((sample.get("source_intake_record") or {}).get("choice_map"))
        or {}
    )
    payload = {
        "task": "Classify this AI2D science diagram question into one of: biology, geography, other.",
        "policy": {
            "labels": ["biology", "geography", "other"],
            "use_other_when": [
                "astronomy/space-science",
                "physics/circuit/mechanics",
                "generic visual label lookup with insufficient biology/geography evidence",
            ],
            "do_not_overcall": "Prefer other when the evidence for biology or geography is weak.",
        },
        "rule_guess": {
            "subject": rule_metadata.get("subject"),
            "confidence": rule_metadata.get("confidence"),
            "scores": rule_metadata.get("scores"),
            "reasons": rule_metadata.get("reasons"),
        },
        "sample": {
            "question": question,
            "answer": answer,
            "choice_map": choice_map,
            "text_excerpt": rule_metadata.get("normalized_text", "")[:1600],
        },
        "return_json_schema": {
            "subject": "biology|geography|other",
            "confidence": "high|medium|low",
            "reasons": ["short reason strings"],
        },
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def llm_classify_sample(sample: Dict[str, Any], rule_metadata: Dict[str, Any], client: Any) -> Optional[Dict[str, Any]]:
    if client is None:
        return None
    system_prompt = (
        "You classify AI2D science diagram questions into biology, geography, or other. "
        "Return exactly one JSON object with keys subject, confidence, reasons. "
        "Use 'other' for astronomy/space, physics/circuit, or generic label-lookup questions with insufficient evidence."
    )
    response = client.chat_json(system_prompt, build_llm_user_prompt(sample, rule_metadata))
    if not isinstance(response, dict):
        return None
    subject = str(response.get("subject", "")).strip().lower()
    confidence = str(response.get("confidence", "")).strip().lower()
    reasons = response.get("reasons") or []
    if subject not in {"biology", "geography", "other"}:
        return None
    if confidence not in {"high", "medium", "low"}:
        confidence = "medium"
    if not isinstance(reasons, list):
        reasons = [str(reasons)] if reasons else []
    return {
        "subject": subject,
        "confidence": confidence,
        "scores": rule_metadata.get("scores", {}).copy(),
        "reasons": [f"llm:{str(item).strip()}" for item in reasons if str(item).strip()][:8] or ["llm:fallback"],
        "text_excerpt": rule_metadata.get("text_excerpt", ""),
        "normalized_text": rule_metadata.get("normalized_text", ""),
        "route": "llm_fallback",
        "rule_subject": rule_metadata.get("subject"),
        "rule_confidence": rule_metadata.get("confidence"),
        "rule_reasons": list(rule_metadata.get("reasons") or []),
        "llm_usage": response.get("_llm_usage"),
        "llm_elapsed_seconds": response.get("_llm_elapsed_seconds"),
        "llm_endpoint_name": response.get("_llm_endpoint_name"),
        "llm_request_mode": response.get("_llm_request_mode"),
    }


def build_llm_client(args: argparse.Namespace) -> Any:
    if not args.llm_fallback:
        return None
    if OpenAICompatibleClient is None or ModelEndpointConfig is None:
        return None
    settings = resolve_llm_endpoint_settings(args)
    if not settings["api_key"]:
        return None
    config = ModelEndpointConfig(
        name="ai2d-subject-fallback",
        base_url=settings["base_url"],
        api_key=settings["api_key"],
        model=settings["model"],
        reasoning_effort=settings["reasoning_effort"],
        temperature=settings["temperature"],
        timeout_seconds=settings["timeout_seconds"],
        enabled=True,
    )
    return OpenAICompatibleClient(config)


def classify_sample(sample: Dict[str, Any], client: Any = None, llm_budget: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
    rule_metadata = rule_classify_sample(sample)
    if not should_use_llm_fallback(rule_metadata):
        return rule_metadata
    if client is None:
        return rule_metadata
    if llm_budget is not None:
        used = int(llm_budget.get("used", 0))
        max_calls = int(llm_budget.get("max_calls", 0))
        if max_calls > 0 and used >= max_calls:
            return rule_metadata
    llm_metadata = llm_classify_sample(sample, rule_metadata, client)
    if llm_metadata is None:
        return rule_metadata
    if llm_budget is not None:
        llm_budget["used"] = int(llm_budget.get("used", 0)) + 1
    return llm_metadata


def current_subject(sample: Dict[str, Any]) -> str:
    for block_name in SUBJECT_FIELDS + ["candidate_problem_record"]:
        block = sample.get(block_name) or {}
        subject = pick_first_nonempty(block.get("subject"))
        if subject:
            return subject
    return ""


def apply_subject(sample: Dict[str, Any], subject: str, metadata: Dict[str, Any], set_other: bool) -> bool:
    should_write = subject in {"biology", "geography"} or (set_other and subject == "other")
    sample["subject_tagging_record"] = {
        "version": "ai2d_subject_rules_v3_llm_fallback",
        "predicted_subject": metadata["subject"],
        "confidence": metadata["confidence"],
        "scores": metadata["scores"],
        "reasons": metadata["reasons"],
        "route": metadata.get("route", "rules"),
    }
    if metadata.get("route") == "llm_fallback":
        sample["subject_tagging_record"]["rule_subject"] = metadata.get("rule_subject")
        sample["subject_tagging_record"]["rule_confidence"] = metadata.get("rule_confidence")
        sample["subject_tagging_record"]["rule_reasons"] = metadata.get("rule_reasons")
        if metadata.get("llm_usage") is not None:
            sample["subject_tagging_record"]["llm_usage"] = metadata.get("llm_usage")
        if metadata.get("llm_elapsed_seconds") is not None:
            sample["subject_tagging_record"]["llm_elapsed_seconds"] = metadata.get("llm_elapsed_seconds")
        if metadata.get("llm_endpoint_name") is not None:
            sample["subject_tagging_record"]["llm_endpoint_name"] = metadata.get("llm_endpoint_name")
        if metadata.get("llm_request_mode") is not None:
            sample["subject_tagging_record"]["llm_request_mode"] = metadata.get("llm_request_mode")
    if not should_write:
        return False
    for block_name in SUBJECT_FIELDS:
        block = sample.get(block_name)
        if isinstance(block, dict):
            block["subject"] = subject
    return True


def preview_row(sample_path: Path, sample: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    problem_main = sample.get("problem_main_record") or {}
    clean = sample.get("clean_problem_record") or {}
    source = sample.get("source_intake_record") or {}
    question = pick_first_nonempty(
        clean.get("normalized_question_text"),
        problem_main.get("normalized_question_text"),
        source.get("raw_question_text"),
    )
    return {
        "sample": sample_path.name,
        "source_problem_id": pick_first_nonempty(
            problem_main.get("source_problem_id"),
            clean.get("source_problem_id"),
            source.get("source_problem_id"),
            sample_path.stem,
        ),
        "current_subject": current_subject(sample),
        "predicted_subject": metadata["subject"],
        "confidence": metadata["confidence"],
        "scores": metadata["scores"],
        "reasons": metadata["reasons"],
        "route": metadata.get("route", "rules"),
        "rule_subject": metadata.get("rule_subject"),
        "question": question[:180],
    }


def iter_sample_paths(dataset_root: Path, limit: int) -> List[Path]:
    sample_paths = sorted((dataset_root / "samples").glob("*.json"))
    if limit > 0:
        sample_paths = sample_paths[:limit]
    return sample_paths


def main() -> None:
    args = parse_args()
    dataset_root = Path(args.dataset_root)
    sample_paths = iter_sample_paths(dataset_root, args.limit)
    llm_settings = resolve_llm_endpoint_settings(args)
    llm_client = build_llm_client(args)
    llm_budget = {"used": 0, "max_calls": max(0, int(args.llm_max_calls))}

    counts = {"biology": 0, "geography": 0, "other": 0}
    route_counts = {"rules": 0, "llm_fallback": 0}
    updated = 0
    preview: List[Dict[str, Any]] = []

    for sample_path in sample_paths:
        sample = read_json(sample_path)
        metadata = classify_sample(sample, client=llm_client, llm_budget=llm_budget)
        counts[metadata["subject"]] = counts.get(metadata["subject"], 0) + 1
        route = metadata.get("route", "rules")
        route_counts[route] = route_counts.get(route, 0) + 1
        wrote_subject = apply_subject(sample, metadata["subject"], metadata, args.set_other)
        if args.write and wrote_subject:
            write_json(sample_path, sample)
            updated += 1
        if len(preview) < args.preview:
            preview.append(preview_row(sample_path, sample, metadata))

    result = {
        "dataset_root": dataset_root.as_posix(),
        "sample_count": len(sample_paths),
        "write": bool(args.write),
        "set_other": bool(args.set_other),
        "llm_fallback": bool(args.llm_fallback),
        "llm_client_enabled": llm_client is not None,
        "llm_config_source": llm_settings["config_source"],
        "llm_base_url": llm_settings["base_url"],
        "llm_model": llm_settings["model"],
        "llm_calls_used": llm_budget["used"],
        "llm_calls_max": llm_budget["max_calls"],
        "updated": updated,
        "counts": counts,
        "route_counts": route_counts,
        "preview": preview,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
