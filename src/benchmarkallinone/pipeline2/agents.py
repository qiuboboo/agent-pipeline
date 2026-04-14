from __future__ import annotations

import json
import math
import re
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .clients import ModelRouter
from .models import ClaimRecord, NodeRecord, SolutionRecord
from .prompts import (
    ANSWER_EQUIVALENCE_SYSTEM_PROMPT,
    ANSWER_REPAIR_SYSTEM_PROMPT,
    CLAIM_EXTRACTION_SYSTEM_PROMPT,
    CLAIM_SET_VALIDATION_SYSTEM_PROMPT,
    COT_POLISH_SYSTEM_PROMPT,
    COT_VERIFY_SYSTEM_PROMPT,
    EVIDENCE_BINDER_SYSTEM_PROMPT,
    FINAL_COT_VALIDATION_SYSTEM_PROMPT,
    KNOWLEDGE_LIBRARIAN_SYSTEM_PROMPT,
    METHOD_PLANNER_SYSTEM_PROMPT,
    NODE_INDUCTION_SYSTEM_PROMPT,
    NODE_SET_VALIDATION_SYSTEM_PROMPT,
    NOVELTY_DETECTOR_SYSTEM_PROMPT,
    PERCEPTION_EXTRACTION_SYSTEM_PROMPT,
    SOLUTION_GROUPER_SYSTEM_PROMPT,
    SOLVER_SYSTEM_PROMPT,
    TEXT_CONDITION_SYSTEM_PROMPT,
    TRACE_MAPPER_SYSTEM_PROMPT,
    build_answer_equivalence_user_prompt,
    build_answer_repair_user_prompt,
    build_claim_extraction_user_prompt,
    build_claim_set_validation_user_prompt,
    build_cot_polish_user_prompt,
    build_cot_verify_user_prompt,
    build_evidence_binding_user_prompt,
    build_final_cot_validation_user_prompt,
    build_knowledge_user_prompt,
    build_method_planner_user_prompt,
    build_node_induction_user_prompt,
    build_node_set_validation_user_prompt,
    build_novelty_detector_user_prompt,
    build_perception_user_prompt,
    build_solution_grouping_user_prompt,
    build_solver_user_prompt,
    build_text_condition_user_prompt,
    build_trace_mapper_user_prompt,
)
from .utils import (
    canonicalize_answer_text,
    canonicalize_free_text,
    lexical_overlap_score,
    normalize_whitespace,
    safe_float,
    split_multiline_answer,
    split_or_alternatives,
    stable_digest,
    unique_list,
)


_FORMULA_CLEAN_PATTERN = re.compile(r"[\s{}]")
_NUMBER_PATTERN = re.compile(r"^[+-]?(?:\d+(?:\.\d+)?|\.\d+)$")
_ALLOWED_CLAIM_TYPES = {
    "perception",
    "text_condition",
    "knowledge_call",
    "derivation",
    "calculation",
    "final_answer",
}
_ALLOWED_NODE_TYPES = {
    "perception",
    "text_condition",
    "knowledge_call",
    "derivation",
    "calculation",
    "final_answer",
}
_ALLOWED_SUPPORT_LEVELS = {"HIGH", "MEDIUM", "LOW"}
_ALLOWED_NOVELTY_LABELS = {
    "old_family_rephrase",
    "old_family_branch_extension",
    "new_solution_family",
    "uncertain_manual_queue",
}
_CLAIM_TYPE_ALIASES = {
    "perception": "perception",
    "perception_fact": "perception",
    "visual_fact": "perception",
    "image_fact": "perception",
    "observation": "perception",
    "diagram_observation": "perception",
    "angle_identification": "perception",
    "identification": "perception",
    "recognition": "perception",
    "classification": "perception",
    "digit_recognition": "perception",
    "text_condition": "text_condition",
    "text_fact": "text_condition",
    "given": "text_condition",
    "goal": "text_condition",
    "constraint": "text_condition",
    "subquestion": "text_condition",
    "instruction": "text_condition",
    "directive": "text_condition",
    "task_instruction": "text_condition",
    "question_requirement": "text_condition",
    "output_requirement": "text_condition",
    "knowledge_call": "knowledge_call",
    "knowledge": "knowledge_call",
    "theorem": "knowledge_call",
    "principle": "knowledge_call",
    "formula": "knowledge_call",
    "rule_call": "knowledge_call",
    "theorem_call": "knowledge_call",
    "formula_call": "knowledge_call",
    "derivation": "derivation",
    "inference": "derivation",
    "relation": "derivation",
    "geometric_relation": "derivation",
    "angle_chase": "derivation",
    "reasoning_step": "derivation",
    "intermediate_step": "derivation",
    "intermediate_conclusion": "derivation",
    "calculation": "calculation",
    "arithmetic": "calculation",
    "algebra": "calculation",
    "equation_setup": "calculation",
    "substitution": "calculation",
    "simplification": "calculation",
    "numeric_computation": "calculation",
    "final_answer": "final_answer",
    "answer": "final_answer",
    "answer_claim": "final_answer",
    "conclusion": "final_answer",
    "final": "final_answer",
}
_NODE_TYPE_ALIASES = dict(_CLAIM_TYPE_ALIASES)
_NOVELTY_LABEL_ALIASES = {
    "old_family_rephrase": "old_family_rephrase",
    "paraphrase": "old_family_rephrase",
    "rephrase": "old_family_rephrase",
    "old_family_branch_extension": "old_family_branch_extension",
    "branch_extension": "old_family_branch_extension",
    "new_solution_family": "new_solution_family",
    "new_family": "new_solution_family",
    "uncertain_manual_queue": "uncertain_manual_queue",
    "uncertain": "uncertain_manual_queue",
}


class AgentContractError(RuntimeError):
    """Raised when an agent response violates the required strict contract."""


class PipelineDataContractError(RuntimeError):
    """Raised when upstream or intermediate pipeline data violates the expected schema."""


def _contract_error(agent_name: str, message: str) -> AgentContractError:
    return AgentContractError(f"[{agent_name}] {message}")


def _data_error(component_name: str, message: str) -> PipelineDataContractError:
    return PipelineDataContractError(f"[{component_name}] {message}")


def _require_response_dict(agent_name: str, response: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not isinstance(response, dict):
        raise _contract_error(agent_name, "LLM returned no JSON object.")
    return response


def _require_non_empty_text(agent_name: str, value: Any, field_name: str) -> str:
    text = normalize_whitespace(value)
    if not text:
        raise _contract_error(agent_name, f"Missing or empty required field `{field_name}`.")
    return text


def _require_list(agent_name: str, value: Any, field_name: str, allow_empty: bool = False) -> List[Any]:
    if not isinstance(value, list):
        raise _contract_error(agent_name, f"Field `{field_name}` must be a list.")
    if not allow_empty and not value:
        raise _contract_error(agent_name, f"Field `{field_name}` must not be empty.")
    return value


def _require_string_list(agent_name: str, value: Any, field_name: str, allow_empty: bool = False) -> List[str]:
    items = _require_list(agent_name, value, field_name, allow_empty=allow_empty)
    normalized: List[str] = []
    for item in items:
        if not isinstance(item, str):
            raise _contract_error(agent_name, f"Field `{field_name}` must contain only strings.")
        stripped = item.strip()
        if stripped:
            normalized.append(stripped)
    if not allow_empty and not normalized:
        raise _contract_error(agent_name, f"Field `{field_name}` contains only empty strings.")
    return normalized


def _require_bool(agent_name: str, value: Any, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise _contract_error(agent_name, f"Field `{field_name}` must be boolean.")
    return value


def _require_float(agent_name: str, value: Any, field_name: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        raise _contract_error(agent_name, f"Field `{field_name}` must be numeric.")


def _require_choice(agent_name: str, value: Any, field_name: str, allowed: set[str]) -> str:
    text = _require_non_empty_text(agent_name, value, field_name)
    normalized = text.upper() if field_name == "support_level" else text
    if normalized not in allowed:
        raise _contract_error(agent_name, f"Field `{field_name}` has unsupported value `{text}`.")
    return normalized


def _normalize_claim_type(value: Any, agent_name: str = "ClaimExtraction") -> str:
    text = _require_non_empty_text(agent_name, value, "claim_type").lower()
    normalized = _CLAIM_TYPE_ALIASES.get(text)
    if normalized is None:
        raise _contract_error(agent_name, f"Unsupported claim_type `{text}`.")
    return normalized


def _normalize_node_type(value: Any, agent_name: str = "NodeInduction") -> str:
    text = _require_non_empty_text(agent_name, value, "node_type").lower()
    normalized = _NODE_TYPE_ALIASES.get(text)
    if normalized is None:
        raise _contract_error(agent_name, f"Unsupported node_type `{text}`.")
    return normalized


def _normalize_novelty_label(value: Any, agent_name: str = "NoveltyDetector") -> str:
    text = _require_non_empty_text(agent_name, value, "novelty_label")
    normalized = _NOVELTY_LABEL_ALIASES.get(text)
    if normalized is None:
        raise _contract_error(agent_name, f"Unsupported novelty_label `{text}`.")
    return normalized


def _load_images(image_paths: Sequence[str]):
    from PIL import Image

    images = []
    for path in image_paths:
        try:
            with Image.open(path) as img:
                images.append(img.convert("RGB"))
        except Exception as exc:  # pragma: no cover
            raise PipelineDataContractError(f"[ImageLoader] Failed to open image `{path}`: {exc}") from exc
    return images


def _problem_image_paths(problem: Dict[str, Any]) -> List[str]:
    output: List[str] = []
    for item in problem.get("images") or []:
        if isinstance(item, str):
            value = item.strip()
            if value:
                output.append(value)
    return output


def _call_router(
    router: ModelRouter,
    system_prompt: str,
    user_prompt: str,
    image_paths: Sequence[str],
    agent_name: str,
    require_images: bool = False,
) -> Dict[str, Any]:
    images = _load_images(image_paths)
    if require_images and not images:
        raise _contract_error(agent_name, "This agent requires image input, but no loadable images were found.")
    response = (
        router.chat_json_with_images(system_prompt, user_prompt, images)
        if images
        else router.chat_json(system_prompt, user_prompt)
    )
    if not isinstance(response, dict):
        error_summary = router.last_error_summary()
        raise _contract_error(
            agent_name,
            f"LLM returned no JSON object. primary_last_error={error_summary.get('primary_last_error')!r}; fallback_last_error={error_summary.get('fallback_last_error')!r}",
        )
    if require_images and response.get("_llm_request_mode") != "multimodal":
        raise _contract_error(
            agent_name,
            f"Image-grounded request must be multimodal, but actual request mode was {response.get('_llm_request_mode')!r}.",
        )
    return response


def _ensure_problem_minimum(problem: Dict[str, Any], component_name: str) -> None:
    if not normalize_whitespace(problem.get("problem_id", "")):
        raise _data_error(component_name, "Problem is missing `problem_id`.")
    if not normalize_whitespace(problem.get("question_text", "")):
        raise _data_error(component_name, "Problem is missing `question_text`.")
    if not normalize_whitespace(problem.get("standard_answer", "")):
        raise _data_error(component_name, "Problem is missing `standard_answer`.")


def _build_ready_context_summary(problem: Dict[str, Any], component_name: str) -> Dict[str, Any]:
    sample_record = problem.get("sample_record") or {}
    summary: Dict[str, Any] = {
        "dataset_name": problem.get("dataset_name", ""),
        "subject": problem.get("subject", ""),
        "alignment_status": problem.get("alignment_status", "unknown"),
        "solvability_score": safe_float(problem.get("solvability_score"), 0.0),
        "question_type": (problem.get("metadata") or {}).get("question_type"),
        "multi_solution_policy": (problem.get("metadata") or {}).get("multi_solution_policy"),
    }

    text_records = sample_record.get("text_structure_records") or []
    if text_records and isinstance(text_records[0], dict):
        first = text_records[0]
        summary["text_segments"] = (first.get("text_segments") or [])[:16]
        summary["targets"] = (first.get("targets") or [])[:8]
        summary["entities"] = (first.get("entities") or [])[:12]

    if problem.get("requires_image"):
        visual_records = sample_record.get("visual_structure_records") or []
        if not visual_records or not isinstance(visual_records[0], dict):
            raise _data_error(component_name, "Problem requires image grounding but ready sample is missing `visual_structure_records`.")
        first_visual = visual_records[0]
        summary["visual_global_attributes"] = first_visual.get("global_attributes") or {}
        summary["visual_entities"] = (first_visual.get("visual_entities") or [])[:20]
        summary["visual_relations"] = (first_visual.get("visual_relations") or [])[:20]

    node_records = sample_record.get("node_records") or []
    if node_records:
        summary["upstream_nodes"] = [
            {
                "node_id": item.get("node_id"),
                "node_type": item.get("node_type"),
                "canonical_value": item.get("canonical_value"),
                "source_refs": item.get("source_refs", []),
            }
            for item in node_records[:20]
            if isinstance(item, dict)
        ]

    return summary


def _augment_prompt_with_ready_context(problem: Dict[str, Any], base_prompt: str, component_name: str) -> str:
    summary = _build_ready_context_summary(problem, component_name)
    image_requirement = ""
    if problem.get("requires_image"):
        image_requirement = (
            "\n\nATTACHED IMAGE REQUIREMENT:\n"
            "This is an image-grounded problem. Images are attached to this request. "
            "Inspect the attached image(s) directly and ground every visual or structural claim in them; "
            "do not rely only on the structured context summary."
        )
    return (
        base_prompt
        + image_requirement
        + "\n\nREADY STRUCTURED CONTEXT (trusted upstream normalized extraction; use this as the authoritative multimodal grounding context):\n"
        + json.dumps(summary, ensure_ascii=False, indent=2)
    )


def _formula_canonical(text: str) -> str:
    return _FORMULA_CLEAN_PATTERN.sub("", canonicalize_answer_text(text))


def _numeric_equal(a: str, b: str, tolerance: float = 1e-6) -> bool:
    if not (_NUMBER_PATTERN.fullmatch(a) and _NUMBER_PATTERN.fullmatch(b)):
        return False
    return math.isclose(float(a), float(b), rel_tol=tolerance, abs_tol=tolerance)


def _part_equivalent(pred_part: str, std_part: str) -> bool:
    pred_canonical = canonicalize_answer_text(pred_part)
    std_canonical = canonicalize_answer_text(std_part)
    if pred_canonical == std_canonical:
        return True
    if _numeric_equal(pred_canonical, std_canonical):
        return True
    std_alternatives = split_or_alternatives(std_part)
    if len(std_alternatives) > 1:
        return any(_part_equivalent(pred_part, candidate) for candidate in std_alternatives)
    pred_alternatives = split_or_alternatives(pred_part)
    if len(pred_alternatives) > 1:
        return any(_part_equivalent(candidate, std_part) for candidate in pred_alternatives)
    return _formula_canonical(pred_part) == _formula_canonical(std_part)


def deterministic_answer_match(problem: Dict[str, Any], predicted_answer: str) -> Dict[str, Any]:
    standard_answer = normalize_whitespace(problem.get("standard_answer", ""))
    predicted_answer = normalize_whitespace(predicted_answer)
    std_parts = split_multiline_answer(standard_answer)
    pred_parts = split_multiline_answer(predicted_answer)
    if len(std_parts) == 1 and len(pred_parts) > 1:
        std_parts = split_multiline_answer(standard_answer.replace(";", "\n"))
    if len(pred_parts) == 1 and len(std_parts) > 1:
        pred_parts = split_multiline_answer(predicted_answer.replace(";", "\n"))
    part_results: List[Dict[str, Any]] = []
    if len(std_parts) != len(pred_parts):
        return {
            "is_equivalent": False,
            "reason": "part_count_mismatch",
            "part_results": [],
        }
    is_equivalent = True
    for standard_part, predicted_part in zip(std_parts, pred_parts):
        part_ok = _part_equivalent(predicted_part, standard_part)
        is_equivalent = is_equivalent and part_ok
        part_results.append(
            {
                "standard_part": standard_part,
                "predicted_part": predicted_part,
                "is_equivalent": part_ok,
                "reason": "deterministic_match" if part_ok else "deterministic_mismatch",
            }
        )
    return {
        "is_equivalent": is_equivalent,
        "reason": "deterministic_match" if is_equivalent else "deterministic_mismatch",
        "part_results": part_results,
    }


def target_method_count_from_score(initial_multi_solution_score: Any, thresholds: Tuple[float, float]) -> int:
    low, high = thresholds
    score = safe_float(initial_multi_solution_score, 0.0)
    if score < low:
        return 1
    if score < high:
        return 2
    return 3


def _normalize_method_plan_candidate(item: Dict[str, Any], index: int) -> Dict[str, Any]:
    method_id = normalize_whitespace(item.get("method_id")) or str(index)
    method_draft = _require_non_empty_text("MethodPlanner", item.get("method_draft"), "method_draft")
    distinctiveness_rationale = _require_non_empty_text("MethodPlanner", item.get("distinctiveness_rationale"), "distinctiveness_rationale")
    image_role = _require_non_empty_text("MethodPlanner", item.get("image_role"), "image_role")
    text_role = _require_non_empty_text("MethodPlanner", item.get("text_role"), "text_role")
    knowledge_role = _require_non_empty_text("MethodPlanner", item.get("knowledge_role"), "knowledge_role")
    return {
        "method_id": method_id,
        "method_draft": method_draft,
        "distinctiveness_rationale": distinctiveness_rationale,
        "image_role": image_role,
        "text_role": text_role,
        "knowledge_role": knowledge_role,
    }


def _method_candidates_are_duplicate(left: Dict[str, Any], right: Dict[str, Any]) -> bool:
    left_draft = canonicalize_free_text(left.get("method_draft", ""))
    right_draft = canonicalize_free_text(right.get("method_draft", ""))
    if left_draft and left_draft == right_draft:
        return True
    draft_overlap = lexical_overlap_score(left.get("method_draft", ""), right.get("method_draft", ""))
    image_overlap = lexical_overlap_score(left.get("image_role", ""), right.get("image_role", ""))
    text_overlap = lexical_overlap_score(left.get("text_role", ""), right.get("text_role", ""))
    knowledge_overlap = lexical_overlap_score(left.get("knowledge_role", ""), right.get("knowledge_role", ""))
    high_role_overlap_count = sum(score >= 0.6 for score in (image_overlap, text_overlap, knowledge_overlap))
    if draft_overlap >= 0.82 and high_role_overlap_count >= 2:
        return True
    if draft_overlap >= 0.9:
        return True
    return False


def plan_methods(
    router: ModelRouter,
    problem: Dict[str, Any],
    method_count: int,
    existing_methods: Optional[Sequence[Dict[str, Any]]] = None,
    attempt_index: int = 1,
    target_method_count: Optional[int] = None,
) -> List[Dict[str, Any]]:
    _ensure_problem_minimum(problem, "MethodPlanner")
    response = _call_router(
        router,
        METHOD_PLANNER_SYSTEM_PROMPT,
        _augment_prompt_with_ready_context(
            problem,
            build_method_planner_user_prompt(
                problem,
                method_count,
                existing_methods=existing_methods or [],
                attempt_index=attempt_index,
                target_method_count=target_method_count or method_count,
            ),
            "MethodPlanner",
        ),
        _problem_image_paths(problem),
        agent_name="MethodPlanner",
        require_images=bool(problem.get("requires_image")),
    )
    methods = _require_list("MethodPlanner", response.get("methods", []), "methods", allow_empty=True)
    normalized: List[Dict[str, Any]] = []
    accepted_methods = list(existing_methods or [])
    for index, item in enumerate(methods, start=1):
        if not isinstance(item, dict):
            raise _contract_error("MethodPlanner", "Each item in `methods` must be an object.")
        candidate = _normalize_method_plan_candidate(item, index)
        if any(_method_candidates_are_duplicate(candidate, existing) for existing in accepted_methods + normalized):
            continue
        normalized.append(candidate)
    return normalized[:method_count]


def plan_method_collection(
    router: ModelRouter,
    problem: Dict[str, Any],
    target_method_count: int,
    max_attempts: int = 3,
) -> Dict[str, Any]:
    collected: List[Dict[str, Any]] = []
    attempt_summaries: List[Dict[str, Any]] = []
    for attempt_index in range(1, max_attempts + 1):
        remaining = target_method_count - len(collected)
        if remaining <= 0:
            break
        new_methods = plan_methods(
            router,
            problem,
            method_count=remaining,
            existing_methods=collected,
            attempt_index=attempt_index,
            target_method_count=target_method_count,
        )
        collected.extend(new_methods)
        attempt_summaries.append(
            {
                "attempt_index": attempt_index,
                "requested_additional_method_count": remaining,
                "accepted_new_method_count": len(new_methods),
                "accepted_total_method_count": len(collected),
            }
        )
    if not collected:
        raise _contract_error("MethodPlanner", "Planner failed to produce any valid unique method drafts.")
    reindexed = []
    for index, item in enumerate(collected, start=1):
        reindexed.append({**item, "method_id": str(index)})
    return {
        "target_method_count_from_score": target_method_count,
        "actual_method_count": len(reindexed),
        "planning_attempt_count": len(attempt_summaries),
        "met_target_method_count": len(reindexed) >= target_method_count,
        "shortfall_reason": "" if len(reindexed) >= target_method_count else "insufficient_distinct_routes_after_retry",
        "attempt_summaries": attempt_summaries,
        "methods": reindexed,
    }


def solve_method(router: ModelRouter, problem: Dict[str, Any], method: Dict[str, Any]) -> Dict[str, Any]:
    _ensure_problem_minimum(problem, "Solver")
    if not normalize_whitespace(method.get("method_draft", "")):
        raise _data_error("Solver", "Method is missing `method_draft`.")
    response = _call_router(
        router,
        SOLVER_SYSTEM_PROMPT,
        _augment_prompt_with_ready_context(problem, build_solver_user_prompt(problem, method), "Solver"),
        problem.get("images", []),
        agent_name="Solver",
        require_images=bool(problem.get("requires_image")),
    )
    cot_raw = _require_non_empty_text("Solver", response.get("cot_raw"), "cot_raw")
    model_answer = _require_non_empty_text("Solver", response.get("model_answer"), "model_answer")
    return {
        "cot": cot_raw,
        "answer": model_answer,
        "meta": response,
    }


def judge_answer_equivalence(router: ModelRouter, problem: Dict[str, Any], predicted_answer: str, cot_text: str) -> Dict[str, Any]:
    _ensure_problem_minimum(problem, "AnswerEquivalenceJudge")
    deterministic = deterministic_answer_match(problem, predicted_answer)
    if deterministic["is_equivalent"]:
        return deterministic
    response = _call_router(
        router,
        ANSWER_EQUIVALENCE_SYSTEM_PROMPT,
        build_answer_equivalence_user_prompt(problem, predicted_answer, cot_text),
        _problem_image_paths(problem),
        agent_name="AnswerEquivalenceJudge",
        require_images=bool(problem.get("requires_image")),
    )
    return {
        "is_equivalent": _require_bool("AnswerEquivalenceJudge", response.get("is_equivalent"), "is_equivalent"),
        "reason": _require_non_empty_text("AnswerEquivalenceJudge", response.get("reason"), "reason"),
        "part_results": _require_list("AnswerEquivalenceJudge", response.get("part_results", []), "part_results", allow_empty=True),
    }


def repair_answer(router: ModelRouter, problem: Dict[str, Any], method: Dict[str, Any], cot_text: str, predicted_answer: str) -> Dict[str, str]:
    _ensure_problem_minimum(problem, "AnswerRepair")
    response = _call_router(
        router,
        ANSWER_REPAIR_SYSTEM_PROMPT,
        _augment_prompt_with_ready_context(problem, build_answer_repair_user_prompt(problem, method, cot_text, predicted_answer), "AnswerRepair"),
        problem.get("images", []),
        agent_name="AnswerRepair",
        require_images=bool(problem.get("requires_image")),
    )
    return {
        "cot": _require_non_empty_text("AnswerRepair", response.get("repaired_cot"), "repaired_cot"),
        "answer": _require_non_empty_text("AnswerRepair", response.get("repaired_answer"), "repaired_answer"),
        "notes": _require_non_empty_text("AnswerRepair", response.get("repair_notes"), "repair_notes"),
    }


def verify_cot(router: ModelRouter, problem: Dict[str, Any], method: Dict[str, Any], cot_text: str) -> Dict[str, Any]:
    _ensure_problem_minimum(problem, "CoTVerify")
    response = _call_router(
        router,
        COT_VERIFY_SYSTEM_PROMPT,
        _augment_prompt_with_ready_context(problem, build_cot_verify_user_prompt(problem, method, cot_text), "CoTVerify"),
        problem.get("images", []),
        agent_name="CoTVerify",
        require_images=bool(problem.get("requires_image")),
    )
    return {
        "verify_pass": _require_bool("CoTVerify", response.get("verify_pass"), "verify_pass"),
        "critic_suggestions": normalize_whitespace(response.get("critic_suggestions", "")),
        "major_failures": _require_list("CoTVerify", response.get("major_failures"), "major_failures", allow_empty=True),
        "extractability_score": _require_float("CoTVerify", response.get("extractability_score"), "extractability_score"),
        "grounding_score": _require_float("CoTVerify", response.get("grounding_score"), "grounding_score"),
        "method_fidelity_score": _require_float("CoTVerify", response.get("method_fidelity_score"), "method_fidelity_score"),
        "meta": response,
    }


def polish_cot(router: ModelRouter, problem: Dict[str, Any], method: Dict[str, Any], cot_text: str, suggestion: str) -> Dict[str, Any]:
    _ensure_problem_minimum(problem, "CoTPolish")
    response = _call_router(
        router,
        COT_POLISH_SYSTEM_PROMPT,
        _augment_prompt_with_ready_context(problem, build_cot_polish_user_prompt(problem, method, cot_text, suggestion), "CoTPolish"),
        problem.get("images", []),
        agent_name="CoTPolish",
        require_images=bool(problem.get("requires_image")),
    )
    return {
        "polished_cot": _require_non_empty_text("CoTPolish", response.get("polished_cot"), "polished_cot"),
        "polish_summary": _require_non_empty_text("CoTPolish", response.get("polish_summary"), "polish_summary"),
        "preserved_method_identity": _require_bool("CoTPolish", response.get("preserved_method_identity"), "preserved_method_identity"),
    }


def extract_ptk(router: ModelRouter, problem: Dict[str, Any]) -> Dict[str, Any]:
    _ensure_problem_minimum(problem, "PTKFoundation")

    p_response = _call_router(
        router,
        PERCEPTION_EXTRACTION_SYSTEM_PROMPT,
        _augment_prompt_with_ready_context(problem, build_perception_user_prompt(problem), "PerceptionExtraction"),
        _problem_image_paths(problem),
        agent_name="PerceptionExtraction",
        require_images=bool(problem.get("requires_image")),
    )
    p_items = _require_list("PerceptionExtraction", p_response.get("p_facts"), "p_facts", allow_empty=False)
    p_facts: List[Dict[str, Any]] = []
    for item in p_items:
        if not isinstance(item, dict):
            raise _contract_error("PerceptionExtraction", "Each `p_fact` must be an object.")
        p_facts.append(
            {
                "p_id": _require_non_empty_text("PerceptionExtraction", item.get("p_id"), "p_id"),
                "fact_text": _require_non_empty_text("PerceptionExtraction", item.get("fact_text"), "fact_text"),
                "confidence": _require_float("PerceptionExtraction", item.get("confidence"), "confidence"),
                "visual_anchor": _require_non_empty_text("PerceptionExtraction", item.get("visual_anchor"), "visual_anchor"),
            }
        )

    t_response = _call_router(
        router,
        TEXT_CONDITION_SYSTEM_PROMPT,
        _augment_prompt_with_ready_context(problem, build_text_condition_user_prompt(problem), "TextCondition"),
        _problem_image_paths(problem),
        agent_name="TextCondition",
        require_images=bool(problem.get("requires_image")),
    )
    t_items = _require_list("TextCondition", t_response.get("t_facts"), "t_facts")
    t_facts: List[Dict[str, Any]] = []
    for item in t_items:
        if not isinstance(item, dict):
            raise _contract_error("TextCondition", "Each `t_fact` must be an object.")
        fact_role = _require_non_empty_text("TextCondition", item.get("fact_role"), "fact_role")
        t_facts.append(
            {
                "t_id": _require_non_empty_text("TextCondition", item.get("t_id"), "t_id"),
                "fact_text": _require_non_empty_text("TextCondition", item.get("fact_text"), "fact_text"),
                "fact_role": fact_role,
            }
        )

    k_response = _call_router(
        router,
        KNOWLEDGE_LIBRARIAN_SYSTEM_PROMPT,
        _augment_prompt_with_ready_context(problem, build_knowledge_user_prompt(problem, p_facts, t_facts), "KnowledgeLibrarian"),
        _problem_image_paths(problem),
        agent_name="KnowledgeLibrarian",
        require_images=bool(problem.get("requires_image")),
    )
    k_items = _require_list("KnowledgeLibrarian", k_response.get("k_atoms"), "k_atoms")
    k_atoms: List[Dict[str, Any]] = []
    for item in k_items:
        if not isinstance(item, dict):
            raise _contract_error("KnowledgeLibrarian", "Each `k_atom` must be an object.")
        k_atoms.append(
            {
                "k_id": _require_non_empty_text("KnowledgeLibrarian", item.get("k_id"), "k_id"),
                "knowledge_text": _require_non_empty_text("KnowledgeLibrarian", item.get("knowledge_text"), "knowledge_text"),
                "knowledge_type": _require_non_empty_text("KnowledgeLibrarian", item.get("knowledge_type"), "knowledge_type"),
                "applicability_note": _require_non_empty_text("KnowledgeLibrarian", item.get("applicability_note"), "applicability_note"),
            }
        )

    problem_record = {
        "problem_id": problem.get("problem_id", ""),
        "question_text": problem.get("question_text", ""),
        "standard_answer": problem.get("standard_answer", ""),
        "images": list(problem.get("images") or []),
        "dataset_name": problem.get("dataset_name", ""),
        "source_problem_id": problem.get("source_problem_id", ""),
        "subject": problem.get("subject", ""),
        "requires_image": bool(problem.get("requires_image")),
        "text_dominant": bool(problem.get("text_dominant")),
        "alignment_status": problem.get("alignment_status", "unknown"),
        "solvability_score": safe_float(problem.get("solvability_score"), 0.0),
        "sample_path": problem.get("sample_path", ""),
    }
    return {
        "problem_record": problem_record,
        "p_facts": p_facts,
        "t_facts": t_facts,
        "k_atoms": k_atoms,
    }


def extract_claims(router: ModelRouter, problem: Dict[str, Any], method: Dict[str, Any], cot_text: str) -> List[Dict[str, Any]]:
    _ensure_problem_minimum(problem, "ClaimExtraction")
    response = _call_router(
        router,
        CLAIM_EXTRACTION_SYSTEM_PROMPT,
        _augment_prompt_with_ready_context(problem, build_claim_extraction_user_prompt(problem, method, cot_text), "ClaimExtraction"),
        _problem_image_paths(problem),
        agent_name="ClaimExtraction",
        require_images=bool(problem.get("requires_image")),
    )
    claims = _require_list("ClaimExtraction", response.get("claims"), "claims")
    output: List[Dict[str, Any]] = []
    seen_ids: set[str] = set()
    for item in claims:
        if not isinstance(item, dict):
            raise _contract_error("ClaimExtraction", "Each claim must be an object.")
        claim_id = _require_non_empty_text("ClaimExtraction", item.get("claim_id"), "claim_id")
        if claim_id in seen_ids:
            raise _contract_error("ClaimExtraction", f"Duplicate claim_id `{claim_id}`.")
        seen_ids.add(claim_id)
        claim_type = _normalize_claim_type(item.get("claim_type"), "ClaimExtraction")
        depends_on = _require_string_list("ClaimExtraction", item.get("depends_on", []), "depends_on", allow_empty=True)
        output.append(
            ClaimRecord(
                claim_id=claim_id,
                problem_id=str(problem.get("problem_id", "")),
                method_id=str(method.get("method_id", "")),
                claim_text=_require_non_empty_text("ClaimExtraction", item.get("claim_text"), "claim_text"),
                claim_type=claim_type,
                depends_on=depends_on,
                evidence_hint=normalize_whitespace(item.get("evidence_hint", "")),
            ).to_dict()
        )
    return output


def induce_nodes(router: ModelRouter, problem: Dict[str, Any], claims: Sequence[Dict[str, Any]], p_facts: Sequence[Dict[str, Any]], t_facts: Sequence[Dict[str, Any]], k_atoms: Sequence[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    if not claims:
        raise _data_error("NodeInduction", "Cannot induce nodes from an empty claim set.")
    claim_lookup = {
        str(item.get("claim_id", "")): item
        for item in claims
        if isinstance(item, dict) and str(item.get("claim_id", ""))
    }
    claim_id_set = set(claim_lookup)
    response = _call_router(
        router,
        NODE_INDUCTION_SYSTEM_PROMPT,
        build_node_induction_user_prompt(problem, claims, p_facts, t_facts, k_atoms),
        _problem_image_paths(problem),
        agent_name="NodeInduction",
        require_images=bool(problem.get("requires_image")),
    )
    canonical_nodes = _require_list("NodeInduction", response.get("canonical_nodes"), "canonical_nodes")
    grouped: Dict[str, NodeRecord] = {}
    claim_mappings: List[Dict[str, Any]] = []
    for item in canonical_nodes:
        if not isinstance(item, dict):
            raise _contract_error("NodeInduction", "Each canonical node item must be an object.")
        claim_id = _require_non_empty_text("NodeInduction", item.get("claim_id"), "claim_id")
        if claim_id not in claim_id_set:
            raise _contract_error("NodeInduction", f"Unknown claim_id `{claim_id}` in canonical_nodes.")
        claim_record = claim_lookup[claim_id]
        claim_text = _require_non_empty_text("NodeInduction", claim_record.get("claim_text"), "claim_text")
        suggested_canonical_claim = _require_non_empty_text("NodeInduction", item.get("canonical_claim"), "canonical_claim")
        node_type = _normalize_node_type(item.get("node_type"), "NodeInduction")
        support_level = _require_choice("NodeInduction", item.get("support_level"), "support_level", _ALLOWED_SUPPORT_LEVELS)

        # Keep node canonicalization source-faithful: do not let NodeInduction expand a node
        # beyond the actual source claim text. We still use the model-suggested canonical claim
        # only for grouping if it is semantically close enough, but the stored canonical claim
        # falls back to the exact source claim text.
        group_key = canonicalize_free_text(claim_text)
        canonical_claim = claim_text
        if canonicalize_free_text(suggested_canonical_claim) == group_key:
            canonical_claim = suggested_canonical_claim

        if group_key not in grouped:
            grouped[group_key] = NodeRecord(
                r_id=f"r_{stable_digest([str(problem.get('problem_id', '')), group_key])}",
                problem_id=str(problem.get("problem_id", "")),
                node_type=node_type,
                canonical_claim=canonical_claim,
                surface_forms=[claim_text],
                equivalence_group_id=f"eq_{stable_digest([group_key], 12)}",
                support_level=support_level,
                source_claim_ids=[claim_id],
            )
        else:
            grouped[group_key].surface_forms = unique_list(grouped[group_key].surface_forms + [claim_text])
            grouped[group_key].source_claim_ids = unique_list(grouped[group_key].source_claim_ids + [claim_id])
        claim_mappings.append(
            {
                "claim_id": claim_id,
                "r_id": grouped[group_key].r_id,
                "equivalence_group_id": grouped[group_key].equivalence_group_id,
            }
        )
    return [node.to_dict() for node in grouped.values()], claim_mappings


def group_solutions(router: ModelRouter, problem: Dict[str, Any], methods: Sequence[Dict[str, Any]], r_nodes: Sequence[Dict[str, Any]], claim_sequences: Sequence[Dict[str, Any]], claim_mappings: Sequence[Dict[str, Any]], k_atoms: Sequence[Dict[str, Any]], planned_method_count: Optional[int] = None) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
    del claim_sequences, k_atoms
    if not methods:
        raise _data_error("SolutionGrouper", "No qualified methods available for solution grouping.")
    r_id_set = {str(node.get("r_id", "")) for node in r_nodes}
    method_id_set = {str(method.get("method_id", "")) for method in methods}
    response = _call_router(
        router,
        SOLUTION_GROUPER_SYSTEM_PROMPT,
        build_solution_grouping_user_prompt(problem, methods, r_nodes, claim_mappings),
        _problem_image_paths(problem),
        agent_name="SolutionGrouper",
        require_images=bool(problem.get("requires_image")),
    )
    raw_solutions = _require_list("SolutionGrouper", response.get("solutions"), "solutions")
    solutions: List[Dict[str, Any]] = []
    for item in raw_solutions:
        if not isinstance(item, dict):
            raise _contract_error("SolutionGrouper", "Each solution must be an object.")
        solution_id = _require_non_empty_text("SolutionGrouper", item.get("solution_id"), "solution_id")
        method_signature = _require_non_empty_text("SolutionGrouper", item.get("method_signature"), "method_signature")
        required_r_ids = _require_string_list("SolutionGrouper", item.get("required_r_ids"), "required_r_ids")
        optional_r_ids = _require_string_list("SolutionGrouper", item.get("optional_r_ids", []), "optional_r_ids", allow_empty=True)
        ordered_core_path = _require_string_list("SolutionGrouper", item.get("ordered_core_path"), "ordered_core_path")
        supported_answer = _require_non_empty_text("SolutionGrouper", item.get("supported_answer"), "supported_answer")
        member_method_ids = _require_string_list("SolutionGrouper", item.get("member_method_ids"), "member_method_ids")
        for r_id in required_r_ids + optional_r_ids + ordered_core_path:
            if r_id not in r_id_set:
                raise _contract_error("SolutionGrouper", f"Unknown r_id `{r_id}` referenced by solution `{solution_id}`.")
        for method_id in member_method_ids:
            if method_id not in method_id_set:
                raise _contract_error("SolutionGrouper", f"Unknown method_id `{method_id}` referenced by solution `{solution_id}`.")
        solutions.append(
            SolutionRecord(
                solution_id=solution_id,
                problem_id=str(problem.get("problem_id", "")),
                method_signature=method_signature,
                required_r_ids=required_r_ids,
                optional_r_ids=optional_r_ids,
                ordered_core_path=ordered_core_path,
                supported_answer=supported_answer,
                member_method_ids=member_method_ids,
            ).to_dict()
        )
    solution_memberships: List[Dict[str, Any]] = []
    for solution in solutions:
        solution_id = str(solution.get("solution_id", ""))
        for order_index, r_id in enumerate(solution.get("required_r_ids") or []):
            solution_memberships.append(
                {
                    "solution_id": solution_id,
                    "r_id": r_id,
                    "membership_role": "required",
                    "order_index": order_index,
                }
            )
        for order_index, r_id in enumerate(solution.get("optional_r_ids") or []):
            solution_memberships.append(
                {
                    "solution_id": solution_id,
                    "r_id": r_id,
                    "membership_role": "optional",
                    "order_index": order_index,
                }
            )
    qualified_method_count = len(methods)
    method_count = planned_method_count if isinstance(planned_method_count, int) and planned_method_count > 0 else qualified_method_count
    coverage_state = {
        "problem_id": problem.get("problem_id", ""),
        "method_count": method_count,
        "qualified_method_count": qualified_method_count,
        "solution_count": len(solutions),
        "node_count": len(r_nodes),
        "coverage_near_saturated": len(solutions) >= max(1, qualified_method_count),
    }
    return solutions, solution_memberships, coverage_state


def bind_evidence(router: ModelRouter, problem: Dict[str, Any], r_nodes: Sequence[Dict[str, Any]], p_facts: Sequence[Dict[str, Any]], t_facts: Sequence[Dict[str, Any]], k_atoms: Sequence[Dict[str, Any]], claim_sequences: Sequence[Dict[str, Any]], claim_mappings: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    del claim_sequences, claim_mappings
    r_id_set = {str(node.get("r_id", "")) for node in r_nodes}
    p_id_set = {str(item.get("p_id", "")) for item in p_facts}
    t_id_set = {str(item.get("t_id", "")) for item in t_facts}
    k_id_set = {str(item.get("k_id", "")) for item in k_atoms}
    response = _call_router(
        router,
        EVIDENCE_BINDER_SYSTEM_PROMPT,
        build_evidence_binding_user_prompt(problem, r_nodes, p_facts, t_facts, k_atoms),
        _problem_image_paths(problem),
        agent_name="EvidenceBinder",
        require_images=bool(problem.get("requires_image")),
    )
    bindings = _require_list("EvidenceBinder", response.get("bindings"), "bindings")
    normalized: List[Dict[str, Any]] = []
    bound_r_ids: set[str] = set()
    for item in bindings:
        if not isinstance(item, dict):
            raise _contract_error("EvidenceBinder", "Each binding must be an object.")
        r_id = _require_non_empty_text("EvidenceBinder", item.get("r_id"), "r_id")
        if r_id not in r_id_set:
            raise _contract_error("EvidenceBinder", f"Unknown r_id `{r_id}` in binding output.")
        p_fact_ids = _require_string_list("EvidenceBinder", item.get("p_fact_ids", []), "p_fact_ids", allow_empty=True)
        t_fact_ids = _require_string_list("EvidenceBinder", item.get("t_fact_ids", []), "t_fact_ids", allow_empty=True)
        k_atom_ids = _require_string_list("EvidenceBinder", item.get("k_atom_ids", []), "k_atom_ids", allow_empty=True)
        predecessor_r_ids = _require_string_list("EvidenceBinder", item.get("predecessor_r_ids", []), "predecessor_r_ids", allow_empty=True)
        for item_id in p_fact_ids:
            if item_id not in p_id_set:
                raise _contract_error("EvidenceBinder", f"Unknown p_fact_id `{item_id}` in binding output.")
        for item_id in t_fact_ids:
            if item_id not in t_id_set:
                raise _contract_error("EvidenceBinder", f"Unknown t_fact_id `{item_id}` in binding output.")
        for item_id in k_atom_ids:
            if item_id not in k_id_set:
                raise _contract_error("EvidenceBinder", f"Unknown k_atom_id `{item_id}` in binding output.")
        for item_id in predecessor_r_ids:
            if item_id not in r_id_set:
                raise _contract_error("EvidenceBinder", f"Unknown predecessor_r_id `{item_id}` in binding output.")
        normalized.append(
            {
                "r_id": r_id,
                "p_fact_ids": p_fact_ids,
                "t_fact_ids": t_fact_ids,
                "k_atom_ids": k_atom_ids,
                "predecessor_r_ids": predecessor_r_ids,
                "support_strength": _require_choice("EvidenceBinder", item.get("support_strength"), "support_strength", _ALLOWED_SUPPORT_LEVELS),
                "binding_rationale": _require_non_empty_text("EvidenceBinder", item.get("binding_rationale"), "binding_rationale"),
            }
        )
        bound_r_ids.add(r_id)
    missing = sorted(r_id_set - bound_r_ids)
    if missing:
        raise _contract_error("EvidenceBinder", f"Missing evidence bindings for nodes: {missing}")
    return normalized


def build_trace_mapping_index(problem_bundle: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "problem_id": problem_bundle.get("problem_record", {}).get("problem_id", ""),
        "node_catalog": [
            {
                "r_id": node.get("r_id"),
                "canonical_claim": node.get("canonical_claim"),
                "surface_forms": node.get("surface_forms", []),
                "node_type": node.get("node_type"),
            }
            for node in problem_bundle.get("r_nodes", [])
        ],
        "solutions": [
            {
                "solution_id": solution.get("solution_id"),
                "required_r_ids": solution.get("required_r_ids", []),
                "optional_r_ids": solution.get("optional_r_ids", []),
                "ordered_core_path": solution.get("ordered_core_path", []),
            }
            for solution in problem_bundle.get("solution_library", [])
        ],
    }


def extract_claims_for_prediction(router: ModelRouter, problem_bundle: Dict[str, Any], trace_record: Dict[str, Any]) -> List[Dict[str, Any]]:
    problem = problem_bundle.get("runtime_problem") or problem_bundle.get("problem_record", {})
    pseudo_method = {
        "method_id": trace_record.get("run_id", "pred"),
        "method_draft": trace_record.get("method_hint", "prediction-trace"),
    }
    return extract_claims(router, problem, pseudo_method, trace_record.get("pred_cot", ""))


def map_trace(router: ModelRouter, problem_bundle: Dict[str, Any], trace_record: Dict[str, Any], novelty_total_threshold: float, novelty_required_threshold: float) -> Dict[str, Any]:
    pred_claims = extract_claims_for_prediction(router, problem_bundle, trace_record)
    trace_problem = problem_bundle.get("runtime_problem") or problem_bundle.get("problem_record", {})
    response = _call_router(
        router,
        TRACE_MAPPER_SYSTEM_PROMPT,
        build_trace_mapper_user_prompt(problem_bundle, trace_record, pred_claims),
        _problem_image_paths(trace_problem),
        agent_name="TraceMapper",
        require_images=bool(trace_problem.get("requires_image")),
    )
    best_solution_id = _require_non_empty_text("TraceMapper", response.get("best_solution_id"), "best_solution_id")
    matched_r_ids = _require_string_list("TraceMapper", response.get("matched_r_ids"), "matched_r_ids", allow_empty=True)
    matched_required_r_ids = _require_string_list("TraceMapper", response.get("matched_required_r_ids"), "matched_required_r_ids", allow_empty=True)
    unmatched_claim_ids = _require_string_list("TraceMapper", response.get("unmatched_claim_ids"), "unmatched_claim_ids", allow_empty=True)
    claim_matches_raw = _require_list("TraceMapper", response.get("claim_matches", []), "claim_matches", allow_empty=True)

    nodes = problem_bundle.get("r_nodes", [])
    r_id_set = {str(node.get("r_id", "")) for node in nodes}
    claim_id_set = {str(claim.get("claim_id", "")) for claim in pred_claims}
    solutions = {str(item.get("solution_id", "")): item for item in problem_bundle.get("solution_library", []) if isinstance(item, dict)}
    if best_solution_id not in solutions:
        raise _contract_error("TraceMapper", f"Unknown solution_id `{best_solution_id}` returned by trace mapper.")
    for r_id in matched_r_ids + matched_required_r_ids:
        if r_id not in r_id_set:
            raise _contract_error("TraceMapper", f"Unknown r_id `{r_id}` returned by trace mapper.")
    for claim_id in unmatched_claim_ids:
        if claim_id not in claim_id_set:
            raise _contract_error("TraceMapper", f"Unknown claim_id `{claim_id}` returned as unmatched.")

    claim_matches: List[Dict[str, Any]] = []
    for item in claim_matches_raw:
        if not isinstance(item, dict):
            raise _contract_error("TraceMapper", "Each claim match must be an object.")
        claim_id = _require_non_empty_text("TraceMapper", item.get("claim_id"), "claim_id")
        r_id = _require_non_empty_text("TraceMapper", item.get("r_id"), "r_id")
        if claim_id not in claim_id_set:
            raise _contract_error("TraceMapper", f"Unknown claim_id `{claim_id}` inside claim_matches.")
        if r_id not in r_id_set:
            raise _contract_error("TraceMapper", f"Unknown r_id `{r_id}` inside claim_matches.")
        claim_matches.append(
            {
                "claim_id": claim_id,
                "r_id": r_id,
                "score": _require_float("TraceMapper", item.get("score"), "score"),
            }
        )

    best_solution = solutions[best_solution_id]
    required_ids = list(best_solution.get("required_r_ids") or [])
    optional_ids = list(best_solution.get("optional_r_ids") or [])
    total_ids = unique_list(required_ids + optional_ids)
    matched_required_r_ids = [r_id for r_id in matched_required_r_ids if r_id in required_ids]
    matched_r_ids = [r_id for r_id in matched_r_ids if r_id in total_ids]

    ordered_core_path = list(best_solution.get("ordered_core_path") or [])
    ordered_positions = [ordered_core_path.index(r_id) for r_id in matched_r_ids if r_id in ordered_core_path]
    topology_consistency_score = 1.0 if ordered_positions == sorted(ordered_positions) and ordered_positions else 0.0 if ordered_core_path else 0.0
    bindings = {item.get("r_id"): item for item in problem_bundle.get("evidence_bindings", []) if isinstance(item, dict)}
    evidence_grounding_score = (
        sum(1 for r_id in matched_r_ids if bindings.get(r_id, {}).get("support_strength") in {"HIGH", "MEDIUM"}) / len(matched_r_ids)
        if matched_r_ids else 0.0
    )

    answer_judgment = judge_answer_equivalence(router, problem_bundle.get("problem_record", {}), trace_record.get("pred_answer", ""), trace_record.get("pred_cot", ""))
    verify_result = verify_cot(
        router,
        trace_problem,
        {"method_id": trace_record.get("run_id", "pred"), "method_draft": trace_record.get("method_hint", "prediction-trace")},
        trace_record.get("pred_cot", ""),
    )

    total_hit_rate = len([r_id for r_id in total_ids if r_id in matched_r_ids]) / len(total_ids) if total_ids else 0.0
    required_hit_rate = len([r_id for r_id in required_ids if r_id in matched_required_r_ids]) / len(required_ids) if required_ids else 0.0
    novelty_candidate = bool(
        answer_judgment.get("is_equivalent")
        and verify_result.get("verify_pass")
        and total_hit_rate < novelty_total_threshold
        and required_hit_rate < novelty_required_threshold
    )
    return {
        "problem_id": problem_bundle.get("problem_record", {}).get("problem_id", ""),
        "model_name": trace_record.get("model_name", ""),
        "run_id": trace_record.get("run_id", ""),
        "answer_correct": bool(answer_judgment.get("is_equivalent")),
        "pred_cot_verified": bool(verify_result.get("verify_pass")),
        "best_solution_id": best_solution_id,
        "matched_r_ids": matched_r_ids,
        "matched_required_r_ids": matched_required_r_ids,
        "unmatched_claim_ids": unmatched_claim_ids,
        "claim_matches": claim_matches,
        "node_hit_rate_total": round(total_hit_rate, 4),
        "node_hit_rate_required": round(required_hit_rate, 4),
        "topology_consistency_score": round(topology_consistency_score, 4),
        "evidence_grounding_score": round(evidence_grounding_score, 4),
        "novelty_candidate": novelty_candidate,
        "pred_claims": pred_claims,
        "answer_judgment": answer_judgment,
        "verify_result": verify_result,
    }


def detect_novelty(router: ModelRouter, problem_bundle: Dict[str, Any], trace_record: Dict[str, Any], mapping_report: Dict[str, Any]) -> Dict[str, Any]:
    novelty_problem = problem_bundle.get("runtime_problem") or problem_bundle.get("problem_record", {})
    response = _call_router(
        router,
        NOVELTY_DETECTOR_SYSTEM_PROMPT,
        build_novelty_detector_user_prompt(problem_bundle, trace_record, mapping_report),
        _problem_image_paths(novelty_problem),
        agent_name="NoveltyDetector",
        require_images=bool(novelty_problem.get("requires_image")),
    )
    novelty_label = _normalize_novelty_label(response.get("novelty_label"), "NoveltyDetector")
    return {
        "novelty_label": novelty_label,
        "reason": _require_non_empty_text("NoveltyDetector", response.get("reason"), "reason"),
        "new_required_claim_ids": _require_string_list("NoveltyDetector", response.get("new_required_claim_ids", []), "new_required_claim_ids", allow_empty=True),
        "new_signature": _require_non_empty_text("NoveltyDetector", response.get("new_signature"), "new_signature"),
    }


def build_patch(problem_bundle: Dict[str, Any], trace_record: Dict[str, Any], mapping_report: Dict[str, Any], novelty_result: Dict[str, Any]) -> Dict[str, Any]:
    if novelty_result.get("novelty_label") != "new_solution_family":
        return {
            "problem_id": problem_bundle.get("problem_record", {}).get("problem_id", ""),
            "patch_applied": False,
            "reason": novelty_result.get("reason", "not_new_solution_family"),
        }
    pred_claims = mapping_report.get("pred_claims", [])
    unmatched_ids = set(mapping_report.get("unmatched_claim_ids", []))
    new_claims = [claim for claim in pred_claims if claim.get("claim_id") in unmatched_ids]
    if not new_claims:
        raise _data_error("PatchWriter", "NoveltyDetector marked trace as new solution, but there are no unmatched claims to turn into new nodes.")
    new_nodes: List[Dict[str, Any]] = []
    for claim in new_claims:
        canonical_claim = normalize_whitespace(claim.get("claim_text", ""))
        if not canonical_claim:
            raise _data_error("PatchWriter", "Encountered unmatched claim with empty claim_text.")
        new_nodes.append(
            NodeRecord(
                r_id=f"r_{stable_digest([problem_bundle.get('problem_record', {}).get('problem_id', ''), canonical_claim, trace_record.get('run_id', 'trace')])}",
                problem_id=problem_bundle.get("problem_record", {}).get("problem_id", ""),
                node_type=normalize_whitespace(claim.get("claim_type", "")) or "derivation",
                canonical_claim=canonical_claim,
                surface_forms=[canonical_claim],
                equivalence_group_id=f"eq_{stable_digest([canonical_claim], 12)}",
                support_level="MEDIUM",
                source_claim_ids=[claim.get("claim_id")],
            ).to_dict()
        )
    new_solution_id = f"s_{stable_digest([problem_bundle.get('problem_record', {}).get('problem_id', ''), trace_record.get('run_id', ''), 'novel'])}"
    new_r_ids = [str(node.get("r_id", "")) for node in new_nodes if str(node.get("r_id", ""))]
    new_solution = SolutionRecord(
        solution_id=new_solution_id,
        problem_id=problem_bundle.get("problem_record", {}).get("problem_id", ""),
        method_signature=novelty_result.get("new_signature", ""),
        required_r_ids=new_r_ids,
        optional_r_ids=[],
        ordered_core_path=new_r_ids,
        supported_answer=normalize_whitespace(trace_record.get("pred_answer", "")),
        member_method_ids=[str(trace_record.get("run_id", "trace"))],
    ).to_dict()
    new_memberships = [
        {
            "solution_id": new_solution_id,
            "r_id": node.get("r_id"),
            "membership_role": "required",
            "order_index": index,
        }
        for index, node in enumerate(new_nodes)
    ]
    new_bindings = [
        {
            "r_id": node.get("r_id"),
            "p_fact_ids": [],
            "t_fact_ids": [],
            "k_atom_ids": [],
            "predecessor_r_ids": [],
            "support_strength": "MEDIUM",
            "binding_rationale": "patch_from_verified_trace",
        }
        for node in new_nodes
    ]
    return {
        "problem_id": problem_bundle.get("problem_record", {}).get("problem_id", ""),
        "patch_applied": True,
        "novelty_label": novelty_result.get("novelty_label"),
        "reason": novelty_result.get("reason", ""),
        "trace_record": trace_record,
        "mapping_report": mapping_report,
        "new_r_nodes": new_nodes,
        "new_solution": new_solution,
        "new_solution_memberships": new_memberships,
        "new_evidence_bindings": new_bindings,
    }
