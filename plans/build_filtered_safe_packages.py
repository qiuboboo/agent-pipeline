import json
import pathlib
import shutil
from collections import Counter

CONFIG = {
    "multi_physics": {
        "package_name": "run_filtered_multi_physics_safe",
        "dataset_name": "Multi-Physics",
        "subject": "物理",
        "source_runs": [
            pathlib.Path("outputs/multi_physics_300_500/run_1a0705c20a9e915f"),
        ],
        "detail": "Filtered safe subset from local Multi-Physics run 300:500 using pass+good-alignment+annotation-ready gating with additional risk exclusions.",
        "selection_file": "plans/multi_physics_filtered_candidate_ids.json",
    },
    "msearth_open_ended": {
        "package_name": "run_filtered_msearth_open_ended_000_300_safe",
        "dataset_name": "MSEarth Open Ended",
        "subject": "地球科学",
        "source_runs": [
            pathlib.Path("outputs/msearth_open_ended_000_300/run_1ecdd5243c8e7f21"),
        ],
        "detail": "Filtered safe subset from local MSEarth Open Ended run 000:300 using pass+good-alignment+annotation-ready gating with additional risk exclusions.",
        "selection_file": "plans/msearth_open_ended_filtered_candidate_ids.json",
    },
}

risk_exacts = {
    "text_only_without_visual_need",
    "metadata_inconsistency",
    "answer_label_only",
    "answer_is_choice_label_only",
    "placeholder_image_count_mismatch",
    "image_placeholder_count_mismatch",
    "options_embedded_in_image",
    "option_text_missing_but_visual_options_present",
    "options_not_textual_in_metadata",
    "option_text_not_in_metadata",
    "multi_placeholder_single_image",
}
risk_substr = [
    "missing_grounded_visual_path",
    "alignment_requires_review",
    "pure_image",
    "rewrite_unusable",
    "rewrite_variant_invalid",
    "rewrite_not_recoverable",
    "rewrite_not_convertible",
    "rewrite_unavailable",
    "rewrite_missing_usable_variant",
]
record_names = [
    "alignment_records.jsonl",
    "asset_records.jsonl",
    "asset_registry_records.jsonl",
    "candidate_pool_entries.jsonl",
    "candidate_problem_records.jsonl",
    "candidate_registration_records.jsonl",
    "clean_pool_entries.jsonl",
    "clean_problem_records.jsonl",
    "cleaning_records.jsonl",
    "field_audit_records.jsonl",
    "initial_scoring_records.jsonl",
    "node_records.jsonl",
    "normalization_records.jsonl",
    "normalized_assets.jsonl",
    "open_ended_problem_variants.jsonl",
    "problem_main_records.jsonl",
    "raw_asset_bundles.jsonl",
    "reject_records.jsonl",
    "rewrite_reports.jsonl",
    "solvability_reports.jsonl",
    "source_intake_records.jsonl",
    "text_structure_records.jsonl",
    "visual_structure_records.jsonl",
]

for dataset_key, cfg in CONFIG.items():
    package_root = pathlib.Path("ready") / dataset_key / cfg["package_name"]
    if package_root.exists():
        shutil.rmtree(package_root)

    safe_ids = []
    source_by_id = {}
    llm = Counter()
    rewrite_counts = Counter()
    record_buffers = {name: [] for name in record_names}
    started_at = None
    finished_at = None

    for run in cfg["source_runs"]:
        top_summary = json.loads((run / "summary.json").read_text(encoding="utf-8"))
        ds_summary = json.loads((run / "datasets" / dataset_key / "summary.json").read_text(encoding="utf-8"))
        starts = [x for x in [started_at, top_summary.get("started_at"), ds_summary.get("started_at")] if x is not None]
        finishes = [x for x in [finished_at, top_summary.get("finished_at"), ds_summary.get("finished_at")] if x is not None]
        started_at = min(starts) if starts else started_at
        finished_at = max(finishes) if finishes else finished_at
        for key, value in (top_summary.get("llm_usage") or {}).items():
            if isinstance(value, (int, float)):
                llm[key] += value
            elif key not in llm:
                llm[key] = value
        for sample_path in (run / "datasets" / dataset_key / "samples").glob("*.json"):
            data = json.loads(sample_path.read_text(encoding="utf-8"))
            pmr = data.get("problem_main_record", {})
            dec = pmr.get("clean_decision")
            al = pmr.get("alignment_status")
            ann = bool(pmr.get("annotation_ready"))
            reason_codes = set(pmr.get("clean_decision_reason_codes") or [])
            bad = any(r in risk_exacts for r in reason_codes) or any(any(s in r for s in risk_substr) for r in reason_codes)
            if dec == "pass" and al == "good" and ann and not bad:
                sid = sample_path.stem
                safe_ids.append(sid)
                source_by_id[sid] = run
                rewrite = pmr.get("rewrite_strategy")
                if rewrite:
                    rewrite_counts[rewrite] += 1

    safe_ids = sorted(set(safe_ids))
    selected = set(safe_ids)

    (package_root / "datasets" / dataset_key / "samples").mkdir(parents=True, exist_ok=True)
    (package_root / "datasets" / dataset_key / "records").mkdir(parents=True, exist_ok=True)
    (package_root / "datasets" / dataset_key / "artifacts" / "images").mkdir(parents=True, exist_ok=True)
    (package_root / "datasets" / dataset_key / "artifacts" / "crops").mkdir(parents=True, exist_ok=True)

    for sid in safe_ids:
        run = source_by_id[sid]
        src_root = run / "datasets" / dataset_key
        shutil.copy2(src_root / "samples" / f"{sid}.json", package_root / "datasets" / dataset_key / "samples" / f"{sid}.json")
        for p in (src_root / "artifacts" / "images").glob(f"{sid}*"):
            shutil.copy2(p, package_root / "datasets" / dataset_key / "artifacts" / "images" / p.name)
        for p in (src_root / "artifacts" / "crops").glob(f"{sid}*"):
            shutil.copy2(p, package_root / "datasets" / dataset_key / "artifacts" / "crops" / p.name)

    needles = [json.dumps(sid) for sid in selected]
    for run in cfg["source_runs"]:
        rec_root = run / "datasets" / dataset_key / "records"
        for name in record_names:
            p = rec_root / name
            if not p.exists():
                continue
            with p.open("r", encoding="utf-8") as fh:
                for line in fh:
                    raw = line.rstrip("\n")
                    if not raw.strip():
                        continue
                    try:
                        json.loads(raw)
                    except Exception:
                        continue
                    if any(n in raw for n in needles):
                        record_buffers[name].append(raw)

    for name, lines in record_buffers.items():
        out = package_root / "datasets" / dataset_key / "records" / name
        with out.open("w", encoding="utf-8", newline="\n") as fh:
            if lines:
                fh.write("\n".join(lines) + "\n")

    sample_count = len(safe_ids)
    ds_summary = {
        "dataset_key": dataset_key,
        "dataset_name": cfg["dataset_name"],
        "subject": cfg["subject"],
        "source_status": "available",
        "detail": cfg["detail"],
        "requested_samples": sample_count,
        "processed_samples": sample_count,
        "decision_counts": {"pass": sample_count, "review": 0, "reject": 0},
        "rewrite_strategy_counts": dict(sorted(rewrite_counts.items())),
        "records_dir": f"datasets/{dataset_key}/records",
        "sample_concurrency": 1,
        "started_at": started_at,
        "finished_at": finished_at,
        "elapsed_seconds": round(float(llm.get("total_request_seconds", 0.0)), 3),
        "llm_usage": dict(llm),
        "filtered_from": {
            "source_runs": [run.as_posix() for run in cfg["source_runs"]],
            "selected_samples": sample_count,
            "selection_rule": "clean_decision=pass AND alignment_status=good AND annotation_ready=true with additional risk exclusions",
            "selection_file": cfg["selection_file"],
        },
    }
    summary = {
        "pipeline_run_id": cfg["package_name"],
        "created_at": finished_at,
        "datasets": [{
            "dataset_key": dataset_key,
            "dataset_name": cfg["dataset_name"],
            "summary_path": f"datasets/{dataset_key}/summary.json",
        }],
        "sample_concurrency": 1,
        "started_at": started_at,
        "finished_at": finished_at,
        "elapsed_seconds": round(float(llm.get("total_request_seconds", 0.0)), 3),
        "llm_usage": dict(llm),
    }

    (package_root / "datasets" / dataset_key / "summary.json").write_text(json.dumps(ds_summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (package_root / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pathlib.Path(cfg["selection_file"]).write_text(json.dumps(safe_ids, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(dataset_key, cfg["package_name"], sample_count)
