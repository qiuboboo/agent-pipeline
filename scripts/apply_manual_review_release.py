#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from review_release_policy import (
    PROJECT_ROOT,
    format_reason_rule,
    format_rule_summary,
    get_release_bucket_runtime,
    load_review_release_policy_config,
    matches_rule,
    normalize_reason_list,
    resolve_project_path,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Apply post-ready manual review release to a candidate bucket and refresh summary/ledger."
    )
    p.add_argument("--dataset-root", help="Path to canonical ready dataset root, e.g. ready/.../datasets/mm_math")
    p.add_argument("--candidate-json", required=True, help="Path to exported candidate json")
    p.add_argument("--candidate-key", help="Candidate list key inside candidate json")
    p.add_argument("--policy-doc", help="Repo-relative policy doc path recorded into sample provenance")
    p.add_argument("--ledger-out", help="Markdown ledger output path")
    p.add_argument("--release-bucket", required=True, help="Bucket label, e.g. A")
    p.add_argument("--release-basis", help="Human-readable release basis")
    p.add_argument("--decision-reason-code", action="append", dest="decision_reason_codes")
    p.add_argument("--approved-via", default="")
    p.add_argument("--adjacent-key", default="")
    p.add_argument("--adjacent-label", default="")
    p.add_argument("--policy-config", help="Path to consolidated review-release YAML config")
    p.add_argument("--dataset", help="Dataset key used to resolve a policy from --policy-config")
    p.add_argument("--dry-run", action="store_true", help="Resolve policy and validate candidate rows without writing files")
    return p.parse_args()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def dump_json(path: Path, data: Any) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def require_value(value: Any, message: str) -> Any:
    if value is None:
        raise ValueError(message)
    if isinstance(value, str) and not value.strip():
        raise ValueError(message)
    if isinstance(value, list) and not value:
        raise ValueError(message)
    return value



def latest_decision(sample: Dict[str, Any]) -> str:
    cleaning = sample.get("cleaning_records") or []
    if cleaning and isinstance(cleaning, list):
        latest = cleaning[-1] or {}
        decision = latest.get("decision")
        if decision:
            return str(decision).strip().lower()
    for key in ("problem_main_record", "clean_problem_record"):
        record = sample.get(key) or {}
        for field in ("decision", "quality_decision", "clean_decision"):
            val = record.get(field)
            if val:
                return str(val).strip().lower()
    return "missing"


def compute_status_counts(samples_dir: Path) -> Dict[str, int]:
    counts = {"pass": 0, "review": 0, "reject": 0, "other": 0, "missing": 0}
    for path in sorted(samples_dir.glob("*.json")):
        sample = load_json(path)
        decision = latest_decision(sample)
        if decision in ("pass", "review", "reject"):
            counts[decision] += 1
        elif decision == "missing":
            counts["missing"] += 1
        else:
            counts["other"] += 1
    return counts


def pick_reason_codes(sample: Dict[str, Any]) -> List[str]:
    pm = sample.get("problem_main_record") or {}
    clean_problem = sample.get("clean_problem_record") or {}
    cleaning_records = sample.get("cleaning_records") or []
    latest_cleaning = cleaning_records[-1] if cleaning_records else {}
    return (
        normalize_reason_list(pm.get("clean_decision_reason_codes"))
        or normalize_reason_list(clean_problem.get("decision_reason_codes"))
        or normalize_reason_list(latest_cleaning.get("decision_reason_codes"))
    )


def pick_original_reason_codes(sample: Dict[str, Any]) -> List[str]:
    pm = sample.get("problem_main_record") or {}
    release_reserved = pm.get("release_reserved") or {}
    manual_release = release_reserved.get("manual_release_decision") or {}
    if manual_release:
        original = normalize_reason_list(manual_release.get("original_decision_reason_codes"))
        if original:
            return original

    clean_pool_entries = sample.get("clean_pool_entries") or []
    if clean_pool_entries and isinstance(clean_pool_entries[0], dict):
        manual_override = clean_pool_entries[0].get("manual_override") or {}
        original = normalize_reason_list(manual_override.get("original_decision_reason_codes"))
        if original:
            return original

    cleaning_records = sample.get("cleaning_records") or []
    latest_cleaning = cleaning_records[-1] if cleaning_records else {}
    if cleaning_records and isinstance(latest_cleaning, dict):
        manual_override = latest_cleaning.get("manual_override") or {}
        original = normalize_reason_list(manual_override.get("original_decision_reason_codes"))
        if original:
            return original

    return pick_reason_codes(sample)



def apply_release(
    sample: Dict[str, Any],
    *,
    now_iso: str,
    policy_doc: str,
    approved_via: str,
    release_bucket: str,
    release_basis: str,
    decision_reason_codes: List[str],
    rationale: str,
) -> Dict[str, Any]:
    pm = sample.get("problem_main_record") or {}
    clean_problem = sample.get("clean_problem_record") or {}
    clean_pool_entries = sample.get("clean_pool_entries") or []
    cleaning_records = sample.get("cleaning_records") or []
    if not clean_pool_entries:
        raise ValueError("missing clean_pool_entries")
    if not cleaning_records:
        raise ValueError("missing cleaning_records")

    original_clean_decision = (
        pm.get("clean_decision")
        or clean_problem.get("clean_decision")
        or cleaning_records[-1].get("decision")
    )
    original_reason_codes = pick_reason_codes(sample)

    override = {
        "approved_at": now_iso,
        "policy_doc": policy_doc,
        "approved_via": approved_via,
        "original_clean_decision": original_clean_decision,
        "original_decision_reason_codes": original_reason_codes,
        "release_bucket": release_bucket,
        "release_basis": release_basis,
    }

    clean_pool = clean_pool_entries[0]
    clean_pool["pool_status"] = "ready_for_annotation"
    clean_pool["clean_decision"] = "pass"
    clean_pool["review_required"] = False
    clean_pool["manual_override"] = deepcopy(override)

    clean_problem["clean_decision"] = "pass"
    clean_problem["decision_reason_codes"] = list(decision_reason_codes)

    pm["current_status"] = "clean_passed"
    pm["clean_decision"] = "pass"
    pm["clean_decision_reason_codes"] = list(decision_reason_codes)
    pm["clean_decision_rationale"] = rationale
    pm["annotation_ready"] = True
    pm["qa_precheck_ready"] = True
    pm["updated_at"] = now_iso
    release_reserved = pm.get("release_reserved") or {}
    release_reserved["manual_release_decision"] = deepcopy(override)
    pm["release_reserved"] = release_reserved

    cleaning = cleaning_records[-1]
    cleaning["decision"] = "pass"
    cleaning["decision_reason_codes"] = list(decision_reason_codes)
    cleaning["decision_rationale"] = rationale
    cleaning["review_ticket_id"] = None
    cleaning["operator_type"] = "manual_override"
    cleaning["finished_at"] = now_iso
    cleaning["manual_override"] = deepcopy(override)

    sample["problem_main_record"] = pm
    sample["clean_problem_record"] = clean_problem
    sample["clean_pool_entries"] = clean_pool_entries
    sample["cleaning_records"] = cleaning_records
    return override


def format_package_rel(dataset_root: Path) -> str:
    package_root = dataset_root.parent.parent
    try:
        return package_root.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return package_root.as_posix()


def generate_ledger(
    *,
    dataset_key: str,
    package_rel: str,
    candidate_json_path: Path,
    ledger_path: Path,
    summary_before: Dict[str, Any],
    summary_after: Dict[str, Any],
    release_bucket: str,
    release_basis: str,
    main_candidates: List[Dict[str, Any]],
    adjacent_candidates: List[Dict[str, Any]],
    adjacent_label: str,
    policy_doc: str,
    main_rule: str,
    adjacent_rule: str,
    now_iso: str,
) -> None:
    run_date = now_iso[:10]
    lines: List[str] = []
    lines.append(f"# {dataset_key} review 放行候选（{run_date}）")
    lines.append("")
    lines.append(f"- canonical ready 包：`{package_rel}`")
    lines.append(f"- 候选来源：`{candidate_json_path.as_posix()}`")
    lines.append("- 放行模板：`docs/review/review_release_template.md`")
    lines.append(f"- 当前执行策略：仅执行 **{release_bucket}档**，即 {main_rule}。")
    lines.append(
        f"- 执行结果（{run_date}）：本页 `{release_bucket}档` 已执行 manual release，`人工接受状态=1`。"
        + (f"相邻 `{adjacent_label}` 仅保留观察，本次未执行。" if adjacent_candidates else "")
    )
    before_counts = summary_before.get("status_counts") or {}
    after_counts = summary_after.get("status_counts") or {}
    lines.append(
        f"- 执行前汇总：`pass={before_counts.get('pass', 0)} / review={before_counts.get('review', 0)} / reject={before_counts.get('reject', 0)}`"
    )
    lines.append(
        f"- 执行后汇总：`pass={after_counts.get('pass', 0)} / review={after_counts.get('review', 0)} / reject={after_counts.get('reject', 0)}`"
    )
    lines.append(f"- 放行 basis：{release_basis}")
    lines.append("")
    lines.append("## 分层规则")
    lines.append("")
    lines.append(f"### {release_bucket}档：本次执行放行")
    lines.append("仅纳入以下规则：")
    lines.append(f"- {main_rule}")
    lines.append("")
    lines.append(f"**{release_bucket}档数量：`{len(main_candidates)}`**")
    lines.append("")
    if adjacent_candidates:
        lines.append(f"### {adjacent_label}：保留观察，本次不执行")
        lines.append("仅纳入以下规则：")
        lines.append(f"- {adjacent_rule}")
        lines.append("")
        lines.append(f"**{adjacent_label} 数量：`{len(adjacent_candidates)}`**")
        lines.append("")
    lines.append("### 模板化口径（可复用）")
    lines.append("- 先构建 canonical ready，不在 `output -> ready` 里改状态。")
    lines.append("- 单独导出候选 ledger。")
    lines.append("- 用户确认后再做 manual override，并保留 provenance。")
    lines.append("- 回写后刷新 `summary.json`，要求 `selection_validation.ok = true` 且 `write_validation.ok = true`。")
    lines.append("")
    lines.append("人工接受状态说明：`1=pass`，`0=reject`，空白表示未执行。")
    lines.append("")
    lines.append(f"## {release_bucket}档（本次已执行）")
    lines.append("")
    lines.append("| # | file | source_split | source_problem_id | problem_id | candidate_id | reason_codes | quality_risk_flags | 人工接受状态 | 备注 |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for idx, row in enumerate(main_candidates, 1):
        qrf = ", ".join(row.get("quality_risk_flags") or []) or "-"
        reasons = ", ".join(row.get("reason_codes") or []) or "-"
        note = "matched configured review-release policy；按 post-ready waiver policy 放行。"
        lines.append(
            f"| {idx} | `{row['file']}` | `{row.get('source_split', '')}` | `{row.get('source_problem_id', '')}` | `{row.get('problem_id', '')}` | `{row.get('candidate_id', '')}` | `{reasons}` | `{qrf}` | 1 | {note} |"
        )
    if adjacent_candidates:
        lines.append("")
        lines.append(f"## {adjacent_label}（本次未执行）")
        lines.append("")
        lines.append("| # | file | source_split | source_problem_id | problem_id | candidate_id | reason_codes | quality_risk_flags | 人工接受状态 | 备注 |")
        lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
        for idx, row in enumerate(adjacent_candidates, 1):
            qrf = ", ".join(row.get("quality_risk_flags") or []) or "-"
            reasons = ", ".join(row.get("reason_codes") or []) or "-"
            note = "保留给下一轮；本次不与当前执行 bucket 混放。"
            lines.append(
                f"| {idx} | `{row['file']}` | `{row.get('source_split', '')}` | `{row.get('source_problem_id', '')}` | `{row.get('problem_id', '')}` | `{row.get('candidate_id', '')}` | `{reasons}` | `{qrf}` |  | {note} |"
            )
    lines.append("")
    lines.append("## 说明")
    lines.append("")
    lines.append(
        "- provenance 写回字段记录在样本内：`problem_main_record.release_reserved.manual_release_decision`、"
        "`clean_pool_entries[0].manual_override`、`cleaning_records[-1].manual_override`。"
    )
    lines.append(f"- 本次 policy doc：`{policy_doc}`")
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    ledger_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def resolve_runtime_config(args: argparse.Namespace) -> Dict[str, Any]:
    defaults: Dict[str, Any] = {}
    dataset_cfg: Dict[str, Any] = {}
    bucket_cfg: Dict[str, Any] = {}
    adjacent_cfg: Dict[str, Any] = {}
    if args.policy_config:
        policy_root = load_review_release_policy_config(resolve_project_path(args.policy_config))
        review_release = policy_root.get("review_release") or {}
        defaults = review_release.get("defaults") or {}
        dataset_key = require_value(args.dataset, "--dataset is required when using --policy-config")
        runtime_cfg = get_release_bucket_runtime(dataset_key, args.release_bucket, resolve_project_path(args.policy_config))
        if not runtime_cfg:
            raise ValueError(f"release bucket policy not found: dataset={dataset_key}, bucket={args.release_bucket}")
        if runtime_cfg.get("enabled") is False:
            raise ValueError(f"release bucket is disabled: dataset={dataset_key}, bucket={args.release_bucket}")
        dataset_cfg = (review_release.get("datasets") or {}).get(dataset_key) or {}
    else:
        dataset_key = args.dataset or ""
        defaults = {}
        runtime_cfg = {}
        dataset_cfg = {}

    dataset_root_raw = args.dataset_root or dataset_cfg.get("dataset_root")
    candidate_key = args.candidate_key or runtime_cfg.get("candidate_key")
    policy_doc = args.policy_doc or runtime_cfg.get("policy_doc") or dataset_cfg.get("policy_doc")
    release_basis = args.release_basis or runtime_cfg.get("release_basis")
    decision_reason_codes = normalize_reason_list(args.decision_reason_codes) or normalize_reason_list(
        runtime_cfg.get("pass_decision_reason_codes")
    )
    approved_via = (
        args.approved_via
        or runtime_cfg.get("approved_via")
        or dataset_cfg.get("approved_via")
        or defaults.get("approved_via")
        or "user_confirmed_chat_policy"
    )
    adjacent_key = args.adjacent_key or runtime_cfg.get("adjacent_key") or ""
    adjacent_label = args.adjacent_label or runtime_cfg.get("adjacent_label") or defaults.get("adjacent_label") or "adjacent bucket"
    selection = runtime_cfg.get("selection") or None
    adjacent_selection = runtime_cfg.get("adjacent_selection") or None
    rule_type = str(runtime_cfg.get("rule_type") or ("structured_selection" if selection else "explicit_candidate_subset"))
    adjacent_rule_type = str(runtime_cfg.get("adjacent_rule_type") or ("structured_selection" if adjacent_selection else "explicit_candidate_subset"))

    require_value(dataset_root_raw, "missing dataset root: pass --dataset-root or configure dataset_root in --policy-config")
    require_value(candidate_key, "missing candidate key: pass --candidate-key or configure candidate_key in --policy-config")
    require_value(policy_doc, "missing policy doc: pass --policy-doc or configure policy_doc in --policy-config")
    require_value(release_basis, "missing release basis: pass --release-basis or configure release_basis in --policy-config")
    require_value(
        decision_reason_codes,
        "missing pass decision reason codes: pass --decision-reason-code or configure pass_decision_reason_codes in --policy-config",
    )
    if not args.dry_run:
        require_value(args.ledger_out, "missing --ledger-out (required unless --dry-run)")

    dataset_root = resolve_project_path(dataset_root_raw)
    if not dataset_key:
        summary_path = dataset_root / "summary.json"
        if summary_path.exists():
            summary_data = load_json(summary_path)
            dataset_key = str(summary_data.get("dataset_key") or dataset_root.name)
        else:
            dataset_key = dataset_root.name

    return {
        "dataset_key": dataset_key,
        "dataset_root": dataset_root,
        "candidate_json_path": resolve_project_path(args.candidate_json),
        "candidate_key": candidate_key,
        "policy_doc": str(policy_doc),
        "ledger_path": resolve_project_path(args.ledger_out) if args.ledger_out else None,
        "release_bucket": args.release_bucket,
        "release_basis": str(release_basis),
        "decision_reason_codes": list(decision_reason_codes),
        "approved_via": str(approved_via),
        "adjacent_key": adjacent_key,
        "adjacent_label": adjacent_label,
        "selection": selection,
        "adjacent_selection": adjacent_selection,
        "rule_type": rule_type,
        "adjacent_rule_type": adjacent_rule_type,
        "policy_config": args.policy_config or "",
    }


def resolve_candidate_rows(
    *,
    rows: List[Dict[str, Any]],
    samples_dir: Path,
    selection: Dict[str, Any] | None,
    rule_type: str,
    label: str,
) -> List[Dict[str, Any]]:
    resolved: List[Dict[str, Any]] = []
    mismatches: List[Dict[str, Any]] = []
    for row in rows:
        sample_path = samples_dir / row["file"]
        if not sample_path.exists():
            raise FileNotFoundError(f"candidate sample file not found: {sample_path}")
        sample = load_json(sample_path)
        pm = sample.get("problem_main_record") or {}
        actual_reason_codes = pick_original_reason_codes(sample)
        resolved_row = dict(row)
        resolved_row["problem_id"] = pm.get("problem_id") or row.get("problem_id")
        resolved_row["candidate_id"] = pm.get("candidate_id") or row.get("candidate_id")
        resolved_row["reason_codes"] = actual_reason_codes or normalize_reason_list(row.get("reason_codes"))
        resolved_row["sample_path"] = sample_path.as_posix()
        resolved_row["current_decision"] = latest_decision(sample)
        resolved_row["sample"] = sample
        if selection and rule_type != "explicit_candidate_subset" and not matches_rule(actual_reason_codes, rule_type, selection):
            mismatches.append(
                {
                    "file": row.get("file"),
                    "expected_rule": format_reason_rule(selection),
                    "actual_reason_codes": actual_reason_codes,
                }
            )
        resolved.append(resolved_row)
    if mismatches:
        preview = json.dumps(mismatches[:10], ensure_ascii=False, indent=2)
        raise ValueError(f"{label} candidates do not match configured selection rule:\n{preview}")
    return resolved


def main() -> None:
    args = parse_args()
    runtime = resolve_runtime_config(args)
    dataset_root = runtime["dataset_root"]
    samples_dir = dataset_root / "samples"
    summary_path = dataset_root / "summary.json"
    candidate_json_path = runtime["candidate_json_path"]
    summary_before = load_json(summary_path)
    candidate_data = load_json(candidate_json_path)

    main_rows = candidate_data.get(runtime["candidate_key"]) or []
    adjacent_rows = []
    if runtime["adjacent_key"]:
        adjacent_rows = candidate_data.get(runtime["adjacent_key"]) or []

    resolved_main_rows = resolve_candidate_rows(
        rows=main_rows,
        samples_dir=samples_dir,
        selection=runtime["selection"],
        rule_type=runtime["rule_type"],
        label="main",
    )
    resolved_adjacent_rows = resolve_candidate_rows(
        rows=adjacent_rows,
        samples_dir=samples_dir,
        selection=runtime["adjacent_selection"],
        rule_type=runtime["adjacent_rule_type"],
        label="adjacent",
    )

    if args.dry_run:
        print(
            json.dumps(
                {
                    "dry_run": True,
                    "dataset_key": runtime["dataset_key"],
                    "dataset_root": dataset_root.as_posix(),
                    "candidate_json": candidate_json_path.as_posix(),
                    "candidate_key": runtime["candidate_key"],
                    "main_candidate_count": len(resolved_main_rows),
                    "adjacent_key": runtime["adjacent_key"],
                    "adjacent_candidate_count": len(resolved_adjacent_rows),
                    "release_bucket": runtime["release_bucket"],
                    "release_basis": runtime["release_basis"],
                    "decision_reason_codes": runtime["decision_reason_codes"],
                    "policy_doc": runtime["policy_doc"],
                    "policy_config": runtime["policy_config"],
                    "selection_rule": format_rule_summary(runtime["rule_type"], runtime["selection"], runtime.get("selection_notes", "")),
                    "adjacent_rule": format_rule_summary(runtime["adjacent_rule_type"], runtime["adjacent_selection"], runtime.get("adjacent_selection_notes", "")) if runtime["adjacent_key"] else "",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    now_iso = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    applied_rows: List[Dict[str, Any]] = []
    for row in resolved_main_rows:
        sample = row.pop("sample")
        pm = sample.get("problem_main_record") or {}
        rationale = (
            f"Manually released on {now_iso[:10]} under the current {runtime['dataset_key']} review-release policy. "
            f"Original automatic review decision was '{pm.get('clean_decision') or latest_decision(sample)}' with reasons {pick_reason_codes(sample)}. "
            f"Accepted as {runtime['release_basis']} under the reusable post-ready release template; this is a post-ready waiver policy rather than a default build-stage pass."
        )
        override = apply_release(
            sample,
            now_iso=now_iso,
            policy_doc=runtime["policy_doc"],
            approved_via=runtime["approved_via"],
            release_bucket=runtime["release_bucket"],
            release_basis=runtime["release_basis"],
            decision_reason_codes=runtime["decision_reason_codes"],
            rationale=rationale,
        )
        dump_json(Path(row["sample_path"]), sample)
        row["manual_override"] = override
        applied_rows.append(row)

    summary_after = load_json(summary_path)
    summary_after["status_counts"] = compute_status_counts(samples_dir)
    if "decision_counts" in summary_after or not summary_after.get("decision_counts"):
        status_counts = summary_after["status_counts"]
        summary_after["decision_counts"] = {
            "pass": status_counts.get("pass", 0),
            "review": status_counts.get("review", 0),
            "reject": status_counts.get("reject", 0),
        }
    written_count = len(list(samples_dir.glob("*.json")))
    status_total = sum(summary_after["status_counts"].values())
    selected = int(summary_after.get("selected_samples") or summary_after.get("requested_samples") or 0)
    processed = int(summary_after.get("processed_samples") or 0)
    scanned = int(summary_after.get("scanned_files") or written_count)
    unique_files = int(summary_after.get("unique_files") or written_count)
    duplicates = int(summary_after.get("duplicate_source_problem_id") or 0)
    summary_after["write_validation"] = {
        "ok": written_count == selected and processed == selected and status_total == selected and scanned == unique_files + duplicates,
        "checks": {
            "written_sample_file_count_matches_selected": written_count == selected,
            "processed_matches_selected": processed == selected,
            "status_sum_matches_selected": status_total == selected,
            "scanned_equals_unique_plus_duplicates": scanned == unique_files + duplicates,
        },
        "written_sample_file_count": written_count,
        "status_total": status_total,
    }
    dump_json(summary_path, summary_after)

    generate_ledger(
        dataset_key=runtime["dataset_key"],
        package_rel=format_package_rel(dataset_root),
        candidate_json_path=candidate_json_path,
        ledger_path=runtime["ledger_path"],
        summary_before=summary_before,
        summary_after=summary_after,
        release_bucket=runtime["release_bucket"],
        release_basis=runtime["release_basis"],
        main_candidates=applied_rows,
        adjacent_candidates=[{k: v for k, v in row.items() if k != "sample"} for row in resolved_adjacent_rows],
        adjacent_label=runtime["adjacent_label"],
        policy_doc=runtime["policy_doc"],
        main_rule=format_rule_summary(runtime["rule_type"], runtime["selection"], runtime.get("selection_notes", "")),
        adjacent_rule=format_rule_summary(runtime["adjacent_rule_type"], runtime["adjacent_selection"], runtime.get("adjacent_selection_notes", "")),
        now_iso=now_iso,
    )

    print(
        json.dumps(
            {
                "dataset_key": runtime["dataset_key"],
                "applied_count": len(applied_rows),
                "adjacent_held_count": len(resolved_adjacent_rows),
                "status_before": summary_before.get("status_counts"),
                "status_after": summary_after.get("status_counts"),
                "write_validation": summary_after.get("write_validation"),
                "policy_doc": runtime["policy_doc"],
                "policy_config": runtime["policy_config"],
                "ledger_out": runtime["ledger_path"].as_posix() if runtime["ledger_path"] else "",
                "approved_at": now_iso,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
