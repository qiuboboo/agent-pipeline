from __future__ import annotations

import re
from copy import deepcopy
from typing import Any, Callable, Dict, List, Optional, Sequence

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
    CLAIM_VERIFY_GLOBAL_SYSTEM_PROMPT,
    CLAIM_VERIFY_GROUNDING_SYSTEM_PROMPT,
    CLAIM_VERIFY_STRUCTURE_SYSTEM_PROMPT,
    CLAIM_VERIFY_SYSTEM_PROMPT,
    KNOWLEDGE_LIBRARIAN_SYSTEM_PROMPT,
    PERCEPTION_EXTRACTION_SYSTEM_PROMPT,
    PTK_K_ATOMS_POLISH_SYSTEM_PROMPT,
    PTK_P_FACTS_POLISH_SYSTEM_PROMPT,
    PTK_STRUCTURE_CRITIC_SYSTEM_PROMPT,
    PTK_T_FACTS_POLISH_SYSTEM_PROMPT,
    PTK_VISUAL_GROUNDING_CRITIC_SYSTEM_PROMPT,
    TEXT_CONDITION_SYSTEM_PROMPT,
    build_claim_extraction_user_prompt,
    build_claim_global_verify_user_prompt,
    build_claim_grounding_verify_user_prompt,
    build_claim_polish_user_prompt,
    build_claim_structure_verify_user_prompt,
    build_claim_set_validation_user_prompt,
    build_claim_verify_user_prompt,
    build_knowledge_user_prompt,
    build_perception_user_prompt,
    build_ptk_k_atoms_polish_user_prompt,
    build_ptk_p_facts_polish_user_prompt,
    build_ptk_structure_critic_user_prompt,
    build_ptk_t_facts_polish_user_prompt,
    build_ptk_visual_grounding_critic_user_prompt,
    build_text_condition_user_prompt,
)
from .utils import canonicalize_free_text, lexical_overlap_score, normalize_whitespace, safe_float, to_plain_text


def _problem_image_paths(problem: Dict[str, Any]) -> List[str]:
    output: List[str] = []
    for item in problem.get("images") or []:
        if isinstance(item, str):
            value = item.strip()
            if value:
                output.append(value)
    return output


_P_ISSUE_PREFIX = "p_facts_"

_T_ISSUE_PREFIX = "t_facts_"

_K_ISSUE_PREFIX = "k_atoms_"

def _ptk_issue_matches_prefix(issue: str, prefix: str) -> bool:
    return normalize_whitespace(issue).startswith(prefix)

def _merge_ptk_critiques(structural: Dict[str, Any], visual: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    merged_issues = list(structural.get("critical_issues", []))
    merged_categories = list(structural.get("issue_categories", []))
    merged_instructions: List[str] = []
    structural_instructions = normalize_whitespace(structural.get("revision_instructions", ""))
    if structural_instructions and structural_instructions != "No changes needed.":
        merged_instructions.append(structural_instructions)
    coverage_score = safe_float(structural.get("coverage_score"), 0.0)
    grounding_scores = [safe_float(structural.get("grounding_score"), 0.0)]

    if isinstance(visual, dict):
        merged_issues.extend(item for item in visual.get("critical_issues", []) if item not in merged_issues)
        merged_categories.extend(item for item in visual.get("issue_categories", []) if item not in merged_categories)
        visual_instructions = normalize_whitespace(visual.get("revision_instructions", ""))
        if visual_instructions and visual_instructions != "No changes needed.":
            merged_instructions.append(visual_instructions)
        grounding_scores.append(safe_float(visual.get("grounding_score"), 0.0))

    merged_pass = bool(structural.get("pass")) and (True if visual is None else bool(visual.get("pass")))
    return {
        "pass": merged_pass,
        "critical_issues": merged_issues,
        "issue_categories": merged_categories,
        "revision_instructions": "No changes needed." if merged_pass else "\n".join(merged_instructions) or "Revise the PTK foundation according to the listed critical issues.",
        "grounding_score": min(grounding_scores) if grounding_scores else 0.0,
        "coverage_score": coverage_score,
        "subcritiques": {
            "structure": deepcopy(structural),
            "visual": deepcopy(visual) if isinstance(visual, dict) else None,
        },
    }

def _infer_ptk_issue_categories(critique: Dict[str, Any]) -> List[str]:
    explicit = [item for item in critique.get("issue_categories", []) if isinstance(item, str) and item.strip()]
    if explicit:
        return explicit
    text_blob = " ".join(
        [
            *[normalize_whitespace(item) for item in critique.get("critical_issues", []) if isinstance(item, str)],
            normalize_whitespace(critique.get("revision_instructions", "")),
        ]
    ).lower()
    inferred: List[str] = []
    if any(marker in text_blob for marker in ("p_fact", "visual", "image", "objective", "overclaim")):
        inferred.append("p_facts_visual_grounding")
    if any(marker in text_blob for marker in ("t_fact", "text given", "explicit given", "goal", "constraint", "subquestion", "text-explicit", "text grounded")):
        inferred.append("t_facts_missing_explicit_givens")
    if any(marker in text_blob for marker in ("k_atom", "knowledge", "solution-specific", "reusable rule", "duplicate rule")):
        inferred.append("k_atoms_solution_specific")
    return inferred

def _coerce_object_list(
    response: Dict[str, Any],
    *,
    agent_name: str,
    field_name: str,
    alt_field_names: Sequence[str],
    marker_fields: Sequence[str],
) -> List[Any]:
    candidate_values = [response.get(field_name)] + [response.get(name) for name in alt_field_names]
    for value in candidate_values:
        if isinstance(value, list):
            return value
        if isinstance(value, dict):
            for nested_name in (field_name, *alt_field_names, "items", "facts", "records", "data"):
                nested_value = value.get(nested_name)
                if isinstance(nested_value, list):
                    return nested_value
            if any(key in value for key in marker_fields):
                return [value]
    raise AgentContractError(f"[{agent_name}] Field `{field_name}` must be a list.")

def _require_probability(agent_name: str, value: Any, field_name: str) -> float:
    score = _require_float(agent_name, value, field_name)
    if score < 0.0 or score > 1.0:
        raise AgentContractError(f"[{agent_name}] Field `{field_name}` must be within [0, 1].")
    return score

def _normalize_p_facts(response: Dict[str, Any], agent_name: str) -> List[Dict[str, Any]]:
    items = _coerce_object_list(
        response,
        agent_name=agent_name,
        field_name="p_facts",
        alt_field_names=("visual_facts", "facts"),
        marker_fields=("p_id", "fact_text", "visual_anchor"),
    )
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
    items = _coerce_object_list(
        response,
        agent_name=agent_name,
        field_name="t_facts",
        alt_field_names=("text_facts", "conditions", "facts"),
        marker_fields=("t_id", "fact_text", "fact_role"),
    )
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
    items = _coerce_object_list(
        response,
        agent_name=agent_name,
        field_name="k_atoms",
        alt_field_names=("knowledge_atoms", "knowledge_facts", "facts"),
        marker_fields=("k_id", "knowledge_text", "knowledge_type"),
    )
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

_ALLOWED_TEXT_FACT_ROLES = {"given", "goal", "constraint", "subquestion"}

_GOAL_PATTERNS = [
    re.compile(r"\bfind\b", re.IGNORECASE),
    re.compile(r"\bdetermine\b", re.IGNORECASE),
    re.compile(r"\bcompute\b", re.IGNORECASE),
    re.compile(r"\bsolve\b", re.IGNORECASE),
    re.compile(r"\bwhat\s+is\b", re.IGNORECASE),
    re.compile(r"求"),
    re.compile(r"判断"),
    re.compile(r"计算"),
    re.compile(r"写出"),
]

_GIVEN_SPLIT_PATTERN = re.compile(r",\s*|\s+and\s+", re.IGNORECASE)

def _normalize_text_fact_text(text: Any) -> str:
    value = normalize_whitespace(text)
    value = re.sub(r"^(?:and)\s+", "", value, flags=re.IGNORECASE)
    value = re.sub(r"[。．\.,，；;:：!?！？]+$", "", value)
    return value.strip()

def _derive_text_facts_from_question(question_text: str) -> List[Dict[str, str]]:
    value = normalize_whitespace(question_text)
    if not value:
        return []

    sentence_parts = [part.strip() for part in re.split(r"(?<=[.!?])\s+", value) if part.strip()]

    goal_start: Optional[int] = None
    for pattern in _GOAL_PATTERNS:
        match = pattern.search(value)
        if match is None:
            continue
        if goal_start is None or match.start() < goal_start:
            goal_start = match.start()

    if goal_start is None and sentence_parts:
        facts: List[Dict[str, str]] = []
        for index, sentence in enumerate(sentence_parts):
            cleaned = _normalize_text_fact_text(sentence)
            if not cleaned:
                continue
            lowered = cleaned.casefold()
            is_goal_like = (
                "____" in cleaned
                or "___" in cleaned
                or "?" in sentence
                or " is ______" in lowered
                or " is _____" in lowered
                or re.search(r"(求|判断|计算|写出)", cleaned) is not None
            )
            if is_goal_like:
                facts.append({"fact_text": cleaned, "fact_role": "goal"})
                continue
            if re.search(r"\b(all devices are considered|assume|assuming|ideal|round to)\b", cleaned, re.IGNORECASE):
                facts.append({"fact_text": cleaned, "fact_role": "constraint"})
                continue
            facts.append({"fact_text": cleaned, "fact_role": "given"})
        return facts

    if goal_start is None:
        return []

    prefix = _normalize_text_fact_text(value[:goal_start])
    if prefix and re.search(r"(观察图像|观察下图|读图|读下图|根据图|结合图像|shown in the figure)", prefix, re.IGNORECASE):
        if not re.search(r"[0-9A-Za-z=<>°%μΩ$]", prefix):
            prefix = ""
    suffix = normalize_whitespace(value[goal_start:])

    facts: List[Dict[str, str]] = []
    if prefix:
        raw_parts = [part for part in (_normalize_text_fact_text(part) for part in _GIVEN_SPLIT_PATTERN.split(prefix)) if part]
        merged_parts: List[str] = []
        carry: Optional[str] = None
        for part in raw_parts:
            if carry is not None:
                part = _normalize_text_fact_text(f"{carry}, {part}")
                carry = None
            if re.fullmatch(r"in\s+[A-Za-z0-9]+", part, re.IGNORECASE):
                carry = part
                continue
            merged_parts.append(part)
        if carry is not None:
            merged_parts.append(carry)
        for part in merged_parts:
            cleaned_part = _normalize_text_fact_text(part)
            if cleaned_part:
                facts.append({"fact_text": cleaned_part, "fact_role": "given"})

    if suffix:
        suffix_parts = [part.strip() for part in re.split(r"(?<=[.!?])\s+", suffix) if part.strip()]
        if suffix_parts:
            facts.append({"fact_text": _normalize_text_fact_text(suffix_parts[0]), "fact_role": "goal"})
            for extra in suffix_parts[1:]:
                cleaned_extra = _normalize_text_fact_text(extra)
                if cleaned_extra:
                    facts.append({"fact_text": cleaned_extra, "fact_role": "constraint"})
        else:
            facts.append({"fact_text": _normalize_text_fact_text(suffix), "fact_role": "goal"})

    return facts

def _sanitize_t_facts(problem: Dict[str, Any], t_facts: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    question_text = normalize_whitespace(problem.get("question_text", ""))
    sanitized_existing: List[Dict[str, str]] = []
    for item in t_facts:
        if not isinstance(item, dict):
            continue
        fact_text = _normalize_text_fact_text(item.get("fact_text", ""))
        fact_role = normalize_whitespace(item.get("fact_role", "")).lower()
        if fact_role == "given" and (
            "____" in fact_text
            or "___" in fact_text
            or "()" in fact_text
            or re.search(r"\b(find|determine|compute|solve|what\s+is)\b", fact_text, re.IGNORECASE)
            or re.search(r"(求|判断|计算|写出)", fact_text)
        ):
            fact_role = "goal"
        if not fact_text or fact_role not in _ALLOWED_TEXT_FACT_ROLES:
            continue
        keep = False
        if fact_role in {"goal", "subquestion", "constraint"}:
            keep = True
        else:
            overlap = lexical_overlap_score(question_text, fact_text)
            question_norm = canonicalize_free_text(question_text)
            fact_norm = canonicalize_free_text(fact_text)
            keep = overlap >= 0.2 or (bool(question_norm) and fact_norm in question_norm)
        if keep:
            sanitized_existing.append({"fact_text": fact_text, "fact_role": fact_role})

    derived_facts = _derive_text_facts_from_question(question_text)
    merged: List[Dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    source_items = (
        [item for item in derived_facts if item.get("fact_role") != "goal"]
        + [item for item in sanitized_existing if item.get("fact_role") != "goal"]
        + [item for item in derived_facts if item.get("fact_role") == "goal"]
        + [item for item in sanitized_existing if item.get("fact_role") == "goal"]
    )
    for item in source_items:
        fact_text = _normalize_text_fact_text(item.get("fact_text", ""))
        fact_role = normalize_whitespace(item.get("fact_role", "")).lower()
        if not fact_text or fact_role not in _ALLOWED_TEXT_FACT_ROLES:
            continue
        duplicate_found = False
        normalized_fact_text = canonicalize_free_text(fact_text).replace(" ", "")
        for existing in merged:
            if existing.get("fact_role") != fact_role:
                continue
            existing_normalized = canonicalize_free_text(existing.get("fact_text", "")).replace(" ", "")
            if existing_normalized == normalized_fact_text or lexical_overlap_score(existing.get("fact_text", ""), fact_text) >= 0.85:
                duplicate_found = True
                break
        if duplicate_found:
            continue
        marker = (canonicalize_free_text(fact_text), fact_role)
        if marker in seen:
            continue
        seen.add(marker)
        merged.append(
            {
                "t_id": f"t{len(merged) + 1}",
                "fact_text": fact_text,
                "fact_role": fact_role,
            }
        )

    if not any(item.get("fact_role") == "goal" for item in merged):
        merged.append(
            {
                "t_id": f"t{len(merged) + 1}",
                "fact_text": _normalize_text_fact_text(question_text or "Solve the problem."),
                "fact_role": "goal",
            }
        )
    goal_items = [item for item in merged if item.get("fact_role") == "goal"]
    has_specific_goal = any(
        not re.fullmatch(r"(求目标角|求值|求结果|求答案|find the answer|solve the problem|determine the result)", item.get("fact_text", ""), re.IGNORECASE)
        for item in goal_items
    )
    if has_specific_goal:
        filtered: List[Dict[str, Any]] = []
        for item in merged:
            if item.get("fact_role") != "goal":
                filtered.append(item)
                continue
            if re.fullmatch(r"(求目标角|求值|求结果|求答案|find the answer|solve the problem|determine the result)", item.get("fact_text", ""), re.IGNORECASE):
                continue
            filtered.append(item)
        merged = [
            {
                **item,
                "t_id": f"t{index + 1}",
            }
            for index, item in enumerate(filtered)
        ]
    return merged

def _sanitize_ptk_foundation(problem: Dict[str, Any], foundation: Dict[str, Any]) -> Dict[str, Any]:
    sanitized = deepcopy(foundation)
    sanitized["t_facts"] = _sanitize_t_facts(problem, sanitized.get("t_facts", []))
    return sanitized

def _heuristic_ptk_foundation_report(problem: Dict[str, Any], foundation: Dict[str, Any]) -> Dict[str, Any]:
    actual_t_facts = foundation.get("t_facts", []) if isinstance(foundation.get("t_facts"), list) else []
    expected_t_facts = _derive_text_facts_from_question(normalize_whitespace(problem.get("question_text", "")))

    actual_markers = {
        (
            canonicalize_free_text(item.get("fact_text", "")),
            normalize_whitespace(item.get("fact_role", "")).lower(),
        )
        for item in actual_t_facts
        if isinstance(item, dict)
        and canonicalize_free_text(item.get("fact_text", ""))
        and normalize_whitespace(item.get("fact_role", "")).lower() in _ALLOWED_TEXT_FACT_ROLES
    }

    missing_expected_t_facts: List[Dict[str, str]] = []
    for item in expected_t_facts:
        fact_text = _normalize_text_fact_text(item.get("fact_text", ""))
        fact_role = normalize_whitespace(item.get("fact_role", "")).lower()
        marker = (canonicalize_free_text(fact_text), fact_role)
        if fact_text and fact_role in _ALLOWED_TEXT_FACT_ROLES and marker not in actual_markers:
            missing_expected_t_facts.append({"fact_text": fact_text, "fact_role": fact_role})

    valid_p_fact_count = sum(
        1
        for item in foundation.get("p_facts", [])
        if isinstance(item, dict)
        and normalize_whitespace(item.get("p_id", ""))
        and normalize_whitespace(item.get("fact_text", ""))
        and normalize_whitespace(item.get("visual_anchor", ""))
    )
    valid_k_atom_count = sum(
        1
        for item in foundation.get("k_atoms", [])
        if isinstance(item, dict)
        and normalize_whitespace(item.get("k_id", ""))
        and normalize_whitespace(item.get("knowledge_text", ""))
        and normalize_whitespace(item.get("knowledge_type", ""))
        and normalize_whitespace(item.get("applicability_note", ""))
    )
    has_goal = any(
        isinstance(item, dict) and normalize_whitespace(item.get("fact_role", "")).lower() == "goal"
        for item in actual_t_facts
    )

    critical_issues: List[str] = []
    if bool(problem.get("requires_image")) and valid_p_fact_count <= 0:
        critical_issues.append("PTK foundation is missing usable image-grounded p_facts.")
    if not has_goal:
        critical_issues.append("PTK foundation is missing a goal t_fact.")
    if missing_expected_t_facts:
        critical_issues.append(
            "PTK foundation is missing explicit text facts derived from the question: "
            + ", ".join(f"{item['fact_role']}={item['fact_text']}" for item in missing_expected_t_facts)
        )
    if valid_k_atom_count <= 0:
        critical_issues.append("PTK foundation is missing usable reusable k_atoms.")

    expected_count = len(expected_t_facts)
    if expected_count <= 0:
        coverage_score = 1.0 if has_goal else 0.0
    else:
        coverage_score = 1.0 - (len(missing_expected_t_facts) / expected_count)
    grounding_denominator = 2 if bool(problem.get("requires_image")) else 1
    grounding_numerator = int(valid_k_atom_count > 0) + (int(valid_p_fact_count > 0) if bool(problem.get("requires_image")) else 0)
    grounding_score = grounding_numerator / grounding_denominator if grounding_denominator else 1.0

    return {
        "pass": not critical_issues,
        "critical_issues": critical_issues,
        "missing_expected_t_facts": missing_expected_t_facts,
        "coverage_score": max(0.0, min(1.0, coverage_score)),
        "grounding_score": max(0.0, min(1.0, grounding_score)),
        "p_fact_count": valid_p_fact_count,
        "k_atom_count": valid_k_atom_count,
    }


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
                current_foundation.get(spec["field_name"], []),
                revision_instructions,
            ),
            "PTKFoundationPolish",
        ),
        _problem_image_paths(problem) if section_name == "p_facts" else [],
        agent_name="PTKFoundationPolish",
        require_images=bool(problem.get("requires_image")) and section_name == "p_facts",
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
        "issue_categories": _require_string_list("PTKFoundationCritic", response.get("issue_categories", []) or [], "issue_categories", allow_empty=True),
        "revision_instructions": _require_non_empty_text(
            "PTKFoundationCritic",
            revision_instructions,
            "revision_instructions",
        ),
        "grounding_score": _require_probability("PTKFoundationCritic", response.get("grounding_score"), "grounding_score"),
        "coverage_score": _require_probability("PTKFoundationCritic", response.get("coverage_score"), "coverage_score"),
    }


def _normalize_claim_verify_partial(response: Dict[str, Any], stage_name: str) -> Dict[str, Any]:
    passed = _require_bool(stage_name, response.get("pass"), "pass")
    revision_instructions = str(response.get("revision_instructions", "") or "").strip()
    if not revision_instructions and passed:
        revision_instructions = "No changes needed."
    issues = _require_string_list(stage_name, response.get("critical_issues", []), "critical_issues", allow_empty=True)
    return {
        "pass": passed,
        "critical_issues": issues,
        "revision_instructions": _require_non_empty_text(stage_name, revision_instructions, "revision_instructions"),
        "atomicity_score": _require_probability(stage_name, response.get("atomicity_score"), "atomicity_score"),
        "dependency_score": _require_probability(stage_name, response.get("dependency_score"), "dependency_score"),
        "grounding_score": _require_probability(stage_name, response.get("grounding_score"), "grounding_score"),
    }


def _normalize_claim_critique(response: Dict[str, Any]) -> Dict[str, Any]:
    return _normalize_claim_verify_partial(response, "ClaimVerify")


def _merge_claim_verify_partials(*partials: Dict[str, Any]) -> Dict[str, Any]:
    reports = [partial for partial in partials if isinstance(partial, dict)]
    if not reports:
        raise AgentContractError("[ClaimVerify] No partial verification reports were available.")
    pass_value = all(bool(report.get("pass")) for report in reports)
    critical_issues: List[str] = []
    revision_chunks: List[str] = []
    for report in reports:
        for issue in report.get("critical_issues", []) or []:
            text = normalize_whitespace(issue)
            if text and text not in critical_issues:
                critical_issues.append(text)
        instructions = normalize_whitespace(report.get("revision_instructions"))
        if instructions and instructions != "No changes needed." and instructions not in revision_chunks:
            revision_chunks.append(instructions)
    return {
        "pass": pass_value,
        "critical_issues": critical_issues,
        "revision_instructions": "No changes needed." if pass_value and not revision_chunks else " | ".join(revision_chunks) or "Review claim sequence for structural and grounding issues.",
        "atomicity_score": min(float(report.get("atomicity_score", 0.0)) for report in reports),
        "dependency_score": min(float(report.get("dependency_score", 0.0)) for report in reports),
        "grounding_score": min(float(report.get("grounding_score", 0.0)) for report in reports),
        "partial_reports": reports,
    }


def _build_ptk_problem_record(problem: Dict[str, Any]) -> Dict[str, Any]:
    return {
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


def _cached_dict_list(value: Any) -> List[Dict[str, Any]]:
    return [deepcopy(item) for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def _extract_ptk_once(
    router: ModelRouter,
    problem: Dict[str, Any],
    progress_state: Optional[Dict[str, Any]] = None,
    save_progress: Optional[Callable[[Dict[str, Any]], None]] = None,
) -> Dict[str, Any]:
    _ensure_problem_minimum(problem, "PTKFoundationBuilder")
    progress = progress_state if isinstance(progress_state, dict) else {}
    image_paths = _problem_image_paths(problem)
    require_images = bool(problem.get("requires_image"))
    cached_problem_record = progress.get("problem_record")
    problem_record = deepcopy(cached_problem_record) if isinstance(cached_problem_record, dict) else _build_ptk_problem_record(problem)

    p_facts = _cached_dict_list(progress.get("p_facts"))
    t_facts = _cached_dict_list(progress.get("t_facts"))
    k_atoms = _cached_dict_list(progress.get("k_atoms"))

    def _persist_substage(next_substage: str, *, foundation: Optional[Dict[str, Any]] = None) -> None:
        if save_progress is None:
            return
        payload = deepcopy(progress)
        payload.update(
            {
                "problem_record": deepcopy(problem_record),
                "p_facts": deepcopy(p_facts),
                "t_facts": deepcopy(t_facts),
                "k_atoms": deepcopy(k_atoms),
                "next_ptk_substage": next_substage,
                "ptk_substage_status": "complete" if foundation is not None else "in_progress",
            }
        )
        if foundation is not None:
            payload["foundation"] = deepcopy(foundation)
        save_progress(payload)

    if not p_facts:
        p_response = _call_router(
            router,
            PERCEPTION_EXTRACTION_SYSTEM_PROMPT,
            _augment_prompt_with_ready_context(problem, build_perception_user_prompt(problem), "PerceptionExtraction"),
            image_paths,
            agent_name="PerceptionExtraction",
            require_images=require_images,
        )
        p_facts = _normalize_p_facts(p_response, "PerceptionExtraction")
        _persist_substage("text_condition")

    if not t_facts:
        t_response = _call_router(
            router,
            TEXT_CONDITION_SYSTEM_PROMPT,
            _augment_prompt_with_ready_context(problem, build_text_condition_user_prompt(problem), "TextCondition"),
            image_paths,
            agent_name="TextCondition",
            require_images=require_images,
        )
        t_facts = _normalize_t_facts(t_response, "TextCondition")
        _persist_substage("knowledge_librarian")

    if not k_atoms:
        k_response = _call_router(
            router,
            KNOWLEDGE_LIBRARIAN_SYSTEM_PROMPT,
            _augment_prompt_with_ready_context(problem, build_knowledge_user_prompt(problem, p_facts, t_facts), "KnowledgeLibrarian"),
            image_paths,
            agent_name="KnowledgeLibrarian",
            require_images=require_images,
        )
        k_atoms = _normalize_k_atoms(k_response, "KnowledgeLibrarian")

    foundation = {
        "problem_record": problem_record,
        "p_facts": p_facts,
        "t_facts": t_facts,
        "k_atoms": k_atoms,
    }
    _persist_substage("complete", foundation=foundation)
    return foundation


def _select_claim_context(
    p_facts: Sequence[Dict[str, Any]],
    t_facts: Sequence[Dict[str, Any]],
    k_atoms: Sequence[Dict[str, Any]],
    *,
    p_limit: int,
    t_limit: int,
    k_limit: int,
) -> Dict[str, List[Dict[str, Any]]]:
    return {
        "p_facts": list(p_facts)[: max(0, p_limit)],
        "t_facts": list(t_facts)[: max(0, t_limit)],
        "k_atoms": list(k_atoms)[: max(0, k_limit)],
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
    narrowed = _select_claim_context(p_facts, t_facts, k_atoms, p_limit=8, t_limit=8, k_limit=8)
    return (
        base_prompt
        + "\n\nGrounded PTK Foundation (compact):\n"
        + "P Facts:\n"
        + to_plain_text(narrowed["p_facts"])
        + "\n\nT Facts:\n"
        + to_plain_text(narrowed["t_facts"])
        + "\n\nK Atoms:\n"
        + to_plain_text(narrowed["k_atoms"])
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
    # Use the newer upstream split structure/visual critics while retaining qjb's
    # router/client interfaces; add deterministic sanity checks before polish.
    response = _call_router(
        router,
        PTK_STRUCTURE_CRITIC_SYSTEM_PROMPT,
        _augment_prompt_with_ready_context(
            problem,
            build_ptk_structure_critic_user_prompt(problem, p_facts, t_facts, k_atoms),
            "PTKFoundationCritic",
        ),
        [],
        agent_name="PTKFoundationCritic",
        require_images=False,
    )
    critique = _normalize_ptk_critique(response)

    visual_report: Optional[Dict[str, Any]] = None
    if bool(problem.get("requires_image")):
        visual_response = _call_router(
            router,
            PTK_VISUAL_GROUNDING_CRITIC_SYSTEM_PROMPT,
            _augment_prompt_with_ready_context(
                problem,
                build_ptk_visual_grounding_critic_user_prompt(problem, p_facts),
                "PTKVisualGroundingCritic",
            ),
            _problem_image_paths(problem),
            agent_name="PTKVisualGroundingCritic",
            require_images=True,
        )
        visual_report = _normalize_ptk_critique({**visual_response, "coverage_score": 1.0})

    merged = _merge_ptk_critiques(critique, visual_report)
    heuristic_report = _heuristic_ptk_foundation_report(
        problem,
        {"p_facts": list(p_facts), "t_facts": list(t_facts), "k_atoms": list(k_atoms)},
    )
    if not heuristic_report.get("pass"):
        merged["pass"] = False
        for issue in heuristic_report.get("critical_issues", []):
            if issue not in merged["critical_issues"]:
                merged["critical_issues"].append(issue)
        if heuristic_report.get("missing_expected_t_facts") and "t_facts_missing_explicit_givens" not in merged["issue_categories"]:
            merged["issue_categories"].append("t_facts_missing_explicit_givens")
        if heuristic_report.get("p_fact_count", 0) <= 0 and bool(problem.get("requires_image")) and "p_facts_visual_grounding" not in merged["issue_categories"]:
            merged["issue_categories"].append("p_facts_visual_grounding")
        if heuristic_report.get("k_atom_count", 0) <= 0 and "k_atoms_missing_required_rule" not in merged["issue_categories"]:
            merged["issue_categories"].append("k_atoms_missing_required_rule")
        heuristic_instructions = "Deterministic PTK sanity check found: " + "; ".join(heuristic_report.get("critical_issues", []))
        if merged.get("revision_instructions") == "No changes needed.":
            merged["revision_instructions"] = heuristic_instructions
        else:
            merged["revision_instructions"] = normalize_whitespace(str(merged.get("revision_instructions", "")) + " " + heuristic_instructions)
        merged["coverage_score"] = min(safe_float(merged.get("coverage_score"), 0.0), safe_float(heuristic_report.get("coverage_score"), 0.0))
        merged["grounding_score"] = min(safe_float(merged.get("grounding_score"), 0.0), safe_float(heuristic_report.get("grounding_score"), 0.0))
    merged["heuristic_report"] = heuristic_report
    merged["component"] = "PTKFoundationCritic"
    return merged


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


def build_ptk_foundation(
    router: ModelRouter,
    problem: Dict[str, Any],
    max_repair_rounds: int = 2,
    progress_state: Optional[Dict[str, Any]] = None,
    save_progress: Optional[Callable[[Dict[str, Any]], None]] = None,
) -> Dict[str, Any]:
    progress = progress_state if isinstance(progress_state, dict) else {}
    cached_foundation = progress.get("foundation")
    if isinstance(cached_foundation, dict) and cached_foundation:
        foundation = deepcopy(cached_foundation)
    else:
        foundation = _extract_ptk_once(
            router,
            problem,
            progress_state=progress,
            save_progress=save_progress,
        )
    foundation = _sanitize_ptk_foundation(problem, foundation)

    raw_audit_rounds = progress.get("audit_rounds")
    audit_rounds: List[Dict[str, Any]] = [
        dict(item) for item in raw_audit_rounds if isinstance(item, dict)
    ] if isinstance(raw_audit_rounds, list) else []

    try:
        next_round_index = int(progress.get("next_round_index", len(audit_rounds)))
    except (TypeError, ValueError):
        next_round_index = len(audit_rounds)
    pending_critique = progress.get("pending_critique") if isinstance(progress.get("pending_critique"), dict) else None
    passed = bool(progress.get("passed")) and pending_critique is None

    def _persist(progress_passed: bool, next_index: int, pending: Optional[Dict[str, Any]]) -> None:
        if save_progress is None:
            return
        save_progress(
            {
                "foundation": deepcopy(foundation),
                "audit_rounds": [dict(item) for item in audit_rounds if isinstance(item, dict)],
                "next_round_index": next_index,
                "pending_critique": dict(pending) if isinstance(pending, dict) else None,
                "passed": bool(progress_passed),
            }
        )

    exhausted_failed_progress = (
        not passed
        and pending_critique is None
        and next_round_index > max_repair_rounds
    )
    if exhausted_failed_progress:
        audit_rounds = []
        next_round_index = 0
        _persist(False, 0, None)
    elif not (isinstance(cached_foundation, dict) and cached_foundation):
        _persist(False, len(audit_rounds), pending_critique)

    if not passed:
        for round_index in range(max(0, next_round_index), max_repair_rounds + 1):
            if isinstance(pending_critique, dict) and pending_critique.get("round_index") == round_index:
                round_record: Dict[str, Any] = dict(pending_critique)
            else:
                critique = critique_ptk_foundation(
                    router,
                    problem,
                    foundation.get("p_facts", []),
                    foundation.get("t_facts", []),
                    foundation.get("k_atoms", []),
                )
                round_record = {"round_index": round_index, **critique}
            if round_record.get("pass"):
                audit_rounds.append(round_record)
                passed = True
                pending_critique = None
                _persist(True, round_index + 1, None)
                break
            if round_index >= max_repair_rounds:
                audit_rounds.append(round_record)
                pending_critique = None
                _persist(False, round_index + 1, None)
                break
            pending_critique = dict(round_record)
            _persist(False, round_index, pending_critique)
            issue_categories = _infer_ptk_issue_categories(round_record)
            round_record["issue_categories"] = issue_categories
            revision_instructions = round_record["revision_instructions"]
            if issue_categories:
                revision_instructions = normalize_whitespace(
                    f"Issue categories: {', '.join(issue_categories)}. {revision_instructions}"
                )
            polished = polish_ptk_foundation(router, problem, foundation, revision_instructions)
            foundation = _sanitize_ptk_foundation(
                problem,
                {
                    **foundation,
                    "p_facts": polished["p_facts"],
                    "t_facts": polished["t_facts"],
                    "k_atoms": polished["k_atoms"],
                },
            )
            round_record["polish_summary"] = polished["revision_summary"]
            round_record["patched_sections"] = polished.get("patched_sections", [])
            round_record["section_summaries"] = polished.get("section_summaries", [])
            audit_rounds.append(round_record)
            pending_critique = None
            _persist(False, round_index + 1, None)

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
    narrowed = _select_claim_context(p_facts, t_facts, k_atoms, p_limit=8, t_limit=8, k_limit=6)

    structure_response = _call_router(
        router,
        CLAIM_VERIFY_STRUCTURE_SYSTEM_PROMPT,
        _augment_prompt_with_ready_context(
            problem,
            build_claim_structure_verify_user_prompt(problem, method, cot_text, claims),
            "ClaimVerify",
        ),
        _problem_image_paths(problem),
        agent_name="ClaimVerifyStructure",
        require_images=bool(problem.get("requires_image")),
    )
    structure_report = _normalize_claim_verify_partial(structure_response, "ClaimVerifyStructure")

    grounding_response = _call_router(
        router,
        CLAIM_VERIFY_GROUNDING_SYSTEM_PROMPT,
        _augment_prompt_with_ready_context(
            problem,
            build_claim_grounding_verify_user_prompt(
                problem,
                method,
                cot_text,
                claims,
                narrowed["p_facts"],
                narrowed["t_facts"],
                narrowed["k_atoms"],
            ),
            "ClaimVerify",
        ),
        _problem_image_paths(problem),
        agent_name="ClaimVerifyGrounding",
        require_images=bool(problem.get("requires_image")),
    )
    grounding_report = _normalize_claim_verify_partial(grounding_response, "ClaimVerifyGrounding")

    global_response = _call_router(
        router,
        CLAIM_VERIFY_GLOBAL_SYSTEM_PROMPT,
        _augment_prompt_with_ready_context(
            problem,
            build_claim_global_verify_user_prompt(problem, method, cot_text, claims),
            "ClaimVerify",
        ),
        _problem_image_paths(problem),
        agent_name="ClaimVerifyGlobal",
        require_images=bool(problem.get("requires_image")),
    )
    global_report = _normalize_claim_verify_partial(global_response, "ClaimVerifyGlobal")

    return _merge_claim_verify_partials(structure_report, grounding_report, global_report)


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
    narrowed = _select_claim_context(p_facts, t_facts, k_atoms, p_limit=8, t_limit=8, k_limit=6)
    response = _call_router(
        router,
        CLAIM_POLISH_SYSTEM_PROMPT,
        _augment_prompt_with_ready_context(
            problem,
            build_claim_polish_user_prompt(
                problem,
                method,
                cot_text,
                claims,
                revision_instructions,
                narrowed["p_facts"],
                narrowed["t_facts"],
                narrowed["k_atoms"],
            ),
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
    progress_state: Optional[Dict[str, Any]] = None,
    save_progress: Optional[Callable[[Dict[str, Any]], None]] = None,
) -> Dict[str, Any]:
    progress = progress_state if isinstance(progress_state, dict) else {}
    cached_claims = progress.get("claims")
    claims: List[Dict[str, Any]]
    if isinstance(cached_claims, list) and cached_claims:
        claims = [dict(item) for item in cached_claims if isinstance(item, dict)]
    else:
        claims = _extract_claims_once(router, problem, method, cot_text, p_facts, t_facts, k_atoms)

    raw_audit_rounds = progress.get("audit_rounds")
    audit_rounds: List[Dict[str, Any]] = [
        dict(item) for item in raw_audit_rounds if isinstance(item, dict)
    ] if isinstance(raw_audit_rounds, list) else []

    try:
        next_round_index = int(progress.get("next_round_index", len(audit_rounds)))
    except (TypeError, ValueError):
        next_round_index = len(audit_rounds)
    pending_critique = progress.get("pending_critique") if isinstance(progress.get("pending_critique"), dict) else None
    passed = bool(progress.get("passed")) and pending_critique is None

    def _persist(progress_passed: bool, next_index: int, pending: Optional[Dict[str, Any]]) -> None:
        if save_progress is None:
            return
        save_progress(
            {
                "claims": [dict(item) for item in claims if isinstance(item, dict)],
                "audit_rounds": [dict(item) for item in audit_rounds if isinstance(item, dict)],
                "next_round_index": next_index,
                "pending_critique": dict(pending) if isinstance(pending, dict) else None,
                "passed": bool(progress_passed),
            }
        )

    exhausted_failed_progress = (
        not passed
        and pending_critique is None
        and next_round_index > max_repair_rounds
    )
    if exhausted_failed_progress:
        audit_rounds = []
        next_round_index = 0
        _persist(False, 0, None)
    elif not (isinstance(cached_claims, list) and claims):
        _persist(False, len(audit_rounds), pending_critique)

    if not passed:
        for round_index in range(max(0, next_round_index), max_repair_rounds + 1):
            if isinstance(pending_critique, dict) and pending_critique.get("round_index") == round_index:
                round_record: Dict[str, Any] = dict(pending_critique)
            else:
                critique = critique_claim_sequence(router, problem, method, cot_text, claims, p_facts, t_facts, k_atoms)
                round_record = {"round_index": round_index, **critique}
            if round_record.get("pass"):
                audit_rounds.append(round_record)
                passed = True
                pending_critique = None
                _persist(True, round_index + 1, None)
                break
            if round_index >= max_repair_rounds:
                audit_rounds.append(round_record)
                pending_critique = None
                _persist(False, round_index + 1, None)
                break
            pending_critique = dict(round_record)
            _persist(False, round_index, pending_critique)
            polished = polish_claim_sequence(
                router,
                problem,
                method,
                cot_text,
                claims,
                round_record["revision_instructions"],
                p_facts,
                t_facts,
                k_atoms,
            )
            claims = polished["claims"]
            round_record["polish_summary"] = polished["revision_summary"]
            audit_rounds.append(round_record)
            pending_critique = None
            _persist(False, round_index + 1, None)

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
