from __future__ import annotations

import argparse
import atexit
import json
import logging
import re
import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from langgraph.checkpoint.memory import InMemorySaver
try:
    from langgraph.checkpoint.sqlite import SqliteSaver  # type: ignore
except ImportError:  # pragma: no cover - optional langgraph extra
    SqliteSaver = None  # type: ignore[assignment]
from langgraph.graph import END, START, StateGraph

from .agents import (
    AgentContractError,
    PipelineDataContractError,
    bind_evidence,
    build_patch,
    build_trace_mapping_index,
    detect_novelty,
    group_solutions,
    induce_nodes,
    judge_answer_equivalence,
    map_trace,
    plan_method_collection,
    polish_cot,
    repair_answer,
    solve_method,
    target_method_count_from_score,
    verify_cot,
)
from .annotation_modules import build_ptk_foundation, extract_claims_bundle
from .clients import ModelRouter
from .config import Pipeline2Config
from .models import BatchState, LoadedReadyProblem, MethodState, ProblemState
from .verification_modules import validate_problem_structure
from .ready_loader import ReadyDataContractError, discover_ready_problems
from .utils import ensure_dir, normalize_whitespace, read_json, stable_digest, utc_now, write_json, write_jsonl


@dataclass
class RuntimeContext:
    project_root: Path
    config: Pipeline2Config
    router: ModelRouter
    ready_root: Path
    output_root: Path
    checkpoint_db_path: Path
    runtime_dir: Path
    runtime_state_path: Path
    method_runs_dir: Path
    problem_outputs_dir: Path
    trace_eval_dir: Path
    incoming_traces_dir: Path
    mapping_reports_dir: Path
    novelty_candidates_dir: Path
    patches_dir: Path
    dataset_patches_dir: Path


RUNTIME_CONTEXT: Optional[RuntimeContext] = None
_SQLITE_CONNECTION: sqlite3.Connection | None = None
_SHARED_CHECKPOINTER: Any = None
_METHOD_GRAPH = None
_PROBLEM_GRAPH = None
_BATCH_GRAPH = None
LOGGER = logging.getLogger("benchmarkallinone.pipeline2")
_STAGE_NAME_PATTERN = re.compile(r"^\[([^\]]+)\]")
_TRANSIENT_STAGE_ERROR_MARKERS = (
    "timeout",
    "timed out",
    "read operation timed out",
    "retry deadline exceeded",
    "connection reset",
    "connectionreseterror",
    "brokenpipeerror",
    "remotedisconnected",
    "remote disconnected",
    "sslerror",
    "unexpected_eof_while_reading",
    "eof occurred in violation of protocol",
    "urlerror",
    "temporarily unavailable",
    "service unavailable",
    "http 408",
    "http 409",
    "http 429",
    "http 500",
    "http 502",
    "http 503",
    "http 504",
)


class StageRetryBudgetExhaustedError(RuntimeError):
    """Raised when a transient stage keeps failing after checkpointed retries."""


def _resolve_log_level(level_name: str) -> int:
    candidate = getattr(logging, str(level_name).upper(), None)
    return candidate if isinstance(candidate, int) else logging.INFO


def _setup_logging(ctx: RuntimeContext) -> None:
    level = _resolve_log_level(ctx.config.runtime.log_level)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(threadName)s | %(name)s | %(message)s")
    root_logger = logging.getLogger("benchmarkallinone.pipeline2")
    root_logger.setLevel(level)
    root_logger.propagate = False

    stream_handler_exists = any(
        isinstance(handler, logging.StreamHandler) and getattr(handler, "_pipeline2_stream_handler", False)
        for handler in root_logger.handlers
    )
    if not stream_handler_exists:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(level)
        stream_handler._pipeline2_stream_handler = True  # type: ignore[attr-defined]
        root_logger.addHandler(stream_handler)
    else:
        for handler in root_logger.handlers:
            if getattr(handler, "_pipeline2_stream_handler", False):
                handler.setLevel(level)
                handler.setFormatter(formatter)

    file_handler_path = ctx.runtime_dir / "pipeline2.log"
    for handler in list(root_logger.handlers):
        if getattr(handler, "_pipeline2_file_handler", False):
            handler_path = Path(getattr(handler, "baseFilename", "")) if getattr(handler, "baseFilename", None) else None
            if not ctx.config.runtime.log_to_file or handler_path != file_handler_path:
                root_logger.removeHandler(handler)
                handler.close()

    if ctx.config.runtime.log_to_file:
        file_handler_exists = any(
            getattr(handler, "_pipeline2_file_handler", False)
            and Path(getattr(handler, "baseFilename", "")) == file_handler_path
            for handler in root_logger.handlers
        )
        if not file_handler_exists:
            file_handler = logging.FileHandler(file_handler_path, encoding="utf-8")
            file_handler.setFormatter(formatter)
            file_handler.setLevel(level)
            file_handler._pipeline2_file_handler = True  # type: ignore[attr-defined]
            root_logger.addHandler(file_handler)


def get_context() -> RuntimeContext:
    if RUNTIME_CONTEXT is None:
        raise RuntimeError("pipeline2 runtime is not initialized")
    return RUNTIME_CONTEXT


def _ensure_checkpoint_parent_dir() -> None:
    ensure_dir(get_context().checkpoint_db_path.parent)


def _build_sqlite_connection() -> sqlite3.Connection:
    _ensure_checkpoint_parent_dir()
    connection = sqlite3.connect(
        str(get_context().checkpoint_db_path),
        check_same_thread=False,
        timeout=30,
    )
    connection.execute("PRAGMA journal_mode=WAL;")
    connection.execute("PRAGMA synchronous=NORMAL;")
    connection.execute("PRAGMA busy_timeout=30000;")
    return connection


def get_shared_checkpointer() -> Any:
    global _SQLITE_CONNECTION, _SHARED_CHECKPOINTER
    if _SHARED_CHECKPOINTER is None:
        if SqliteSaver is not None:
            _SQLITE_CONNECTION = _build_sqlite_connection()
            _SHARED_CHECKPOINTER = SqliteSaver(_SQLITE_CONNECTION)
        else:
            _SHARED_CHECKPOINTER = InMemorySaver()
    return _SHARED_CHECKPOINTER


def close_shared_checkpointer() -> None:
    global _SQLITE_CONNECTION, _SHARED_CHECKPOINTER
    if _SQLITE_CONNECTION is not None:
        _SQLITE_CONNECTION.close()
    _SQLITE_CONNECTION = None
    _SHARED_CHECKPOINTER = None


atexit.register(close_shared_checkpointer)


def _make_batch_thread_id(batch_id: str) -> str:
    return f"batch::{batch_id}"


def _make_problem_thread_id(batch_id: str, problem_id: str) -> str:
    return f"problem::{batch_id}::{problem_id}"


def _make_method_thread_id(batch_id: str, problem_id: str, method_id: str) -> str:
    return f"method::{batch_id}::{problem_id}::{method_id}"


def _make_thread_config(thread_id: str) -> Dict[str, Any]:
    return {"configurable": {"thread_id": thread_id}}


def _stage_cache_path(batch_id: str, problem_id: str, stage_name: str, item_key: str) -> Path:
    filename = f"{stable_digest([batch_id, problem_id, stage_name, item_key], length=16)}.json"
    return get_context().runtime_dir / "stage_cache" / batch_id / problem_id / stage_name / filename


def _load_stage_cache_record(batch_id: str, problem_id: str, stage_name: str, item_key: str) -> Optional[Dict[str, Any]]:
    path = _stage_cache_path(batch_id, problem_id, stage_name, item_key)
    if not path.exists():
        return None
    try:
        payload = read_json(path)
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def _write_stage_cache_record(batch_id: str, problem_id: str, stage_name: str, item_key: str, payload: Dict[str, Any]) -> None:
    write_json(_stage_cache_path(batch_id, problem_id, stage_name, item_key), payload)


def _thread_has_checkpoints(graph: Any, config: Dict[str, Any]) -> bool:
    try:
        return next(iter(graph.get_state_history(config)), None) is not None
    except Exception:
        return False


def _invoke_resumable_graph(graph: Any, initial_state: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    if not _thread_has_checkpoints(graph, config):
        return graph.invoke(initial_state, config)
    snapshot = graph.get_state(config)
    if getattr(snapshot, "next", None):
        return graph.invoke(None, config)
    values = snapshot.values
    if not isinstance(values, dict):
        raise RuntimeError("Checkpointed state is not a dict and cannot be resumed.")
    return values


def _stage_retry_attempt_budget() -> int:
    return max(1, int(get_context().config.runtime.stage_retry_attempts or 1))


def _stage_retry_sleep_seconds(attempt_index: int) -> float:
    base_seconds = max(0.0, float(get_context().config.runtime.stage_retry_backoff_seconds or 0.0))
    return min(10.0, base_seconds * max(1, attempt_index))


def _exception_message(exc: Exception) -> str:
    return normalize_whitespace(str(exc))


def _extract_stage_name(exc: Exception, default: str) -> str:
    message = _exception_message(exc)
    if not message:
        return default
    match = _STAGE_NAME_PATTERN.match(message)
    if match is None:
        return default
    stage_name = normalize_whitespace(match.group(1))
    return stage_name or default


def _is_transient_stage_error(exc: Exception) -> bool:
    if isinstance(exc, StageRetryBudgetExhaustedError):
        return False
    if not isinstance(exc, (AgentContractError, RuntimeError)):
        return False
    message = _exception_message(exc).lower()
    if not message:
        return False
    return any(marker in message for marker in _TRANSIENT_STAGE_ERROR_MARKERS)


def _invoke_graph_with_stage_retries(
    *,
    graph: Any,
    initial_state: Dict[str, Any],
    config: Dict[str, Any],
    scope_label: str,
) -> Dict[str, Any]:
    max_attempts = _stage_retry_attempt_budget()
    last_exc: Exception | None = None
    for attempt_index in range(1, max_attempts + 1):
        try:
            return _invoke_resumable_graph(graph=graph, initial_state=initial_state, config=config)
        except Exception as exc:
            last_exc = exc
            stage_name = _extract_stage_name(exc, default=scope_label)
            is_transient = _is_transient_stage_error(exc)
            LOGGER.warning(
                "[stage-retry-check] scope=%s stage=%s attempt=%s/%s transient=%s error_type=%s error=%s",
                scope_label,
                stage_name,
                attempt_index,
                max_attempts,
                is_transient,
                type(exc).__name__,
                str(exc),
            )
            if not is_transient:
                raise
            if attempt_index >= max_attempts:
                raise StageRetryBudgetExhaustedError(
                    f"[{stage_name}] Same-stage retry budget exhausted after {max_attempts} attempt(s); checkpoint resume did not recover the transient failure. last_error={type(exc).__name__}: {exc}"
                ) from exc
            sleep_seconds = _stage_retry_sleep_seconds(attempt_index)
            LOGGER.info(
                "[stage-retry-resume] scope=%s stage=%s next_attempt=%s/%s sleep_seconds=%.2f",
                scope_label,
                stage_name,
                attempt_index + 1,
                max_attempts,
                sleep_seconds,
            )
            if sleep_seconds > 0:
                time.sleep(sleep_seconds)
    if last_exc is None:
        raise RuntimeError(f"{scope_label} failed before any retry attempt could be recorded.")
    raise last_exc


def _determine_method_count(initial_multi_solution_score: Any) -> int:
    return target_method_count_from_score(
        initial_multi_solution_score,
        get_context().config.thresholds.method_score_thresholds,
    )


def _build_empty_method(method_id: int, planned: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "method_id": str(method_id),
        "method_draft": normalize_whitespace(planned.get("method_draft", "")),
        "CoT_raw": "",
        "model_answer": "",
        "is_answer_match": False,
        "answer_match_reason": "",
        "answer_match_part_results": [],
        "CoT_answer_check_final": "",
        "answer_answer_check_final": "",
        "CoT_verify_0": False,
        "CoT_qualify_0": "",
        "CoT_after_polish_1": "",
        "CoT_verify_1": False,
        "CoT_qualify_1": "",
        "CoT_after_polish_2": "",
        "CoT_verify_2": False,
        "CoT_qualify_2": "",
        "CoT_after_polish_3": "",
        "CoT_verify_3": False,
        "CoT_qualify_3": "",
        "is_final_CoT_qualified": False,
        "CoT_final": "",
        "planner_metadata": {
            "distinctiveness_rationale": normalize_whitespace(planned.get("distinctiveness_rationale", "")),
            "image_role": normalize_whitespace(planned.get("image_role", "")),
            "text_role": normalize_whitespace(planned.get("text_role", "")),
            "knowledge_role": normalize_whitespace(planned.get("knowledge_role", "")),
        },
        "solver_metadata": {},
        "verify_reports": [],
    }


def _write_method_snapshot(batch_id: str, problem_id: str, method: Dict[str, Any]) -> None:
    ctx = get_context()
    if not ctx.config.runtime.save_runtime_snapshots:
        return
    target = ctx.method_runs_dir / batch_id / problem_id / f"method_{method.get('method_id', 'unknown')}.json"
    write_json(target, method)


def _generate_cot_node(state: MethodState) -> Dict[str, Any]:
    method = deepcopy(state["method"])
    problem = state["problem"]
    payload = solve_method(get_context().router, problem=problem, method=method)
    method["CoT_raw"] = payload["cot"]
    method["model_answer"] = payload["answer"]
    method["solver_metadata"] = payload.get("meta", {})
    return {
        "batch_id": state["batch_id"],
        "problem": problem,
        "method": method,
        "current_cot_text": payload["cot"],
        "current_cot_key": "CoT_raw",
        "current_answer": payload["answer"],
    }


def _answer_check_node(state: MethodState) -> Dict[str, Any]:
    method = deepcopy(state["method"])
    problem = state["problem"]
    current_cot_text = state.get("current_cot_text", method.get("CoT_raw", ""))
    current_answer = state.get("current_answer", method.get("model_answer", ""))

    judgment = judge_answer_equivalence(get_context().router, problem, current_answer, current_cot_text)
    method["is_answer_match"] = bool(judgment.get("is_equivalent"))
    method["answer_match_reason"] = normalize_whitespace(judgment.get("reason", ""))
    method["answer_match_part_results"] = judgment.get("part_results") or []

    if method["is_answer_match"]:
        method["CoT_answer_check_final"] = current_cot_text
        method["answer_answer_check_final"] = current_answer
        return {
            "batch_id": state["batch_id"],
            "problem": problem,
            "method": method,
            "current_cot_text": current_cot_text,
            "current_cot_key": "CoT_answer_check_final",
            "current_answer": current_answer,
        }

    repaired = repair_answer(get_context().router, problem, method, current_cot_text, current_answer)
    recheck = judge_answer_equivalence(get_context().router, problem, repaired["answer"], repaired["cot"])
    method["is_answer_match"] = bool(recheck.get("is_equivalent"))
    method["answer_match_reason"] = normalize_whitespace(recheck.get("reason", "")) or normalize_whitespace(repaired.get("notes", ""))
    method["answer_match_part_results"] = recheck.get("part_results") or []
    method["CoT_answer_check_final"] = repaired["cot"]
    method["answer_answer_check_final"] = repaired["answer"]
    return {
        "batch_id": state["batch_id"],
        "problem": problem,
        "method": method,
        "current_cot_text": repaired["cot"],
        "current_cot_key": "CoT_answer_check_final",
        "current_answer": repaired["answer"],
    }


def _verify_round(state: MethodState, round_index: int) -> Dict[str, Any]:
    method = deepcopy(state["method"])
    problem = state["problem"]
    result = verify_cot(get_context().router, problem, method, state.get("current_cot_text", ""))
    verify_key = f"CoT_verify_{round_index}"
    qualify_key = f"CoT_qualify_{round_index}"
    method[verify_key] = bool(result.get("verify_pass")) and bool(method.get("is_answer_match"))
    method[qualify_key] = normalize_whitespace(result.get("critic_suggestions", ""))
    verify_meta = result.get("meta") or {}
    method.setdefault("verify_reports", []).append({
        "round_index": round_index,
        "verify_pass": method[verify_key],
        "critic_suggestions": method[qualify_key],
        "major_failures": result.get("major_failures") or [],
        "extractability_score": result.get("extractability_score"),
        "grounding_score": result.get("grounding_score"),
        "method_fidelity_score": result.get("method_fidelity_score"),
        "llm_request_mode": verify_meta.get("_llm_request_mode"),
        "llm_endpoint_name": verify_meta.get("_llm_endpoint_name"),
        "llm_elapsed_seconds": verify_meta.get("_llm_elapsed_seconds"),
    })
    return {"method": method}


def _verify_round_0_node(state: MethodState) -> Dict[str, Any]:
    return _verify_round(state, 0)


def _verify_round_1_node(state: MethodState) -> Dict[str, Any]:
    return _verify_round(state, 1)


def _verify_round_2_node(state: MethodState) -> Dict[str, Any]:
    return _verify_round(state, 2)


def _verify_round_3_node(state: MethodState) -> Dict[str, Any]:
    return _verify_round(state, 3)


def _polish_round(state: MethodState, round_index: int, suggestion_key: str, output_key: str) -> Dict[str, Any]:
    method = deepcopy(state["method"])
    problem = state["problem"]
    result = polish_cot(
        get_context().router,
        problem,
        method,
        state.get("current_cot_text", ""),
        method.get(suggestion_key, ""),
    )
    method[output_key] = result["polished_cot"]
    return {
        "batch_id": state["batch_id"],
        "problem": problem,
        "method": method,
        "current_cot_text": result["polished_cot"],
        "current_cot_key": output_key,
        "current_answer": state.get("current_answer", method.get("answer_answer_check_final", "")),
    }


def _polish_round_1_node(state: MethodState) -> Dict[str, Any]:
    return _polish_round(state, 1, "CoT_qualify_0", "CoT_after_polish_1")


def _polish_round_2_node(state: MethodState) -> Dict[str, Any]:
    return _polish_round(state, 2, "CoT_qualify_1", "CoT_after_polish_2")


def _polish_round_3_node(state: MethodState) -> Dict[str, Any]:
    return _polish_round(state, 3, "CoT_qualify_2", "CoT_after_polish_3")


def _route_after_verify_0(state: MethodState) -> str:
    return "finalize_method" if state["method"].get("CoT_verify_0") else "polish_round_1"


def _route_after_verify_1(state: MethodState) -> str:
    return "finalize_method" if state["method"].get("CoT_verify_1") else "polish_round_2"


def _route_after_verify_2(state: MethodState) -> str:
    return "finalize_method" if state["method"].get("CoT_verify_2") else "polish_round_3"


def _finalize_method_node(state: MethodState) -> Dict[str, Any]:
    method = deepcopy(state["method"])
    if not method.get("is_answer_match"):
        method["is_final_CoT_qualified"] = False
        method["CoT_final"] = method.get("CoT_answer_check_final") or method.get("CoT_raw", "")
        return {"method": method}

    final_candidates = [
        ("CoT_verify_0", "CoT_answer_check_final"),
        ("CoT_verify_1", "CoT_after_polish_1"),
        ("CoT_verify_2", "CoT_after_polish_2"),
        ("CoT_verify_3", "CoT_after_polish_3"),
    ]
    for verify_key, cot_key in final_candidates:
        if method.get(verify_key):
            method["is_final_CoT_qualified"] = True
            method["CoT_final"] = method.get(cot_key, "")
            return {"method": method}

    method["is_final_CoT_qualified"] = False
    method["CoT_final"] = (
        method.get("CoT_after_polish_3")
        or method.get("CoT_after_polish_2")
        or method.get("CoT_after_polish_1")
        or method.get("CoT_answer_check_final", "")
    )
    return {"method": method}


def build_method_graph():
    global _METHOD_GRAPH
    if _METHOD_GRAPH is not None:
        return _METHOD_GRAPH
    graph = StateGraph(MethodState)
    graph.add_node("generate_cot", _generate_cot_node)
    graph.add_node("answer_check", _answer_check_node)
    graph.add_node("verify_round_0", _verify_round_0_node)
    graph.add_node("polish_round_1", _polish_round_1_node)
    graph.add_node("verify_round_1", _verify_round_1_node)
    graph.add_node("polish_round_2", _polish_round_2_node)
    graph.add_node("verify_round_2", _verify_round_2_node)
    graph.add_node("polish_round_3", _polish_round_3_node)
    graph.add_node("verify_round_3", _verify_round_3_node)
    graph.add_node("finalize_method", _finalize_method_node)
    graph.add_edge(START, "generate_cot")
    graph.add_edge("generate_cot", "answer_check")
    graph.add_edge("answer_check", "verify_round_0")
    graph.add_conditional_edges("verify_round_0", _route_after_verify_0, {"finalize_method": "finalize_method", "polish_round_1": "polish_round_1"})
    graph.add_edge("polish_round_1", "verify_round_1")
    graph.add_conditional_edges("verify_round_1", _route_after_verify_1, {"finalize_method": "finalize_method", "polish_round_2": "polish_round_2"})
    graph.add_edge("polish_round_2", "verify_round_2")
    graph.add_conditional_edges("verify_round_2", _route_after_verify_2, {"finalize_method": "finalize_method", "polish_round_3": "polish_round_3"})
    graph.add_edge("polish_round_3", "verify_round_3")
    graph.add_edge("verify_round_3", "finalize_method")
    graph.add_edge("finalize_method", END)
    _METHOD_GRAPH = graph.compile(checkpointer=get_shared_checkpointer())
    return _METHOD_GRAPH


def _prepare_methods_node(state: ProblemState) -> Dict[str, Any]:
    problem = deepcopy(state["problem"])
    if problem.get("method"):
        return {"batch_id": state["batch_id"], "problem": problem}
    target_method_count = _determine_method_count(problem.get("initial_multi_solution_score"))
    planning_bundle = plan_method_collection(
        get_context().router,
        problem=problem,
        target_method_count=target_method_count,
        max_attempts=3,
    )
    problem["method"] = [
        _build_empty_method(method_id=index, planned=planned)
        for index, planned in enumerate(planning_bundle["methods"], start=1)
    ]
    problem["method_planning_metadata"] = {
        key: value for key, value in planning_bundle.items() if key != "methods"
    }
    return {"batch_id": state["batch_id"], "problem": problem}


def _build_ptk_node(state: ProblemState) -> Dict[str, Any]:
    batch_id = state["batch_id"]
    problem = deepcopy(state["problem"])
    problem_id = str(problem.get("problem_id", "unknown_problem"))
    cached_bundle = _load_stage_cache_record(batch_id, problem_id, "ptk_foundation", "bundle")
    if (
        isinstance(cached_bundle, dict)
        and isinstance(cached_bundle.get("problem_record"), dict)
        and isinstance(cached_bundle.get("p_facts"), list)
        and isinstance(cached_bundle.get("t_facts"), list)
        and isinstance(cached_bundle.get("k_atoms"), list)
        and isinstance(cached_bundle.get("audit"), dict)
    ):
        ptk_bundle = deepcopy(cached_bundle)
        print(
            f"[pipeline2 stage-cache] Reused PTK foundation for problem `{problem_id}`.",
            flush=True,
        )
    else:
        progress_state = _load_stage_cache_record(batch_id, problem_id, "ptk_foundation_progress", "bundle")
        if isinstance(progress_state, dict) and progress_state:
            print(
                f"[pipeline2 stage-cache] Resuming PTK foundation progress for problem `{problem_id}`.",
                flush=True,
            )

        def _save_ptk_progress(
            payload: Dict[str, Any],
            *,
            _batch_id: str = batch_id,
            _problem_id: str = problem_id,
        ) -> None:
            _write_stage_cache_record(_batch_id, _problem_id, "ptk_foundation_progress", "bundle", payload)

        ptk_bundle = build_ptk_foundation(
            get_context().router,
            problem,
            max_repair_rounds=4,
            progress_state=progress_state,
            save_progress=_save_ptk_progress,
        )
        _write_stage_cache_record(batch_id, problem_id, "ptk_foundation", "bundle", ptk_bundle)
    return {
        "problem": problem,
        "problem_record": ptk_bundle["problem_record"],
        "p_facts": ptk_bundle["p_facts"],
        "t_facts": ptk_bundle["t_facts"],
        "k_atoms": ptk_bundle["k_atoms"],
        "ptk_audit": ptk_bundle["audit"],
    }


def _run_single_method(batch_id: str, problem: Dict[str, Any], method: Dict[str, Any]) -> Dict[str, Any]:
    method_graph = build_method_graph()
    problem_id = str(problem.get("problem_id", "unknown_problem"))
    method_id = str(method.get("method_id", "unknown_method"))
    config = _make_thread_config(_make_method_thread_id(batch_id, problem_id, method_id))
    result = _invoke_graph_with_stage_retries(
        graph=method_graph,
        initial_state={
            "batch_id": batch_id,
            "problem": deepcopy(problem),
            "method": deepcopy(method),
        },
        config=config,
        scope_label=f"method `{method_id}` for problem `{problem_id}`",
    )
    return result["method"]


def _run_methods_node(state: ProblemState) -> Dict[str, Any]:
    batch_id = state["batch_id"]
    problem = deepcopy(state["problem"])
    problem_id = str(problem.get("problem_id", "unknown_problem"))
    processed_methods: List[Dict[str, Any]] = []
    for method in problem.get("method", []):
        method_id = str(method.get("method_id", "unknown_method"))
        cached_record = _load_stage_cache_record(batch_id, problem_id, "method_results", method_id)
        cached_method = cached_record.get("method") if isinstance(cached_record, dict) else None
        if isinstance(cached_method, dict) and str(cached_method.get("method_id", "")) == method_id:
            processed = deepcopy(cached_method)
            print(
                f"[pipeline2 stage-cache] Reused method result for problem `{problem_id}` method `{method_id}`.",
                flush=True,
            )
        else:
            processed = _run_single_method(batch_id=batch_id, problem=problem, method=method)
            _write_stage_cache_record(batch_id, problem_id, "method_results", method_id, {"method": processed})
        processed_methods.append(processed)
        _write_method_snapshot(batch_id, problem_id, processed)
    problem["method"] = processed_methods
    return {"batch_id": batch_id, "problem": problem}


def _namespace_claims_for_method(method_id: str, claims: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    method_token = normalize_whitespace(method_id) or "unknown_method"
    prefix = f"m{method_token}__"
    raw_to_namespaced: Dict[str, str] = {}
    for claim in claims:
        if not isinstance(claim, dict):
            continue
        raw_claim_id = str(claim.get("claim_id", "")).strip()
        if not raw_claim_id:
            continue
        namespaced_claim_id = raw_claim_id if raw_claim_id.startswith(prefix) else f"{prefix}{raw_claim_id}"
        raw_to_namespaced[raw_claim_id] = namespaced_claim_id
        raw_to_namespaced[namespaced_claim_id] = namespaced_claim_id

    normalized_claims: List[Dict[str, Any]] = []
    for claim in claims:
        if not isinstance(claim, dict):
            continue
        raw_claim_id = str(claim.get("claim_id", "")).strip()
        normalized_claim = deepcopy(claim)
        normalized_claim["method_id"] = method_id
        normalized_claim["claim_id"] = raw_to_namespaced.get(raw_claim_id, f"{prefix}{raw_claim_id}") if raw_claim_id else ""
        normalized_claim["depends_on"] = [
            raw_to_namespaced.get(str(dep).strip(), f"{prefix}{str(dep).strip()}")
            for dep in (claim.get("depends_on") or [])
            if str(dep).strip()
        ]
        normalized_claims.append(normalized_claim)
    return normalized_claims


def _extract_claims_node(state: ProblemState) -> Dict[str, Any]:
    batch_id = state["batch_id"]
    problem = deepcopy(state["problem"])
    problem_id = str(problem.get("problem_id", "unknown_problem"))
    qualified_methods: List[Dict[str, Any]] = []
    claim_sequences: List[Dict[str, Any]] = []
    claim_extraction_failures: List[Dict[str, Any]] = []
    cot_variants: List[Dict[str, Any]] = []
    for method in problem.get("method", []):
        method_id = str(method.get("method_id", ""))
        variant_record = {
            "problem_id": problem.get("problem_id"),
            "method_id": method.get("method_id"),
            "method_draft": method.get("method_draft"),
            "cot_raw": method.get("CoT_raw", ""),
            "cot_final": method.get("CoT_final", ""),
            "answer_final": method.get("answer_answer_check_final", method.get("model_answer", "")),
            "is_answer_match": bool(method.get("is_answer_match")),
            "is_final_CoT_qualified": bool(method.get("is_final_CoT_qualified")),
            "claim_extraction_status": "not_attempted",
            "claim_extraction_error": "",
        }
        cot_variants.append(variant_record)
        if not (method.get("is_answer_match") and method.get("is_final_CoT_qualified")):
            method["claim_extraction_status"] = "skipped_unqualified_cot"
            method["claim_extraction_error"] = ""
            variant_record["claim_extraction_status"] = "skipped_unqualified_cot"
            continue
        qualified_methods.append(method)
        method["claim_extraction_status"] = "pending"
        cached_bundle = _load_stage_cache_record(batch_id, problem_id, "claim_bundles", method_id)
        try:
            if (
                isinstance(cached_bundle, dict)
                and str(cached_bundle.get("method_id", "")) == method_id
                and isinstance(cached_bundle.get("claims"), list)
                and isinstance(cached_bundle.get("audit"), dict)
            ):
                claim_bundle = deepcopy(cached_bundle)
                print(
                    f"[pipeline2 stage-cache] Reused claim bundle for problem `{problem_id}` method `{method_id}`.",
                    flush=True,
                )
            else:
                progress_state = _load_stage_cache_record(batch_id, problem_id, "claim_bundle_progress", method_id)
                if isinstance(progress_state, dict) and progress_state:
                    print(
                        f"[pipeline2 stage-cache] Resuming claim bundle progress for problem `{problem_id}` method `{method_id}`.",
                        flush=True,
                    )

                def _save_claim_progress(
                    payload: Dict[str, Any],
                    *,
                    _batch_id: str = batch_id,
                    _problem_id: str = problem_id,
                    _method_id: str = method_id,
                ) -> None:
                    _write_stage_cache_record(_batch_id, _problem_id, "claim_bundle_progress", _method_id, payload)

                claim_bundle = extract_claims_bundle(
                    get_context().router,
                    problem,
                    method,
                    method.get("CoT_final", ""),
                    state.get("p_facts", []),
                    state.get("t_facts", []),
                    state.get("k_atoms", []),
                    max_repair_rounds=4,
                    progress_state=progress_state,
                    save_progress=_save_claim_progress,
                )
                _write_stage_cache_record(batch_id, problem_id, "claim_bundles", method_id, claim_bundle)
        except PipelineDataContractError as exc:
            latest_progress = _load_stage_cache_record(batch_id, problem_id, "claim_bundle_progress", method_id)
            latest_audit_rounds = latest_progress.get("audit_rounds", []) if isinstance(latest_progress, dict) else []
            latest_claims = latest_progress.get("claims", []) if isinstance(latest_progress, dict) else []
            failure_audit = {
                "component": "ClaimExtractionAgent",
                "problem_id": problem.get("problem_id"),
                "method_id": method.get("method_id"),
                "passed": False,
                "error_type": type(exc).__name__,
                "error_message": str(exc),
                "rounds": latest_audit_rounds if isinstance(latest_audit_rounds, list) else [],
                "partial_claim_count": len(latest_claims) if isinstance(latest_claims, list) else 0,
            }
            claim_extraction_failures.append(
                {
                    "problem_id": problem.get("problem_id"),
                    "method_id": method.get("method_id"),
                    "method_draft": method.get("method_draft"),
                    "cot_final": method.get("CoT_final", ""),
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                    "claim_audit": failure_audit,
                }
            )
            method["claim_extraction_status"] = "failed"
            method["claim_extraction_error"] = str(exc)
            variant_record["claim_extraction_status"] = "failed"
            variant_record["claim_extraction_error"] = str(exc)
            print(
                f"[pipeline2 annotate] Claim extraction skipped for problem `{problem_id}` method `{method_id}` after explicit contract failure: {exc}",
                flush=True,
            )
            continue
        claim_sequences.append(
            {
                "problem_id": problem.get("problem_id"),
                "method_id": method.get("method_id"),
                "method_draft": method.get("method_draft"),
                "cot_final": method.get("CoT_final", ""),
                "answer_final": method.get("answer_answer_check_final", ""),
                "claims": _namespace_claims_for_method(method_id, claim_bundle["claims"]),
                "claim_audit": claim_bundle["audit"],
            }
        )
        method["claim_extraction_status"] = "passed"
        method["claim_extraction_error"] = ""
        variant_record["claim_extraction_status"] = "passed"
    if not qualified_methods:
        raise PipelineDataContractError(
            f"[ClaimExtractionGate] Problem `{problem.get('problem_id', 'unknown_problem')}` has no qualified methods; cannot continue to node extraction."
        )
    if not claim_sequences:
        failed_method_ids = ", ".join(str(item.get("method_id", "")) for item in claim_extraction_failures if item.get("method_id"))
        raise PipelineDataContractError(
            f"[ClaimExtractionGate] Problem `{problem.get('problem_id', 'unknown_problem')}` had qualified methods but none produced a valid claim sequence. Failed method_ids: {failed_method_ids or 'unknown'}."
        )
    if claim_extraction_failures:
        failed_method_ids = ", ".join(str(item.get("method_id", "")) for item in claim_extraction_failures if item.get("method_id"))
        raise PipelineDataContractError(
            f"[ClaimExtractionGate] Problem `{problem.get('problem_id', 'unknown_problem')}` had one or more qualified methods fail claim extraction. Failed method_ids: {failed_method_ids or 'unknown'}."
        )
    return {
        "problem": problem,
        "cot_variants": cot_variants,
        "claim_sequences": claim_sequences,
        "claim_extraction_failures": claim_extraction_failures,
        "problem_record": state.get("problem_record", {}),
        "p_facts": state.get("p_facts", []),
        "t_facts": state.get("t_facts", []),
        "k_atoms": state.get("k_atoms", []),
        "ptk_audit": state.get("ptk_audit", {}),
    }


def _induce_nodes_node(state: ProblemState) -> Dict[str, Any]:
    problem = deepcopy(state["problem"])
    all_claims: List[Dict[str, Any]] = []
    for sequence in state.get("claim_sequences", []):
        all_claims.extend(sequence.get("claims") or [])
    r_nodes, claim_mappings = induce_nodes(
        get_context().router,
        problem,
        all_claims,
        state.get("p_facts", []),
        state.get("t_facts", []),
        state.get("k_atoms", []),
    )
    return {
        "problem": problem,
        "r_nodes": r_nodes,
        "claim_mappings": claim_mappings,
    }


def _group_solutions_node(state: ProblemState) -> Dict[str, Any]:
    problem = deepcopy(state["problem"])
    structured_method_ids = {
        str(sequence.get("method_id", ""))
        for sequence in state.get("claim_sequences", [])
        if isinstance(sequence, dict) and str(sequence.get("method_id", ""))
    }
    structured_methods = [
        method
        for method in problem.get("method", [])
        if str(method.get("method_id", "")) in structured_method_ids
    ]
    solution_library, solution_memberships, coverage_state = group_solutions(
        get_context().router,
        problem,
        structured_methods,
        state.get("r_nodes", []),
        state.get("claim_sequences", []),
        state.get("claim_mappings", []),
        state.get("k_atoms", []),
        planned_method_count=len(problem.get("method", [])),
    )
    return {
        "problem": problem,
        "solution_library": solution_library,
        "solution_memberships": solution_memberships,
        "coverage_state": coverage_state,
    }


def _bind_evidence_node(state: ProblemState) -> Dict[str, Any]:
    problem = deepcopy(state["problem"])
    evidence_bindings = bind_evidence(
        get_context().router,
        problem,
        state.get("r_nodes", []),
        state.get("p_facts", []),
        state.get("t_facts", []),
        state.get("k_atoms", []),
        state.get("claim_sequences", []),
        state.get("claim_mappings", []),
    )
    problem_bundle = {
        "annotation_pipeline_version": "ptk_claim_closed_loop_v2",
        "method_planning_metadata": problem.get("method_planning_metadata", {}),
        "problem_record": state.get("problem_record", {}),
        "p_facts": state.get("p_facts", []),
        "t_facts": state.get("t_facts", []),
        "k_atoms": state.get("k_atoms", []),
        "ptk_foundation_audit": state.get("ptk_audit", {}),
        "claim_sequences": state.get("claim_sequences", []),
        "claim_extraction_failures": state.get("claim_extraction_failures", []),
        "claim_extraction_audits": [
            sequence.get("claim_audit", {})
            for sequence in state.get("claim_sequences", [])
            if isinstance(sequence, dict)
        ] + [
            failure.get("claim_audit", {})
            for failure in state.get("claim_extraction_failures", [])
            if isinstance(failure, dict) and isinstance(failure.get("claim_audit"), dict)
        ],
        "claim_mappings": state.get("claim_mappings", []),
        "r_nodes": state.get("r_nodes", []),
        "solution_library": state.get("solution_library", []),
        "solution_memberships": state.get("solution_memberships", []),
        "evidence_bindings": evidence_bindings,
        "cot_variants": state.get("cot_variants", []),
        "coverage_state": state.get("coverage_state", {}),
        "runtime_problem": problem,
    }
    trace_mapping_index = build_trace_mapping_index(problem_bundle)
    problem_bundle["trace_mapping_index"] = trace_mapping_index
    return {
        "problem": problem,
        "evidence_bindings": evidence_bindings,
        "trace_mapping_index": trace_mapping_index,
        "problem_bundle": problem_bundle,
    }


def _attach_validation_annotations(problem_bundle: Dict[str, Any], verification_audit: Dict[str, Any]) -> None:
    final_reports = {
        str(item.get("method_id", "")): item
        for item in verification_audit.get("final_cot_validations", [])
        if isinstance(item, dict)
    }
    claim_reports = {
        str(item.get("method_id", "")): item
        for item in verification_audit.get("claim_set_validations", [])
        if isinstance(item, dict)
    }
    node_report = verification_audit.get("node_set_validation", {})
    node_judgments = {
        str(item.get("r_id", "")): item
        for item in node_report.get("node_judgments", [])
        if isinstance(item, dict)
    }

    runtime_problem = problem_bundle.get("runtime_problem", {})
    for method in runtime_problem.get("method", []) or []:
        if not isinstance(method, dict):
            continue
        method_id = str(method.get("method_id", ""))
        if method_id in final_reports:
            method["final_cot_validation"] = final_reports[method_id]
        if method_id in claim_reports:
            method["claim_set_validation"] = claim_reports[method_id]

    for sequence in problem_bundle.get("claim_sequences", []) or []:
        if not isinstance(sequence, dict):
            continue
        method_id = str(sequence.get("method_id", ""))
        claim_report = claim_reports.get(method_id)
        if claim_report is None:
            continue
        sequence["claim_set_validation"] = claim_report
        claim_judgments = {
            str(item.get("claim_id", "")): item
            for item in claim_report.get("claim_judgments", [])
            if isinstance(item, dict)
        }
        for claim in sequence.get("claims", []) or []:
            if not isinstance(claim, dict):
                continue
            claim_id = str(claim.get("claim_id", ""))
            if claim_id in claim_judgments:
                claim["validation"] = claim_judgments[claim_id]

    for node in problem_bundle.get("r_nodes", []) or []:
        if not isinstance(node, dict):
            continue
        r_id = str(node.get("r_id", ""))
        if r_id in node_judgments:
            node["validation"] = node_judgments[r_id]


def _validate_problem_structure_node(state: ProblemState) -> Dict[str, Any]:
    problem = deepcopy(state["problem"])
    problem_bundle = deepcopy(state.get("problem_bundle", {}))
    if not problem_bundle:
        raise PipelineDataContractError(
            f"[ProblemStructureValidation] Problem `{problem.get('problem_id', 'unknown_problem')}` has no problem bundle to validate."
        )

    if not get_context().config.runtime.enable_problem_structure_validation:
        verification_audit = {
            "component": "ProblemStructureValidation",
            "enabled": False,
            "passed": True,
            "validated_method_ids": [],
            "skipped_method_ids": [
                str(item.get("method_id", ""))
                for item in problem.get("method", [])
                if isinstance(item, dict)
            ],
            "validated_node_count": 0,
            "final_cot_validations": [],
            "claim_set_validations": [],
            "node_set_validation": {},
            "global_failures": [],
            "summary": "Problem structure validation disabled by runtime config.",
        }
        problem_bundle["verification_audit"] = verification_audit
        return {
            "problem": problem,
            "problem_bundle": problem_bundle,
            "verification_audit": verification_audit,
        }

    verification_audit = validate_problem_structure(
        get_context().router,
        problem,
        state.get("claim_sequences", []),
        state.get("r_nodes", []),
        state.get("claim_mappings", []),
        state.get("p_facts", []),
        state.get("t_facts", []),
        state.get("k_atoms", []),
    )
    _attach_validation_annotations(problem_bundle, verification_audit)
    problem_bundle["verification_audit"] = verification_audit

    if get_context().config.runtime.fail_on_problem_structure_validation and not verification_audit.get("passed"):
        raise PipelineDataContractError(
            f"[ProblemStructureValidation] Problem `{problem.get('problem_id', 'unknown_problem')}` failed structural verification."
        )

    return {
        "problem": problem,
        "problem_bundle": problem_bundle,
        "verification_audit": verification_audit,
    }


def _write_problem_outputs(problem_bundle: Dict[str, Any]) -> None:
    ctx = get_context()
    problem_id = str(problem_bundle.get("problem_record", {}).get("problem_id", "unknown_problem"))
    write_json(ctx.problem_outputs_dir / f"{problem_id}.json", problem_bundle)


def _finalize_problem_bundle_node(state: ProblemState) -> Dict[str, Any]:
    problem_bundle = deepcopy(state.get("problem_bundle", {}))
    _write_problem_outputs(problem_bundle)
    return {"problem_bundle": problem_bundle}


def build_problem_graph():
    global _PROBLEM_GRAPH
    if _PROBLEM_GRAPH is not None:
        return _PROBLEM_GRAPH
    graph = StateGraph(ProblemState)
    graph.add_node("prepare_methods", _prepare_methods_node)
    graph.add_node("build_ptk", _build_ptk_node)
    graph.add_node("run_methods", _run_methods_node)
    graph.add_node("extract_claims", _extract_claims_node)
    graph.add_node("induce_nodes", _induce_nodes_node)
    graph.add_node("group_solutions", _group_solutions_node)
    graph.add_node("bind_evidence", _bind_evidence_node)
    graph.add_node("validate_problem_structure", _validate_problem_structure_node)
    graph.add_node("finalize_problem_bundle", _finalize_problem_bundle_node)
    graph.add_edge(START, "prepare_methods")
    graph.add_edge("prepare_methods", "build_ptk")
    graph.add_edge("build_ptk", "run_methods")
    graph.add_edge("run_methods", "extract_claims")
    graph.add_edge("extract_claims", "induce_nodes")
    graph.add_edge("induce_nodes", "group_solutions")
    graph.add_edge("group_solutions", "bind_evidence")
    graph.add_edge("bind_evidence", "validate_problem_structure")
    graph.add_edge("validate_problem_structure", "finalize_problem_bundle")
    graph.add_edge("finalize_problem_bundle", END)
    _PROBLEM_GRAPH = graph.compile(checkpointer=get_shared_checkpointer())
    return _PROBLEM_GRAPH


def _run_single_problem(batch_id: str, problem: Dict[str, Any]) -> Dict[str, Any]:
    problem_graph = build_problem_graph()
    problem_id = str(problem.get("problem_id", "unknown_problem"))
    LOGGER.info("[problem-start] batch_id=%s problem_id=%s sample_path=%s", batch_id, problem_id, problem.get("sample_path", ""))
    config = _make_thread_config(_make_problem_thread_id(batch_id, problem_id))
    result = _invoke_graph_with_stage_retries(
        graph=problem_graph,
        initial_state={"batch_id": batch_id, "problem": deepcopy(problem)},
        config=config,
        scope_label=f"problem `{problem_id}`",
    )
    problem_bundle = result.get("problem_bundle", {})
    LOGGER.info(
        "[problem-done] batch_id=%s problem_id=%s methods=%s claims=%s r_nodes=%s solutions=%s",
        batch_id,
        problem_id,
        len((problem_bundle.get("runtime_problem") or {}).get("method") or []),
        len(problem_bundle.get("claim_sequences") or []),
        len(problem_bundle.get("r_nodes") or []),
        len(problem_bundle.get("solution_library") or []),
    )
    return problem_bundle


def _build_problem_error_record(problem: Dict[str, Any], attempts_exhausted: int, exc: Exception) -> Dict[str, Any]:
    problem_id = str(problem.get("problem_id", "unknown_problem"))
    return {
        "problem_id": problem_id,
        "status": "unavailable",
        "current_status": "problem_unavailable",
        "attempts_exhausted": attempts_exhausted,
        "error_type": type(exc).__name__,
        "error_message": str(exc),
        "dataset_name": problem.get("dataset_name", ""),
        "source_problem_id": problem.get("source_problem_id", ""),
        "subject": problem.get("subject", ""),
        "sample_path": problem.get("sample_path", ""),
        "question_text": problem.get("question_text", ""),
        "standard_answer": problem.get("standard_answer", ""),
        "images": list(problem.get("images") or []),
    }


def _write_problem_error_record(problem_error: Dict[str, Any]) -> None:
    problem_id = str(problem_error.get("problem_id", "unknown_problem"))
    target = get_context().output_root / "problem_errors" / f"{problem_id}.json"
    write_json(target, problem_error)


def _run_problem_with_retries(batch_id: str, problem: Dict[str, Any]) -> Dict[str, Any]:
    max_attempts = max(1, int(get_context().config.runtime.problem_retry_attempts or 1))
    problem_id = str(problem.get("problem_id", "unknown_problem"))
    last_exc: Exception | None = None
    attempts_used = 0
    for attempt_index in range(1, max_attempts + 1):
        attempts_used = attempt_index
        LOGGER.info(
            "[problem-attempt-start] batch_id=%s problem_id=%s attempt=%s/%s",
            batch_id,
            problem_id,
            attempt_index,
            max_attempts,
        )
        try:
            result = _run_single_problem(batch_id, problem)
            LOGGER.info(
                "[problem-attempt-done] batch_id=%s problem_id=%s attempt=%s/%s",
                batch_id,
                problem_id,
                attempt_index,
                max_attempts,
            )
            return result
        except Exception as exc:
            last_exc = exc
            LOGGER.exception(
                "[problem-attempt-failed] batch_id=%s problem_id=%s attempt=%s/%s error_type=%s error=%s",
                batch_id,
                problem_id,
                attempt_index,
                max_attempts,
                type(exc).__name__,
                str(exc),
            )
            if isinstance(exc, StageRetryBudgetExhaustedError):
                LOGGER.warning(
                    "[problem-attempt-stop] batch_id=%s problem_id=%s attempt=%s/%s reason=stage_retry_budget_exhausted",
                    batch_id,
                    problem_id,
                    attempt_index,
                    max_attempts,
                )
                break
            if attempt_index >= max_attempts:
                break
            time.sleep(min(5.0, 0.5 * attempt_index))
    if last_exc is None:
        last_exc = RuntimeError("Unknown problem processing failure.")
    if not get_context().config.runtime.continue_on_problem_error:
        raise RuntimeError(f"Failed to process problem `{problem_id}` after {attempts_used or max_attempts} attempts.") from last_exc
    problem_error = _build_problem_error_record(problem, attempts_used or max_attempts, last_exc)
    _write_problem_error_record(problem_error)
    LOGGER.warning(
        "[problem-marked-unavailable] batch_id=%s problem_id=%s attempts=%s",
        batch_id,
        problem_id,
        attempts_used or max_attempts,
    )
    return problem_error


def _format_problem_failure(problem: Dict[str, Any], exc: Exception) -> Dict[str, Any]:
    problem_id = str(problem.get("problem_id", "unknown_problem"))
    summary = {
        "problem_id": problem_id,
        "source_problem_id": problem.get("source_problem_id", ""),
        "sample_path": problem.get("sample_path", ""),
        "error_type": type(exc).__name__,
        "error": str(exc),
        "status": "failed",
        "stage": "unknown",
    }
    text = str(exc)
    if "ClaimExtractionGate" in text:
        summary["stage"] = "ClaimExtractionGate"
    elif "ClaimExtraction" in text:
        summary["stage"] = "ClaimExtraction"
    elif "ClaimPolish" in text:
        summary["stage"] = "ClaimPolish"
    elif "CoTVerify" in text:
        summary["stage"] = "CoTVerify"
    elif "MethodPlanner" in text:
        summary["stage"] = "MethodPlanner"
    elif "PTKFoundationGate" in text:
        summary["stage"] = "PTKFoundationGate"
    elif "ProblemStructureValidation" in text:
        summary["stage"] = "ProblemStructureValidation"
    elif "ReadyLoader" in text:
        summary["stage"] = "ReadyLoader"
    return summary


def _process_problems_in_parallel_node(state: BatchState) -> BatchState:
    batch_id = state["batch_id"]
    problems = deepcopy(state.get("problems", []))
    if not problems:
        LOGGER.warning("[batch-empty] batch_id=%s has no problems to process", batch_id)
        return {"batch_id": batch_id, "problems": [], "failed_problems": []}
    max_workers = min(get_context().config.runtime.max_problem_workers, len(problems))
    LOGGER.info("[batch-start] batch_id=%s problem_count=%s max_workers=%s", batch_id, len(problems), max_workers)
    output: List[Dict[str, Any] | None] = [None] * len(problems)
    failures: List[Dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="pipeline2-problem") as executor:
        future_map = {executor.submit(_run_problem_with_retries, batch_id, problem): index for index, problem in enumerate(problems)}
        for future in as_completed(future_map):
            index = future_map[future]
            problem_id = str(problems[index].get("problem_id", f"problem_{index}"))
            try:
                output[index] = future.result()
            except Exception as exc:
                failure = _format_problem_failure(problems[index], exc)
                failures.append(failure)
                LOGGER.exception(
                    "[problem-failed] batch_id=%s problem_id=%s stage=%s error_type=%s error=%s",
                    batch_id,
                    problem_id,
                    failure.get("stage", "unknown"),
                    failure.get("error_type", type(exc).__name__),
                    failure.get("error", str(exc)),
                )
    LOGGER.info(
        "[batch-done] batch_id=%s success_count=%s failed_count=%s",
        batch_id,
        len([item for item in output if item is not None]),
        len(failures),
    )
    return {
        "batch_id": batch_id,
        "problems": [item for item in output if item is not None],
        "failed_problems": failures,
    }


def build_batch_graph():
    global _BATCH_GRAPH
    if _BATCH_GRAPH is not None:
        return _BATCH_GRAPH
    graph = StateGraph(BatchState)
    graph.add_node("process_problems_in_parallel", _process_problems_in_parallel_node)
    graph.add_edge(START, "process_problems_in_parallel")
    graph.add_edge("process_problems_in_parallel", END)
    _BATCH_GRAPH = graph.compile(checkpointer=get_shared_checkpointer())
    return _BATCH_GRAPH


def initialize_runtime(config: Pipeline2Config, project_root: Path) -> RuntimeContext:
    global RUNTIME_CONTEXT, _METHOD_GRAPH, _PROBLEM_GRAPH, _BATCH_GRAPH
    ready_root = config.resolve_path(config.paths.ready_root, project_root)
    output_root = config.resolve_path(config.paths.output_root, project_root)
    checkpoint_db_path = config.resolve_path(config.paths.checkpoint_db_path, project_root)
    runtime_dir = output_root / "annotation_runtime"
    ctx = RuntimeContext(
        project_root=project_root,
        config=config,
        router=ModelRouter.from_configs(config.models.primary, config.models.fallback),
        ready_root=ready_root,
        output_root=output_root,
        checkpoint_db_path=checkpoint_db_path,
        runtime_dir=runtime_dir,
        runtime_state_path=runtime_dir / "problems.json",
        method_runs_dir=runtime_dir / "method_runs",
        problem_outputs_dir=output_root / "problems",
        trace_eval_dir=output_root / "trace_eval",
        incoming_traces_dir=output_root / "trace_eval" / "incoming_traces",
        mapping_reports_dir=output_root / "trace_eval" / "mapping_reports",
        novelty_candidates_dir=output_root / "trace_eval" / "novelty_candidates",
        patches_dir=output_root / "patches",
        dataset_patches_dir=output_root / "patches" / "dataset_patches",
    )
    for directory in [
        ctx.output_root,
        ctx.runtime_dir,
        ctx.method_runs_dir,
        ctx.problem_outputs_dir,
        ctx.trace_eval_dir,
        ctx.incoming_traces_dir,
        ctx.mapping_reports_dir,
        ctx.novelty_candidates_dir,
        ctx.patches_dir,
        ctx.dataset_patches_dir,
        ctx.checkpoint_db_path.parent,
    ]:
        ensure_dir(directory)
    _setup_logging(ctx)
    RUNTIME_CONTEXT = ctx
    _METHOD_GRAPH = None
    _PROBLEM_GRAPH = None
    _BATCH_GRAPH = None
    close_shared_checkpointer()
    LOGGER.info(
        "[runtime-init] ready_root=%s output_root=%s checkpoint_db_path=%s log_level=%s log_to_file=%s",
        ctx.ready_root,
        ctx.output_root,
        ctx.checkpoint_db_path,
        ctx.config.runtime.log_level,
        ctx.config.runtime.log_to_file,
    )
    return ctx


def _loaded_problems_to_runtime(problems: Sequence[LoadedReadyProblem]) -> List[Dict[str, Any]]:
    return [problem.to_runtime_problem() | {"sample_record": problem.sample_record} for problem in problems]


def run_annotation_pipeline(config: Pipeline2Config, project_root: Path, batch_id: Optional[str] = None) -> Dict[str, Any]:
    ctx = initialize_runtime(config, project_root)
    ctx.router.ensure_available("pipeline2 annotate")
    loaded_problems = discover_ready_problems(
        ready_root=ctx.ready_root,
        workspace_root=project_root,
        include_manual_review=config.runtime.include_manual_review,
        max_problems=config.runtime.max_problems,
        max_images=config.runtime.max_images_per_problem,
    )
    if not loaded_problems:
        raise ReadyDataContractError(f"[ReadyLoader] No eligible ready problems were loaded from `{ctx.ready_root}`.")
    runtime_problems = _loaded_problems_to_runtime(loaded_problems)
    actual_batch_id = batch_id or f"pipeline2_{utc_now().replace(':', '').replace('-', '')}"
    LOGGER.info(
        "[annotate-start] batch_id=%s loaded_problem_count=%s include_manual_review=%s max_images=%s stage_retry_attempts=%s stage_retry_backoff_seconds=%s",
        actual_batch_id,
        len(loaded_problems),
        config.runtime.include_manual_review,
        config.runtime.max_images_per_problem,
        config.runtime.stage_retry_attempts,
        config.runtime.stage_retry_backoff_seconds,
    )
    batch_graph = build_batch_graph()
    config_payload = _make_thread_config(_make_batch_thread_id(actual_batch_id))
    result = _invoke_resumable_graph(
        graph=batch_graph,
        initial_state={"batch_id": actual_batch_id, "problems": runtime_problems},
        config=config_payload,
    )
    runtime_state = {
        "batch_id": actual_batch_id,
        "problems": result.get("problems", []),
        "failed_problems": result.get("failed_problems", []),
    }
    if ctx.config.runtime.save_runtime_snapshots:
        write_json(ctx.runtime_state_path, runtime_state)
        write_json(ctx.runtime_dir / "failed_problems.json", runtime_state["failed_problems"])
    usage_summary = ctx.router.usage_summary()
    write_json(ctx.output_root / "usage_summary.json", usage_summary)
    LOGGER.info(
        "[annotate-done] batch_id=%s success_count=%s failed_count=%s primary_requests=%s fallback_requests=%s",
        actual_batch_id,
        len(runtime_state["problems"]),
        len(runtime_state["failed_problems"]),
        (usage_summary.get("primary") or {}).get("request_count", 0),
        ((usage_summary.get("fallback") or {}) if isinstance(usage_summary.get("fallback"), dict) else {}).get("request_count", 0),
    )
    return runtime_state


def resume_annotation_pipeline(config: Pipeline2Config, project_root: Path, batch_id: str) -> Dict[str, Any]:
    ctx = initialize_runtime(config, project_root)
    LOGGER.info(
        "[annotate-resume] batch_id=%s stage_retry_attempts=%s stage_retry_backoff_seconds=%s",
        batch_id,
        config.runtime.stage_retry_attempts,
        config.runtime.stage_retry_backoff_seconds,
    )
    batch_graph = build_batch_graph()
    config_payload = _make_thread_config(_make_batch_thread_id(batch_id))
    result = _invoke_resumable_graph(
        graph=batch_graph,
        initial_state={"batch_id": batch_id, "problems": []},
        config=config_payload,
    )
    runtime_state = {
        "batch_id": batch_id,
        "problems": result.get("problems", []),
        "failed_problems": result.get("failed_problems", []),
    }
    if ctx.config.runtime.save_runtime_snapshots:
        write_json(ctx.runtime_state_path, runtime_state)
        write_json(ctx.runtime_dir / "failed_problems.json", runtime_state["failed_problems"])
    usage_summary = ctx.router.usage_summary()
    write_json(ctx.output_root / "usage_summary.json", usage_summary)
    LOGGER.info(
        "[annotate-resume-done] batch_id=%s success_count=%s failed_count=%s primary_requests=%s fallback_requests=%s",
        batch_id,
        len(runtime_state["problems"]),
        len(runtime_state["failed_problems"]),
        (usage_summary.get("primary") or {}).get("request_count", 0),
        ((usage_summary.get("fallback") or {}) if isinstance(usage_summary.get("fallback"), dict) else {}).get("request_count", 0),
    )
    return runtime_state


def _iter_trace_records(path: Path) -> List[Dict[str, Any]]:
    if path.suffix.lower() == ".jsonl":
        rows: List[Dict[str, Any]] = []
        with path.open("r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                if isinstance(data, dict):
                    rows.append(data)
        return rows
    data = read_json(path)
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        traces = data.get("traces")
        if isinstance(traces, list):
            return [item for item in traces if isinstance(item, dict)]
        return [data]
    return []


def evaluate_traces(config: Pipeline2Config, project_root: Path, trace_file: Path) -> Dict[str, Any]:
    ctx = initialize_runtime(config, project_root)
    ctx.router.ensure_available("pipeline2 evaluate-traces")
    trace_records = _iter_trace_records(trace_file)
    if not trace_records:
        raise PipelineDataContractError(f"[TraceEval] No trace records were parsed from `{trace_file}`.")
    LOGGER.info("[trace-eval-start] trace_file=%s trace_count=%s", trace_file, len(trace_records))
    write_json(ctx.incoming_traces_dir / trace_file.name.replace(trace_file.suffix, ".json"), trace_records)
    mapping_rows: List[Dict[str, Any]] = []
    novelty_rows: List[Dict[str, Any]] = []
    patch_rows: List[Dict[str, Any]] = []
    for trace_record in trace_records:
        problem_id = str(trace_record.get("problem_id", ""))
        if not problem_id:
            raise PipelineDataContractError("[TraceEval] Each trace record must include `problem_id`.")
        bundle_path = ctx.problem_outputs_dir / f"{problem_id}.json"
        if not bundle_path.exists():
            raise PipelineDataContractError(f"[TraceEval] Missing canonical problem output for `{problem_id}` at `{bundle_path}`.")
        problem_bundle = read_json(bundle_path)
        mapping_report = map_trace(
            ctx.router,
            problem_bundle,
            trace_record,
            novelty_total_threshold=config.thresholds.novelty_total_threshold,
            novelty_required_threshold=config.thresholds.novelty_required_threshold,
        )
        novelty_result = detect_novelty(ctx.router, problem_bundle, trace_record, mapping_report)
        patch = build_patch(problem_bundle, trace_record, mapping_report, novelty_result)
        mapping_rows.append(mapping_report)
        novelty_rows.append(
            {
                "problem_id": problem_id,
                "run_id": trace_record.get("run_id", ""),
                **novelty_result,
            }
        )
        patch_rows.append(patch)
        LOGGER.info(
            "[trace-eval-item] problem_id=%s run_id=%s novelty_label=%s patch_applied=%s",
            problem_id,
            trace_record.get("run_id", ""),
            novelty_result.get("novelty_label", "unknown"),
            patch.get("patch_applied"),
        )
        write_json(ctx.mapping_reports_dir / f"{problem_id}__{trace_record.get('run_id', 'trace')}.json", mapping_report)
        write_json(ctx.novelty_candidates_dir / f"{problem_id}__{trace_record.get('run_id', 'trace')}.json", {"mapping_report": mapping_report, "novelty_result": novelty_result})
        if patch.get("patch_applied") and config.runtime.enable_trace_patch_writes:
            write_json(ctx.dataset_patches_dir / f"{problem_id}__{trace_record.get('run_id', 'trace')}.json", patch)
    write_jsonl(ctx.trace_eval_dir / "mapping_reports.jsonl", mapping_rows)
    write_jsonl(ctx.trace_eval_dir / "novelty_candidates.jsonl", novelty_rows)
    write_jsonl(ctx.trace_eval_dir / "dataset_patches.jsonl", patch_rows)
    usage_summary = ctx.router.usage_summary()
    write_json(ctx.output_root / "usage_summary.json", usage_summary)
    result = {
        "trace_count": len(trace_records),
        "mapping_report_count": len(mapping_rows),
        "novelty_candidate_count": len([row for row in novelty_rows if row.get("novelty_label") in {"new_solution_family", "uncertain_manual_queue"}]),
        "patch_count": len([row for row in patch_rows if row.get("patch_applied")]),
    }
    LOGGER.info("[trace-eval-done] trace_file=%s result=%s", trace_file, result)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="pipeline2: 第二步标注、节点化、命中率评测与新解回流（严格无内容 fallback 模式）")
    subparsers = parser.add_subparsers(dest="command")
    default_config_path = str(Path(__file__).resolve().parent / "configs" / "default_pipeline2.yaml")

    annotate_parser = subparsers.add_parser("annotate", help="从 ready 样本构建完整标注产物；若任一关键 LLM 输出缺失则显式失败")
    annotate_parser.add_argument("--config", type=str, default=default_config_path, help="pipeline2 YAML 配置路径")
    annotate_parser.add_argument("--batch-id", type=str, default=None, help="运行批次 ID")
    annotate_parser.add_argument("--resume-batch-id", type=str, default=None, help="恢复已有批次运行")

    eval_parser = subparsers.add_parser("evaluate-traces", help="对评测轨迹进行节点命中率计算与新解判定；严格要求题目主 JSON 已存在")
    eval_parser.add_argument("--config", type=str, default=default_config_path, help="pipeline2 YAML 配置路径")
    eval_parser.add_argument("--trace-file", type=str, required=True, help="评测轨迹 JSON/JSONL 文件路径")

    parser.set_defaults(command="annotate")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = Path(__file__).resolve().parents[3]
    config = Pipeline2Config.from_yaml(getattr(args, "config", None))
    if args.command == "evaluate-traces":
        result = evaluate_traces(config, project_root, Path(args.trace_file))
    elif getattr(args, "resume_batch_id", None):
        result = resume_annotation_pipeline(config, project_root, args.resume_batch_id)
    else:
        result = run_annotation_pipeline(config, project_root, batch_id=getattr(args, "batch_id", None))
    print(json.dumps(result, ensure_ascii=False, indent=2))
