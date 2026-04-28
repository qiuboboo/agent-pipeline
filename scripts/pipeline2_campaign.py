#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from benchmarkallinone.pipeline2.ready_loader import discover_ready_problems
from benchmarkallinone.pipeline2.utils import ensure_dir, read_json, utc_now, write_json

DEFAULT_STATE_FILE = PROJECT_ROOT / "pipeline2" / "campaign_controller" / "state.json"
DEFAULT_RUNS_ROOT = PROJECT_ROOT / "pipeline2" / "campaign_controller" / "runs"
DEFAULT_HISTORY_GLOB = "pipeline2/outputs*"
DEFAULT_MODEL = "gpt-5.4"
DEFAULT_BASE_URL = "https://www.msutools.cn"
DEFAULT_API_KEY_ENV = "OPENAI_API_KEY"
DEFAULT_WIRE_API = "responses"
DEFAULT_REASONING_EFFORT = "high"
DEFAULT_LOCAL_ENV_FILE = PROJECT_ROOT / "src" / "benchmarkallinone" / "pipeline2" / "configs" / "pipeline2.local.env"


@dataclass
class ProblemRecord:
    problem_id: str
    dataset_name: str
    sample_path: str
    source_problem_id: str
    subject: str
    question_text: str
    standard_answer: str

    def as_dict(self) -> Dict[str, Any]:
        return self.__dict__.copy()


def _load_state(path: Path) -> Dict[str, Any]:
    if path.exists():
        return read_json(path)
    return {
        "campaign_id": f"campaign_{utc_now().replace(':', '').replace('-', '')}",
        "ready_root": "",
        "project_root": str(PROJECT_ROOT),
        "problems": {},
        "dataset_order": [],
        "dataset_cursor": 0,
        "current_run": None,
        "history_roots": [],
        "updated_at": utc_now(),
    }


def _save_state(path: Path, state: Dict[str, Any]) -> None:
    state["updated_at"] = utc_now()
    write_json(path, state)


def _default_problem_state(problem: ProblemRecord) -> Dict[str, Any]:
    return {
        "problem_id": problem.problem_id,
        "dataset_name": problem.dataset_name,
        "sample_path": problem.sample_path,
        "source_problem_id": problem.source_problem_id,
        "subject": problem.subject,
        "question_text": problem.question_text,
        "standard_answer": problem.standard_answer,
        "status": "pending",  # pending|running|passed|failed|repair_exhausted
        "attempts_total": 0,
        "repair_attempts": 0,
        "max_repairs": 1,
        "last_batch_id": None,
        "last_run_dir": None,
        "last_output_root": None,
        "last_error_type": None,
        "last_error_message": None,
        "last_stage_cache_root": None,
        "last_result_source": None,
        "pass_output_path": None,
        "history": [],
    }


def _discover_problem_records(ready_root: Path, project_root: Path) -> List[ProblemRecord]:
    loaded = discover_ready_problems(
        ready_root=ready_root,
        workspace_root=project_root,
        include_manual_review=False,
        max_problems=0,
        max_images=3,
    )
    out: List[ProblemRecord] = []
    for item in loaded:
        runtime_problem = item.to_runtime_problem()
        out.append(
            ProblemRecord(
                problem_id=str(runtime_problem.get("problem_id", "")),
                dataset_name=str(runtime_problem.get("dataset_name", "")),
                sample_path=str(runtime_problem.get("sample_path", "")),
                source_problem_id=str(runtime_problem.get("source_problem_id", "")),
                subject=str(runtime_problem.get("subject", "")),
                question_text=str(runtime_problem.get("question_text", "")),
                standard_answer=str(runtime_problem.get("standard_answer", "")),
            )
        )
    return out


def _iter_history_output_roots(project_root: Path, patterns: Sequence[str]) -> Iterable[Path]:
    seen = set()
    for pattern in patterns:
        for path in project_root.glob(pattern):
            resolved = str(path.resolve())
            if resolved in seen or not path.exists() or not path.is_dir():
                continue
            seen.add(resolved)
            yield path.resolve()


def _record_history_item(problem_state: Dict[str, Any], item: Dict[str, Any]) -> None:
    history = problem_state.setdefault("history", [])
    marker = json.dumps(item, ensure_ascii=False, sort_keys=True)
    if marker not in {json.dumps(row, ensure_ascii=False, sort_keys=True) for row in history}:
        history.append(item)


def _ingest_pass(problem_state: Dict[str, Any], bundle_path: Path) -> None:
    problem_state["status"] = "passed"
    problem_state["pass_output_path"] = str(bundle_path)
    problem_state["last_result_source"] = "problem_bundle"
    problem_state["last_output_root"] = str(bundle_path.parents[1])
    problem_state["last_run_dir"] = str(bundle_path.parents[1])
    _record_history_item(
        problem_state,
        {
            "kind": "pass",
            "path": str(bundle_path),
            "updated_at": utc_now(),
        },
    )


def _ingest_failure(problem_state: Dict[str, Any], failure_path: Path, payload: Dict[str, Any]) -> None:
    if problem_state.get("status") != "passed":
        repair_attempts = int(problem_state.get("repair_attempts") or 0)
        max_repairs = int(problem_state.get("max_repairs") or 1)
        problem_state["status"] = "repair_exhausted" if repair_attempts >= max_repairs else "failed"
    problem_state["last_batch_id"] = payload.get("batch_id") or problem_state.get("last_batch_id")
    problem_state["last_run_dir"] = str(failure_path.parents[1])
    problem_state["last_output_root"] = str(failure_path.parents[1])
    problem_state["last_error_type"] = payload.get("error_type")
    problem_state["last_error_message"] = payload.get("error_message")
    stage_root = ((payload.get("stage_cache_summary") or {}).get("stage_cache_root"))
    if stage_root:
        problem_state["last_stage_cache_root"] = str(stage_root)
    _record_history_item(
        problem_state,
        {
            "kind": "failure",
            "path": str(failure_path),
            "error_type": payload.get("error_type"),
            "batch_id": payload.get("batch_id"),
            "updated_at": utc_now(),
        },
    )


def cmd_plan(args: argparse.Namespace) -> int:
    state_file = Path(args.state_file).resolve()
    project_root = Path(args.project_root).resolve()
    ready_root = Path(args.ready_root).resolve()
    state = _load_state(state_file)
    if args.reset:
        state = {
            "campaign_id": args.campaign_id or f"campaign_{utc_now().replace(':', '').replace('-', '')}",
            "ready_root": str(ready_root),
            "project_root": str(project_root),
            "problems": {},
            "dataset_order": [],
            "dataset_cursor": 0,
            "current_run": None,
            "history_roots": [],
            "updated_at": utc_now(),
        }
    else:
        state["campaign_id"] = args.campaign_id or state.get("campaign_id") or f"campaign_{utc_now().replace(':', '').replace('-', '')}"
        state["ready_root"] = str(ready_root)
        state["project_root"] = str(project_root)

    records = _discover_problem_records(ready_root=ready_root, project_root=project_root)
    seen_datasets: List[str] = []
    for rec in records:
        if not rec.problem_id:
            continue
        if rec.dataset_name and rec.dataset_name not in seen_datasets:
            seen_datasets.append(rec.dataset_name)
        existing = state["problems"].get(rec.problem_id)
        merged = _default_problem_state(rec)
        if isinstance(existing, dict):
            merged.update(existing)
            merged.update(rec.as_dict())
        state["problems"][rec.problem_id] = merged
    state["dataset_order"] = seen_datasets
    if args.history_root:
        state["history_roots"] = [str(Path(item).resolve()) for item in args.history_root]
    _save_state(state_file, state)
    print(
        json.dumps(
            {
                "state_file": str(state_file),
                "campaign_id": state["campaign_id"],
                "problem_count": len(state["problems"]),
                "dataset_count": len(state["dataset_order"]),
                "ready_root": str(ready_root),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def cmd_sync_history(args: argparse.Namespace) -> int:
    state_file = Path(args.state_file).resolve()
    state = _load_state(state_file)
    project_root = Path(state.get("project_root") or args.project_root or PROJECT_ROOT).resolve()
    patterns = args.history_glob or state.get("history_roots") or [DEFAULT_HISTORY_GLOB]
    if isinstance(patterns, str):
        patterns = [patterns]

    for problem_state in state.get("problems", {}).values():
        problem_state["max_repairs"] = int(args.max_repairs)

    scanned_roots = []
    for output_root in _iter_history_output_roots(project_root, list(patterns)):
        scanned_roots.append(str(output_root))
        problems_dir = output_root / "problems"
        if problems_dir.exists():
            for bundle_path in sorted(problems_dir.glob("*.json")):
                try:
                    payload = read_json(bundle_path)
                except Exception:
                    continue
                problem_id = str(((payload.get("problem_record") or {}).get("problem_id")) or bundle_path.stem)
                if not problem_id:
                    continue
                problem_state = state.setdefault("problems", {}).setdefault(problem_id, {"history": []})
                _ingest_pass(problem_state, bundle_path)
        error_dir = output_root / "problem_errors"
        if error_dir.exists():
            for failure_path in sorted(error_dir.glob("*.json")):
                try:
                    payload = read_json(failure_path)
                except Exception:
                    continue
                problem_id = str(payload.get("problem_id") or failure_path.stem)
                if not problem_id:
                    continue
                problem_state = state.setdefault("problems", {}).setdefault(problem_id, {"history": []})
                problem_state.setdefault("repair_attempts", 0)
                problem_state["max_repairs"] = int(args.max_repairs)
                _ingest_failure(problem_state, failure_path, payload)

    _save_state(state_file, state)
    counts = defaultdict(int)
    for item in state.get("problems", {}).values():
        counts[str(item.get("status") or "unknown")] += 1
    print(
        json.dumps(
            {
                "state_file": str(state_file),
                "scanned_roots": scanned_roots,
                "counts": dict(counts),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def _matches_filters(problem: Dict[str, Any], problem_ids: Sequence[str], datasets: Sequence[str]) -> bool:
    if problem_ids and str(problem.get("problem_id") or "") not in set(problem_ids):
        return False
    if datasets and str(problem.get("dataset_name") or "") not in set(datasets):
        return False
    return True


def _sort_problem_ids(problem_ids: Sequence[str], problems: Dict[str, Dict[str, Any]]) -> List[str]:
    return sorted(
        problem_ids,
        key=lambda pid: (
            str(problems[pid].get("dataset_name") or ""),
            str(problems[pid].get("sample_path") or ""),
            pid,
        ),
    )


def _round_robin_order(problem_ids: Sequence[str], state: Dict[str, Any]) -> List[str]:
    problems = state.get("problems", {})
    dataset_order = list(state.get("dataset_order") or [])
    if not dataset_order:
        dataset_order = sorted({str(problems[pid].get("dataset_name") or "") for pid in problem_ids})
        state["dataset_order"] = dataset_order
    buckets: Dict[str, deque[str]] = defaultdict(deque)
    for pid in _sort_problem_ids(problem_ids, problems):
        buckets[str(problems[pid].get("dataset_name") or "")].append(pid)
    if not dataset_order:
        return []
    cursor = int(state.get("dataset_cursor") or 0)
    ordered: List[str] = []
    total = len(problem_ids)
    while len(ordered) < total:
        progressed = False
        for step in range(len(dataset_order)):
            index = (cursor + step) % len(dataset_order)
            dataset_name = dataset_order[index]
            if buckets.get(dataset_name):
                ordered.append(buckets[dataset_name].popleft())
                cursor = (index + 1) % len(dataset_order)
                progressed = True
                break
        if not progressed:
            break
    state["dataset_cursor"] = cursor
    return ordered


def _choose_problem_ids(
    *,
    state: Dict[str, Any],
    source: str,
    strategy: str,
    count: int,
    problem_ids: Sequence[str],
    datasets: Sequence[str],
    max_repairs: int,
) -> List[str]:
    problems = state.get("problems", {})
    candidates: List[str] = []
    for pid, item in problems.items():
        if not _matches_filters(item, problem_ids, datasets):
            continue
        status = str(item.get("status") or "pending")
        attempts_total = int(item.get("attempts_total") or 0)
        repair_attempts = int(item.get("repair_attempts") or 0)
        has_cache = bool(item.get("last_stage_cache_root"))
        if source == "unseen":
            if status != "pending":
                continue
            if attempts_total != 0:
                continue
            candidates.append(pid)
        elif source == "repair":
            if status in {"passed", "running", "repair_exhausted"}:
                continue
            if attempts_total <= 0:
                continue
            if repair_attempts >= int(max_repairs):
                continue
            if not has_cache:
                continue
            candidates.append(pid)
        else:
            raise ValueError(f"Unknown source: {source}")
    if strategy == "round_robin":
        ordered = _round_robin_order(candidates, state)
    else:
        ordered = _sort_problem_ids(candidates, problems)
    if count > 0:
        return ordered[:count]
    return ordered


def _symlink_or_copy(src: Path, dst: Path) -> None:
    if dst.exists() or dst.is_symlink():
        if dst.is_dir() and not dst.is_symlink():
            shutil.rmtree(dst)
        else:
            dst.unlink()
    ensure_dir(dst.parent)
    try:
        dst.symlink_to(src)
    except Exception:
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)


def _prepare_single_problem_ready(problem: Dict[str, Any], run_root: Path, source_ready_root: Path, ready_root_name: str = "ready") -> Path:
    sample_path = Path(problem["sample_path"]).resolve()
    if not sample_path.exists():
        raise FileNotFoundError(f"Sample path does not exist: {sample_path}")
    dataset_root = sample_path.parent.parent
    try:
        relative_dataset_root = dataset_root.relative_to(source_ready_root.resolve())
    except Exception:
        relative_dataset_root = dataset_root.name
    target_ready_root = run_root / ready_root_name
    target_dataset_root = target_ready_root / relative_dataset_root
    ensure_dir(target_dataset_root)
    _symlink_or_copy(dataset_root / "samples", target_dataset_root / "samples")
    if (dataset_root / "artifacts").exists():
        _symlink_or_copy(dataset_root / "artifacts", target_dataset_root / "artifacts")
    return target_ready_root


def _build_yaml_config(
    *,
    ready_root: Path,
    output_root: Path,
    checkpoint_db_path: Path,
    base_url: str,
    api_key_env: str,
    model: str,
    reasoning_effort: str,
    wire_api: str,
    include_manual_review: bool,
    max_images_per_problem: int,
    stage_retry_attempts: int,
    stage_retry_backoff_seconds: float,
    problem_retry_attempts: int,
) -> Dict[str, Any]:
    return {
        "paths": {
            "ready_root": str(ready_root),
            "output_root": str(output_root),
            "checkpoint_db_path": str(checkpoint_db_path),
        },
        "runtime": {
            "include_manual_review": include_manual_review,
            "max_problems": 1,
            "max_problem_workers": 1,
            "max_images_per_problem": max_images_per_problem,
            "save_runtime_snapshots": True,
            "save_problem_bundles": True,
            "enable_trace_patch_writes": True,
            "enable_problem_structure_validation": True,
            "fail_on_problem_structure_validation": True,
            "stage_retry_attempts": stage_retry_attempts,
            "stage_retry_backoff_seconds": stage_retry_backoff_seconds,
            "problem_retry_attempts": problem_retry_attempts,
            "continue_on_problem_error": True,
        },
        "thresholds": {
            "method_score_thresholds": [0.33, 0.67],
            "novelty_total_threshold": 0.55,
            "novelty_required_threshold": 0.50,
        },
        "models": {
            "primary": {
                "name": "primary",
                "provider": "OpenAI",
                "base_url": base_url,
                "api_key": f"${{{api_key_env}}}",
                "model": model,
                "reasoning_effort": reasoning_effort,
                "wire_api": wire_api,
                "requires_openai_auth": True,
                "disable_response_storage": True,
                "temperature": 0.1,
                "timeout_seconds": 180,
                "enabled": True,
            },
            "fallback": None,
        },
    }


def _maybe_salvage_stage_cache(problem: Dict[str, Any], new_output_root: Path, batch_id: str) -> Optional[str]:
    stage_cache_root = problem.get("last_stage_cache_root")
    if not stage_cache_root:
        return None
    src_root = Path(stage_cache_root)
    if not src_root.exists():
        return None
    dst_root = new_output_root / "annotation_runtime" / "stage_cache" / batch_id / problem["problem_id"]
    if dst_root.exists():
        shutil.rmtree(dst_root)
    ensure_dir(dst_root.parent)
    shutil.copytree(src_root, dst_root)
    return str(dst_root)


def _load_env_file(path: Path) -> Dict[str, str]:
    if not path.exists():
        return {}
    env_map: Dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]
        env_map[key] = value
    unresolved = True
    max_passes = 5
    while unresolved and max_passes > 0:
        unresolved = False
        max_passes -= 1
        for key, value in list(env_map.items()):
            expanded = os.path.expandvars(value)
            for ref_key, ref_val in env_map.items():
                expanded = expanded.replace(f"${{{ref_key}}}", ref_val).replace(f"${ref_key}", ref_val)
            if expanded != value:
                env_map[key] = expanded
                if "$" in expanded:
                    unresolved = True
    return env_map


def _run_command(command: List[str], cwd: Path, env_file: Optional[Path] = None) -> int:
    env = os.environ.copy()
    if env_file is not None:
        env.update(_load_env_file(env_file))
    process = subprocess.run(command, cwd=str(cwd), env=env, check=False)
    return int(process.returncode)


def _assert_no_current_run(state: Dict[str, Any]) -> None:
    current = state.get("current_run")
    if isinstance(current, dict):
        raise RuntimeError(
            "There is already a current_run in state. Resume or finalize it first before launching a new batch of tasks."
        )


def _prepare_run(
    *,
    state: Dict[str, Any],
    state_file: Path,
    project_root: Path,
    runs_root: Path,
    ready_root: Path,
    problem: Dict[str, Any],
    run_kind: str,
    model: str,
    base_url: str,
    api_key_env: str,
    wire_api: str,
    reasoning_effort: str,
    max_images_per_problem: int,
    stage_retry_attempts: int,
    stage_retry_backoff_seconds: float,
    problem_retry_attempts: int,
) -> Dict[str, Any]:
    timestamp = utc_now().replace(":", "").replace("-", "")
    batch_id = f"p2ctl__{problem['dataset_name']}__{problem['problem_id']}__{run_kind}__{timestamp}".replace(" ", "_")
    run_root = runs_root / batch_id
    ensure_dir(run_root)

    single_ready_root = _prepare_single_problem_ready(problem, run_root, ready_root)
    output_root = run_root / "output"
    checkpoint_db_path = run_root / "runtime" / "pipeline_langgraph.sqlite"
    config_path = run_root / "config.yaml"
    config_payload = _build_yaml_config(
        ready_root=single_ready_root,
        output_root=output_root,
        checkpoint_db_path=checkpoint_db_path,
        base_url=base_url,
        api_key_env=api_key_env,
        model=model,
        reasoning_effort=reasoning_effort,
        wire_api=wire_api,
        include_manual_review=False,
        max_images_per_problem=max_images_per_problem,
        stage_retry_attempts=stage_retry_attempts,
        stage_retry_backoff_seconds=stage_retry_backoff_seconds,
        problem_retry_attempts=problem_retry_attempts,
    )
    config_path.write_text(yaml.safe_dump(config_payload, sort_keys=False, allow_unicode=True), encoding="utf-8")

    salvaged_cache_root = None
    if run_kind == "repair_once":
        salvaged_cache_root = _maybe_salvage_stage_cache(problem, output_root, batch_id)
        problem["repair_attempts"] = int(problem.get("repair_attempts") or 0) + 1

    problem["attempts_total"] = int(problem.get("attempts_total") or 0) + 1
    problem["status"] = "running"
    problem["last_batch_id"] = batch_id
    problem["last_run_dir"] = str(run_root)
    problem["last_output_root"] = str(output_root)
    problem["last_result_source"] = run_kind

    state["current_run"] = {
        "problem_id": problem["problem_id"],
        "dataset_name": problem.get("dataset_name"),
        "batch_id": batch_id,
        "run_kind": run_kind,
        "run_root": str(run_root),
        "config_path": str(config_path),
        "output_root": str(output_root),
        "checkpoint_db_path": str(checkpoint_db_path),
        "salvaged_cache_root": salvaged_cache_root,
    }
    _save_state(state_file, state)

    command = [
        str(project_root / ".venv" / "bin" / "python"),
        "run_pipeline2.py",
        "annotate",
        "--config",
        str(config_path),
        "--batch-id",
        batch_id,
    ]
    return {
        "problem_id": problem["problem_id"],
        "dataset_name": problem.get("dataset_name"),
        "batch_id": batch_id,
        "run_kind": run_kind,
        "run_root": str(run_root),
        "config_path": str(config_path),
        "output_root": str(output_root),
        "command": command,
        "salvaged_cache_root": salvaged_cache_root,
    }


def _finalize_current_run(state_file: Path) -> Dict[str, Any]:
    state = _load_state(state_file)
    current = state.get("current_run")
    if not isinstance(current, dict):
        return {"status": "no_current_run"}
    problem_id = str(current.get("problem_id") or "")
    output_root = Path(current.get("output_root") or "")
    if not problem_id or not output_root.exists():
        raise RuntimeError("Current run output root is missing or does not exist.")
    bundle_path = output_root / "problems" / f"{problem_id}.json"
    error_path = output_root / "problem_errors" / f"{problem_id}.json"
    problem_state = state.get("problems", {}).get(problem_id)
    if not isinstance(problem_state, dict):
        raise RuntimeError(f"Problem `{problem_id}` is missing in state.")
    if bundle_path.exists():
        _ingest_pass(problem_state, bundle_path)
    elif error_path.exists():
        payload = read_json(error_path)
        _ingest_failure(problem_state, error_path, payload)
    else:
        problem_state["status"] = "failed"
        problem_state["last_error_type"] = "MissingResultArtifacts"
        problem_state["last_error_message"] = f"Neither `{bundle_path}` nor `{error_path}` exists."
    state["current_run"] = None
    _save_state(state_file, state)
    return {
        "problem_id": problem_id,
        "status": problem_state.get("status"),
        "pass_output_path": problem_state.get("pass_output_path"),
        "last_error_type": problem_state.get("last_error_type"),
    }


def _preview_rows(state: Dict[str, Any], selected_problem_ids: Sequence[str], run_kind: str) -> List[Dict[str, Any]]:
    problems = state.get("problems", {})
    rows: List[Dict[str, Any]] = []
    for pid in selected_problem_ids:
        item = problems[pid]
        rows.append(
            {
                "problem_id": pid,
                "dataset_name": item.get("dataset_name"),
                "sample_path": item.get("sample_path"),
                "attempts_total": item.get("attempts_total"),
                "repair_attempts": item.get("repair_attempts"),
                "status": item.get("status"),
                "planned_run_kind": run_kind,
            }
        )
    return rows


def _execute_problem_batch(
    *,
    args: argparse.Namespace,
    state: Dict[str, Any],
    state_file: Path,
    selected_problem_ids: Sequence[str],
    run_kind: str,
) -> Dict[str, Any]:
    _assert_no_current_run(state)
    project_root = Path(state.get("project_root") or args.project_root or PROJECT_ROOT).resolve()
    ready_root = Path(state.get("ready_root") or args.ready_root or "").resolve()
    runs_root = Path(args.runs_root).resolve()
    results: List[Dict[str, Any]] = []
    for pid in selected_problem_ids:
        state = _load_state(state_file)
        problem = state["problems"][pid]
        prepared = _prepare_run(
            state=state,
            state_file=state_file,
            project_root=project_root,
            runs_root=runs_root,
            ready_root=ready_root,
            problem=problem,
            run_kind=run_kind,
            model=args.model,
            base_url=args.base_url,
            api_key_env=args.api_key_env,
            wire_api=args.wire_api,
            reasoning_effort=args.reasoning_effort,
            max_images_per_problem=args.max_images_per_problem,
            stage_retry_attempts=args.stage_retry_attempts,
            stage_retry_backoff_seconds=args.stage_retry_backoff_seconds,
            problem_retry_attempts=args.problem_retry_attempts,
        )
        if args.execute:
            prepared["exit_code"] = _run_command(
                prepared["command"],
                cwd=project_root,
                env_file=Path(getattr(args, "env_file", DEFAULT_LOCAL_ENV_FILE)).resolve(),
            )
            prepared["finalize"] = _finalize_current_run(state_file)
        results.append(prepared)
    return {
        "mode": run_kind,
        "count": len(selected_problem_ids),
        "items": results,
    }


def cmd_run_unseen(args: argparse.Namespace) -> int:
    state_file = Path(args.state_file).resolve()
    state = _load_state(state_file)
    selected = _choose_problem_ids(
        state=state,
        source="unseen",
        strategy=args.strategy,
        count=max(0, int(args.count)),
        problem_ids=args.problem_id,
        datasets=args.dataset,
        max_repairs=args.max_repairs,
    )
    if not args.execute:
        print(json.dumps({"mode": "run-unseen", "count": len(selected), "items": _preview_rows(state, selected, "fresh")}, ensure_ascii=False, indent=2))
        return 0
    result = _execute_problem_batch(args=args, state=state, state_file=state_file, selected_problem_ids=selected, run_kind="fresh")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_repair_errors(args: argparse.Namespace) -> int:
    state_file = Path(args.state_file).resolve()
    state = _load_state(state_file)
    selected = _choose_problem_ids(
        state=state,
        source="repair",
        strategy=args.strategy,
        count=max(0, int(args.limit)),
        problem_ids=args.problem_id,
        datasets=args.dataset,
        max_repairs=args.max_repairs,
    )
    if not args.execute:
        print(json.dumps({"mode": "repair-errors", "count": len(selected), "items": _preview_rows(state, selected, "repair_once")}, ensure_ascii=False, indent=2))
        return 0
    result = _execute_problem_batch(args=args, state=state, state_file=state_file, selected_problem_ids=selected, run_kind="repair_once")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_resume_interrupted(args: argparse.Namespace) -> int:
    state_file = Path(args.state_file).resolve()
    state = _load_state(state_file)
    current = state.get("current_run")
    if not isinstance(current, dict):
        print(json.dumps({"status": "no_current_run"}, ensure_ascii=False, indent=2))
        return 0
    project_root = Path(state.get("project_root") or args.project_root or PROJECT_ROOT).resolve()
    batch_id = str(current.get("batch_id") or "")
    config_path = str(current.get("config_path") or "")
    if not batch_id or not config_path:
        raise RuntimeError("Current run metadata is incomplete.")
    command = [
        str(project_root / ".venv" / "bin" / "python"),
        "run_pipeline2.py",
        "annotate",
        "--config",
        config_path,
        "--resume-batch-id",
        batch_id,
    ]
    result = {
        "mode": "resume-interrupted",
        "batch_id": batch_id,
        "problem_id": current.get("problem_id"),
        "config_path": config_path,
        "command": command,
    }
    if args.execute:
        result["exit_code"] = _run_command(
            command,
            cwd=project_root,
            env_file=Path(getattr(args, "env_file", DEFAULT_LOCAL_ENV_FILE)).resolve(),
        )
        result["finalize"] = _finalize_current_run(state_file)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_finalize_current(args: argparse.Namespace) -> int:
    print(json.dumps(_finalize_current_run(Path(args.state_file).resolve()), ensure_ascii=False, indent=2))
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    state = _load_state(Path(args.state_file).resolve())
    counts = defaultdict(int)
    by_dataset = defaultdict(lambda: defaultdict(int))
    for item in state.get("problems", {}).values():
        status = str(item.get("status") or "unknown")
        dataset = str(item.get("dataset_name") or "")
        counts[status] += 1
        by_dataset[dataset][status] += 1
    print(
        json.dumps(
            {
                "campaign_id": state.get("campaign_id"),
                "ready_root": state.get("ready_root"),
                "current_run": state.get("current_run"),
                "counts": dict(counts),
                "dataset_cursor": state.get("dataset_cursor"),
                "dataset_order": state.get("dataset_order"),
                "by_dataset": {k: dict(v) for k, v in by_dataset.items()},
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def _add_common_run_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--project-root", default=str(PROJECT_ROOT))
    parser.add_argument("--state-file", default=str(DEFAULT_STATE_FILE))
    parser.add_argument("--runs-root", default=str(DEFAULT_RUNS_ROOT))
    parser.add_argument("--strategy", choices=["round_robin", "sequential"], default="round_robin")
    parser.add_argument("--problem-id", action="append", default=[])
    parser.add_argument("--dataset", action="append", default=[])
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--api-key-env", default=DEFAULT_API_KEY_ENV)
    parser.add_argument("--env-file", default=str(DEFAULT_LOCAL_ENV_FILE))
    parser.add_argument("--wire-api", default=DEFAULT_WIRE_API)
    parser.add_argument("--reasoning-effort", default=DEFAULT_REASONING_EFFORT)
    parser.add_argument("--max-images-per-problem", type=int, default=3)
    parser.add_argument("--stage-retry-attempts", type=int, default=3)
    parser.add_argument("--stage-retry-backoff-seconds", type=float, default=1.0)
    parser.add_argument("--problem-retry-attempts", type=int, default=1)
    parser.add_argument("--max-repairs", type=int, default=1)
    parser.add_argument("--execute", action="store_true")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="External controller for pipeline2 full-ready campaigns.")
    sub = parser.add_subparsers(dest="command", required=True)

    plan = sub.add_parser("plan", help="Discover ready problems and initialize/update state.")
    plan.add_argument("--project-root", default=str(PROJECT_ROOT))
    plan.add_argument("--ready-root", required=True)
    plan.add_argument("--state-file", default=str(DEFAULT_STATE_FILE))
    plan.add_argument("--campaign-id", default=None)
    plan.add_argument("--reset", action="store_true")
    plan.add_argument("--history-root", action="append", default=[])
    plan.set_defaults(func=cmd_plan)

    sync = sub.add_parser("sync-history", help="Scan historical outputs and mark passed / failed problems globally.")
    sync.add_argument("--project-root", default=str(PROJECT_ROOT))
    sync.add_argument("--state-file", default=str(DEFAULT_STATE_FILE))
    sync.add_argument("--history-glob", action="append", default=[])
    sync.add_argument("--max-repairs", type=int, default=1)
    sync.set_defaults(func=cmd_sync_history)

    resume = sub.add_parser("resume-interrupted", help="Resume the last interrupted single-problem run.")
    resume.add_argument("--project-root", default=str(PROJECT_ROOT))
    resume.add_argument("--state-file", default=str(DEFAULT_STATE_FILE))
    resume.add_argument("--execute", action="store_true")
    resume.set_defaults(func=cmd_resume_interrupted)

    repair = sub.add_parser("repair-errors", help="Repair failed problems from cached stage state. Default: all eligible failures.")
    _add_common_run_args(repair)
    repair.add_argument("--limit", type=int, default=0, help="How many failed problems to repair. 0 = all eligible.")
    repair.set_defaults(func=cmd_repair_errors)

    unseen = sub.add_parser("run-unseen", help="Run problems that have never been processed before.")
    _add_common_run_args(unseen)
    unseen.add_argument("--count", type=int, default=1, help="How many unseen problems to run.")
    unseen.set_defaults(func=cmd_run_unseen)

    finalize = sub.add_parser("finalize-current", help="Ingest the current run's result artifacts into controller state.")
    finalize.add_argument("--state-file", default=str(DEFAULT_STATE_FILE))
    finalize.set_defaults(func=cmd_finalize_current)

    status = sub.add_parser("status", help="Show controller state summary.")
    status.add_argument("--state-file", default=str(DEFAULT_STATE_FILE))
    status.set_defaults(func=cmd_status)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
