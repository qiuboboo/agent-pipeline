from __future__ import annotations

import argparse
import atexit
import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from langgraph.checkpoint.memory import InMemorySaver
try:
    from langgraph.checkpoint.sqlite import SqliteSaver  # type: ignore
except ImportError:  # pragma: no cover
    SqliteSaver = None  # type: ignore[assignment]
from langgraph.graph import END, START, StateGraph

from .agents import (
    PipelineDataContractError,
    judge_answer_equivalence,
    plan_method_collection,
    polish_cot,
    repair_answer,
    solve_method,
    target_method_count_from_score,
    verify_cot,
)
from .clients import ModelRouter
from .config import Pipeline2Config
from .models import BatchState, LoadedReadyProblem, MethodState, ProblemState
from .ready_loader import ReadyDataContractError, discover_ready_problems
from .utils import ensure_dir, normalize_whitespace, utc_now, write_json


@dataclass
class VerifiedCotRuntimeContext:
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


RUNTIME_CONTEXT: Optional[VerifiedCotRuntimeContext] = None
_SQLITE_CONNECTION: sqlite3.Connection | None = None
_SHARED_CHECKPOINTER: Any = None
_METHOD_GRAPH = None
_PROBLEM_GRAPH = None
_BATCH_GRAPH = None


def get_context() -> VerifiedCotRuntimeContext:
    if RUNTIME_CONTEXT is None:
        raise RuntimeError("verified_cot_pipeline runtime is not initialized")
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
    return f"verified-cot::batch::{batch_id}"


def _make_problem_thread_id(batch_id: str, problem_id: str) -> str:
    return f"verified-cot::problem::{batch_id}::{problem_id}"


def _make_method_thread_id(batch_id: str, problem_id: str, method_id: str) -> str:
    return f"verified-cot::method::{batch_id}::{problem_id}::{method_id}"


def _make_thread_config(thread_id: str) -> Dict[str, Any]:
    return {"configurable": {"thread_id": thread_id}}


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


def _generate_cot_node(state: MethodState) -> MethodState:
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


def _answer_check_node(state: MethodState) -> MethodState:
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


def _verify_round(state: MethodState, round_index: int) -> MethodState:
    method = deepcopy(state["method"])
    problem = state["problem"]
    result = verify_cot(get_context().router, problem, method, state.get("current_cot_text", ""))
    verify_key = f"CoT_verify_{round_index}"
    qualify_key = f"CoT_qualify_{round_index}"
    method[verify_key] = bool(result.get("verify_pass")) and bool(method.get("is_answer_match"))
    method[qualify_key] = normalize_whitespace(result.get("critic_suggestions", ""))
    method.setdefault("verify_reports", []).append(
        {
            "round_index": round_index,
            "verify_pass": method[verify_key],
            "critic_suggestions": method[qualify_key],
            "major_failures": result.get("major_failures") or [],
            "extractability_score": result.get("extractability_score"),
            "grounding_score": result.get("grounding_score"),
            "method_fidelity_score": result.get("method_fidelity_score"),
        }
    )
    return {"method": method}


def _verify_round_0_node(state: MethodState) -> MethodState:
    return _verify_round(state, 0)


def _verify_round_1_node(state: MethodState) -> MethodState:
    return _verify_round(state, 1)


def _verify_round_2_node(state: MethodState) -> MethodState:
    return _verify_round(state, 2)


def _verify_round_3_node(state: MethodState) -> MethodState:
    return _verify_round(state, 3)


def _polish_round(state: MethodState, suggestion_key: str, output_key: str) -> MethodState:
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


def _polish_round_1_node(state: MethodState) -> MethodState:
    return _polish_round(state, "CoT_qualify_0", "CoT_after_polish_1")


def _polish_round_2_node(state: MethodState) -> MethodState:
    return _polish_round(state, "CoT_qualify_1", "CoT_after_polish_2")


def _polish_round_3_node(state: MethodState) -> MethodState:
    return _polish_round(state, "CoT_qualify_2", "CoT_after_polish_3")


def _route_after_verify_0(state: MethodState) -> str:
    return "finalize_method" if state["method"].get("CoT_verify_0") else "polish_round_1"


def _route_after_verify_1(state: MethodState) -> str:
    return "finalize_method" if state["method"].get("CoT_verify_1") else "polish_round_2"


def _route_after_verify_2(state: MethodState) -> str:
    return "finalize_method" if state["method"].get("CoT_verify_2") else "polish_round_3"


def _finalize_method_node(state: MethodState) -> MethodState:
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
    graph.add_conditional_edges(
        "verify_round_0",
        _route_after_verify_0,
        {"finalize_method": "finalize_method", "polish_round_1": "polish_round_1"},
    )
    graph.add_edge("polish_round_1", "verify_round_1")
    graph.add_conditional_edges(
        "verify_round_1",
        _route_after_verify_1,
        {"finalize_method": "finalize_method", "polish_round_2": "polish_round_2"},
    )
    graph.add_edge("polish_round_2", "verify_round_2")
    graph.add_conditional_edges(
        "verify_round_2",
        _route_after_verify_2,
        {"finalize_method": "finalize_method", "polish_round_3": "polish_round_3"},
    )
    graph.add_edge("polish_round_3", "verify_round_3")
    graph.add_edge("verify_round_3", "finalize_method")
    graph.add_edge("finalize_method", END)
    _METHOD_GRAPH = graph.compile(checkpointer=get_shared_checkpointer())
    return _METHOD_GRAPH


def _prepare_methods_node(state: ProblemState) -> ProblemState:
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


def _run_single_method(batch_id: str, problem: Dict[str, Any], method: Dict[str, Any]) -> Dict[str, Any]:
    method_graph = build_method_graph()
    config = _make_thread_config(
        _make_method_thread_id(
            batch_id,
            str(problem.get("problem_id", "unknown_problem")),
            str(method.get("method_id", "unknown_method")),
        )
    )
    result = _invoke_resumable_graph(
        graph=method_graph,
        initial_state={
            "batch_id": batch_id,
            "problem": deepcopy(problem),
            "method": deepcopy(method),
        },
        config=config,
    )
    return result["method"]


def _run_methods_node(state: ProblemState) -> ProblemState:
    problem = deepcopy(state["problem"])
    processed_methods: List[Dict[str, Any]] = []
    for method in problem.get("method", []):
        processed = _run_single_method(batch_id=state["batch_id"], problem=problem, method=method)
        processed_methods.append(processed)
        _write_method_snapshot(state["batch_id"], str(problem.get("problem_id", "unknown_problem")), processed)
    problem["method"] = processed_methods
    return {"batch_id": state["batch_id"], "problem": problem}


def _build_verified_cot_problem_output(batch_id: str, problem: Dict[str, Any]) -> Dict[str, Any]:
    methods: List[Dict[str, Any]] = []
    qualified_method_count = 0
    for method in problem.get("method", []):
        method_record = {
            "method_id": method.get("method_id"),
            "method_draft": method.get("method_draft", ""),
            "CoT_raw": method.get("CoT_raw", ""),
            "model_answer": method.get("model_answer", ""),
            "is_answer_match": bool(method.get("is_answer_match")),
            "answer_match_reason": method.get("answer_match_reason", ""),
            "answer_match_part_results": method.get("answer_match_part_results", []),
            "CoT_answer_check_final": method.get("CoT_answer_check_final", ""),
            "answer_answer_check_final": method.get("answer_answer_check_final", ""),
            "CoT_verify_0": bool(method.get("CoT_verify_0")),
            "CoT_qualify_0": method.get("CoT_qualify_0", ""),
            "CoT_after_polish_1": method.get("CoT_after_polish_1", ""),
            "CoT_verify_1": bool(method.get("CoT_verify_1")),
            "CoT_qualify_1": method.get("CoT_qualify_1", ""),
            "CoT_after_polish_2": method.get("CoT_after_polish_2", ""),
            "CoT_verify_2": bool(method.get("CoT_verify_2")),
            "CoT_qualify_2": method.get("CoT_qualify_2", ""),
            "CoT_after_polish_3": method.get("CoT_after_polish_3", ""),
            "CoT_verify_3": bool(method.get("CoT_verify_3")),
            "CoT_qualify_3": method.get("CoT_qualify_3", ""),
            "is_final_CoT_qualified": bool(method.get("is_final_CoT_qualified")),
            "CoT_final": method.get("CoT_final", ""),
            "planner_metadata": method.get("planner_metadata", {}),
            "solver_metadata": method.get("solver_metadata", {}),
            "verify_reports": method.get("verify_reports", []),
        }
        methods.append(method_record)
        if method_record["is_answer_match"] and method_record["is_final_CoT_qualified"]:
            qualified_method_count += 1
    if qualified_method_count == 0:
        raise PipelineDataContractError(
            f"[VerifiedCoTOutput] Problem `{problem.get('problem_id', 'unknown_problem')}` produced no verified CoT methods."
        )
    planning_metadata = problem.get("method_planning_metadata", {})
    return {
        "batch_id": batch_id,
        "problem_id": problem.get("problem_id", ""),
        "question_text": problem.get("question_text", ""),
        "standard_answer": problem.get("standard_answer", ""),
        "images": list(problem.get("images") or []),
        "initial_multi_solution_score": problem.get("initial_multi_solution_score"),
        "method": methods,
        "method_planning_metadata": planning_metadata,
        "input_context": {
            "dataset_name": problem.get("dataset_name", ""),
            "source_problem_id": problem.get("source_problem_id", ""),
            "subject": problem.get("subject", ""),
            "requires_image": bool(problem.get("requires_image")),
            "text_dominant": bool(problem.get("text_dominant")),
            "alignment_status": problem.get("alignment_status", "unknown"),
            "solvability_score": problem.get("solvability_score", 0.0),
            "sample_path": problem.get("sample_path", ""),
            "clean_pool_status": problem.get("clean_pool_status", ""),
            "clean_decision": problem.get("clean_decision", ""),
        },
        "verified_cot_summary": {
            "target_method_count_from_score": planning_metadata.get("target_method_count_from_score", len(methods)),
            "planned_method_count": len(methods),
            "qualified_method_count": qualified_method_count,
            "verified_cot_ready": True,
        },
    }


def _write_verified_cot_problem_output(problem_output: Dict[str, Any]) -> None:
    ctx = get_context()
    problem_id = str(problem_output.get("problem_id", "unknown_problem"))
    write_json(ctx.problem_outputs_dir / f"{problem_id}.json", problem_output)


def _finalize_verified_cot_problem_node(state: ProblemState) -> ProblemState:
    problem = deepcopy(state["problem"])
    verified_output = _build_verified_cot_problem_output(state["batch_id"], problem)
    _write_verified_cot_problem_output(verified_output)
    return {"problem_bundle": verified_output}


def build_problem_graph():
    global _PROBLEM_GRAPH
    if _PROBLEM_GRAPH is not None:
        return _PROBLEM_GRAPH
    graph = StateGraph(ProblemState)
    graph.add_node("prepare_methods", _prepare_methods_node)
    graph.add_node("run_methods", _run_methods_node)
    graph.add_node("finalize_verified_cot_problem", _finalize_verified_cot_problem_node)
    graph.add_edge(START, "prepare_methods")
    graph.add_edge("prepare_methods", "run_methods")
    graph.add_edge("run_methods", "finalize_verified_cot_problem")
    graph.add_edge("finalize_verified_cot_problem", END)
    _PROBLEM_GRAPH = graph.compile(checkpointer=get_shared_checkpointer())
    return _PROBLEM_GRAPH


def _run_single_problem(batch_id: str, problem: Dict[str, Any]) -> Dict[str, Any]:
    problem_graph = build_problem_graph()
    config = _make_thread_config(
        _make_problem_thread_id(batch_id, str(problem.get("problem_id", "unknown_problem")))
    )
    result = _invoke_resumable_graph(
        graph=problem_graph,
        initial_state={"batch_id": batch_id, "problem": deepcopy(problem)},
        config=config,
    )
    return result.get("problem_bundle", {})


def _process_problems_in_parallel_node(state: BatchState) -> BatchState:
    batch_id = state["batch_id"]
    problems = deepcopy(state.get("problems", []))
    if not problems:
        return {"batch_id": batch_id, "problems": []}
    max_workers = min(get_context().config.runtime.max_problem_workers, len(problems))
    output: List[Dict[str, Any] | None] = [None] * len(problems)
    with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="verified-cot-problem") as executor:
        future_map = {
            executor.submit(_run_single_problem, batch_id, problem): index
            for index, problem in enumerate(problems)
        }
        for future in as_completed(future_map):
            index = future_map[future]
            try:
                output[index] = future.result()
            except Exception as exc:
                problem_id = problems[index].get("problem_id", f"problem_{index}")
                raise RuntimeError(f"Failed to process verified CoT problem `{problem_id}`.") from exc
    return {"batch_id": batch_id, "problems": [item for item in output if item is not None]}


def build_batch_graph():
    global _BATCH_GRAPH
    if _BATCH_GRAPH is not None:
        return _BATCH_GRAPH
    graph = StateGraph(BatchState)
    graph.add_node("process_problems_verified_cot", _process_problems_in_parallel_node)
    graph.add_edge(START, "process_problems_verified_cot")
    graph.add_edge("process_problems_verified_cot", END)
    _BATCH_GRAPH = graph.compile(checkpointer=get_shared_checkpointer())
    return _BATCH_GRAPH


def initialize_runtime(config: Pipeline2Config, project_root: Path) -> VerifiedCotRuntimeContext:
    global RUNTIME_CONTEXT, _METHOD_GRAPH, _PROBLEM_GRAPH, _BATCH_GRAPH
    ready_root = config.resolve_path(config.paths.ready_root, project_root)
    output_root = config.resolve_path(config.paths.output_root, project_root)
    checkpoint_db_path = config.resolve_path(config.paths.checkpoint_db_path, project_root)
    runtime_dir = output_root / "annotation_runtime"
    ctx = VerifiedCotRuntimeContext(
        project_root=project_root,
        config=config,
        router=ModelRouter.from_configs(config.models.primary),
        ready_root=ready_root,
        output_root=output_root,
        checkpoint_db_path=checkpoint_db_path,
        runtime_dir=runtime_dir,
        runtime_state_path=runtime_dir / "problems.json",
        method_runs_dir=runtime_dir / "method_runs",
        problem_outputs_dir=output_root / "problems",
    )
    for directory in [
        ctx.output_root,
        ctx.runtime_dir,
        ctx.method_runs_dir,
        ctx.problem_outputs_dir,
        ctx.checkpoint_db_path.parent,
    ]:
        ensure_dir(directory)
    RUNTIME_CONTEXT = ctx
    _METHOD_GRAPH = None
    _PROBLEM_GRAPH = None
    _BATCH_GRAPH = None
    close_shared_checkpointer()
    return ctx


def _loaded_problems_to_runtime(problems: Sequence[LoadedReadyProblem]) -> List[Dict[str, Any]]:
    return [problem.to_runtime_problem() | {"sample_record": problem.sample_record} for problem in problems]


def run_verified_cot_pipeline(config: Pipeline2Config, project_root: Path, batch_id: Optional[str] = None) -> Dict[str, Any]:
    ctx = initialize_runtime(config, project_root)
    ctx.router.ensure_available("verified-cot annotate")
    loaded_problems = discover_ready_problems(
        ready_root=ctx.ready_root,
        workspace_root=project_root,
        include_manual_review=config.runtime.include_manual_review,
        max_problems=config.runtime.max_problems,
        max_images=config.runtime.max_images_per_problem,
    )
    if not loaded_problems:
        raise ReadyDataContractError(
            f"[ReadyLoader] No eligible ready problems were loaded from `{ctx.ready_root}`."
        )
    runtime_problems = _loaded_problems_to_runtime(loaded_problems)
    actual_batch_id = batch_id or f"verified_cot_{utc_now().replace(':', '').replace('-', '')}"
    batch_graph = build_batch_graph()
    config_payload = _make_thread_config(_make_batch_thread_id(actual_batch_id))
    result = _invoke_resumable_graph(
        graph=batch_graph,
        initial_state={"batch_id": actual_batch_id, "problems": runtime_problems},
        config=config_payload,
    )
    runtime_state = {"batch_id": actual_batch_id, "problems": result.get("problems", [])}
    if ctx.config.runtime.save_runtime_snapshots:
        write_json(ctx.runtime_state_path, runtime_state)
    write_json(ctx.output_root / "usage_summary.json", ctx.router.usage_summary())
    return runtime_state


def resume_verified_cot_pipeline(config: Pipeline2Config, project_root: Path, batch_id: str) -> Dict[str, Any]:
    ctx = initialize_runtime(config, project_root)
    batch_graph = build_batch_graph()
    config_payload = _make_thread_config(_make_batch_thread_id(batch_id))
    result = _invoke_resumable_graph(
        graph=batch_graph,
        initial_state={"batch_id": batch_id, "problems": []},
        config=config_payload,
    )
    runtime_state = {"batch_id": batch_id, "problems": result.get("problems", [])}
    if ctx.config.runtime.save_runtime_snapshots:
        write_json(ctx.runtime_state_path, runtime_state)
    write_json(ctx.output_root / "usage_summary.json", ctx.router.usage_summary())
    return runtime_state


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="verified-cot pipeline: 从 ready 输入到给出经过验证的 CoT（严格无内容 fallback 模式）"
    )
    default_config_path = str(Path(__file__).resolve().parent / "configs" / "verified_cot_default.yaml")
    parser.add_argument(
        "--config",
        type=str,
        default=default_config_path,
        help="verified CoT 子流水线 YAML 配置路径",
    )
    parser.add_argument("--batch-id", type=str, default=None, help="运行批次 ID")
    parser.add_argument("--resume-batch-id", type=str, default=None, help="恢复已有批次运行")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = Path(__file__).resolve().parents[1]
    config = Pipeline2Config.from_yaml(getattr(args, "config", None))
    if getattr(args, "resume_batch_id", None):
        result = resume_verified_cot_pipeline(config, project_root, args.resume_batch_id)
    else:
        result = run_verified_cot_pipeline(config, project_root, batch_id=getattr(args, "batch_id", None))
    print(json.dumps(result, ensure_ascii=False, indent=2))
