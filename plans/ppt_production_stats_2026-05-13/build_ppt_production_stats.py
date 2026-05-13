#!/usr/bin/env python3
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

import yaml


ROOT = Path("/home/lijingyue/qiujianbo/agent-pipeline")
OUTPUTS_DIR = ROOT / "outputs"
READY_DIR = ROOT / "ready"
DOCS_REVIEW_DIR = ROOT / "docs" / "review"
POLICY_PATH = ROOT / "configs" / "review_release_policies.yaml"
OUT_DIR = ROOT / "plans" / "ppt_production_stats_2026-05-13"
DATASET_LEVEL1_TAXONOMY = {
    "ai2d": "science_diagram_understanding",
    "cmm_math": "math",
    "eee_bench": "circuit",
    "emma_chemistry": "chemistry",
    "emma_physics": "physics",
    "geometry3k": "math",
    "geoqa_plus": "math",
    "geosqa": "geography",
    "mathvision": "math",
    "mm_math": "math",
    "msearth_open_ended": "earth_science",
    "multi_physics": "physics",
    "physreason": "physics",
    "phyx": "physics",
    "scemqa": "mixed_science",
    "scemqa_biology": "biology",
    "scemqa_chemistry": "chemistry",
    "scemqa_math": "math",
    "sciverse_biology": "biology",
    "sciverse_chemistry": "chemistry",
    "sciverse_physics": "physics",
    "seephys": "physics",
}


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def read_yaml(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def resolve_repo_path(path_str):
    path = Path(path_str)
    if path.is_absolute():
        return path
    return ROOT / path


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def write_csv(path: Path, rows, fieldnames):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_md_table(path: Path, title: str, rows, fieldnames, notes=None):
    with path.open("w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n")
        if notes:
            for note in notes:
                f.write(f"- {note}\n")
            f.write("\n")
        f.write("| " + " | ".join(fieldnames) + " |\n")
        f.write("|" + "|".join(["---"] * len(fieldnames)) + "|\n")
        for row in rows:
            vals = []
            for key in fieldnames:
                val = row.get(key, "")
                if isinstance(val, float):
                    vals.append(f"{val:.6f}".rstrip("0").rstrip("."))
                else:
                    vals.append(str(val))
            f.write("| " + " | ".join(vals) + " |\n")


def detect_candidate_list_key(obj):
    preferred = [
        "strict_rewrite_usable_review_candidates",
        "rewrite_usable_no_key_condition_gap_candidates",
        "strict_B1_bucket_candidates",
        "strict_B2_bucket_candidates",
        "A1_alignment_metadata_candidates",
        "strict_A_bucket_candidates",
    ]
    for key in preferred:
        if isinstance(obj.get(key), list):
            return key
    for key, value in obj.items():
        if isinstance(value, list) and "candidate" in key.lower():
            return key
    return None


def resolve_candidate_file(policy_bucket):
    candidate_json = policy_bucket.get("candidate_json")
    if candidate_json:
        path = resolve_repo_path(candidate_json)
        if path.exists():
            return path
    candidate_key = policy_bucket.get("candidate_key")
    if candidate_key:
        matches = sorted(DOCS_REVIEW_DIR.glob(f"*{candidate_key}*.json"))
        if len(matches) == 1:
            return matches[0]
    return None


def normalize_taxonomy(domain_tags):
    if not domain_tags:
        return "unknown"
    tag = domain_tags[0]
    mapping = {
        "数学": "math",
        "几何": "math",
        "math": "math",
        "物理": "physics",
        "Physics": "physics",
        "化学": "chemistry",
        "Chemistry": "chemistry",
        "Biology": "biology",
        "生物": "biology",
        "地理": "geography",
        "电子电路": "circuit",
        "电气电子工程领域": "circuit",
        "地球科学": "earth_science",
        "数学、物理、生物、化学": "mixed_science",
        "科学图解理解": "science_diagram_understanding",
    }
    return mapping.get(tag, tag)


def reason_category(reason):
    reason = reason or ""
    if any(x in reason for x in ["alignment", "metadata", "annotation", "mismatch", "inconsisten", "conflict"]):
        return "alignment_metadata_consistency"
    if any(x in reason for x in ["visual", "grounded", "image", "diagram", "resolution", "small_image"]):
        return "visual_grounding_image_quality"
    if any(x in reason for x in ["rewrite", "split_variant", "choice", "option", "open", "text_relation"]):
        return "rewrite_structure_options"
    if any(x in reason for x in ["answer", "verifiable", "target", "solvability", "failure"]):
        return "answer_target_solvability"
    return "other"


def source_attribution(reason):
    reason = reason or ""
    if any(x in reason for x in ["alignment", "metadata", "annotation", "mismatch", "conflict", "inconsisten"]):
        return "metadata_alignment"
    if any(x in reason for x in ["visual", "grounded", "image", "diagram", "resolution", "small_image"]):
        return "visual_grounding"
    if any(x in reason for x in ["rewrite", "split_variant", "choice", "option"]):
        return "rewrite_or_structure"
    if any(x in reason for x in ["answer", "verifiable", "target", "solvability"]):
        return "answer_or_solvability"
    return "other"


def compute_rewrite_resolvability(sample):
    rewrite_reports = sample.get("rewrite_reports") or []
    solvability_reports = sample.get("solvability_reports") or []
    field_audits = sample.get("field_audit_records") or []
    strategy = rewrite_reports[0].get("strategy") if rewrite_reports else ""
    rewritten = any((x.get("change_type") == "question_rewritten") for x in field_audits)
    solvable = any((x.get("decision_hint") == "pass" and not x.get("failure_codes")) for x in solvability_reports)
    if strategy == "keep_open" and not rewritten:
        return "rewrite_not_needed"
    if rewritten and solvable:
        return "rewritten_and_solvable"
    if rewritten and not solvable:
        return "rewritten_but_still_risky"
    if strategy:
        return f"strategy_{strategy}"
    return "unknown"


def production_ready_dirs():
    return sorted([p for p in READY_DIR.iterdir() if p.is_dir() and (p / "summary.json").exists()])


def canonical_run_paths_from_ready(ready_dirs):
    run_paths = {}
    for ready_dir in ready_dirs:
        summary = read_json(ready_dir / "summary.json")
        for run_path in summary.get("source_runs", []):
            run_path = Path(run_path)
            run_paths[str(run_path)] = run_path
    return run_paths


def build_run_usage_summary(canonical_runs):
    rows = []
    agg = Counter()
    sums = defaultdict(float)
    for run_dir in sorted(canonical_runs.values()):
        summary_path = run_dir / "summary.json"
        if not summary_path.exists():
            continue
        summary = read_json(summary_path)
        run_id = summary.get("pipeline_run_id") or run_dir.name
        for dataset in summary.get("datasets", []):
            usage = dataset.get("llm_usage") or {}
            processed = dataset.get("processed_samples") or 0
            request_count = usage.get("request_count") or 0
            row = {
                "run_id": run_id,
                "run_dir": str(run_dir),
                "output_dir": str(run_dir.parent),
                "dataset": dataset.get("dataset_key"),
                "processed_samples": processed,
                "request_count": request_count,
                "successful_request_count": usage.get("successful_request_count") or 0,
                "failed_request_count": usage.get("failed_request_count") or 0,
                "retry_count": usage.get("retry_count") or 0,
                "text_request_count": usage.get("text_request_count") or 0,
                "multimodal_request_count": usage.get("multimodal_request_count") or 0,
                "total_request_seconds": usage.get("total_request_seconds") or 0.0,
                "prompt_tokens": usage.get("prompt_tokens") or 0,
                "completion_tokens": usage.get("completion_tokens") or 0,
                "total_tokens": usage.get("total_tokens") or 0,
                "cached_tokens": usage.get("cached_tokens") or 0,
                "reasoning_tokens": usage.get("reasoning_tokens") or 0,
                "requests_with_usage": usage.get("requests_with_usage") or 0,
            }
            row["avg_requests_per_sample"] = (request_count / processed) if processed else 0.0
            row["avg_request_seconds_per_sample"] = (row["total_request_seconds"] / processed) if processed else 0.0
            row["avg_seconds_per_request"] = (row["total_request_seconds"] / request_count) if request_count else 0.0
            rows.append(row)
            agg["run_count"] += 1
            for key in [
                "processed_samples",
                "request_count",
                "successful_request_count",
                "failed_request_count",
                "retry_count",
                "text_request_count",
                "multimodal_request_count",
                "prompt_tokens",
                "completion_tokens",
                "total_tokens",
                "cached_tokens",
                "reasoning_tokens",
                "requests_with_usage",
            ]:
                agg[key] += row[key]
            sums["total_request_seconds"] += row["total_request_seconds"]
    totals = {
        "run_count": agg["run_count"],
        "processed_samples": agg["processed_samples"],
        "request_count": agg["request_count"],
        "successful_request_count": agg["successful_request_count"],
        "failed_request_count": agg["failed_request_count"],
        "retry_count": agg["retry_count"],
        "text_request_count": agg["text_request_count"],
        "multimodal_request_count": agg["multimodal_request_count"],
        "total_request_seconds": round(sums["total_request_seconds"], 6),
        "prompt_tokens": agg["prompt_tokens"],
        "completion_tokens": agg["completion_tokens"],
        "total_tokens": agg["total_tokens"],
        "cached_tokens": agg["cached_tokens"],
        "reasoning_tokens": agg["reasoning_tokens"],
        "requests_with_usage": agg["requests_with_usage"],
    }
    totals["avg_requests_per_sample"] = (totals["request_count"] / totals["processed_samples"]) if totals["processed_samples"] else 0.0
    totals["avg_request_seconds_per_sample"] = (totals["total_request_seconds"] / totals["processed_samples"]) if totals["processed_samples"] else 0.0
    totals["avg_seconds_per_request"] = (totals["total_request_seconds"] / totals["request_count"]) if totals["request_count"] else 0.0
    return rows, totals


def build_conversion_table(ready_dirs):
    rows = []
    for ready_dir in ready_dirs:
        summary = read_json(ready_dir / "summary.json")
        release_counts = ((summary.get("release_gate") or {}).get("counts")) or {}
        rows.append({
            "dataset": summary.get("dataset_key"),
            "processed": summary.get("scanned_files", 0),
            "pass": (summary.get("original_status_counts_before_release_gate") or {}).get("pass", 0),
            "review": (summary.get("original_status_counts_before_release_gate") or {}).get("review", 0),
            "reject": (summary.get("original_status_counts_before_release_gate") or {}).get("reject", 0),
            "released_review": release_counts.get("released_review", 0),
            "dropped_review": release_counts.get("dropped_review", 0),
            "dedup_removed": summary.get("duplicate_source_problem_id", 0),
            "final_ready": (summary.get("status_counts") or {}).get("pass", 0),
        })
    return sorted(rows, key=lambda x: x["dataset"])


def load_policy_rows():
    policy = read_yaml(POLICY_PATH)
    return (((policy or {}).get("review_release") or {}).get("datasets")) or {}


def build_release_execution_table(ready_dirs, policy_rows):
    rows = []
    for ready_dir in ready_dirs:
        dataset = ready_dir.name
        manifest = read_json(ready_dir / "selection_manifest.json")
        release_gate = manifest.get("release_gate") or {}
        kept = manifest.get("kept_samples") or []
        per_bucket = defaultdict(lambda: {"actual_released_count": 0, "rule_types": set(), "release_basis": set(), "candidate_jsons": set()})
        for item in kept:
            if item.get("released_from_review"):
                bucket = item.get("release_bucket") or ""
                entry = per_bucket[bucket]
                entry["actual_released_count"] += 1
                entry["release_basis"].add(item.get("release_basis") or "")
                if item.get("candidate_json"):
                    entry["candidate_jsons"].add(item.get("candidate_json"))
                mode = item.get("release_mode") or ""
                if mode == "explicit_candidate_subset":
                    entry["rule_types"].add("explicit_candidate_subset")
                elif mode == "structured_selection":
                    entry["rule_types"].add("structured_selection")
                else:
                    entry["rule_types"].add(mode or "unknown")

        dataset_policy = policy_rows.get(dataset, {})
        release_buckets = dataset_policy.get("release_buckets") or {}
        all_buckets = sorted(set(per_bucket.keys()) | set(release_buckets.keys()))
        for bucket in all_buckets:
            policy_bucket = release_buckets.get(bucket) or {}
            candidate_count = ""
            candidate_file = resolve_candidate_file(policy_bucket)
            candidate_json = str(candidate_file) if candidate_file else policy_bucket.get("candidate_json")
            if not candidate_json:
                candidate_jsons = per_bucket.get(bucket, {}).get("candidate_jsons") or set()
                candidate_json = next(iter(candidate_jsons), "")
                candidate_file = Path(candidate_json) if candidate_json else None
            candidate_list_key = ""
            if candidate_json and candidate_file and candidate_file.exists():
                candidate_obj = read_json(candidate_file)
                candidate_list_key = detect_candidate_list_key(candidate_obj) or ""
                if "candidate_count" in candidate_obj and isinstance(candidate_obj["candidate_count"], int):
                    candidate_count = candidate_obj["candidate_count"]
                elif candidate_list_key:
                    candidate_count = len(candidate_obj.get(candidate_list_key, []))
            elif bucket in per_bucket and bucket and bucket in (release_gate.get("structured_release_buckets") or []):
                candidate_count = ""

            rule_type = ""
            if policy_bucket.get("selection"):
                rule_type = "structured_selection"
            elif candidate_json or policy_bucket.get("candidate_key"):
                rule_type = "explicit_candidate_subset"
            elif bucket in per_bucket and per_bucket[bucket]["rule_types"]:
                rule_type = ",".join(sorted(per_bucket[bucket]["rule_types"]))
            elif bucket:
                rule_type = "structured_selection"

            release_basis = ""
            if policy_bucket.get("release_basis"):
                release_basis = policy_bucket["release_basis"]
            elif bucket in per_bucket and per_bucket[bucket]["release_basis"]:
                release_basis = " / ".join(sorted(x for x in per_bucket[bucket]["release_basis"] if x))

            rows.append({
                "dataset": dataset,
                "bucket": bucket,
                "rule_type": rule_type,
                "candidate_count": candidate_count,
                "actual_released_count": per_bucket.get(bucket, {}).get("actual_released_count", 0),
                "release_basis": release_basis,
            })
    return sorted(rows, key=lambda x: (x["dataset"], x["bucket"]))


def build_empty_bucket_table(ready_dirs):
    targets = ["eee_bench", "mathvision", "emma_physics", "msearth_open_ended"]
    rows = []
    for dataset in targets:
        summary = read_json(READY_DIR / dataset / "summary.json")
        manifest = read_json(READY_DIR / dataset / "selection_manifest.json")
        release_gate = summary.get("release_gate") or {}
        counts = release_gate.get("counts") or {}
        kept = manifest.get("kept_samples") or []
        explicit = [x for x in kept if x.get("released_from_review") and ((x.get("release_mode") == "explicit_candidate_subset") or x.get("candidate_json"))]
        rows.append({
            "dataset": dataset,
            "final_ready": (summary.get("status_counts") or {}).get("pass", 0),
            "pass_original": counts.get("pass_original", 0),
            "released_review": counts.get("released_review", 0),
            "dropped_review": counts.get("dropped_review", 0),
            "explicit_release_candidate_count": release_gate.get("explicit_release_candidate_count", 0),
            "explicit_or_manual_release_exists": "yes" if explicit or release_gate.get("explicit_release_candidate_count", 0) else "no",
        })
    return rows


def build_taxonomy_tables(ready_dirs):
    taxonomy_counter = Counter()
    dataset_taxonomy = defaultdict(Counter)
    total_ready = 0
    for ready_dir in ready_dirs:
        dataset = ready_dir.name
        for sample_path in sorted((ready_dir / "samples").glob("*.json")):
            sample = read_json(sample_path)
            level1 = DATASET_LEVEL1_TAXONOMY.get(dataset)
            if not level1:
                level1 = normalize_taxonomy((sample.get("problem_main_record") or {}).get("domain_tags") or [])
            taxonomy_counter[level1] += 1
            dataset_taxonomy[dataset][level1] += 1
            total_ready += 1
    level1_rows = [{"taxonomy_level1": k, "ready_samples": v} for k, v in sorted(taxonomy_counter.items())]
    taxonomies = sorted(taxonomy_counter.keys())
    heatmap_rows = []
    for dataset in sorted(dataset_taxonomy.keys()):
        row = {"dataset": dataset}
        for taxonomy in taxonomies:
            row[taxonomy] = dataset_taxonomy[dataset].get(taxonomy, 0)
        heatmap_rows.append(row)
    totals = {
        "total_ready_samples": total_ready,
        "dataset_count": len(dataset_taxonomy),
        "taxonomy_class_count": len(taxonomies),
    }
    return level1_rows, heatmap_rows, totals


def build_reason_source_tables(ready_dirs):
    reason_counter = Counter()
    source_counter = Counter()
    rewrite_counter = Counter()
    for ready_dir in ready_dirs:
        manifest = read_json(ready_dir / "selection_manifest.json")
        for item in manifest.get("kept_samples", []):
            sample_path = ready_dir / item["sample_path"]
            sample = read_json(sample_path)
            reasons = item.get("source_reason_codes") or []
            if not reasons:
                reasons = list((sample.get("problem_main_record") or {}).get("clean_decision_reason_codes") or [])
            for reason in reasons:
                reason_counter[reason_category(reason)] += 1
                source_counter[source_attribution(reason)] += 1
            for risk in (sample.get("problem_main_record") or {}).get("quality_risk_flags") or []:
                reason_counter[reason_category(risk)] += 1
                source_counter[source_attribution(risk)] += 1
            for solv in sample.get("solvability_reports") or []:
                for failure in solv.get("failure_codes") or []:
                    reason_counter[reason_category(failure)] += 1
                    source_counter[source_attribution(failure)] += 1
            rewrite_counter[compute_rewrite_resolvability(sample)] += 1
    reason_rows = [{"reason_category": k, "occurrence_count": v} for k, v in sorted(reason_counter.items())]
    source_rows = [{"source_attribution": k, "occurrence_count": v} for k, v in sorted(source_counter.items())]
    rewrite_rows = [{"rewrite_resolvability": k, "occurrence_count": v} for k, v in sorted(rewrite_counter.items())]
    return reason_rows, source_rows, rewrite_rows


def build_readme(tables):
    lines = [
        "# PPT Production Stats 2026-05-13",
        "",
        "This directory contains PPT-facing production statistics built from the current local canonical `agent-pipeline/outputs` and `agent-pipeline/ready` state.",
        "",
        "## Source Files",
        "",
        "- `outputs/*/run_*/summary.json`: canonical run-level usage and request timing.",
        "- `ready/*/summary.json`: outputs-to-ready conversion, dedup, release-gate totals, final ready counts.",
        "- `ready/*/selection_manifest.json`: sample-level release execution, `released_from_review`, `release_bucket`, `release_mode`, `candidate_json`, and `source_reason_codes`.",
        "- `ready/*/samples/*.json`: taxonomy (`problem_main_record.domain_tags`), rewrite strategy, solvability reports, and quality-risk/failure-code occurrences.",
        "- `configs/review_release_policies.yaml`: configured review-release buckets and release basis text.",
        "- `docs/review/*.json`: explicit candidate-set files used to measure `candidate_count` for explicit/manual release buckets.",
        "",
        "## Canonical Scope",
        "",
        "- Table 1 uses the union of `source_runs` referenced by current production `ready/*/summary.json` directories, so smoke/debug outputs are excluded by construction.",
        "- Tables 2-6 use the current production `ready/` top-level dataset directories.",
        "",
        "## Caveats",
        "",
        "- `candidate_count` and `actual_released_count` are intentionally separated. `candidate_count` comes from explicit candidate JSON metadata/list length when available; `actual_released_count` comes from `selection_manifest.kept_samples[].released_from_review`.",
        "- Some datasets have empty `structured_release_buckets` but non-zero explicit/manual release via `explicit_release_candidate_count` and `release_mode=explicit_candidate_subset`.",
        "- Table 3 keeps `candidate_count` and `actual_released_count` separate. For explicit buckets, `candidate_count` comes from candidate JSON metadata/list length; if the candidate JSON is older than the final ready execution, the two values may legitimately differ.",
        "- Table 5 level-1 taxonomy is mapped primarily from the final ready dataset package into a compact presentation taxonomy, with `domain_tags` used only as fallback for unmapped datasets.",
        "- Table 6 counts are reason occurrences, not unique samples. The source is primarily `selection_manifest.source_reason_codes`, with supplemental occurrence counting from sample `quality_risk_flags` and solvability `failure_codes`.",
        "- `rewrite_resolvability` is an occurrence-level operational bucket derived from sample rewrite strategy, audit trail, and solvability outcome: `rewrite_not_needed / rewritten_and_solvable / rewritten_but_still_risky`.",
        "",
        "## Files",
        "",
    ]
    for name, desc in tables:
        lines.append(f"- `{name}`: {desc}")
    lines.append("")
    return "\n".join(lines)


def main():
    ensure_dir(OUT_DIR)
    ready_dirs = production_ready_dirs()
    policy_rows = load_policy_rows()
    canonical_runs = canonical_run_paths_from_ready(ready_dirs)

    run_rows, run_totals = build_run_usage_summary(canonical_runs)
    conversion_rows = build_conversion_table(ready_dirs)
    release_rows = build_release_execution_table(ready_dirs, policy_rows)
    empty_bucket_rows = build_empty_bucket_table(ready_dirs)
    level1_rows, heatmap_rows, taxonomy_totals = build_taxonomy_tables(ready_dirs)
    reason_rows, source_rows, rewrite_rows = build_reason_source_tables(ready_dirs)

    write_csv(OUT_DIR / "01_run_level_usage_summary.csv", run_rows, [
        "run_id", "run_dir", "output_dir", "dataset", "processed_samples", "request_count",
        "successful_request_count", "failed_request_count", "retry_count", "text_request_count",
        "multimodal_request_count", "total_request_seconds", "prompt_tokens", "completion_tokens",
        "total_tokens", "cached_tokens", "reasoning_tokens", "requests_with_usage",
        "avg_requests_per_sample", "avg_request_seconds_per_sample", "avg_seconds_per_request",
    ])
    write_md_table(OUT_DIR / "01_run_level_usage_summary.md", "Canonical Production Outputs Run-Level Usage Summary", [
        {
            **run_totals,
            "avg_requests_per_sample": run_totals["avg_requests_per_sample"],
            "avg_request_seconds_per_sample": run_totals["avg_request_seconds_per_sample"],
            "avg_seconds_per_request": run_totals["avg_seconds_per_request"],
        }
    ], [
        "run_count", "processed_samples", "request_count", "successful_request_count",
        "failed_request_count", "retry_count", "text_request_count", "multimodal_request_count",
        "total_request_seconds", "prompt_tokens", "completion_tokens", "total_tokens",
        "cached_tokens", "reasoning_tokens", "requests_with_usage", "avg_requests_per_sample",
        "avg_request_seconds_per_sample", "avg_seconds_per_request",
    ], notes=["Aggregate over canonical production runs referenced by current production ready summaries."])

    write_csv(OUT_DIR / "02_dataset_level_outputs_to_ready_conversion.csv", conversion_rows, [
        "dataset", "processed", "pass", "review", "reject", "released_review",
        "dropped_review", "dedup_removed", "final_ready",
    ])
    write_md_table(OUT_DIR / "02_dataset_level_outputs_to_ready_conversion.md", "Dataset-Level Outputs-to-Ready Conversion", conversion_rows, [
        "dataset", "processed", "pass", "review", "reject", "released_review",
        "dropped_review", "dedup_removed", "final_ready",
    ])

    write_csv(OUT_DIR / "03_review_release_actual_execution.csv", release_rows, [
        "dataset", "bucket", "rule_type", "candidate_count", "actual_released_count", "release_basis",
    ])
    write_md_table(OUT_DIR / "03_review_release_actual_execution.md", "Review Release Actual Execution", release_rows, [
        "dataset", "bucket", "rule_type", "candidate_count", "actual_released_count", "release_basis",
    ], notes=["`candidate_count` is never substituted by `actual_released_count`; explicit buckets use candidate JSON counts when available."])

    write_csv(OUT_DIR / "04_empty_release_buckets.csv", empty_bucket_rows, [
        "dataset", "final_ready", "pass_original", "released_review", "dropped_review",
        "explicit_release_candidate_count", "explicit_or_manual_release_exists",
    ])
    write_md_table(OUT_DIR / "04_empty_release_buckets.md", "Datasets With Empty Release Buckets", empty_bucket_rows, [
        "dataset", "final_ready", "pass_original", "released_review", "dropped_review",
        "explicit_release_candidate_count", "explicit_or_manual_release_exists",
    ])

    write_csv(OUT_DIR / "05_ready_taxonomy_level1_distribution.csv", level1_rows, [
        "taxonomy_level1", "ready_samples",
    ])
    write_md_table(OUT_DIR / "05_ready_taxonomy_level1_distribution.md", "Final Ready Taxonomy Level-1 Distribution", level1_rows, [
        "taxonomy_level1", "ready_samples",
    ], notes=[f"total_ready_samples={taxonomy_totals['total_ready_samples']}", f"dataset_count={taxonomy_totals['dataset_count']}", f"taxonomy_class_count={taxonomy_totals['taxonomy_class_count']}"])
    heatmap_fields = ["dataset"] + [k for k in heatmap_rows[0].keys() if k != "dataset"] if heatmap_rows else ["dataset"]
    write_csv(OUT_DIR / "05_dataset_taxonomy_heatmap.csv", heatmap_rows, heatmap_fields)
    write_md_table(OUT_DIR / "05_dataset_taxonomy_heatmap.md", "Dataset × Taxonomy Heatmap", heatmap_rows, heatmap_fields)

    write_csv(OUT_DIR / "06_reason_category_distribution.csv", reason_rows, [
        "reason_category", "occurrence_count",
    ])
    write_md_table(OUT_DIR / "06_reason_category_distribution.md", "Review Reason Category Distribution", reason_rows, [
        "reason_category", "occurrence_count",
    ], notes=["Counts are reason occurrences, not unique samples."])
    write_csv(OUT_DIR / "06_source_attribution_distribution.csv", source_rows, [
        "source_attribution", "occurrence_count",
    ])
    write_md_table(OUT_DIR / "06_source_attribution_distribution.md", "Review Source Attribution Distribution", source_rows, [
        "source_attribution", "occurrence_count",
    ], notes=["Counts are occurrence-level attribution counts derived from reason/failure/risk signals."])
    write_csv(OUT_DIR / "06_rewrite_resolvability_distribution.csv", rewrite_rows, [
        "rewrite_resolvability", "occurrence_count",
    ])
    write_md_table(OUT_DIR / "06_rewrite_resolvability_distribution.md", "Rewrite-Resolvability Distribution", rewrite_rows, [
        "rewrite_resolvability", "occurrence_count",
    ], notes=["Counts are occurrence-level operational buckets over ready samples."])

    tables = [
        ("01_run_level_usage_summary.csv / .md", "canonical production outputs run-level usage summary"),
        ("02_dataset_level_outputs_to_ready_conversion.csv / .md", "dataset-level outputs-to-ready conversion"),
        ("03_review_release_actual_execution.csv / .md", "review release actual execution"),
        ("04_empty_release_buckets.csv / .md", "datasets with empty release buckets"),
        ("05_ready_taxonomy_level1_distribution.csv / .md", "level-1 taxonomy distribution"),
        ("05_dataset_taxonomy_heatmap.csv / .md", "dataset × taxonomy heatmap"),
        ("06_reason_category_distribution.csv / .md", "reason category distribution"),
        ("06_source_attribution_distribution.csv / .md", "source attribution distribution"),
        ("06_rewrite_resolvability_distribution.csv / .md", "rewrite-resolvability distribution"),
    ]
    (OUT_DIR / "README.md").write_text(build_readme(tables), encoding="utf-8")
    print(f"wrote {OUT_DIR}")


if __name__ == "__main__":
    main()
