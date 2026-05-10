#!/usr/bin/env python3
from __future__ import annotations

import argparse
import dataclasses
import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
DEFAULT_DATASET_ROOT = PROJECT_ROOT / "ready" / "ai2d"
DEFAULT_PIPELINE2_CONFIG_PATH = SRC_ROOT / "benchmarkallinone" / "pipeline2" / "configs" / "default_pipeline2.yaml"
TAGGING_VERSION = "ai2d_subject_rules_v5_bio_geo_other"
SUBJECT_LABELS = [
    "biology",
    "geography",
    "other",
]
CONCRETE_SUBJECTS = set(SUBJECT_LABELS) - {"other"}
SUBJECT_DISPLAY_NAMES = {
    "biology": "生物",
    "geography": "地理",
    "other": "其他/证据不足",
}

if SRC_ROOT.exists():
    sys.path.insert(0, str(SRC_ROOT))

try:
    from benchmarkallinone.pipeline2.clients import OpenAICompatibleClient
    from benchmarkallinone.pipeline2.config import ModelEndpointConfig, Pipeline2Config
    from benchmarkallinone.pipeline2.utils import env_expand
except Exception:
    OpenAICompatibleClient = None
    ModelEndpointConfig = None
    Pipeline2Config = None
    env_expand = None

BIOLOGY_PATTERNS: Sequence[Tuple[str, str, int]] = [
    ("life cycle", "phrase:life cycle", 5),
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
    ("lizard", "token:lizard", 3),
    ("lizards", "token:lizards", 3),
    ("snake", "token:snake", 3),
    ("rabbit", "token:rabbit", 3),
    ("deer", "token:deer", 3),
    ("coyote", "token:coyote", 3),
    ("grasshopper", "token:grasshopper", 3),
    ("cockroach", "token:cockroach", 3),
    ("house fly", "phrase:house fly", 4),
    ("fly", "token:fly", 2),
    ("bacteria", "token:bacteria", 3),
    ("fungi", "token:fungi", 3),
    ("dna", "token:dna", 3),
    ("gene", "token:gene", 3),
    ("genes", "token:genes", 3),
    ("leaf", "token:leaf", 2),
    ("roots", "token:roots", 2),
    ("flower", "token:flower", 2),
    ("egg", "token:egg", 2),
    ("caterpillar", "token:caterpillar", 4),
    ("butterfly", "token:butterfly", 4),
    ("chrysalis", "token:chrysalis", 4),
    ("larva", "token:larva", 4),
    ("nymph", "token:nymph", 4),
    ("nymphs", "token:nymphs", 4),
    ("pupa", "token:pupa", 4),
    ("seed", "token:seed", 3),
    ("seeds", "token:seeds", 3),
    ("herbivore", "token:herbivore", 4),
    ("herbivores", "token:herbivores", 4),
    ("carnivore", "token:carnivore", 4),
    ("carnivores", "token:carnivores", 4),
    ("omnivore", "token:omnivore", 4),
    ("omnivores", "token:omnivores", 4),
    ("algae", "token:algae", 3),
    ("rotifer", "token:rotifer", 3),
    ("centrioles", "token:centrioles", 3),
    ("chloroplast", "token:chloroplast", 4),
    ("mitochondria", "token:mitochondria", 4),
    ("quadriceps", "token:quadriceps", 3),
    ("thigh", "token:thigh", 2),
    ("stomach", "token:stomach", 3),
    ("heart", "token:heart", 3),
    ("lung", "token:lung", 3),
    ("lungs", "token:lungs", 3),
    ("brain", "token:brain", 3),
    ("cerebrum", "token:cerebrum", 4),
    ("cerebellum", "token:cerebellum", 4),
    ("hypothalamus", "token:hypothalamus", 4),
    ("brain stem", "phrase:brain stem", 4),
    ("pancreas", "token:pancreas", 4),
    ("liver", "token:liver", 3),
    ("pharynx", "token:pharynx", 3),
    ("oesophagus", "token:oesophagus", 3),
    ("esophagus", "token:esophagus", 3),
    ("pleural space", "phrase:pleural space", 4),
    ("pectoral", "token:pectoral", 3),
    ("pectoralis", "token:pectoralis", 4),
    ("deltoid", "token:deltoid", 3),
    ("bicep", "token:bicep", 3),
    ("biceps", "token:biceps", 3),
    ("chest", "token:chest", 2),
    ("lobe", "token:lobe", 3),
    ("lobes", "token:lobes", 3),
    ("bone", "token:bone", 2),
    ("bones", "token:bones", 2),
    ("muscle", "token:muscle", 2),
    ("muscles", "token:muscles", 2),
    ("tooth", "token:tooth", 2),
    ("teeth", "token:teeth", 2),
    ("canine", "token:canine", 2),
    ("midrib", "token:midrib", 4),
    ("frond", "token:frond", 4),
    ("costa", "token:costa", 4),
    ("stipe", "token:stipe", 4),
    ("panicle", "token:panicle", 4),
    ("raceme", "token:raceme", 4),
    ("ascospore", "token:ascospore", 4),
    ("ascospores", "token:ascospores", 4),
    ("leaflet", "token:leaflet", 3),
    ("leaflets", "token:leaflets", 3),
    ("respiratory", "token:respiratory", 3),
    ("digestive", "token:digestive", 3),
    ("circulatory", "token:circulatory", 3),
    ("skeletal", "token:skeletal", 3),
    ("muscular", "token:muscular", 3),
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
    ("transpiration", "token:transpiration", 4),
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
    ("earth and the sun", "phrase:earth and the sun", 5),
    ("solar system", "phrase:solar system", 5),
    ("new moon", "phrase:new moon", 5),
    ("full moon", "phrase:full moon", 5),
    ("moon phase", "phrase:moon phase", 5),
    ("phase of the moon", "phrase:phase of the moon", 5),
    ("moon", "token:moon", 4),
    ("lunar", "token:lunar", 4),
    ("waxing", "token:waxing", 4),
    ("waning", "token:waning", 4),
    ("gibbous", "token:gibbous", 4),
    ("eclipse", "token:eclipse", 4),
    ("equinox", "token:equinox", 5),
    ("vernal equinox", "phrase:vernal equinox", 6),
    ("spring tide", "phrase:spring tide", 5),
    ("neap tide", "phrase:neap tide", 5),
    ("tide", "token:tide", 3),
    ("tides", "token:tides", 3),
    ("planet", "token:planet", 4),
    ("planets", "token:planets", 4),
    ("orbit", "token:orbit", 3),
    ("star", "token:star", 3),
    ("stars", "token:stars", 3),
    ("constellation", "token:constellation", 4),
    ("sun", "token:sun", 3),
    ("crust", "token:crust", 4),
    ("mantle", "token:mantle", 4),
    ("core", "token:core", 3),
    ("soil", "token:soil", 4),
    ("horizon", "token:horizon", 4),
    ("volcano", "token:volcano", 4),
    ("earthquake", "token:earthquake", 4),
    ("mineral", "token:mineral", 3),
    ("minerals", "token:minerals", 3),
    ("plateau", "token:plateau", 3),
    ("plain", "token:plain", 2),
    ("valley", "token:valley", 2),
    ("coast", "token:coast", 2),
    ("map", "token:map", 2),
    ("delta", "token:delta", 2),
    ("runoff", "token:runoff", 4),
]

OTHER_HINT_PATTERNS: Sequence[Tuple[str, str, int]] = []

CATEGORY_PATTERNS: Dict[str, Sequence[Tuple[str, str, int]]] = {
    "biology": BIOLOGY_PATTERNS,
    "geography": GEOGRAPHY_PATTERNS,
}

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
        "--manifest-out",
        default="",
        help="Optional JSONL path for per-sample subject labels and evidence.",
    )
    parser.add_argument(
        "--summary-out",
        default="",
        help="Optional JSON path for the aggregate result. Default only prints to stdout.",
    )
    parser.add_argument(
        "--split-ready-root",
        default="",
        help=(
            "Optional output root. When set, copy the input ready dataset into one ready-like directory per "
            "predicted subject, e.g. <root>/ai2d_biology, <root>/ai2d_geography, <root>/ai2d_other."
        ),
    )
    parser.add_argument(
        "--split-mode",
        choices=["copy", "manifest-only"],
        default="copy",
        help="How --split-ready-root behaves. copy writes samples/assets; manifest-only writes only split manifests.",
    )
    parser.add_argument(
        "--overwrite-splits",
        action="store_true",
        help="Allow replacing existing ai2d_* split directories under --split-ready-root.",
    )
    parser.add_argument(
        "--set-other",
        action="store_true",
        help="When writing, also write subject=other for uncertain samples. Default only writes concrete subjects.",
    )
    parser.add_argument(
        "--llm-fallback",
        action="store_true",
        help="Call an OpenAI-compatible JSON model after rule classification. Default scope is rule-other only.",
    )
    parser.add_argument(
        "--llm-fallback-scope",
        choices=["other", "uncertain"],
        default=os.environ.get("AI2D_SUBJECT_LLM_FALLBACK_SCOPE", "other"),
        help=(
            "Which rule outputs should be sent to LLM when --llm-fallback is enabled. "
            "'other' only sends rule-classified other samples; 'uncertain' also sends low-confidence/ambiguous samples."
        ),
    )
    parser.add_argument(
        "--llm-max-calls",
        type=int,
        default=20,
        help="Maximum fallback LLM calls to make in one run when --llm-fallback is enabled (default: 20).",
    )
    parser.add_argument(
        "--llm-prompt-out",
        default="",
        help="Optional JSONL path recording the exact system/user prompts sent to LLM fallback.",
    )
    parser.add_argument(
        "--llm-config",
        default=os.environ.get("AI2D_SUBJECT_PIPELINE2_CONFIG", ""),
        help="Optional pipeline2 YAML config to inherit primary model settings from.",
    )
    parser.add_argument("--llm-base-url", default=os.environ.get("AI2D_SUBJECT_BASE_URL", ""))
    parser.add_argument("--llm-api-key", default=os.environ.get("AI2D_SUBJECT_API_KEY", ""))
    parser.add_argument("--llm-model", default=os.environ.get("AI2D_SUBJECT_MODEL", ""))
    parser.add_argument("--llm-api-mode", default=os.environ.get("AI2D_SUBJECT_API_MODE", ""))
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
    path.parent.mkdir(parents=True, exist_ok=True)
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


def load_env_file(path: Path) -> Dict[str, str]:
    env_map: Dict[str, str] = {}
    if not path.exists():
        return env_map
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        env_map[key] = value
    return env_map


def resolve_pipeline2_primary_config(config_path: str) -> Tuple[Optional[Any], Optional[str], Dict[str, str]]:
    if Pipeline2Config is None:
        return None, None, {}
    candidate_paths: List[Path] = []
    if config_path:
        candidate_paths.append(Path(config_path))
    if DEFAULT_PIPELINE2_CONFIG_PATH.exists():
        candidate_paths.append(DEFAULT_PIPELINE2_CONFIG_PATH)
    for candidate in candidate_paths:
        try:
            file_env_map = load_env_file(candidate.parent / "pipeline2.local.env")
            env_map = {**file_env_map, **os.environ}
            with candidate.open("r", encoding="utf-8") as file:
                raw = yaml.safe_load(file) or {}
            expanded = env_expand(raw, env_map) if env_expand is not None else raw
            config = Pipeline2Config.from_dict(expanded)
            return config.models.primary, str(candidate), file_env_map
        except Exception:
            continue
    return None, None, {}


def resolve_llm_endpoint_settings(args: argparse.Namespace) -> Dict[str, Any]:
    inherited_config, inherited_source, pipeline2_env = resolve_pipeline2_primary_config(args.llm_config)

    base_url = first_present(
        args.llm_base_url,
        getattr(inherited_config, "base_url", None),
        pipeline2_env.get("ANNOTATION_API_BASE_URL"),
        os.environ.get("ANNOTATION_API_BASE_URL"),
        os.environ.get("PIPELINE2_BASE_URL_PRIMARY"),
        os.environ.get("OPENAI_BASE_URL"),
        "https://synai996.space/v1",
    )
    api_key = first_present(
        args.llm_api_key,
        getattr(inherited_config, "api_key", None),
        pipeline2_env.get("ANNOTATION_API_KEY"),
        os.environ.get("ANNOTATION_API_KEY"),
        os.environ.get("PIPELINE2_API_KEY_PRIMARY"),
        os.environ.get("OPENAI_API_KEY"),
        "",
    )
    model = first_present(
        args.llm_model,
        getattr(inherited_config, "model", None),
        pipeline2_env.get("ANNOTATION_MODEL"),
        os.environ.get("ANNOTATION_MODEL"),
        "gpt-5.4",
    )
    api_mode = first_present(
        args.llm_api_mode,
        getattr(inherited_config, "wire_api", None),
        getattr(inherited_config, "api_mode", None) if getattr(inherited_config, "api_mode", None) != "chat_completions" else None,
        pipeline2_env.get("ANNOTATION_API_MODE"),
        os.environ.get("ANNOTATION_API_MODE"),
        os.environ.get("PIPELINE2_WIRE_API_PRIMARY"),
        os.environ.get("PIPELINE2_API_MODE_PRIMARY"),
        os.environ.get("OPENAI_API_MODE"),
        "responses",
    )
    reasoning_effort = first_present(
        args.llm_reasoning_effort,
        getattr(inherited_config, "reasoning_effort", None),
        pipeline2_env.get("ANNOTATION_REASONING_EFFORT"),
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
        "api_mode": str(api_mode),
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


def category_scores(text: str) -> Tuple[Dict[str, int], Dict[str, List[str]]]:
    scores: Dict[str, int] = {}
    reasons: Dict[str, List[str]] = {}
    for subject, patterns in CATEGORY_PATTERNS.items():
        score, subject_reasons = score_patterns(text, patterns)
        scores[subject] = score
        reasons[subject] = subject_reasons
    other_score, other_reasons = score_patterns(text, OTHER_HINT_PATTERNS)
    scores["other"] = other_score
    reasons["other"] = other_reasons
    return scores, reasons


def choose_subject(scores: Dict[str, int], reasons_by_subject: Dict[str, List[str]]) -> Tuple[str, str, List[str]]:
    biology_score = int(scores.get("biology", 0) or 0)
    geography_score = int(scores.get("geography", 0) or 0)
    other_score = int(scores.get("other", 0) or 0)
    best_subject = "biology" if biology_score >= geography_score else "geography"
    best_score = max(biology_score, geography_score)
    second_score = min(biology_score, geography_score)

    if best_score >= 5 and best_score >= second_score + 2:
        confidence = "high" if best_score >= 8 and best_score >= second_score + 4 else "medium"
        return best_subject, confidence, reasons_by_subject.get(best_subject, [])[:8]

    if best_score >= 4 and best_score > other_score and best_score >= second_score + 3:
        return best_subject, "medium", reasons_by_subject.get(best_subject, [])[:8]

    if best_score >= 3 and second_score == 0 and best_score > other_score:
        return best_subject, "low", reasons_by_subject.get(best_subject, [])[:8]

    return "other", "low" if other_score == 0 else "medium", (reasons_by_subject.get("other") or ["fallback:uncertain-subject"])[:8]


def rule_classify_sample(sample: Dict[str, Any]) -> Dict[str, Any]:
    text_parts = gather_sample_texts(sample)
    normalized = normalize_text(text_parts)
    scores, reasons_by_subject = category_scores(normalized)
    subject, confidence, reasons = choose_subject(scores, reasons_by_subject)

    return {
        "subject": subject,
        "subject_display_name": SUBJECT_DISPLAY_NAMES.get(subject, subject),
        "confidence": confidence,
        "scores": scores,
        "reasons": reasons[:8],
        "text_excerpt": normalized[:240],
        "normalized_text": normalized,
        "route": "rules",
    }


def should_use_llm_fallback(rule_metadata: Dict[str, Any], scope: str = "other") -> bool:
    scores = rule_metadata.get("scores") or {}
    biology_score = int(scores.get("biology", 0) or 0)
    geography_score = int(scores.get("geography", 0) or 0)
    best_score = max(biology_score, geography_score)
    second_score = min(biology_score, geography_score)
    other_score = int(scores.get("other", 0) or 0)
    subject = rule_metadata.get("subject")
    confidence = rule_metadata.get("confidence")
    reasons = rule_metadata.get("reasons") or []

    if subject == "other":
        return True
    if scope != "uncertain":
        return False
    if confidence == "low":
        return True
    if "fallback:uncertain-subject" in reasons or "fallback:non-bio-geo" in reasons:
        return True
    if best_score >= 2 and best_score - second_score <= 1:
        return True
    if other_score >= best_score and best_score >= 2:
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
        "task": "Classify this AI2D science diagram question into exactly one of: biology, geography, other.",
        "policy": {
            "labels": SUBJECT_LABELS,
            "label_meanings": SUBJECT_DISPLAY_NAMES,
            "biology_includes": ["organisms", "food webs", "life cycles", "cells", "human body/anatomy"],
            "geography_includes": ["maps", "landforms", "water/rock cycles", "weather/climate", "earth structure", "astronomy/moon phases/solar system"],
            "use_other_when": ["physics", "chemistry", "engineering", "generic visual label lookup with insufficient biology/geography evidence"],
            "do_not_overcall": "Prefer other when evidence for biology or geography is weak.",
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
            "subject": "|".join(SUBJECT_LABELS),
            "confidence": "high|medium|low",
            "reasons": ["short reason strings"],
        },
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def build_llm_system_prompt() -> str:
    return (
        "You classify AI2D science diagram questions into exactly one of biology, geography, or other. "
        "Return exactly one JSON object with keys subject, confidence, reasons. "
        "Use geography for earth science, maps, weather, geology, astronomy, moon phases, and solar system. "
        "Use biology for organisms, ecology, life cycles, cells, and human anatomy. "
        "Use other for physics, chemistry, engineering, or generic label-lookup questions with insufficient evidence."
    )


def build_llm_prompt_record(sample_path: Optional[Path], sample: Dict[str, Any], rule_metadata: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "sample": sample_path.name if sample_path is not None else "",
        "problem_id": current_problem_id(sample, sample_path) if sample_path is not None else "",
        "source_problem_id": current_source_problem_id(sample, sample_path) if sample_path is not None else "",
        "rule_subject": rule_metadata.get("subject"),
        "rule_confidence": rule_metadata.get("confidence"),
        "rule_scores": rule_metadata.get("scores"),
        "rule_reasons": rule_metadata.get("reasons"),
        "system_prompt": build_llm_system_prompt(),
        "user_prompt": build_llm_user_prompt(sample, rule_metadata),
    }


def llm_classify_sample(sample: Dict[str, Any], rule_metadata: Dict[str, Any], client: Any) -> Optional[Dict[str, Any]]:
    if client is None:
        return None
    response = client.chat_json(build_llm_system_prompt(), build_llm_user_prompt(sample, rule_metadata))
    if not isinstance(response, dict):
        return None
    subject = str(response.get("subject", "")).strip().lower()
    confidence = str(response.get("confidence", "")).strip().lower()
    reasons = response.get("reasons") or []
    if subject not in set(SUBJECT_LABELS):
        return None
    if confidence not in {"high", "medium", "low"}:
        confidence = "medium"
    if not isinstance(reasons, list):
        reasons = [str(reasons)] if reasons else []
    return {
        "subject": subject,
        "subject_display_name": SUBJECT_DISPLAY_NAMES.get(subject, subject),
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
    config_kwargs = {
        "name": "ai2d-subject-fallback",
        "base_url": settings["base_url"],
        "api_key": settings["api_key"],
        "model": settings["model"],
        "reasoning_effort": settings["reasoning_effort"],
        "temperature": settings["temperature"],
        "timeout_seconds": settings["timeout_seconds"],
        "enabled": True,
    }
    if dataclasses.is_dataclass(ModelEndpointConfig):
        field_names = {field.name for field in dataclasses.fields(ModelEndpointConfig)}
        if "wire_api" in field_names:
            config_kwargs["wire_api"] = settings["api_mode"]
        elif "api_mode" in field_names:
            config_kwargs["api_mode"] = settings["api_mode"]
        config_kwargs = {key: value for key, value in config_kwargs.items() if key in field_names}
    else:
        config_kwargs["api_mode"] = settings["api_mode"]
    config = ModelEndpointConfig(**config_kwargs)
    return OpenAICompatibleClient(config)


def classify_sample(
    sample: Dict[str, Any],
    client: Any = None,
    llm_budget: Optional[Dict[str, int]] = None,
    llm_fallback_scope: str = "other",
    sample_path: Optional[Path] = None,
    llm_prompt_rows: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    rule_metadata = rule_classify_sample(sample)
    if not should_use_llm_fallback(rule_metadata, scope=llm_fallback_scope):
        return rule_metadata
    if client is None:
        return rule_metadata
    if llm_budget is not None:
        used = int(llm_budget.get("used", 0))
        max_calls = int(llm_budget.get("max_calls", 0))
        if max_calls > 0 and used >= max_calls:
            return rule_metadata
        llm_budget["attempted"] = int(llm_budget.get("attempted", 0)) + 1
    if llm_prompt_rows is not None:
        llm_prompt_rows.append(build_llm_prompt_record(sample_path, sample, rule_metadata))
    llm_metadata = llm_classify_sample(sample, rule_metadata, client)
    if llm_metadata is None:
        if llm_budget is not None:
            llm_budget["failed"] = int(llm_budget.get("failed", 0)) + 1
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


def current_problem_id(sample: Dict[str, Any], sample_path: Path) -> str:
    for block_name in ["problem_main_record", "clean_problem_record", "normalization_record", "source_intake_record"]:
        block = sample.get(block_name) or {}
        problem_id = pick_first_nonempty(block.get("problem_id"))
        if problem_id:
            return problem_id
    return sample_path.stem


def current_source_problem_id(sample: Dict[str, Any], sample_path: Path) -> str:
    for block_name in ["problem_main_record", "clean_problem_record", "normalization_record", "source_intake_record"]:
        block = sample.get(block_name) or {}
        source_problem_id = pick_first_nonempty(block.get("source_problem_id"))
        if source_problem_id:
            return source_problem_id
    return current_problem_id(sample, sample_path)


def sample_question(sample: Dict[str, Any]) -> str:
    problem_main = sample.get("problem_main_record") or {}
    clean = sample.get("clean_problem_record") or {}
    source = sample.get("source_intake_record") or {}
    return pick_first_nonempty(
        clean.get("normalized_question_text"),
        problem_main.get("normalized_question_text"),
        source.get("raw_question_text"),
    )


def sample_answer(sample: Dict[str, Any]) -> str:
    problem_main = sample.get("problem_main_record") or {}
    clean = sample.get("clean_problem_record") or {}
    source = sample.get("source_intake_record") or {}
    return pick_first_nonempty(
        clean.get("normalized_answer_text"),
        problem_main.get("normalized_answer_text"),
        source.get("raw_answer_text"),
    )


def add_subject_tagging_record(sample: Dict[str, Any], metadata: Dict[str, Any]) -> None:
    sample["subject_tagging_record"] = {
        "version": TAGGING_VERSION,
        "predicted_subject": metadata["subject"],
        "predicted_subject_display_name": metadata.get("subject_display_name", SUBJECT_DISPLAY_NAMES.get(metadata["subject"], metadata["subject"])),
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


def set_subject_fields(sample: Dict[str, Any], subject: str) -> None:
    for block_name in SUBJECT_FIELDS:
        block = sample.get(block_name)
        if isinstance(block, dict):
            block["subject"] = subject


def apply_subject(sample: Dict[str, Any], subject: str, metadata: Dict[str, Any], set_other: bool) -> bool:
    should_write = subject in CONCRETE_SUBJECTS or (set_other and subject == "other")
    add_subject_tagging_record(sample, metadata)
    if not should_write:
        return False
    set_subject_fields(sample, subject)
    return True


def preview_row(sample_path: Path, sample: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "sample": sample_path.name,
        "problem_id": current_problem_id(sample, sample_path),
        "source_problem_id": current_source_problem_id(sample, sample_path),
        "current_subject": current_subject(sample),
        "predicted_subject": metadata["subject"],
        "predicted_subject_display_name": metadata.get("subject_display_name", SUBJECT_DISPLAY_NAMES.get(metadata["subject"], metadata["subject"])),
        "confidence": metadata["confidence"],
        "scores": metadata["scores"],
        "reasons": metadata["reasons"],
        "route": metadata.get("route", "rules"),
        "rule_subject": metadata.get("rule_subject"),
        "question": sample_question(sample)[:180],
    }


def iter_sample_paths(dataset_root: Path, limit: int) -> List[Path]:
    sample_paths = sorted((dataset_root / "samples").glob("*.json"))
    if limit > 0:
        sample_paths = sample_paths[:limit]
    return sample_paths


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def manifest_row(sample_path: Path, sample: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    row = preview_row(sample_path, sample, metadata)
    row["answer"] = sample_answer(sample)[:180]
    row["text_excerpt"] = metadata.get("text_excerpt", "")
    return row


def rewrite_canonical_fields_for_split(sample: Dict[str, Any], dataset_key: str, sample_id: str, sample_index: int, images: List[str]) -> None:
    sample["canonical_dataset_key"] = dataset_key
    sample["canonical_sample_id"] = sample_id
    sample["canonical_sample_index"] = sample_index
    sample["sample_path"] = f"samples/{sample_id}.json"
    if images:
        sample["image_path"] = images[0]
        sample["images"] = images
    elif "image_path" in sample:
        sample.pop("image_path", None)
        sample["images"] = []


def relative_paths_from_sample(sample: Dict[str, Any], key: str) -> List[str]:
    values: List[str] = []
    raw = sample.get(key)
    if isinstance(raw, str) and raw.strip():
        values.append(raw.strip())
    elif isinstance(raw, list):
        for item in raw:
            if isinstance(item, str) and item.strip():
                values.append(item.strip())
    return values


def copy_if_exists(src_root: Path, dst_root: Path, relative_path: str) -> str:
    rel = Path(relative_path)
    src = src_root / rel
    dst = dst_root / rel
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    return rel.as_posix()


def build_split_ready_dirs(dataset_root: Path, split_root: Path, rows: List[Dict[str, Any]], overwrite: bool, split_mode: str) -> Dict[str, Any]:
    split_root.mkdir(parents=True, exist_ok=True)
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(str(row["predicted_subject"]), []).append(row)

    stats: Dict[str, Any] = {}
    sample_by_name = {Path(row["sample"]).name: row for row in rows}
    for subject, subject_rows in sorted(grouped.items()):
        dataset_key = f"ai2d_{subject}"
        dst_root = split_root / dataset_key
        if dst_root.exists():
            if not overwrite:
                raise FileExistsError(f"{dst_root} already exists; pass --overwrite-splits to replace it")
            shutil.rmtree(dst_root)
        dst_root.mkdir(parents=True, exist_ok=True)

        written_samples = 0
        split_manifest_rows: List[Dict[str, Any]] = []
        if split_mode == "copy":
            for sample_index, row in enumerate(subject_rows):
                src_sample_path = dataset_root / "samples" / row["sample"]
                sample = read_json(src_sample_path)
                sample_id = f"{dataset_key}{sample_index:05d}"

                image_paths = relative_paths_from_sample(sample, "images")
                if not image_paths:
                    image_paths = relative_paths_from_sample(sample, "image_path")
                copied_images = [copy_if_exists(dataset_root, dst_root, path) for path in image_paths]

                split_metadata = {
                    "subject": subject,
                    "subject_display_name": SUBJECT_DISPLAY_NAMES.get(subject, subject),
                    "confidence": row.get("confidence", ""),
                    "scores": row.get("scores", {}),
                    "reasons": row.get("reasons", []),
                    "route": row.get("route", "rules"),
                    "rule_subject": row.get("rule_subject"),
                }
                add_subject_tagging_record(sample, split_metadata)
                set_subject_fields(sample, subject)
                rewrite_canonical_fields_for_split(sample, dataset_key, sample_id, sample_index, copied_images)
                write_json(dst_root / "samples" / f"{sample_id}.json", sample)

                split_row = dict(row)
                split_row.update(
                    {
                        "canonical_dataset_key": dataset_key,
                        "canonical_sample_id": sample_id,
                        "canonical_sample_index": sample_index,
                        "sample_path": f"samples/{sample_id}.json",
                        "image_paths": copied_images,
                    }
                )
                split_manifest_rows.append(split_row)
                written_samples += 1
        else:
            split_manifest_rows = [dict(row) for row in subject_rows]

        write_jsonl(dst_root / "ai2d_subject_manifest.jsonl", split_manifest_rows)
        write_json(
            dst_root / "summary.json",
            {
                "dataset_key": dataset_key,
                "parent_dataset_root": dataset_root.as_posix(),
                "subject": subject,
                "subject_display_name": SUBJECT_DISPLAY_NAMES.get(subject, subject),
                "sample_count": len(subject_rows),
                "written_sample_file_count": written_samples,
                "split_mode": split_mode,
                "tagging_version": TAGGING_VERSION,
            },
        )
        stats[subject] = {
            "dataset_key": dataset_key,
            "dataset_root": dst_root.as_posix(),
            "sample_count": len(subject_rows),
            "written_sample_file_count": written_samples,
        }

    if sample_by_name:
        write_json(
            split_root / "ai2d_subject_split_summary.json",
            {
                "parent_dataset_root": dataset_root.as_posix(),
                "split_root": split_root.as_posix(),
                "tagging_version": TAGGING_VERSION,
                "subjects": stats,
            },
        )
    return stats


def main() -> None:
    args = parse_args()
    dataset_root = Path(args.dataset_root)
    sample_paths = iter_sample_paths(dataset_root, args.limit)
    llm_settings = resolve_llm_endpoint_settings(args)
    llm_client = build_llm_client(args)
    llm_budget = {"used": 0, "attempted": 0, "failed": 0, "max_calls": max(0, int(args.llm_max_calls))}

    counts = {subject: 0 for subject in SUBJECT_LABELS}
    confidence_counts: Dict[str, int] = {}
    route_counts = {"rules": 0, "llm_fallback": 0}
    updated = 0
    preview: List[Dict[str, Any]] = []
    manifest_rows: List[Dict[str, Any]] = []
    llm_prompt_rows: List[Dict[str, Any]] = []

    for sample_path in sample_paths:
        sample = read_json(sample_path)
        metadata = classify_sample(
            sample,
            client=llm_client,
            llm_budget=llm_budget,
            llm_fallback_scope=args.llm_fallback_scope,
            sample_path=sample_path,
            llm_prompt_rows=llm_prompt_rows,
        )
        counts[metadata["subject"]] = counts.get(metadata["subject"], 0) + 1
        confidence_counts[metadata["confidence"]] = confidence_counts.get(metadata["confidence"], 0) + 1
        route = metadata.get("route", "rules")
        route_counts[route] = route_counts.get(route, 0) + 1
        row = manifest_row(sample_path, sample, metadata)
        wrote_subject = apply_subject(sample, metadata["subject"], metadata, args.set_other)
        if args.write and wrote_subject:
            write_json(sample_path, sample)
            updated += 1
        manifest_rows.append(row)
        if len(preview) < args.preview:
            preview.append(row)

    split_stats: Dict[str, Any] = {}
    if args.manifest_out:
        write_jsonl(Path(args.manifest_out), manifest_rows)
    if args.llm_prompt_out:
        write_jsonl(Path(args.llm_prompt_out), llm_prompt_rows)
    if args.split_ready_root:
        split_stats = build_split_ready_dirs(
            dataset_root=dataset_root,
            split_root=Path(args.split_ready_root),
            rows=manifest_rows,
            overwrite=bool(args.overwrite_splits),
            split_mode=args.split_mode,
        )

    result = {
        "dataset_root": dataset_root.as_posix(),
        "sample_count": len(sample_paths),
        "tagging_version": TAGGING_VERSION,
        "classification_labels": SUBJECT_LABELS,
        "classification_policy": {
            "biology": "organisms, ecology, life cycles, cells, and human anatomy",
            "geography": "maps, landforms, water/rock cycles, weather/climate, earth structure, astronomy/moon phases/solar system",
            "other": "physics, chemistry, engineering, or insufficient biology/geography evidence",
        },
        "write": bool(args.write),
        "set_other": bool(args.set_other),
        "manifest_out": args.manifest_out,
        "summary_out": args.summary_out,
        "split_ready_root": args.split_ready_root,
        "split_mode": args.split_mode,
        "llm_fallback": bool(args.llm_fallback),
        "llm_fallback_scope": args.llm_fallback_scope,
        "llm_prompt_out": args.llm_prompt_out,
        "llm_client_enabled": llm_client is not None,
        "llm_config_source": llm_settings["config_source"],
        "llm_base_url": llm_settings["base_url"],
        "llm_model": llm_settings["model"],
        "llm_api_mode": llm_settings["api_mode"],
        "llm_calls_used": llm_budget["used"],
        "llm_calls_attempted": llm_budget["attempted"],
        "llm_calls_failed": llm_budget["failed"],
        "llm_calls_max": llm_budget["max_calls"],
        "llm_prompt_count": len(llm_prompt_rows),
        "updated": updated,
        "counts": counts,
        "confidence_counts": confidence_counts,
        "route_counts": route_counts,
        "subject_display_names": SUBJECT_DISPLAY_NAMES,
        "split_stats": split_stats,
        "preview": preview,
    }
    if args.summary_out:
        write_json(Path(args.summary_out), result)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
