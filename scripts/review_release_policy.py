from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

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
