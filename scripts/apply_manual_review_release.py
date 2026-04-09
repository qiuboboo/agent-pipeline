#!/usr/bin/env python3
import argparse
import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Apply post-ready manual review release to a candidate bucket and refresh summary/ledger.")
    p.add_argument("--dataset-root", required=True, help="Path to canonical ready dataset root, e.g. ready/.../datasets/mm_math")
    p.add_argument("--candidate-json", required=True, help="Path to exported candidate json")
    p.add_argument("--candidate-key", required=True, help="Candidate list key inside candidate json")
    p.add_argument("--policy-doc", required=True, help="Repo-relative policy doc path recorded into sample provenance")
    p.add_argument("--ledger-out", required=True, help="Markdown ledger output path")
    p.add_argument("--release-bucket", required=True, help="Bucket label, e.g. A")
    p.add_argument("--release-basis", required=True, help="Human-readable release basis")
    p.add_argument("--decision-reason-code", action="append", dest="decision_reason_codes", required=True)
    p.add_argument("--approved-via", default="user_confirmed_chat_policy")
    p.add_argument("--adjacent-key", default="")
    p.add_argument("--adjacent-label", default="adjacent bucket")
    return p.parse_args()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def dump_json(path: Path, data: Any) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


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


def image_markdown(problem_id: str, dataset_key: str, package_rel: str) -> str:
    img_rel = f"../{package_rel}/datasets/{dataset_key}/artifacts/images/{problem_id}_primary.png"
    return f"![]({img_rel})"


def normalize_reason_list(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(x) for x in value]
    return []


def apply_release(sample: Dict[str, Any], *, now_iso: str, policy_doc: str, approved_via: str, release_bucket: str, release_basis: str, decision_reason_codes: List[str], rationale: str) -> Dict[str, Any]:
    pm = sample.get("problem_main_record") or {}
    clean_problem = sample.get("clean_problem_record") or {}
    clean_pool_entries = sample.get("clean_pool_entries") or []
    cleaning_records = sample.get("cleaning_records") or []
    if not clean_pool_entries:
        raise ValueError("missing clean_pool_entries")
    if not cleaning_records:
        raise ValueError("missing cleaning_records")

    original_clean_decision = pm.get("clean_decision") or clean_problem.get("clean_decision") or cleaning_records[-1].get("decision")
    original_reason_codes = normalize_reason_list(pm.get("clean_decision_reason_codes")) or normalize_reason_list(clean_problem.get("decision_reason_codes")) or normalize_reason_list(cleaning_records[-1].get("decision_reason_codes"))

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
) -> None:
    lines: List[str] = []
    lines.append(f"# {dataset_key} review 放行候选（2026-04-09）")
    lines.append("")
    lines.append(f"- canonical ready 包：`{package_rel}`")
    lines.append(f"- 候选来源：`{candidate_json_path.as_posix()}`")
    lines.append(f"- 放行模板：`docs/review/review_release_template.md`")
    lines.append(f"- 当前执行策略：仅执行 **{release_bucket}档**，即 exact `clean_decision_reason_codes == [\"alignment_requires_review\"]`。")
    lines.append(f"- 执行结果（2026-04-09）：本页 `{release_bucket}档` 已执行 manual release，`人工接受状态=1`。相邻 `{adjacent_label}` 仅保留观察，本次未执行。")
    before_counts = summary_before.get("status_counts") or {}
    after_counts = summary_after.get("status_counts") or {}
    lines.append(f"- 执行前汇总：`pass={before_counts.get('pass', 0)} / review={before_counts.get('review', 0)} / reject={before_counts.get('reject', 0)}`")
    lines.append(f"- 执行后汇总：`pass={after_counts.get('pass', 0)} / review={after_counts.get('review', 0)} / reject={after_counts.get('reject', 0)}`")
    lines.append(f"- 放行 basis：{release_basis}")
    lines.append("")
    lines.append("## 分层规则")
    lines.append("")
    lines.append("### A档：本次执行放行")
    lines.append("仅纳入以下 exact reason 组合：")
    lines.append("- `alignment_requires_review`")
    lines.append("")
    lines.append(f"**A档数量：`{len(main_candidates)}`**")
    lines.append("")
    lines.append(f"### {adjacent_label}：保留观察，本次不执行")
    lines.append("仅纳入以下 exact reason 组合：")
    lines.append("- `alignment_requires_review + text_sufficient`")
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
    lines.append("## A档（本次已执行）")
    lines.append("")
    lines.append("| # | file | source_split | source_problem_id | problem_id | candidate_id | quality_risk_flags | 人工接受状态 | 备注 |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for idx, row in enumerate(main_candidates, 1):
        qrf = ", ".join(row.get("quality_risk_flags") or [])
        qrf = qrf if qrf else "-"
        note = "alignment-only review gate；按 post-ready waiver policy 放行。"
        lines.append(
            f"| {idx} | `{row['file']}` | `{row['source_split']}` | `{row['source_problem_id']}` | `{row['problem_id']}` | `{row['candidate_id']}` | `{qrf}` | 1 | {note} |"
        )
    lines.append("")
    lines.append(f"## {adjacent_label}（本次未执行）")
    lines.append("")
    lines.append("| # | file | source_split | source_problem_id | problem_id | candidate_id | quality_risk_flags | 人工接受状态 | 备注 |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for idx, row in enumerate(adjacent_candidates, 1):
        qrf = ", ".join(row.get("quality_risk_flags") or [])
        qrf = qrf if qrf else "-"
        note = "保留给下一轮；本次不与 strict A-bucket 混放。"
        lines.append(
            f"| {idx} | `{row['file']}` | `{row['source_split']}` | `{row['source_problem_id']}` | `{row['problem_id']}` | `{row['candidate_id']}` | `{qrf}` |  | {note} |"
        )
    lines.append("")
    lines.append("## 说明")
    lines.append("")
    lines.append(f"- provenance 写回字段记录在样本内：`problem_main_record.release_reserved.manual_release_decision`、`clean_pool_entries[0].manual_override`、`cleaning_records[-1].manual_override`。")
    lines.append(f"- 本次 policy doc：`{policy_doc}`")
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    ledger_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    dataset_root = Path(args.dataset_root)
    samples_dir = dataset_root / "samples"
    summary_path = dataset_root / "summary.json"
    candidate_json_path = Path(args.candidate_json)
    ledger_path = Path(args.ledger_out)

    summary_before = load_json(summary_path)
    candidate_data = load_json(candidate_json_path)
    main_rows = candidate_data.get(args.candidate_key) or []
    adjacent_rows = []
    if args.adjacent_key:
        adjacent_rows = candidate_data.get(args.adjacent_key) or []
        if not adjacent_rows and args.adjacent_key == "adjacent_bucket_candidates":
            adjacent_rows = candidate_data.get("adjacent_text_sufficient_candidates") or []
    dataset_key = summary_before["dataset_key"]
    package_rel = dataset_root.parent.parent.as_posix()
    now_iso = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    applied_rows: List[Dict[str, Any]] = []
    for row in main_rows:
        sample_path = samples_dir / row["file"]
        sample = load_json(sample_path)
        pm = sample.get("problem_main_record") or {}
        candidate_id = pm.get("candidate_id")
        problem_id = pm.get("problem_id")
        rationale = (
            f"Manually released on {now_iso[:10]} under the current {dataset_key} review-release policy. "
            f"Original automatic review decision was 'review' with reasons {normalize_reason_list(pm.get('clean_decision_reason_codes'))}. "
            f"Accepted as {args.release_basis} under the reusable post-ready release template; this is a post-ready waiver policy rather than a default build-stage pass."
        )
        override = apply_release(
            sample,
            now_iso=now_iso,
            policy_doc=args.policy_doc,
            approved_via=args.approved_via,
            release_bucket=args.release_bucket,
            release_basis=args.release_basis,
            decision_reason_codes=args.decision_reason_codes,
            rationale=rationale,
        )
        dump_json(sample_path, sample)
        applied = dict(row)
        applied["problem_id"] = problem_id
        applied["candidate_id"] = candidate_id
        applied["manual_override"] = override
        applied_rows.append(applied)

    resolved_adjacent: List[Dict[str, Any]] = []
    for row in adjacent_rows:
        sample_path = samples_dir / row["file"]
        sample = load_json(sample_path)
        pm = sample.get("problem_main_record") or {}
        resolved = dict(row)
        resolved["problem_id"] = pm.get("problem_id") or row.get("problem_id")
        resolved["candidate_id"] = pm.get("candidate_id") or row.get("candidate_id")
        resolved_adjacent.append(resolved)

    summary_after = load_json(summary_path)
    summary_after["status_counts"] = compute_status_counts(samples_dir)
    written_count = len(list(samples_dir.glob("*.json")))
    status_total = sum(summary_after["status_counts"].values())
    selected = int(summary_after.get("selected_samples") or 0)
    processed = int(summary_after.get("processed_samples") or 0)
    scanned = int(summary_after.get("scanned_files") or 0)
    unique_files = int(summary_after.get("unique_files") or 0)
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
        dataset_key=dataset_key,
        package_rel=package_rel,
        candidate_json_path=candidate_json_path,
        ledger_path=ledger_path,
        summary_before=summary_before,
        summary_after=summary_after,
        release_bucket=args.release_bucket,
        release_basis=args.release_basis,
        main_candidates=applied_rows,
        adjacent_candidates=resolved_adjacent,
        adjacent_label=args.adjacent_label,
        policy_doc=args.policy_doc,
    )

    print(json.dumps({
        "dataset_key": dataset_key,
        "applied_count": len(applied_rows),
        "adjacent_held_count": len(resolved_adjacent),
        "status_before": summary_before.get("status_counts"),
        "status_after": summary_after.get("status_counts"),
        "write_validation": summary_after.get("write_validation"),
        "policy_doc": args.policy_doc,
        "ledger_out": ledger_path.as_posix(),
        "approved_at": now_iso,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
