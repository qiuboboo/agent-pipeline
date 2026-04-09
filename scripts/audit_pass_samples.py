#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "benchmarkallinone" / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from benchmarkallinone.pipeline import (  # noqa: E402
    PipelineConfig,
    canonicalize_answer_text,
    resolve_multiple_choice_answer_text,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit run outputs with emphasis on pass samples.")
    parser.add_argument("--config", default="benchmarkallinone/configs/agent_multidataset_validation_30.yaml")
    parser.add_argument("--run-dir", default="", help="Specific run directory. If omitted, use latest run under config output_root.")
    parser.add_argument("--include-non-pass", action="store_true", help="Audit all samples, not only pass samples.")
    return parser.parse_args()


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def find_latest_run(output_root: Path) -> Path:
    candidates = sorted((path for path in output_root.glob("run_*") if path.is_dir()), key=lambda item: item.stat().st_mtime, reverse=True)
    if not candidates:
        raise FileNotFoundError(f"No run_* directories found under {output_root}")
    return candidates[0]


def build_spec_lookup(config: PipelineConfig) -> Dict[str, Any]:
    lookup: Dict[str, Any] = {}
    for spec in config.datasets:
        lookup[spec.key.lower()] = spec
        lookup[spec.display_name.lower()] = spec
    return lookup


def sample_decision(sample: Dict[str, Any]) -> str:
    clean_problem_record = sample.get("clean_problem_record") or {}
    decision = clean_problem_record.get("clean_decision")
    if decision:
        return str(decision)
    problem_main_record = sample.get("problem_main_record") or {}
    decision = problem_main_record.get("clean_decision")
    if decision:
        return str(decision)
    clean_pool_entries = sample.get("clean_pool_entries") or []
    if clean_pool_entries and isinstance(clean_pool_entries[0], dict):
        decision = clean_pool_entries[0].get("clean_decision")
        if decision:
            return str(decision)
    return "unknown"


def first_rewrite_variant(sample: Dict[str, Any]) -> Dict[str, Any]:
    rewrite_reports = sample.get("rewrite_reports") or []
    if not rewrite_reports or not isinstance(rewrite_reports[0], dict):
        return {}
    variants = rewrite_reports[0].get("variants") or []
    if not variants or not isinstance(variants[0], dict):
        return {}
    return variants[0]


def rewrite_strategy(sample: Dict[str, Any]) -> str:
    rewrite_reports = sample.get("rewrite_reports") or []
    if rewrite_reports and isinstance(rewrite_reports[0], dict):
        return str(rewrite_reports[0].get("strategy") or "unknown")
    return "unknown"


def audit_sample(sample_path: Path, spec_lookup: Dict[str, Any], include_non_pass: bool = False) -> Optional[Dict[str, Any]]:
    sample = read_json(sample_path)
    decision = sample_decision(sample)
    if not include_non_pass and decision != "pass":
        return None

    dataset_key = sample_path.parents[1].name.lower()
    spec = spec_lookup.get(dataset_key)
    source_intake = sample.get("source_intake_record") or {}
    normalization_record = sample.get("normalization_record") or {}
    clean_problem_record = sample.get("clean_problem_record") or {}
    rewrite_reports = sample.get("rewrite_reports") or []
    rewrite_report = rewrite_reports[0] if rewrite_reports and isinstance(rewrite_reports[0], dict) else {}
    variant = first_rewrite_variant(sample)
    choice_map = source_intake.get("choice_map") or {}
    raw_answer = str(source_intake.get("raw_answer_text") or "")
    normalized_answer = str(normalization_record.get("normalized_answer_text") or "")
    expected_answer = str(variant.get("expected_answer") or "")
    strategy = rewrite_strategy(sample)
    reason_codes = clean_problem_record.get("decision_reason_codes") or []
    rewritten_question = str(variant.get("rewritten_question_text") or "")
    mcq_pattern = re.compile(
        r"\b(which of the following|following statements?|following intervals?|which statement|which option|among the following)\b",
        re.IGNORECASE,
    )

    issues: List[str] = []
    if decision == "pass":
        if not normalized_answer:
            issues.append("pass_missing_normalized_answer")
        if not expected_answer:
            issues.append("pass_missing_expected_answer")
        if strategy == "split_open":
            issues.append("pass_with_split_open")
        if strategy in {"blank_open", "keep_open"} and canonicalize_answer_text(normalized_answer) != canonicalize_answer_text(expected_answer):
            issues.append("pass_expected_answer_mismatch")
        if strategy in {"blank_open", "keep_open"} and mcq_pattern.search(rewritten_question):
            issues.append("pass_rewritten_still_mcq_like")
        if any(code in {"answer_annotation_inconsistent", "gold_answer_mismatch", "rewrite_expected_answer_mismatch", "rewrite_mcq_residual"} for code in reason_codes):
            issues.append("pass_contains_answer_mismatch_reason_code")
        if rewrite_report.get("consistency_check_passed") is False:
            issues.append("pass_failed_rewrite_consistency_check")
        if rewrite_report.get("question_check_passed") is False:
            issues.append("pass_failed_rewrite_question_check")
        asset_registry_record = sample.get("asset_registry_record") or {}
        if asset_registry_record.get("registry_passed") is False:
            issues.append("pass_with_failed_asset_registry")
        requires_image = bool((sample.get("problem_main_record") or {}).get("requires_image"))
        image_count = int((sample.get("problem_main_record") or {}).get("image_count") or 0)
        if requires_image and image_count <= 0:
            issues.append("pass_missing_required_image")

    if spec is not None and choice_map and getattr(spec, "answer_index_base", None) is not None:
        resolved_answer = resolve_multiple_choice_answer_text(raw_answer, choice_map, spec.answer_index_base)
        if raw_answer.strip().lstrip("+-").isdigit() and canonicalize_answer_text(normalized_answer) != canonicalize_answer_text(resolved_answer):
            issues.append("numeric_index_mapping_mismatch")
    else:
        resolved_answer = ""

    return {
        "sample_path": str(sample_path),
        "dataset_key": dataset_key,
        "decision": decision,
        "rewrite_strategy": strategy,
        "problem_id": str((sample.get("problem_main_record") or {}).get("problem_id") or sample_path.stem),
        "source_problem_id": str(source_intake.get("source_problem_id") or ""),
        "raw_answer_text": raw_answer,
        "resolved_answer_text": resolved_answer,
        "normalized_answer_text": normalized_answer,
        "expected_answer": expected_answer,
        "reason_codes": list(reason_codes),
        "issues": issues,
    }


def iter_sample_files(run_dir: Path) -> Iterable[Path]:
    for sample_path in sorted(run_dir.glob("datasets/*/samples/prob_*.json")):
        if sample_path.name.endswith(".json.bak"):
            continue
        yield sample_path


def write_reports(run_dir: Path, audited: List[Dict[str, Any]], config_path: Path) -> Dict[str, Path]:
    analysis_dir = run_dir / "analysis"
    analysis_dir.mkdir(parents=True, exist_ok=True)
    json_path = analysis_dir / "pass_sample_audit.json"
    md_path = analysis_dir / "pass_sample_audit.md"

    issue_counter: Counter[str] = Counter()
    dataset_issue_counter: Dict[str, Counter[str]] = defaultdict(Counter)
    dataset_pass_counter: Counter[str] = Counter()
    flagged = []

    for row in audited:
        if row["decision"] == "pass":
            dataset_pass_counter[row["dataset_key"]] += 1
        if row["issues"]:
            flagged.append(row)
            for issue in row["issues"]:
                issue_counter[issue] += 1
                dataset_issue_counter[row["dataset_key"]][issue] += 1

    payload = {
        "config_path": str(config_path),
        "run_dir": str(run_dir),
        "audited_sample_count": len(audited),
        "flagged_sample_count": len(flagged),
        "issue_counter": dict(issue_counter),
        "dataset_pass_counter": dict(dataset_pass_counter),
        "flagged_samples": flagged,
    }
    with json_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)
        file.write("\n")

    lines: List[str] = []
    lines.append("# Pass Sample Audit")
    lines.append("")
    lines.append(f"- Config: `{config_path}`")
    lines.append(f"- Run dir: `{run_dir}`")
    lines.append(f"- Audited sample count: {len(audited)}")
    lines.append(f"- Flagged sample count: {len(flagged)}")
    lines.append("")
    lines.append("## Issue Summary")
    lines.append("")
    if issue_counter:
        for issue, count in issue_counter.most_common():
            lines.append(f"- `{issue}`: {count}")
    else:
        lines.append("- No issues found.")
    lines.append("")
    lines.append("## Dataset Summary")
    lines.append("")
    for dataset_key in sorted(set(list(dataset_pass_counter.keys()) + list(dataset_issue_counter.keys()))):
        lines.append(f"### {dataset_key}")
        lines.append("")
        lines.append(f"- pass samples audited: {dataset_pass_counter.get(dataset_key, 0)}")
        issue_map = dataset_issue_counter.get(dataset_key)
        if issue_map:
            for issue, count in issue_map.most_common():
                lines.append(f"- `{issue}`: {count}")
        else:
            lines.append("- no flagged issues")
        lines.append("")
    lines.append("## Flagged Samples")
    lines.append("")
    if flagged:
        for row in flagged:
            lines.append(f"### {row['problem_id']}")
            lines.append("")
            lines.append(f"- sample_path: `{row['sample_path']}`")
            lines.append(f"- dataset: `{row['dataset_key']}`")
            lines.append(f"- decision: `{row['decision']}`")
            lines.append(f"- rewrite_strategy: `{row['rewrite_strategy']}`")
            lines.append(f"- raw_answer_text: `{row['raw_answer_text']}`")
            lines.append(f"- resolved_answer_text: `{row['resolved_answer_text']}`")
            lines.append(f"- normalized_answer_text: `{row['normalized_answer_text']}`")
            lines.append(f"- expected_answer: `{row['expected_answer']}`")
            lines.append(f"- issues: `{', '.join(row['issues'])}`")
            lines.append("")
    else:
        lines.append("- No flagged samples.")
        lines.append("")

    md_path.write_text("\n".join(lines), encoding="utf-8")
    return {"json": json_path, "md": md_path}


def main() -> None:
    args = parse_args()
    config_path = PROJECT_ROOT / args.config
    config = PipelineConfig.from_yaml(str(config_path))
    run_dir = Path(args.run_dir) if args.run_dir else find_latest_run(PROJECT_ROOT / config.output_root)
    if not run_dir.is_absolute():
        run_dir = PROJECT_ROOT / run_dir
    spec_lookup = build_spec_lookup(config)
    audited = []
    for sample_path in iter_sample_files(run_dir):
        row = audit_sample(sample_path, spec_lookup, include_non_pass=args.include_non_pass)
        if row is not None:
            audited.append(row)
    report_paths = write_reports(run_dir, audited, config_path)
    flagged = [row for row in audited if row["issues"]]
    print(f"AUDITED={len(audited)}")
    print(f"FLAGGED={len(flagged)}")
    print(f"JSON_REPORT={report_paths['json']}")
    print(f"MD_REPORT={report_paths['md']}")
    for row in flagged[:20]:
        print(f"FLAGGED_SAMPLE={row['problem_id']} issues={','.join(row['issues'])}")


if __name__ == "__main__":
    main()
