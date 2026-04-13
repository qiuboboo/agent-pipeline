from __future__ import annotations

from typing import Any, Dict, List, Sequence

from .agents import (
    AgentContractError,
    PipelineDataContractError,
    _augment_prompt_with_ready_context,
    _call_router,
    _ensure_problem_minimum,
    _normalize_claim_type,
    _require_bool,
    _require_float,
    _require_list,
    _require_non_empty_text,
    _require_string_list,
)
from .clients import ModelRouter
from .models import ClaimRecord
from .prompts import (
    CLAIM_EXTRACTION_SYSTEM_PROMPT,
    CLAIM_POLISH_SYSTEM_PROMPT,
    CLAIM_VERIFY_SYSTEM_PROMPT,
    KNOWLEDGE_LIBRARIAN_SYSTEM_PROMPT,
    PERCEPTION_EXTRACTION_SYSTEM_PROMPT,
    PTK_FOUNDATION_CRITIC_SYSTEM_PROMPT,
    PTK_FOUNDATION_POLISH_SYSTEM_PROMPT,
    TEXT_CONDITION_SYSTEM_PROMPT,
    build_claim_extraction_user_prompt,
    build_claim_polish_user_prompt,
    build_claim_verify_user_prompt,
    build_knowledge_user_prompt,
    build_perception_user_prompt,
    build_ptk_foundation_critic_user_prompt,
    build_ptk_foundation_polish_user_prompt,
    build_text_condition_user_prompt,
)
from .utils import safe_float, to_plain_text


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


def _normalize_p_facts(response: Dict[str, Any], agent_name: str) -> List[Dict[str, Any]]:
    items = _require_list(agent_name, response.get("p_facts"), "p_facts", allow_empty=False)
    output: List[Dict[str, Any]] = []
    seen_ids: set[str] = set()
    for item in items:
        if not isinstance(item, dict):
            raise AgentContractError(f"[{agent_name}] Each `p_fact` must be an object.")
        p_id = _require_non_empty_text(agent_name, item.get("p_id"), "p_id")
        if p_id in seen_ids:
            raise AgentContractError(f"[{agent_name}] Duplicate `p_id` `{p_id}`.")
        seen_ids.add(p_id)
        output.append(
            {
                "p_id": p_id,
                "fact_text": _require_non_empty_text(agent_name, item.get("fact_text"), "fact_text"),
                "confidence": _require_probability(agent_name, item.get("confidence"), "confidence"),
                "visual_anchor": _require_non_empty_text(agent_name, item.get("visual_anchor"), "visual_anchor"),
            }
        )
    return output


def _normalize_t_facts(response: Dict[str, Any], agent_name: str) -> List[Dict[str, Any]]:
    items = _require_list(agent_name, response.get("t_facts"), "t_facts", allow_empty=False)
    output: List[Dict[str, Any]] = []
    seen_ids: set[str] = set()
    for item in items:
        if not isinstance(item, dict):
            raise AgentContractError(f"[{agent_name}] Each `t_fact` must be an object.")
        t_id = _require_non_empty_text(agent_name, item.get("t_id"), "t_id")
        if t_id in seen_ids:
            raise AgentContractError(f"[{agent_name}] Duplicate `t_id` `{t_id}`.")
        seen_ids.add(t_id)
        output.append(
            {
                "t_id": t_id,
                "fact_text": _require_non_empty_text(agent_name, item.get("fact_text"), "fact_text"),
                "fact_role": _require_non_empty_text(agent_name, item.get("fact_role"), "fact_role"),
            }
        )
    return output


def _normalize_k_atoms(response: Dict[str, Any], agent_name: str) -> List[Dict[str, Any]]:
    items = _require_list(agent_name, response.get("k_atoms"), "k_atoms", allow_empty=False)
    output: List[Dict[str, Any]] = []
    seen_ids: set[str] = set()
    for item in items:
        if not isinstance(item, dict):
            raise AgentContractError(f"[{agent_name}] Each `k_atom` must be an object.")
        k_id = _require_non_empty_text(agent_name, item.get("k_id"), "k_id")
        if k_id in seen_ids:
            raise AgentContractError(f"[{agent_name}] Duplicate `k_id` `{k_id}`.")
        seen_ids.add(k_id)
        output.append(
            {
                "k_id": k_id,
                "knowledge_text": _require_non_empty_text(agent_name, item.get("knowledge_text"), "knowledge_text"),
                "knowledge_type": _require_non_empty_text(agent_name, item.get("knowledge_type"), "knowledge_type"),
                "applicability_note": _require_non_empty_text(agent_name, item.get("applicability_note"), "applicability_note"),
            }
        )
    return output


def _validate_claim_sequence(agent_name: str, claims: Sequence[Dict[str, Any]]) -> None:
    all_ids = {str(item.get("claim_id", "")) for item in claims}
    seen: set[str] = set()
    for item in claims:
        claim_id = str(item.get("claim_id", ""))
        for dependency in item.get("depends_on") or []:
            if dependency == claim_id:
                raise AgentContractError(f"[{agent_name}] Claim `{claim_id}` cannot depend on itself.")
            if dependency not in all_ids:
                raise AgentContractError(f"[{agent_name}] Claim `{claim_id}` depends on unknown claim `{dependency}`.")
            if dependency not in seen:
                raise AgentContractError(
                    f"[{agent_name}] Claim `{claim_id}` depends on `{dependency}` before it appears in the ordered claim sequence."
                )
        seen.add(claim_id)


def _normalize_claims_response(
    response: Dict[str, Any],
    *,
    agent_name: str,
    problem_id: str,
    method_id: str,
) -> List[Dict[str, Any]]:
    items = _require_list(agent_name, response.get("claims"), "claims", allow_empty=False)
    output: List[Dict[str, Any]] = []
    seen_ids: set[str] = set()
    for item in items:
        if not isinstance(item, dict):
            raise AgentContractError(f"[{agent_name}] Each claim must be an object.")
        claim_id = _require_non_empty_text(agent_name, item.get("claim_id"), "claim_id")
        if claim_id in seen_ids:
            raise AgentContractError(f"[{agent_name}] Duplicate claim_id `{claim_id}`.")
        seen_ids.add(claim_id)
        output.append(
            ClaimRecord(
                claim_id=claim_id,
                problem_id=problem_id,
                method_id=method_id,
                claim_text=_require_non_empty_text(agent_name, item.get("claim_text"), "claim_text"),
                claim_type=_normalize_claim_type(item.get("claim_type"), agent_name),
                depends_on=_require_string_list(agent_name, item.get("depends_on", []), "depends_on", allow_empty=True),
                evidence_hint=_require_non_empty_text(agent_name, item.get("evidence_hint"), "evidence_hint"),
            ).to_dict()
        )
    _validate_claim_sequence(agent_name, output)
    return output


def _normalize_ptk_critique(response: Dict[str, Any]) -> Dict[str, Any]:
    passed = _require_bool("PTKFoundationCritic", response.get("pass"), "pass")
    revision_instructions = str(response.get("revision_instructions", "") or "").strip()
    if not revision_instructions and passed:
        revision_instructions = "No changes needed."
    return {
        "pass": passed,
        "critical_issues": _require_string_list("PTKFoundationCritic", response.get("critical_issues", []), "critical_issues", allow_empty=True),
        "revision_instructions": _require_non_empty_text(
            "PTKFoundationCritic",
            revision_instructions,
            "revision_instructions",
        ),
        "grounding_score": _require_probability("PTKFoundationCritic", response.get("grounding_score"), "grounding_score"),
        "coverage_score": _require_probability("PTKFoundationCritic", response.get("coverage_score"), "coverage_score"),
    }


def _normalize_claim_critique(response: Dict[str, Any]) -> Dict[str, Any]:
    passed = _require_bool("ClaimVerify", response.get("pass"), "pass")
    revision_instructions = str(response.get("revision_instructions", "") or "").strip()
    if not revision_instructions and passed:
        revision_instructions = "No changes needed."
    return {
        "pass": passed,
        "critical_issues": _require_string_list("ClaimVerify", response.get("critical_issues", []), "critical_issues", allow_empty=True),
        "revision_instructions": _require_non_empty_text("ClaimVerify", revision_instructions, "revision_instructions"),
        "atomicity_score": _require_probability("ClaimVerify", response.get("atomicity_score"), "atomicity_score"),
        "dependency_score": _require_probability("ClaimVerify", response.get("dependency_score"), "dependency_score"),
        "grounding_score": _require_probability("ClaimVerify", response.get("grounding_score"), "grounding_score"),
    }


def _extract_ptk_once(router: ModelRouter, problem: Dict[str, Any]) -> Dict[str, Any]:
    _ensure_problem_minimum(problem, "PTKFoundationBuilder")
    image_paths = _problem_image_paths(problem)
    require_images = bool(problem.get("requires_image"))

    p_response = _call_router(
        router,
        PERCEPTION_EXTRACTION_SYSTEM_PROMPT,
        _augment_prompt_with_ready_context(problem, build_perception_user_prompt(problem), "PerceptionExtraction"),
        image_paths,
        agent_name="PerceptionExtraction",
        require_images=require_images,
    )
    p_facts = _normalize_p_facts(p_response, "PerceptionExtraction")

    t_response = _call_router(
        router,
        TEXT_CONDITION_SYSTEM_PROMPT,
        _augment_prompt_with_ready_context(problem, build_text_condition_user_prompt(problem), "TextCondition"),
        image_paths,
        agent_name="TextCondition",
        require_images=require_images,
    )
    t_facts = _normalize_t_facts(t_response, "TextCondition")

    k_response = _call_router(
        router,
        KNOWLEDGE_LIBRARIAN_SYSTEM_PROMPT,
        _augment_prompt_with_ready_context(problem, build_knowledge_user_prompt(problem, p_facts, t_facts), "KnowledgeLibrarian"),
        image_paths,
        agent_name="KnowledgeLibrarian",
        require_images=require_images,
    )
    k_atoms = _normalize_k_atoms(k_response, "KnowledgeLibrarian")

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


def _build_claim_extraction_prompt(
    problem: Dict[str, Any],
    method: Dict[str, Any],
    cot_text: str,
    p_facts: Sequence[Dict[str, Any]],
    t_facts: Sequence[Dict[str, Any]],
    k_atoms: Sequence[Dict[str, Any]],
) -> str:
    base_prompt = build_claim_extraction_user_prompt(problem, method, cot_text)
    return (
        base_prompt
        + "\n\nGrounded PTK Foundation:\n"
        + "P Facts:\n"
        + to_plain_text(list(p_facts))
        + "\n\nT Facts:\n"
        + to_plain_text(list(t_facts))
        + "\n\nK Atoms:\n"
        + to_plain_text(list(k_atoms))
    )


def _extract_claims_once(
    router: ModelRouter,
    problem: Dict[str, Any],
    method: Dict[str, Any],
    cot_text: str,
    p_facts: Sequence[Dict[str, Any]],
    t_facts: Sequence[Dict[str, Any]],
    k_atoms: Sequence[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    _ensure_problem_minimum(problem, "ClaimExtraction")
    image_paths = _problem_image_paths(problem)
    response = _call_router(
        router,
        CLAIM_EXTRACTION_SYSTEM_PROMPT,
        _augment_prompt_with_ready_context(
            problem,
            _build_claim_extraction_prompt(problem, method, cot_text, p_facts, t_facts, k_atoms),
            "ClaimExtraction",
        ),
        image_paths,
        agent_name="ClaimExtraction",
        require_images=bool(problem.get("requires_image")),
    )
    return _normalize_claims_response(
        response,
        agent_name="ClaimExtraction",
        problem_id=str(problem.get("problem_id", "")),
        method_id=str(method.get("method_id", "")),
    )


def critique_ptk_foundation(
    router: ModelRouter,
    problem: Dict[str, Any],
    p_facts: Sequence[Dict[str, Any]],
    t_facts: Sequence[Dict[str, Any]],
    k_atoms: Sequence[Dict[str, Any]],
) -> Dict[str, Any]:
    _ensure_problem_minimum(problem, "PTKFoundationCritic")
    response = _call_router(
        router,
        PTK_FOUNDATION_CRITIC_SYSTEM_PROMPT,
        _augment_prompt_with_ready_context(
            problem,
            build_ptk_foundation_critic_user_prompt(problem, p_facts, t_facts, k_atoms),
            "PTKFoundationCritic",
        ),
        _problem_image_paths(problem),
        agent_name="PTKFoundationCritic",
        require_images=bool(problem.get("requires_image")),
    )
    return _normalize_ptk_critique(response)


def polish_ptk_foundation(
    router: ModelRouter,
    problem: Dict[str, Any],
    current_foundation: Dict[str, Any],
    revision_instructions: str,
) -> Dict[str, Any]:
    _ensure_problem_minimum(problem, "PTKFoundationPolish")
    response = _call_router(
        router,
        PTK_FOUNDATION_POLISH_SYSTEM_PROMPT,
        _augment_prompt_with_ready_context(
            problem,
            build_ptk_foundation_polish_user_prompt(
                problem,
                current_foundation.get("p_facts", []),
                current_foundation.get("t_facts", []),
                current_foundation.get("k_atoms", []),
                revision_instructions,
            ),
            "PTKFoundationPolish",
        ),
        _problem_image_paths(problem),
        agent_name="PTKFoundationPolish",
        require_images=bool(problem.get("requires_image")),
    )
    return {
        "p_facts": _normalize_p_facts(response, "PTKFoundationPolish"),
        "t_facts": _normalize_t_facts(response, "PTKFoundationPolish"),
        "k_atoms": _normalize_k_atoms(response, "PTKFoundationPolish"),
        "revision_summary": _require_non_empty_text("PTKFoundationPolish", response.get("revision_summary"), "revision_summary"),
    }


def build_ptk_foundation(router: ModelRouter, problem: Dict[str, Any], max_repair_rounds: int = 2) -> Dict[str, Any]:
    foundation = _extract_ptk_once(router, problem)
    audit_rounds: List[Dict[str, Any]] = []
    passed = False

    for round_index in range(max_repair_rounds + 1):
        critique = critique_ptk_foundation(
            router,
            problem,
            foundation.get("p_facts", []),
            foundation.get("t_facts", []),
            foundation.get("k_atoms", []),
        )
        round_record: Dict[str, Any] = {"round_index": round_index, **critique}
        if critique["pass"]:
            audit_rounds.append(round_record)
            passed = True
            break
        if round_index >= max_repair_rounds:
            audit_rounds.append(round_record)
            break
        polished = polish_ptk_foundation(router, problem, foundation, critique["revision_instructions"])
        foundation = {
            **foundation,
            "p_facts": polished["p_facts"],
            "t_facts": polished["t_facts"],
            "k_atoms": polished["k_atoms"],
        }
        round_record["polish_summary"] = polished["revision_summary"]
        audit_rounds.append(round_record)

    audit = {
        "component": "PTKFoundationBuilder",
        "passed": passed,
        "max_repair_rounds": max_repair_rounds,
        "rounds": audit_rounds,
    }
    if not passed:
        raise PipelineDataContractError(
            f"[PTKFoundationGate] Problem `{problem.get('problem_id', 'unknown_problem')}` failed PTK foundation validation after {max_repair_rounds + 1} rounds."
        )
    return {**foundation, "audit": audit}


def critique_claim_sequence(
    router: ModelRouter,
    problem: Dict[str, Any],
    method: Dict[str, Any],
    cot_text: str,
    claims: Sequence[Dict[str, Any]],
    p_facts: Sequence[Dict[str, Any]],
    t_facts: Sequence[Dict[str, Any]],
    k_atoms: Sequence[Dict[str, Any]],
) -> Dict[str, Any]:
    _ensure_problem_minimum(problem, "ClaimVerify")
    response = _call_router(
        router,
        CLAIM_VERIFY_SYSTEM_PROMPT,
        _augment_prompt_with_ready_context(
            problem,
            build_claim_verify_user_prompt(problem, method, cot_text, claims, p_facts, t_facts, k_atoms),
            "ClaimVerify",
        ),
        _problem_image_paths(problem),
        agent_name="ClaimVerify",
        require_images=bool(problem.get("requires_image")),
    )
    return _normalize_claim_critique(response)


def polish_claim_sequence(
    router: ModelRouter,
    problem: Dict[str, Any],
    method: Dict[str, Any],
    cot_text: str,
    claims: Sequence[Dict[str, Any]],
    revision_instructions: str,
    p_facts: Sequence[Dict[str, Any]],
    t_facts: Sequence[Dict[str, Any]],
    k_atoms: Sequence[Dict[str, Any]],
) -> Dict[str, Any]:
    _ensure_problem_minimum(problem, "ClaimPolish")
    response = _call_router(
        router,
        CLAIM_POLISH_SYSTEM_PROMPT,
        _augment_prompt_with_ready_context(
            problem,
            build_claim_polish_user_prompt(problem, method, cot_text, claims, revision_instructions, p_facts, t_facts, k_atoms),
            "ClaimPolish",
        ),
        _problem_image_paths(problem),
        agent_name="ClaimPolish",
        require_images=bool(problem.get("requires_image")),
    )
    return {
        "claims": _normalize_claims_response(
            response,
            agent_name="ClaimPolish",
            problem_id=str(problem.get("problem_id", "")),
            method_id=str(method.get("method_id", "")),
        ),
        "revision_summary": _require_non_empty_text("ClaimPolish", response.get("revision_summary"), "revision_summary"),
    }


def extract_claims_bundle(
    router: ModelRouter,
    problem: Dict[str, Any],
    method: Dict[str, Any],
    cot_text: str,
    p_facts: Sequence[Dict[str, Any]],
    t_facts: Sequence[Dict[str, Any]],
    k_atoms: Sequence[Dict[str, Any]],
    max_repair_rounds: int = 2,
) -> Dict[str, Any]:
    claims = _extract_claims_once(router, problem, method, cot_text, p_facts, t_facts, k_atoms)
    audit_rounds: List[Dict[str, Any]] = []
    passed = False

    for round_index in range(max_repair_rounds + 1):
        critique = critique_claim_sequence(router, problem, method, cot_text, claims, p_facts, t_facts, k_atoms)
        round_record: Dict[str, Any] = {"round_index": round_index, **critique}
        if critique["pass"]:
            audit_rounds.append(round_record)
            passed = True
            break
        if round_index >= max_repair_rounds:
            audit_rounds.append(round_record)
            break
        polished = polish_claim_sequence(
            router,
            problem,
            method,
            cot_text,
            claims,
            critique["revision_instructions"],
            p_facts,
            t_facts,
            k_atoms,
        )
        claims = polished["claims"]
        round_record["polish_summary"] = polished["revision_summary"]
        audit_rounds.append(round_record)

    audit = {
        "component": "ClaimExtractionAgent",
        "problem_id": problem.get("problem_id", ""),
        "method_id": method.get("method_id", ""),
        "passed": passed,
        "max_repair_rounds": max_repair_rounds,
        "rounds": audit_rounds,
    }
    if not passed:
        raise PipelineDataContractError(
            f"[ClaimExtractionGate] Problem `{problem.get('problem_id', 'unknown_problem')}` method `{method.get('method_id', 'unknown_method')}` failed claim validation after {max_repair_rounds + 1} rounds."
        )
    return {
        "problem_id": problem.get("problem_id", ""),
        "method_id": method.get("method_id", ""),
        "claims": claims,
        "audit": audit,
    }
