from __future__ import annotations

from typing import Any, Dict, List, Sequence

from .agents import (
    AgentContractError,
    PipelineDataContractError,
    _augment_prompt_with_ready_context,
    _call_router,
    _ensure_problem_minimum,
    _require_bool,
    _require_float,
    _require_list,
    _require_non_empty_text,
    _require_string_list,
)
from .clients import ModelRouter
from .prompts import (
    CLAIM_SET_VALIDATION_SYSTEM_PROMPT,
    FINAL_COT_VALIDATION_SYSTEM_PROMPT,
    NODE_SET_VALIDATION_SYSTEM_PROMPT,
    build_claim_set_validation_user_prompt,
    build_final_cot_validation_user_prompt,
    build_node_set_validation_user_prompt,
)
from .utils import normalize_whitespace


def _problem_image_paths(problem: Dict[str, Any]) -> List[str]:
    output: List[str] = []
    for item in problem.get("images") or []:
        if isinstance(item, str):
            value = item.strip()
            if value:
                output.append(value)
    return output


def _require_probability(agent_name: str, value: Any, field_name: str) -> float:
    score = _require_float(agent_name, value, field_name)
    if score < 0.0 or score > 1.0:
        raise AgentContractError(f"[{agent_name}] Field `{field_name}` must be within [0, 1].")
    return score


def _normalize_final_cot_validation(response: Dict[str, Any]) -> Dict[str, Any]:
    passed = _require_bool("FinalCoTValidation", response.get("pass"), "pass")
    unsupported_steps = _require_string_list(
        "FinalCoTValidation",
        response.get("unsupported_steps", []),
        "unsupported_steps",
        allow_empty=True,
    )
    missing_bridge_steps = _require_string_list(
        "FinalCoTValidation",
        response.get("missing_bridge_steps", []),
        "missing_bridge_steps",
        allow_empty=True,
    )
    failure_reasons = _require_string_list(
        "FinalCoTValidation",
        response.get("failure_reasons", []),
        "failure_reasons",
        allow_empty=True,
    )
    if passed and (unsupported_steps or missing_bridge_steps or failure_reasons):
        raise AgentContractError(
            "[FinalCoTValidation] `pass=true` requires `unsupported_steps`, `missing_bridge_steps`, and `failure_reasons` to all be empty."
        )
    return {
        "pass": passed,
        "answer_consistency": _require_bool(
            "FinalCoTValidation", response.get("answer_consistency"), "answer_consistency"
        ),
        "grounding_ok": _require_bool("FinalCoTValidation", response.get("grounding_ok"), "grounding_ok"),
        "method_fidelity_ok": _require_bool(
            "FinalCoTValidation", response.get("method_fidelity_ok"), "method_fidelity_ok"
        ),
        "unsupported_steps": unsupported_steps,
        "missing_bridge_steps": missing_bridge_steps,
        "failure_reasons": failure_reasons,
        "confidence": _require_probability("FinalCoTValidation", response.get("confidence"), "confidence"),
        "summary": _require_non_empty_text("FinalCoTValidation", response.get("summary"), "summary"),
    }


def _normalize_claim_judgments(
    response: Dict[str, Any],
    *,
    claims: Sequence[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    raw_items = _require_list("ClaimSetValidation", response.get("claim_judgments"), "claim_judgments")
    expected_ids = [str(item.get("claim_id", "")) for item in claims]
    expected_id_set = set(expected_ids)
    seen: set[str] = set()
    judgments: List[Dict[str, Any]] = []
    for item in raw_items:
        if not isinstance(item, dict):
            raise AgentContractError("[ClaimSetValidation] Each `claim_judgments` item must be an object.")
        claim_id = _require_non_empty_text("ClaimSetValidation", item.get("claim_id"), "claim_id")
        if claim_id not in expected_id_set:
            raise AgentContractError(f"[ClaimSetValidation] Unknown claim_id `{claim_id}` in `claim_judgments`.")
        if claim_id in seen:
            raise AgentContractError(f"[ClaimSetValidation] Duplicate claim_id `{claim_id}` in `claim_judgments`.")
        seen.add(claim_id)
        judgments.append(
            {
                "claim_id": claim_id,
                "supported": _require_bool("ClaimSetValidation", item.get("supported"), "supported"),
                "atomic": _require_bool("ClaimSetValidation", item.get("atomic"), "atomic"),
                "dependency_valid": _require_bool(
                    "ClaimSetValidation", item.get("dependency_valid"), "dependency_valid"
                ),
                "grounded": _require_bool("ClaimSetValidation", item.get("grounded"), "grounded"),
                "issue_types": _require_string_list(
                    "ClaimSetValidation",
                    item.get("issue_types", []),
                    "issue_types",
                    allow_empty=True,
                ),
                "reason": _require_non_empty_text("ClaimSetValidation", item.get("reason"), "reason"),
            }
        )
    missing = [claim_id for claim_id in expected_ids if claim_id and claim_id not in seen]
    if missing:
        raise AgentContractError(
            f"[ClaimSetValidation] Missing judgments for claim_id(s): {', '.join(missing)}."
        )
    return judgments


def _normalize_claim_set_validation(
    response: Dict[str, Any],
    *,
    claims: Sequence[Dict[str, Any]],
) -> Dict[str, Any]:
    passed = _require_bool("ClaimSetValidation", response.get("pass"), "pass")
    global_failures = _require_string_list(
        "ClaimSetValidation",
        response.get("global_failures", []),
        "global_failures",
        allow_empty=True,
    )
    if passed and global_failures:
        raise AgentContractError("[ClaimSetValidation] `pass=true` requires `global_failures` to be empty.")
    return {
        "pass": passed,
        "dependency_closure_ok": _require_bool(
            "ClaimSetValidation", response.get("dependency_closure_ok"), "dependency_closure_ok"
        ),
        "grounding_ok": _require_bool("ClaimSetValidation", response.get("grounding_ok"), "grounding_ok"),
        "global_failures": global_failures,
        "claim_judgments": _normalize_claim_judgments(response, claims=claims),
        "summary": _require_non_empty_text("ClaimSetValidation", response.get("summary"), "summary"),
    }


def _normalize_node_judgments(
    response: Dict[str, Any],
    *,
    r_nodes: Sequence[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    raw_items = _require_list("NodeSetValidation", response.get("node_judgments"), "node_judgments")
    expected_ids = [str(item.get("r_id", "")) for item in r_nodes]
    expected_id_set = set(expected_ids)
    seen: set[str] = set()
    judgments: List[Dict[str, Any]] = []
    for item in raw_items:
        if not isinstance(item, dict):
            raise AgentContractError("[NodeSetValidation] Each `node_judgments` item must be an object.")
        r_id = _require_non_empty_text("NodeSetValidation", item.get("r_id"), "r_id")
        if r_id not in expected_id_set:
            raise AgentContractError(f"[NodeSetValidation] Unknown r_id `{r_id}` in `node_judgments`.")
        if r_id in seen:
            raise AgentContractError(f"[NodeSetValidation] Duplicate r_id `{r_id}` in `node_judgments`.")
        seen.add(r_id)
        judgments.append(
            {
                "r_id": r_id,
                "supported": _require_bool("NodeSetValidation", item.get("supported"), "supported"),
                "has_valid_source_claims": _require_bool(
                    "NodeSetValidation",
                    item.get("has_valid_source_claims"),
                    "has_valid_source_claims",
                ),
                "overmerged": _require_bool("NodeSetValidation", item.get("overmerged"), "overmerged"),
                "missing_key_information": _require_bool(
                    "NodeSetValidation",
                    item.get("missing_key_information"),
                    "missing_key_information",
                ),
                "issue_types": _require_string_list(
                    "NodeSetValidation",
                    item.get("issue_types", []),
                    "issue_types",
                    allow_empty=True,
                ),
                "reason": _require_non_empty_text("NodeSetValidation", item.get("reason"), "reason"),
            }
        )
    missing = [r_id for r_id in expected_ids if r_id and r_id not in seen]
    if missing:
        raise AgentContractError(
            f"[NodeSetValidation] Missing judgments for r_id(s): {', '.join(missing)}."
        )
    return judgments


def _normalize_node_set_validation(
    response: Dict[str, Any],
    *,
    r_nodes: Sequence[Dict[str, Any]],
) -> Dict[str, Any]:
    passed = _require_bool("NodeSetValidation", response.get("pass"), "pass")
    global_failures = _require_string_list(
        "NodeSetValidation",
        response.get("global_failures", []),
        "global_failures",
        allow_empty=True,
    )
    if passed and global_failures:
        raise AgentContractError("[NodeSetValidation] `pass=true` requires `global_failures` to be empty.")
    return {
        "pass": passed,
        "coverage_ok": _require_bool("NodeSetValidation", response.get("coverage_ok"), "coverage_ok"),
        "merge_quality_ok": _require_bool(
            "NodeSetValidation", response.get("merge_quality_ok"), "merge_quality_ok"
        ),
        "global_failures": global_failures,
        "node_judgments": _normalize_node_judgments(response, r_nodes=r_nodes),
        "summary": _require_non_empty_text("NodeSetValidation", response.get("summary"), "summary"),
    }


def _with_llm_meta(report: Dict[str, Any], response: Dict[str, Any]) -> Dict[str, Any]:
    return {
        **report,
        "llm_request_mode": response.get("_llm_request_mode"),
        "llm_endpoint_name": response.get("_llm_endpoint_name"),
        "llm_elapsed_seconds": response.get("_llm_elapsed_seconds"),
    }


def validate_final_cot(
    router: ModelRouter,
    problem: Dict[str, Any],
    method: Dict[str, Any],
    cot_text: str,
    answer_text: str,
) -> Dict[str, Any]:
    _ensure_problem_minimum(problem, "FinalCoTValidation")
    if not normalize_whitespace(method.get("method_draft", "")):
        raise PipelineDataContractError("[FinalCoTValidation] Method is missing `method_draft`.")
    if not normalize_whitespace(cot_text):
        raise PipelineDataContractError("[FinalCoTValidation] `cot_text` must not be empty.")
    if not normalize_whitespace(answer_text):
        raise PipelineDataContractError("[FinalCoTValidation] `answer_text` must not be empty.")
    response = _call_router(
        router,
        FINAL_COT_VALIDATION_SYSTEM_PROMPT,
        _augment_prompt_with_ready_context(
            problem,
            build_final_cot_validation_user_prompt(problem, method, cot_text, answer_text),
            "FinalCoTValidation",
        ),
        _problem_image_paths(problem),
        agent_name="FinalCoTValidation",
        require_images=bool(problem.get("requires_image")),
    )
    return _with_llm_meta(_normalize_final_cot_validation(response), response)


def validate_claim_set(
    router: ModelRouter,
    problem: Dict[str, Any],
    method: Dict[str, Any],
    cot_text: str,
    claims: Sequence[Dict[str, Any]],
    p_facts: Sequence[Dict[str, Any]],
    t_facts: Sequence[Dict[str, Any]],
    k_atoms: Sequence[Dict[str, Any]],
) -> Dict[str, Any]:
    _ensure_problem_minimum(problem, "ClaimSetValidation")
    if not claims:
        raise PipelineDataContractError("[ClaimSetValidation] Cannot validate an empty claim set.")
    response = _call_router(
        router,
        CLAIM_SET_VALIDATION_SYSTEM_PROMPT,
        _augment_prompt_with_ready_context(
            problem,
            build_claim_set_validation_user_prompt(problem, method, cot_text, claims, p_facts, t_facts, k_atoms),
            "ClaimSetValidation",
        ),
        _problem_image_paths(problem),
        agent_name="ClaimSetValidation",
        require_images=bool(problem.get("requires_image")),
    )
    return _with_llm_meta(_normalize_claim_set_validation(response, claims=claims), response)


def validate_node_set(
    router: ModelRouter,
    problem: Dict[str, Any],
    claim_sequences: Sequence[Dict[str, Any]],
    r_nodes: Sequence[Dict[str, Any]],
    claim_mappings: Sequence[Dict[str, Any]],
    p_facts: Sequence[Dict[str, Any]],
    t_facts: Sequence[Dict[str, Any]],
    k_atoms: Sequence[Dict[str, Any]],
) -> Dict[str, Any]:
    _ensure_problem_minimum(problem, "NodeSetValidation")
    if not r_nodes:
        raise PipelineDataContractError("[NodeSetValidation] Cannot validate an empty `r_nodes` set.")
    claim_id_set = {
        str(claim.get("claim_id", ""))
        for sequence in claim_sequences
        for claim in (sequence.get("claims") or [])
        if isinstance(claim, dict) and str(claim.get("claim_id", ""))
    }
    if not claim_id_set:
        raise PipelineDataContractError("[NodeSetValidation] No claims were available to validate the node set.")
    r_id_set = {str(node.get("r_id", "")) for node in r_nodes if isinstance(node, dict) and str(node.get("r_id", ""))}
    for mapping in claim_mappings:
        if not isinstance(mapping, dict):
            raise PipelineDataContractError("[NodeSetValidation] Each claim mapping must be an object.")
        claim_id = _require_non_empty_text("NodeSetValidation", mapping.get("claim_id"), "claim_id")
        r_id = _require_non_empty_text("NodeSetValidation", mapping.get("r_id"), "r_id")
        if claim_id not in claim_id_set:
            raise PipelineDataContractError(
                f"[NodeSetValidation] claim_mappings references unknown claim_id `{claim_id}`."
            )
        if r_id not in r_id_set:
            raise PipelineDataContractError(
                f"[NodeSetValidation] claim_mappings references unknown r_id `{r_id}`."
            )
    for node in r_nodes:
        if not isinstance(node, dict):
            raise PipelineDataContractError("[NodeSetValidation] Each r_node must be an object.")
        _require_non_empty_text("NodeSetValidation", node.get("r_id"), "r_id")
        source_claim_ids = _require_string_list(
            "NodeSetValidation",
            node.get("source_claim_ids", []),
            "source_claim_ids",
            allow_empty=False,
        )
        for claim_id in source_claim_ids:
            if claim_id not in claim_id_set:
                raise PipelineDataContractError(
                    f"[NodeSetValidation] r_node references unknown source_claim_id `{claim_id}`."
                )
    response = _call_router(
        router,
        NODE_SET_VALIDATION_SYSTEM_PROMPT,
        _augment_prompt_with_ready_context(
            problem,
            build_node_set_validation_user_prompt(
                problem,
                claim_sequences,
                r_nodes,
                claim_mappings,
                p_facts,
                t_facts,
                k_atoms,
            ),
            "NodeSetValidation",
        ),
        _problem_image_paths(problem),
        agent_name="NodeSetValidation",
        require_images=bool(problem.get("requires_image")),
    )
    return _with_llm_meta(_normalize_node_set_validation(response, r_nodes=r_nodes), response)


def validate_problem_structure(
    router: ModelRouter,
    problem: Dict[str, Any],
    claim_sequences: Sequence[Dict[str, Any]],
    r_nodes: Sequence[Dict[str, Any]],
    claim_mappings: Sequence[Dict[str, Any]],
    p_facts: Sequence[Dict[str, Any]],
    t_facts: Sequence[Dict[str, Any]],
    k_atoms: Sequence[Dict[str, Any]],
) -> Dict[str, Any]:
    _ensure_problem_minimum(problem, "ProblemStructureValidation")
    if not claim_sequences:
        raise PipelineDataContractError(
            f"[ProblemStructureValidation] Problem `{problem.get('problem_id', 'unknown_problem')}` has no claim sequences to validate."
        )
    methods = {
        str(item.get("method_id", "")): item
        for item in problem.get("method", [])
        if isinstance(item, dict) and str(item.get("method_id", ""))
    }
    if not methods:
        raise PipelineDataContractError(
            f"[ProblemStructureValidation] Problem `{problem.get('problem_id', 'unknown_problem')}` has no methods in runtime problem state."
        )

    final_cot_validations: List[Dict[str, Any]] = []
    claim_set_validations: List[Dict[str, Any]] = []
    validated_method_ids: List[str] = []

    for sequence in claim_sequences:
        if not isinstance(sequence, dict):
            raise PipelineDataContractError("[ProblemStructureValidation] Each claim sequence must be an object.")
        method_id = _require_non_empty_text(
            "ProblemStructureValidation", sequence.get("method_id"), "method_id"
        )
        method = methods.get(method_id)
        if method is None:
            raise PipelineDataContractError(
                f"[ProblemStructureValidation] claim_sequence references unknown method_id `{method_id}`."
            )
        cot_text = _require_non_empty_text(
            "ProblemStructureValidation", sequence.get("cot_final"), "cot_final"
        )
        answer_text = normalize_whitespace(
            sequence.get("answer_final")
            or method.get("answer_answer_check_final")
            or method.get("model_answer")
            or ""
        )
        if not answer_text:
            raise PipelineDataContractError(
                f"[ProblemStructureValidation] Method `{method_id}` is missing `answer_final` for validation."
            )
        final_report = validate_final_cot(router, problem, method, cot_text, answer_text)
        final_cot_validations.append({"method_id": method_id, **final_report})

        claim_report = validate_claim_set(
            router,
            problem,
            method,
            cot_text,
            sequence.get("claims") or [],
            p_facts,
            t_facts,
            k_atoms,
        )
        claim_set_validations.append({"method_id": method_id, **claim_report})
        validated_method_ids.append(method_id)

    node_set_validation = validate_node_set(
        router,
        problem,
        claim_sequences,
        r_nodes,
        claim_mappings,
        p_facts,
        t_facts,
        k_atoms,
    )

    global_failures: List[str] = []
    for report in final_cot_validations:
        if not report.get("pass"):
            global_failures.append(
                f"Final CoT validation failed for method `{report.get('method_id', 'unknown_method')}`."
            )
    for report in claim_set_validations:
        if not report.get("pass"):
            global_failures.append(
                f"Claim-set validation failed for method `{report.get('method_id', 'unknown_method')}`."
            )
    if not node_set_validation.get("pass"):
        global_failures.append("Node-set validation failed.")
    global_failures.extend(node_set_validation.get("global_failures", []))

    skipped_method_ids = [
        method_id for method_id in methods.keys() if method_id not in set(validated_method_ids)
    ]
    passed = (
        all(report.get("pass") for report in final_cot_validations)
        and all(report.get("pass") for report in claim_set_validations)
        and bool(node_set_validation.get("pass"))
    )
    summary = (
        "All validated final CoTs, claim sets, and nodes passed structural verification."
        if passed
        else "One or more validated final CoTs, claim sets, or nodes failed structural verification."
    )
    return {
        "component": "ProblemStructureValidation",
        "passed": passed,
        "validated_method_ids": validated_method_ids,
        "skipped_method_ids": skipped_method_ids,
        "validated_node_count": len(r_nodes),
        "final_cot_validations": final_cot_validations,
        "claim_set_validations": claim_set_validations,
        "node_set_validation": node_set_validation,
        "global_failures": global_failures,
        "summary": summary,
    }
