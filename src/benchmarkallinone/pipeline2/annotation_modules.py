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
    PTK_K_ATOMS_POLISH_SYSTEM_PROMPT,
    PTK_P_FACTS_POLISH_SYSTEM_PROMPT,
    PTK_T_FACTS_POLISH_SYSTEM_PROMPT,
    TEXT_CONDITION_SYSTEM_PROMPT,
    build_claim_extraction_user_prompt,
    build_claim_polish_user_prompt,
    build_claim_verify_user_prompt,
    build_knowledge_user_prompt,
    build_perception_user_prompt,
    build_ptk_foundation_critic_user_prompt,
    build_ptk_foundation_polish_user_prompt,
    build_ptk_k_atoms_polish_user_prompt,
    build_ptk_p_facts_polish_user_prompt,
    build_ptk_t_facts_polish_user_prompt,
    build_text_condition_user_prompt,
)
from .utils import normalize_whitespace, safe_float, to_plain_text


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


def _coerce_string_list(value: Any) -> List[str]:
    if not isinstance(value, list):
        return []
    output: List[str] = []
    for item in value:
        if isinstance(item, str):
            text = item.strip()
            if text:
                output.append(text)
    return output


def _topologically_reorder_claims(claims: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    dependency_map: Dict[str, List[str]] = {
        str(item.get("claim_id", "")): [str(dep) for dep in item.get("depends_on") or []]
        for item in claims
    }
    claim_map: Dict[str, Dict[str, Any]] = {str(item.get("claim_id", "")): dict(item) for item in claims}
    indegree: Dict[str, int] = {claim_id: 0 for claim_id in claim_map}
    followers: Dict[str, List[str]] = {claim_id: [] for claim_id in claim_map}
    for claim_id, deps in dependency_map.items():
        for dep in deps:
            if dep in indegree:
                indegree[claim_id] += 1
                followers[dep].append(claim_id)

    queue = sorted(
        [claim_id for claim_id, degree in indegree.items() if degree == 0],
        key=lambda claim_id: int(claim_map[claim_id].get("_original_index", 0)),
    )
    ordered_ids: List[str] = []
    while queue:
        current = queue.pop(0)
        ordered_ids.append(current)
        for follower in sorted(followers[current], key=lambda claim_id: int(claim_map[claim_id].get("_original_index", 0))):
            indegree[follower] -= 1
            if indegree[follower] == 0:
                queue.append(follower)
                queue.sort(key=lambda claim_id: int(claim_map[claim_id].get("_original_index", 0)))

    if len(ordered_ids) != len(claim_map):
        leftovers = [claim_id for claim_id in claim_map if claim_id not in set(ordered_ids)]
        leftovers.sort(key=lambda claim_id: int(claim_map[claim_id].get("_original_index", 0)))
        ordered_ids.extend(leftovers)

    return [claim_map[claim_id] for claim_id in ordered_ids]


def _repair_claim_sequence_locally(claims: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    prepared: List[Dict[str, Any]] = []
    seen_raw_ids: set[str] = set()
    for index, item in enumerate(claims):
        if not isinstance(item, dict):
            continue
        claim_text = normalize_whitespace(item.get("claim_text"))
        if not claim_text:
            continue
        raw_id = normalize_whitespace(item.get("claim_id")) or f"claim_{index + 1}"
        if raw_id in seen_raw_ids:
            raw_id = f"{raw_id}__{index + 1}"
        seen_raw_ids.add(raw_id)
        try:
            claim_type = _normalize_claim_type(item.get("claim_type"), "ClaimRepair")
        except Exception:
            claim_type = "derivation"
        prepared.append(
            {
                "claim_id": raw_id,
                "claim_text": claim_text,
                "claim_type": claim_type,
                "depends_on": _coerce_string_list(item.get("depends_on", [])),
                "evidence_hint": normalize_whitespace(item.get("evidence_hint")) or "Derived from CoT step and PTK context.",
                "_original_index": index,
            }
        )

    if not prepared:
        return []

    all_ids = {str(item.get("claim_id", "")) for item in prepared}
    for item in prepared:
        deps: List[str] = []
        for dependency in item.get("depends_on") or []:
            if dependency == item.get("claim_id"):
                continue
            if dependency not in all_ids:
                continue
            if dependency in deps:
                continue
            deps.append(dependency)
        item["depends_on"] = deps

    ordered = _topologically_reorder_claims(prepared)
    old_to_new: Dict[str, str] = {}
    for index, item in enumerate(ordered, start=1):
        old_to_new[str(item.get("claim_id", ""))] = f"c{index}"

    repaired: List[Dict[str, Any]] = []
    seen: set[str] = set()
    for item in ordered:
        new_id = old_to_new[str(item.get("claim_id", ""))]
        mapped_deps: List[str] = []
        for dependency in item.get("depends_on") or []:
            mapped = old_to_new.get(str(dependency))
            if not mapped or mapped == new_id or mapped not in seen:
                continue
            if mapped in mapped_deps:
                continue
            mapped_deps.append(mapped)
        repaired.append(
            {
                "claim_id": new_id,
                "claim_text": str(item.get("claim_text", "")),
                "claim_type": str(item.get("claim_type", "derivation")),
                "depends_on": mapped_deps,
                "evidence_hint": normalize_whitespace(item.get("evidence_hint")) or "Derived from CoT step and PTK context.",
            }
        )
        seen.add(new_id)
    return repaired


def _normalize_claims_response(
    response: Dict[str, Any],
    *,
    agent_name: str,
    problem_id: str,
    method_id: str,
) -> List[Dict[str, Any]]:
    items = _require_list(agent_name, response.get("claims"), "claims", allow_empty=False)
    raw_claims: List[Dict[str, Any]] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        raw_claims.append(
            {
                "claim_id": item.get("claim_id") or f"claim_{index + 1}",
                "claim_text": item.get("claim_text", ""),
                "claim_type": item.get("claim_type", "derivation"),
                "depends_on": item.get("depends_on", []),
                "evidence_hint": item.get("evidence_hint", ""),
            }
        )
    repaired = _repair_claim_sequence_locally(raw_claims)
    if not repaired:
        raise AgentContractError(f"[{agent_name}] No usable claims remained after local repair.")
    output: List[Dict[str, Any]] = []
    for item in repaired:
        output.append(
            ClaimRecord(
                claim_id=_require_non_empty_text(agent_name, item.get("claim_id"), "claim_id"),
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


def _normalize_ptk_section_targets(revision_instructions: str, current_foundation: Dict[str, Any]) -> List[str]:
    normalized = normalize_whitespace(revision_instructions).lower()
    targets: List[str] = []
    checks = [
        ("p_facts", ["p_facts", "p facts", "p-facts", "visual facts", "perception facts", "visual grounding", "visual anchor"]),
        ("t_facts", ["t_facts", "t facts", "t-facts", "text facts", "text conditions", "verbatim wording", "question wording"]),
        ("k_atoms", ["k_atoms", "k atoms", "k-atoms", "knowledge atoms", "knowledge rules", "knowledge"]),
    ]
    for section, keywords in checks:
        if any(keyword in normalized for keyword in keywords):
            targets.append(section)
    if targets:
        return targets

    fallback_targets: List[str] = []
    if current_foundation.get("p_facts"):
        fallback_targets.append("p_facts")
    if current_foundation.get("t_facts"):
        fallback_targets.append("t_facts")
    if current_foundation.get("k_atoms"):
        fallback_targets.append("k_atoms")
    return fallback_targets or ["p_facts", "t_facts", "k_atoms"]


def _polish_ptk_section(
    router: ModelRouter,
    problem: Dict[str, Any],
    current_foundation: Dict[str, Any],
    revision_instructions: str,
    section_name: str,
) -> Dict[str, Any]:
    _ensure_problem_minimum(problem, "PTKFoundationPolish")
    section_specs = {
        "p_facts": {
            "system_prompt": PTK_P_FACTS_POLISH_SYSTEM_PROMPT,
            "prompt_builder": build_ptk_p_facts_polish_user_prompt,
            "field_name": "p_facts",
            "normalizer": _normalize_p_facts,
            "summary_label": "p_facts",
        },
        "t_facts": {
            "system_prompt": PTK_T_FACTS_POLISH_SYSTEM_PROMPT,
            "prompt_builder": build_ptk_t_facts_polish_user_prompt,
            "field_name": "t_facts",
            "normalizer": _normalize_t_facts,
            "summary_label": "t_facts",
        },
        "k_atoms": {
            "system_prompt": PTK_K_ATOMS_POLISH_SYSTEM_PROMPT,
            "prompt_builder": build_ptk_k_atoms_polish_user_prompt,
            "field_name": "k_atoms",
            "normalizer": _normalize_k_atoms,
            "summary_label": "k_atoms",
        },
    }
    spec = section_specs.get(section_name)
    if spec is None:
        raise PipelineDataContractError(f"[PTKFoundationPolish] Unsupported section patch target `{section_name}`.")

    response = _call_router(
        router,
        spec["system_prompt"],
        _augment_prompt_with_ready_context(
            problem,
            spec["prompt_builder"](
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
    normalized_items = spec["normalizer"](response, "PTKFoundationPolish")
    revision_summary = _require_non_empty_text("PTKFoundationPolish", response.get("revision_summary"), "revision_summary")
    return {
        spec["field_name"]: normalized_items,
        "revision_summary": revision_summary,
        "patched_section": spec["summary_label"],
    }


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
    section_targets = _normalize_ptk_section_targets(revision_instructions, current_foundation)
    patched_foundation = {
        **current_foundation,
        "p_facts": list(current_foundation.get("p_facts", [])),
        "t_facts": list(current_foundation.get("t_facts", [])),
        "k_atoms": list(current_foundation.get("k_atoms", [])),
    }
    section_summaries: List[Dict[str, Any]] = []

    for section_name in section_targets:
        patch_result = _polish_ptk_section(
            router,
            problem,
            patched_foundation,
            revision_instructions,
            section_name,
        )
        patched_foundation[section_name] = patch_result[section_name]
        section_summaries.append(
            {
                "section": patch_result["patched_section"],
                "revision_summary": patch_result["revision_summary"],
            }
        )

    return {
        "p_facts": _normalize_p_facts({"p_facts": patched_foundation.get("p_facts", [])}, "PTKFoundationPolish"),
        "t_facts": _normalize_t_facts({"t_facts": patched_foundation.get("t_facts", [])}, "PTKFoundationPolish"),
        "k_atoms": _normalize_k_atoms({"k_atoms": patched_foundation.get("k_atoms", [])}, "PTKFoundationPolish"),
        "revision_summary": " | ".join(item["revision_summary"] for item in section_summaries if item.get("revision_summary"))
        or _require_non_empty_text("PTKFoundationPolish", normalize_whitespace(revision_instructions), "revision_summary"),
        "patched_sections": [item["section"] for item in section_summaries],
        "section_summaries": section_summaries,
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
        round_record["patched_sections"] = polished.get("patched_sections", [])
        round_record["section_summaries"] = polished.get("section_summaries", [])
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
        "status": "passed" if passed else "soft_failed",
    }
    return {
        "problem_id": problem.get("problem_id", ""),
        "method_id": method.get("method_id", ""),
        "claims": claims,
        "audit": audit,
        "claim_gate_passed": passed,
        "claim_gate_status": "passed" if passed else "soft_failed",
    }
