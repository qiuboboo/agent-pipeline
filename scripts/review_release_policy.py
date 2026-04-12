from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY_CONFIG = PROJECT_ROOT / "configs" / "review_release_policies.yaml"


def load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"yaml root must be a mapping: {path}")
    return data


def resolve_project_path(raw: str | Path) -> Path:
    path = raw if isinstance(raw, Path) else Path(raw)
    return path if path.is_absolute() else PROJECT_ROOT / path


def normalize_reason_list(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(x) for x in value if str(x)]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def format_reason_rule(selection: Dict[str, Any] | None) -> str:
    if not selection:
        return "未配置 reason-code 匹配规则"
    match_mode = str(selection.get("match_mode") or "exact_set")
    expected = normalize_reason_list(selection.get("decision_reason_codes"))
    encoded = json.dumps(expected, ensure_ascii=False)
    if match_mode == "exact":
        return f"exact `clean_decision_reason_codes == {encoded}`"
    if match_mode == "exact_set":
        return f"exact reason-code set == `{encoded}`"
    if match_mode == "contains_all":
        return f"contains all reason codes in `{encoded}`"
    if match_mode == "any_of":
        return f"contains any reason code in `{encoded}`"
    return f"{match_mode} `{encoded}`"


def matches_selection(actual: List[str], selection: Dict[str, Any] | None) -> bool:
    if not selection:
        return True
    expected = normalize_reason_list(selection.get("decision_reason_codes"))
    match_mode = str(selection.get("match_mode") or "exact_set")
    if match_mode == "exact":
        return actual == expected
    if match_mode == "exact_set":
        return len(actual) == len(expected) and sorted(actual) == sorted(expected)
    if match_mode == "contains_all":
        return set(expected).issubset(set(actual))
    if match_mode == "any_of":
        return bool(set(expected) & set(actual))
    raise ValueError(f"unsupported match_mode: {match_mode}")


def load_review_release_policy_config(path: Path | None = None) -> Dict[str, Any]:
    config_path = path or DEFAULT_POLICY_CONFIG
    if not config_path.exists():
        return {}
    return load_yaml(config_path)


def get_review_release_datasets(path: Path | None = None) -> Dict[str, Any]:
    policy_root = load_review_release_policy_config(path)
    review_release = policy_root.get("review_release") or {}
    return review_release.get("datasets") or {}


def get_dataset_policy(dataset_key: str, path: Path | None = None) -> Dict[str, Any]:
    datasets = get_review_release_datasets(path)
    return datasets.get(dataset_key) or {}


def get_dataset_root_from_policy(dataset_key: str, path: Path | None = None) -> Path | None:
    dataset_policy = get_dataset_policy(dataset_key, path)
    raw = dataset_policy.get("dataset_root")
    if not raw:
        return None
    return resolve_project_path(raw)


def infer_rule_type(rule_cfg: Dict[str, Any] | None) -> str:
    cfg = rule_cfg or {}
    if cfg.get("rule_type"):
        return str(cfg.get("rule_type"))
    if cfg.get("selection"):
        return "structured_selection"
    if cfg.get("selection_notes") or cfg.get("candidate_key"):
        return "explicit_candidate_subset"
    return "structured_selection"


def normalize_bucket_rule(
    dataset_cfg: Dict[str, Any],
    bucket_key: str,
    *,
    defaults: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    defaults = defaults or {}
    bucket_cfg = (dataset_cfg.get("release_buckets") or {}).get(bucket_key) or {}
    if not bucket_cfg:
        review_rules = dataset_cfg.get("review_release_rules") or {}
        explicit_rules = dataset_cfg.get("explicit_release_rules") or {}
        bucket_cfg = review_rules.get(bucket_key) or explicit_rules.get(bucket_key) or {}
    if not bucket_cfg:
        return {}

    adjacent_cfg = bucket_cfg.get("adjacent_observation") or {}
    rule_type = infer_rule_type(bucket_cfg)
    adjacent_rule_type = infer_rule_type(adjacent_cfg) if adjacent_cfg else ""

    return {
        "bucket_key": bucket_key,
        "enabled": bucket_cfg.get("enabled", True),
        "rule_type": rule_type,
        "candidate_key": str(bucket_cfg.get("candidate_key") or f"{bucket_key}_candidates"),
        "selection": bucket_cfg.get("selection") or None,
        "selection_notes": str(bucket_cfg.get("selection_notes") or ""),
        "policy_doc": str(bucket_cfg.get("policy_doc") or dataset_cfg.get("policy_doc") or ""),
        "release_basis": str(bucket_cfg.get("release_basis") or ""),
        "approved_via": str(bucket_cfg.get("approved_via") or dataset_cfg.get("approved_via") or defaults.get("approved_via") or "user_confirmed_chat_policy"),
        "pass_decision_reason_codes": normalize_reason_list(bucket_cfg.get("pass_decision_reason_codes")),
        "adjacent_key": str(adjacent_cfg.get("candidate_key") or ""),
        "adjacent_label": str(adjacent_cfg.get("label") or defaults.get("adjacent_label") or "adjacent bucket"),
        "adjacent_rule_type": adjacent_rule_type,
        "adjacent_selection": adjacent_cfg.get("selection") or None,
        "adjacent_selection_notes": str(adjacent_cfg.get("selection_notes") or ""),
    }


def format_rule_summary(rule_type: str, selection: Dict[str, Any] | None, selection_notes: str = "") -> str:
    if rule_type == "explicit_candidate_subset":
        return selection_notes or "explicit candidate-json subset"
    return format_reason_rule(selection)


def matches_rule(actual: List[str], rule_type: str, selection: Dict[str, Any] | None) -> bool:
    if rule_type == "explicit_candidate_subset":
        return True
    return matches_selection(actual, selection)


def get_release_bucket_runtime(dataset_key: str, bucket_key: str, path: Path | None = None) -> Dict[str, Any]:
    policy_root = load_review_release_policy_config(path)
    review_release = policy_root.get("review_release") or {}
    defaults = review_release.get("defaults") or {}
    dataset_cfg = (review_release.get("datasets") or {}).get(dataset_key) or {}
    if not dataset_cfg:
        return {}
    runtime = normalize_bucket_rule(dataset_cfg, bucket_key, defaults=defaults)
    if not runtime:
        return {}
    runtime["dataset_key"] = dataset_key
    runtime["dataset_root"] = resolve_project_path(dataset_cfg.get("dataset_root")) if dataset_cfg.get("dataset_root") else None
    return runtime


def iter_dataset_roots(path: Path | None = None) -> Iterable[Path]:
    seen: set[str] = set()
    for _, dataset_policy in (get_review_release_datasets(path) or {}).items():
        raw = dataset_policy.get("dataset_root")
        if not raw:
            continue
        dataset_root = resolve_project_path(raw)
        key = str(dataset_root.resolve()) if dataset_root.exists() else str(dataset_root)
        if key in seen:
            continue
        seen.add(key)
        yield dataset_root
