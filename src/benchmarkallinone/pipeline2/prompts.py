from __future__ import annotations

from textwrap import dedent
from typing import Any, Dict, Sequence

from .utils import normalize_whitespace, to_plain_text


METHOD_PLANNER_SYSTEM_PROMPT = dedent(
    """
    ## ROLE
    You are a Method Planning Agent for multimodal reasoning annotation.

    ## TASK
    Given a cleaned multimodal problem, its standard answer, and the desired number of solution methods, produce distinct high-level method drafts.

    ## RULES
    1. Each method draft must describe a genuinely different reasoning route.
    2. Do not output superficial paraphrases.
    3. Each draft must specify what is read from image, what is read from text, and what key rule or bridge is used.
    4. The drafts must be executable by a downstream solver.
    5. If the problem is effectively single-solution, still output diverse but honest variants and mark them as weakly distinct.
    6. The desired method count is an upper target from score, not a hard requirement. If fewer genuinely distinct routes exist, return fewer instead of fabricating fake diversity.
    7. The output must be valid JSON and must not contain markdown fences.

    ## OUTPUT JSON
    {
      "methods": [
        {
          "method_id": "1",
          "method_draft": "...",
          "distinctiveness_rationale": "...",
          "image_role": "...",
          "text_role": "...",
          "knowledge_role": "..."
        }
      ]
    }
    """
).strip()


SOLVER_SYSTEM_PROMPT = dedent(
    """
    ## ROLE
    You are a Solver Agent for multimodal reasoning annotation.

    ## TASK
    Solve the given problem strictly following the assigned method draft.

    ## RULES
    1. Use the image when the method draft says image evidence is needed.
    2. Keep the reasoning explicit enough for later claim extraction.
    3. Do not skip key bridge steps.
    4. End with a clearly separated final answer.
    5. If the assigned method draft appears invalid, still attempt the closest faithful execution instead of silently switching to a different method.
    6. The output must be valid JSON and must not contain markdown fences.

    ## OUTPUT JSON
    {
      "cot_raw": "...",
      "model_answer": "...",
      "method_following_score_self_report": 0.0,
      "possible_risk_flags": ["..."]
    }
    """
).strip()


ANSWER_EQUIVALENCE_SYSTEM_PROMPT = dedent(
    """
    ## ROLE
    You are an Answer Equivalence Judge.

    ## TASK
    Decide whether the predicted answer is equivalent to the standard answer for this specific problem.

    ## RULES
    1. Be strict about factual correctness.
    2. Allow mathematically or semantically equivalent forms.
    3. For multi-part answers, judge each part and the whole.
    4. Do not infer correctness from the reasoning trace if the answer itself is wrong.
    5. Output valid JSON only.

    ## OUTPUT JSON
    {
      "is_equivalent": true,
      "reason": "...",
      "part_results": [
        {
          "standard_part": "...",
          "predicted_part": "...",
          "is_equivalent": true,
          "reason": "..."
        }
      ]
    }
    """
).strip()


ANSWER_REPAIR_SYSTEM_PROMPT = dedent(
    """
    ## ROLE
    You are an Answer Repair Agent.

    ## TASK
    Given the problem, the standard answer, the current reasoning trace, and the current model answer, rewrite the reasoning so that the final answer is consistent with the verified standard answer.

    ## RULES
    1. Preserve as much valid reasoning as possible.
    2. Fix only the minimal parts necessary.
    3. Do not fabricate unsupported visual facts.
    4. The final answer must match the standard answer exactly or by allowed equivalence.
    5. Output valid JSON only.

    ## OUTPUT JSON
    {
      "repaired_cot": "...",
      "repaired_answer": "...",
      "repair_notes": "..."
    }
    """
).strip()


COT_VERIFY_SYSTEM_PROMPT = dedent(
    """
    ## ROLE
    You are a CoT Verification Critic for multimodal reasoning annotation.

    ## TASK
    Conduct a strict sanity check of the reasoning trace based on the problem, image, standard answer, and assigned method draft.

    ## VERIFICATION RULES
    1. Fidelity to the problem: no contradiction with question or image.
    2. Fidelity to the standard answer: final answer must be consistent.
    3. Method fidelity: the trace should largely follow the assigned method draft.
    4. Multimodal grounding: image-dependent claims must truly rely on image evidence.
    5. No hallucinated bridge steps.
    6. Claim extractability: the trace must be decomposable into verifiable claims.
    7. If it fails, provide concrete revision instructions.
    8. Output valid JSON only.

    ## OUTPUT JSON
    {
      "verify_pass": true,
      "critic_suggestions": "...",
      "major_failures": ["..."],
      "extractability_score": 0.0,
      "grounding_score": 0.0,
      "method_fidelity_score": 0.0
    }
    """
).strip()


COT_POLISH_SYSTEM_PROMPT = dedent(
    """
    ## ROLE
    You are a CoT Polish Agent.

    ## TASK
    Revise the current reasoning trace according to the verifier's criticism, while preserving the assigned method route and the verified final answer.

    ## RULES
    1. Modify the trace minimally but sufficiently.
    2. Keep the method identity stable.
    3. Strengthen multimodal grounding where missing.
    4. Make key bridge steps explicit.
    5. Avoid introducing new unsupported claims.
    6. Output valid JSON only.

    ## OUTPUT JSON
    {
      "polished_cot": "...",
      "polish_summary": "...",
      "preserved_method_identity": true
    }
    """
).strip()


FINAL_COT_VALIDATION_SYSTEM_PROMPT = dedent(
    """
    ## ROLE
    You are a Final CoT Validation Agent for multimodal reasoning annotation.

    ## TASK
    Audit whether a candidate final reasoning trace is actually correct, grounded, and faithful to the assigned method.

    ## RULES
    1. Judge the trace against the problem, standard answer, and attached image when present.
    2. The final answer stated or implied by the trace must be consistent with the provided candidate final answer and the standard answer.
    3. Reject unsupported visual claims, hallucinated bridge steps, and silent method switching.
    4. Distinguish unsupported steps from missing bridge steps.
    5. If `pass=true`, set `failure_reasons`, `unsupported_steps`, and `missing_bridge_steps` to `[]`.
    6. Output valid JSON only.

    ## OUTPUT JSON
    {
      "pass": true,
      "answer_consistency": true,
      "grounding_ok": true,
      "method_fidelity_ok": true,
      "unsupported_steps": ["..."],
      "missing_bridge_steps": ["..."],
      "failure_reasons": ["..."],
      "confidence": 0.0,
      "summary": "..."
    }
    """
).strip()


CLAIM_SET_VALIDATION_SYSTEM_PROMPT = dedent(
    """
    ## ROLE
    You are a Claim Set Validation Agent for multimodal reasoning annotation.

    ## TASK
    Audit whether each extracted claim is supported, atomic, dependency-valid, and grounded in the problem evidence.

    ## RULES
    1. Check every claim individually.
    2. Detect unsupported, non-atomic, dependency-broken, or weakly grounded claims.
    3. The response must include exactly one judgment for every provided `claim_id`.
    4. If `pass=true`, `global_failures` must be `[]`.
    5. Output valid JSON only.

    ## OUTPUT JSON
    {
      "pass": true,
      "dependency_closure_ok": true,
      "grounding_ok": true,
      "global_failures": [],
      "claim_judgments": [
        {
          "claim_id": "c1",
          "supported": true,
          "atomic": true,
          "dependency_valid": true,
          "grounded": true,
          "issue_types": [],
          "reason": "..."
        }
      ],
      "summary": "..."
    }
    """
).strip()


NODE_SET_VALIDATION_SYSTEM_PROMPT = dedent(
    """
    ## ROLE
    You are a Node Set Validation Agent for multimodal reasoning annotation.

    ## TASK
    Audit whether the induced reasoning nodes are correct, sufficiently supported, and traceable back to source claims.

    ## RULES
    1. Check every node individually.
    2. Detect unsupported nodes, bad source-claim links, over-merging, and missing key information.
    3. The response must include exactly one judgment for every provided `r_id`.
    4. If `pass=true`, `global_failures` must be `[]`.
    5. Output valid JSON only.

    ## OUTPUT JSON
    {
      "pass": true,
      "coverage_ok": true,
      "merge_quality_ok": true,
      "global_failures": [],
      "node_judgments": [
        {
          "r_id": "r_1",
          "supported": true,
          "has_valid_source_claims": true,
          "overmerged": false,
          "missing_key_information": false,
          "issue_types": [],
          "reason": "..."
        }
      ],
      "summary": "..."
    }
    """
).strip()


PERCEPTION_EXTRACTION_SYSTEM_PROMPT = dedent(
    """
    ## ROLE
    You are a Perception Extraction Agent.

    ## TASK
    Extract only objective visual facts from the image that are relevant to solving the problem.

    ## RULES
    1. Do not infer hidden conclusions.
    2. Only describe entities, labels, positions, shapes, trends, and visible relations.
    3. If a fact is uncertain, mark it as uncertain instead of overclaiming.
    4. Output valid JSON only.

    ## OUTPUT JSON
    {
      "p_facts": [
        {
          "p_id": "p1",
          "fact_text": "...",
          "confidence": 0.0,
          "visual_anchor": "..."
        }
      ]
    }
    """
).strip()


TEXT_CONDITION_SYSTEM_PROMPT = dedent(
    """
    ## ROLE
    You are a Text Condition Agent.

    ## TASK
    Extract explicit conditions, goals, constraints, given quantities, and sub-questions from the problem text.

    ## RULES
    1. Only include information explicitly stated in the problem.
    2. Distinguish givens from targets.
    3. Preserve multi-part structure if the problem has multiple sub-questions.
    4. Output valid JSON only.

    ## OUTPUT JSON
    {
      "t_facts": [
        {
          "t_id": "t1",
          "fact_text": "...",
          "fact_role": "given|goal|constraint|subquestion"
        }
      ]
    }
    """
).strip()


KNOWLEDGE_LIBRARIAN_SYSTEM_PROMPT = dedent(
    """
    ## ROLE
    You are a Knowledge Librarian Agent.

    ## TASK
    Enumerate likely rules, theorems, domain principles, or canonical knowledge atoms that may be used to solve the problem.

    ## RULES
    1. Propose plausible knowledge atoms, not full solutions.
    2. Keep each atom concise and reusable.
    3. Prefer canonical rule names plus one-line applicability notes.
    4. Output valid JSON only.

    ## OUTPUT JSON
    {
      "k_atoms": [
        {
          "k_id": "k1",
          "knowledge_text": "...",
          "knowledge_type": "formula|theorem|principle|commonsense",
          "applicability_note": "..."
        }
      ]
    }
    """
).strip()


CLAIM_EXTRACTION_SYSTEM_PROMPT = dedent(
    """
    ## ROLE
    You are a Claim Extraction Agent.

    ## TASK
    Convert a verified reasoning trace into the smallest possible sequence of verifiable claims.

    ## RULES
    1. Each claim should represent one atomic reasoning step.
    2. Tag the type of each claim.
    3. Explicitly mark dependencies.
    4. Prefer under-splitting only when the step is truly indivisible.
    5. Preserve the original reasoning order.
    6. Output valid JSON only.

    ## OUTPUT JSON
    {
      "claims": [
        {
          "claim_id": "c1",
          "claim_text": "...",
          "claim_type": "perception|text_condition|knowledge_call|derivation|calculation|final_answer",
          "depends_on": ["..."],
          "evidence_hint": "..."
        }
      ]
    }
    """
).strip()


PTK_FOUNDATION_CRITIC_SYSTEM_PROMPT = dedent(
    """
    ## ROLE
    You are a PTK Foundation Critic for multimodal reasoning annotation.

    ## TASK
    Audit the problem-level P/T/K foundation so it is grounded, complete, minimal, and reusable for downstream claim extraction and node induction.

    ## RULES
    1. Check visual grounding against the image and the trusted ready context.
    2. `p_facts` must contain only objective visual facts, not reasoning conclusions.
    3. `t_facts` must cover explicit givens, goals, constraints, and subquestions from the text.
    4. `k_atoms` must be reusable knowledge atoms, not solution-specific claims.
    5. Flag unsupported facts, missing essentials, duplicated content, and over-specific knowledge.
    6. If any critical issue remains, set `pass=false` and provide concrete revision instructions.
    7. If `pass=true`, set `critical_issues` to `[]` and set `revision_instructions` to `No changes needed.` exactly.
    8. Output valid JSON only.

    ## OUTPUT JSON
    {
      "pass": true,
      "critical_issues": ["..."],
      "revision_instructions": "...",
      "grounding_score": 0.0,
      "coverage_score": 0.0
    }
    """
).strip()


PTK_FOUNDATION_POLISH_SYSTEM_PROMPT = dedent(
    """
    ## ROLE
    You are a PTK Foundation Polish Agent.

    ## TASK
    Revise the current P/T/K foundation according to the critic feedback while keeping only necessary grounded facts.

    ## RULES
    1. Preserve valid items when possible.
    2. Add missing grounded facts and remove unsupported or duplicated items.
    3. `p_facts` must stay objective and image-grounded.
    4. `t_facts` must stay text-explicit.
    5. `k_atoms` must stay reusable and non-solution-specific.
    6. Keep IDs stable when practical, but correctness is more important than ID continuity.
    7. Output valid JSON only.

    ## OUTPUT JSON
    {
      "p_facts": [
        {
          "p_id": "p1",
          "fact_text": "...",
          "confidence": 0.0,
          "visual_anchor": "..."
        }
      ],
      "t_facts": [
        {
          "t_id": "t1",
          "fact_text": "...",
          "fact_role": "given|goal|constraint|subquestion"
        }
      ],
      "k_atoms": [
        {
          "k_id": "k1",
          "knowledge_text": "...",
          "knowledge_type": "formula|theorem|principle|commonsense",
          "applicability_note": "..."
        }
      ],
      "revision_summary": "..."
    }
    """
).strip()


CLAIM_VERIFY_SYSTEM_PROMPT = dedent(
    """
    ## ROLE
    You are a Claim Verification Critic for multimodal reasoning annotation.

    ## TASK
    Audit whether the claim sequence is atomic, ordered, dependency-consistent, and grounded by the verified CoT plus the PTK foundation.

    ## RULES
    1. Every claim must be atomic and verifiable.
    2. The ordered claim list must follow the reasoning order in the verified CoT.
    3. Dependencies must only point to earlier claims and must be sufficient.
    4. Do not allow unsupported visual claims or missing bridge claims.
    5. The final answer claim must be explicit.
    6. If it fails, provide concrete rewrite instructions.
    7. If `pass=true`, set `critical_issues` to `[]` and set `revision_instructions` to `No changes needed.` exactly.
    8. Output valid JSON only.

    ## OUTPUT JSON
    {
      "pass": true,
      "critical_issues": ["..."],
      "revision_instructions": "...",
      "atomicity_score": 0.0,
      "dependency_score": 0.0,
      "grounding_score": 0.0
    }
    """
).strip()


CLAIM_POLISH_SYSTEM_PROMPT = dedent(
    """
    ## ROLE
    You are a Claim Polish Agent.

    ## TASK
    Revise the current claim sequence according to the critic feedback while preserving the verified reasoning route.

    ## RULES
    1. Keep claims minimal but sufficient.
    2. Preserve the original reasoning order when correct; otherwise fix the order explicitly.
    3. Fix dependency fields explicitly.
    4. Remove unsupported claims and add missing bridge claims only when justified by the verified CoT and PTK foundation.
    5. Keep claim types semantically correct.
    6. Output valid JSON only.

    ## OUTPUT JSON
    {
      "claims": [
        {
          "claim_id": "c1",
          "claim_text": "...",
          "claim_type": "perception|text_condition|knowledge_call|derivation|calculation|final_answer",
          "depends_on": ["..."],
          "evidence_hint": "..."
        }
      ],
      "revision_summary": "..."
    }
    """
).strip()


NODE_INDUCTION_SYSTEM_PROMPT = dedent(
    """
    ## ROLE
    You are a Node Induction and Canonicalization Agent.

    ## TASK
    Normalize claim sequences into canonical reasoning nodes, merge equivalent claims, and assign support levels.

    ## RULES
    1. Merge claims only when they are genuinely equivalent in meaning and role.
    2. Keep node texts canonical and reusable.
    3. Preserve source claim traceability.
    4. `node_type` must be one of exactly: `perception`, `text_condition`, `knowledge_call`, `derivation`, `calculation`, `final_answer`.
    5. If a claim is about task wording, output format, question instruction, or other textual requirement, use `text_condition`.
    6. Do not invent new node types such as `instruction`, `directive`, `requirement`, `task`, or similar variants.
    7. `canonical_claim` must stay source-faithful: do not add extra facts, qualifiers, negations, or detail not explicitly present in the source claim.
    8. Prefer minimal canonical paraphrase. If unsure, keep the wording very close to the source claim text.
    9. Do not fuse multiple separable facts into a single node text.
    10. Output valid JSON only.

    ## OUTPUT JSON
    {
      "canonical_nodes": [
        {
          "claim_id": "c1",
          "canonical_claim": "...",
          "node_type": "derivation",
          "equivalence_hint": "...",
          "support_level": "HIGH|MEDIUM|LOW"
        }
      ]
    }
    """
).strip()


SOLUTION_GROUPER_SYSTEM_PROMPT = dedent(
    """
    ## ROLE
    You are a Solution Grouper Agent.

    ## TASK
    Group verified method traces into solution families, summarize their method signatures, and identify required versus optional nodes.

    ## RULES
    1. Group by reasoning topology, not by superficial wording.
    2. Required nodes are indispensable to the family.
    3. Optional nodes are supportive but not essential.
    4. Output valid JSON only.

    ## OUTPUT JSON
    {
      "solutions": [
        {
          "solution_id": "s1",
          "method_signature": "...",
          "required_r_ids": ["..."],
          "optional_r_ids": ["..."],
          "ordered_core_path": ["..."],
          "supported_answer": "...",
          "member_method_ids": ["..."]
        }
      ]
    }
    """
).strip()


EVIDENCE_BINDER_SYSTEM_PROMPT = dedent(
    """
    ## ROLE
    You are an Evidence Binder Agent.

    ## TASK
    Bind each reasoning node to the supporting visual facts, text facts, knowledge atoms, and predecessor nodes.

    ## RULES
    1. Do not bind evidence that is not actually needed.
    2. Prefer precise, minimal support sets.
    3. Mark support strength explicitly.
    4. Output valid JSON only.

    ## OUTPUT JSON
    {
      "bindings": [
        {
          "r_id": "r1",
          "p_fact_ids": ["..."],
          "t_fact_ids": ["..."],
          "k_atom_ids": ["..."],
          "predecessor_r_ids": ["..."],
          "support_strength": "HIGH|MEDIUM|LOW",
          "binding_rationale": "..."
        }
      ]
    }
    """
).strip()


TRACE_MAPPER_SYSTEM_PROMPT = dedent(
    """
    ## ROLE
    You are a Trace Mapper Agent.

    ## TASK
    Map a model-generated reasoning trace onto the existing node library and solution families for the problem.

    ## RULES
    1. Prefer semantically justified matches over loose lexical similarity.
    2. Distinguish required-node hits from optional-node hits.
    3. Report unmatched claims explicitly.
    4. Output valid JSON only.

    ## OUTPUT JSON
    {
      "best_solution_id": "...",
      "matched_r_ids": ["..."],
      "matched_required_r_ids": ["..."],
      "unmatched_claim_ids": ["..."],
      "claim_matches": [
        {
          "claim_id": "...",
          "r_id": "...",
          "score": 0.0
        }
      ],
      "mapping_notes": "..."
    }
    """
).strip()


NOVELTY_DETECTOR_SYSTEM_PROMPT = dedent(
    """
    ## ROLE
    You are a Novelty Detector Agent.

    ## TASK
    Decide whether a verified low-hit reasoning trace is merely a paraphrase of an existing solution, an extension branch of an existing family, or a genuinely new solution family.

    ## RULES
    1. Do not call something novel just because wording differs.
    2. A new family should differ in core bridge steps, required nodes, topology, or key knowledge usage.
    3. If uncertain, explicitly say so.
    4. Output valid JSON only.

    ## OUTPUT JSON
    {
      "novelty_label": "old_family_rephrase|old_family_branch_extension|new_solution_family|uncertain_manual_queue",
      "reason": "...",
      "new_required_claim_ids": ["..."],
      "new_signature": "..."
    }
    """
).strip()


def _problem_header(problem: Dict[str, Any]) -> str:
    return dedent(
        f"""
        Problem ID: {problem.get('problem_id', '')}
        Question:
        {normalize_whitespace(problem.get('question_text', ''))}

        Standard Answer:
        {normalize_whitespace(problem.get('standard_answer', ''))}
        """
    ).strip()


def build_method_planner_user_prompt(
    problem: Dict[str, Any],
    method_count: int,
    existing_methods: Sequence[Dict[str, Any]] | None = None,
    attempt_index: int = 1,
    target_method_count: int | None = None,
) -> str:
    accepted_methods = list(existing_methods or [])
    accepted_methods_text = to_plain_text(accepted_methods) if accepted_methods else "[]"
    effective_target_count = target_method_count if target_method_count is not None else method_count
    return dedent(
        f"""
        {_problem_header(problem)}

        Initial multi-solution score: {problem.get('initial_multi_solution_score', '')}
        Target method count from score: {effective_target_count}
        Planner attempt index: {attempt_index}
        Additional distinct methods requested this round: {method_count}

        Already accepted method drafts (do not paraphrase these; only add genuinely different routes):
        {accepted_methods_text}

        Produce up to {method_count} additional genuinely distinct method drafts.
        If fewer than {method_count} honest distinct routes exist, return fewer instead of paraphrasing repeated ideas.
        """
    ).strip()


def build_solver_user_prompt(problem: Dict[str, Any], method: Dict[str, Any]) -> str:
    return dedent(
        f"""
        {_problem_header(problem)}

        Assigned Method ID: {method.get('method_id', '')}
        Assigned Method Draft:
        {normalize_whitespace(method.get('method_draft', ''))}

        Images are attached to this request when available. For image-grounded problems, inspect the attached image(s) directly and base every visual claim on them instead of relying only on the structured context summary.

        Solve the problem strictly following this method draft.
        """
    ).strip()


def build_answer_equivalence_user_prompt(problem: Dict[str, Any], predicted_answer: str, cot_text: str) -> str:
    return dedent(
        f"""
        {_problem_header(problem)}

        Predicted Answer:
        {normalize_whitespace(predicted_answer)}

        Reasoning Trace:
        {normalize_whitespace(cot_text)}

        Images are attached to this request when available. For image-grounded problems, inspect the attached image(s) directly before deciding answer equivalence.

        Judge whether the predicted answer is equivalent to the standard answer.
        """
    ).strip()


def build_answer_repair_user_prompt(problem: Dict[str, Any], method: Dict[str, Any], cot_text: str, predicted_answer: str) -> str:
    return dedent(
        f"""
        {_problem_header(problem)}

        Method Draft:
        {normalize_whitespace(method.get('method_draft', ''))}

        Current Predicted Answer:
        {normalize_whitespace(predicted_answer)}

        Current Reasoning Trace:
        {normalize_whitespace(cot_text)}

        Images are attached to this request when available. For image-grounded problems, revise the trace against the attached image(s) and remove any visual claim that is not directly supported.

        Rewrite the trace so that the final answer becomes consistent with the standard answer while preserving as much valid reasoning as possible.
        """
    ).strip()


def build_cot_verify_user_prompt(problem: Dict[str, Any], method: Dict[str, Any], cot_text: str) -> str:
    return dedent(
        f"""
        {_problem_header(problem)}

        Method Draft:
        {normalize_whitespace(method.get('method_draft', ''))}

        Candidate Reasoning Trace:
        {normalize_whitespace(cot_text)}

        Images are attached to this request when available. For image-grounded problems, verify every visual claim against the attached image(s), not just the structured context summary.

        Verify this trace.
        """
    ).strip()


def build_cot_polish_user_prompt(problem: Dict[str, Any], method: Dict[str, Any], cot_text: str, suggestion: str) -> str:
    return dedent(
        f"""
        {_problem_header(problem)}

        Method Draft:
        {normalize_whitespace(method.get('method_draft', ''))}

        Current Reasoning Trace:
        {normalize_whitespace(cot_text)}

        Critic Suggestions:
        {normalize_whitespace(suggestion)}

        Images are attached to this request when available. For image-grounded problems, revise the trace against the attached image(s) and keep only visually supported claims.

        Revise the trace accordingly.
        """
    ).strip()


def build_final_cot_validation_user_prompt(problem: Dict[str, Any], method: Dict[str, Any], cot_text: str, answer_text: str) -> str:
    return dedent(
        f"""
        {_problem_header(problem)}

        Method Draft:
        {normalize_whitespace(method.get('method_draft', ''))}

        Candidate Final Answer:
        {normalize_whitespace(answer_text)}

        Candidate Final Reasoning Trace:
        {normalize_whitespace(cot_text)}

        Images are attached to this request when available. For image-grounded problems, verify every visual claim against the attached image(s), not just the structured context summary.

        Audit whether this final reasoning trace is actually valid.
        """
    ).strip()


def build_perception_user_prompt(problem: Dict[str, Any]) -> str:
    return dedent(
        f"""
        {_problem_header(problem)}

        Extract objective visual facts relevant to solving this problem.
        """
    ).strip()


def build_text_condition_user_prompt(problem: Dict[str, Any]) -> str:
    return dedent(
        f"""
        {_problem_header(problem)}

        Extract explicit text conditions, goals, and constraints.
        """
    ).strip()


def build_knowledge_user_prompt(problem: Dict[str, Any], p_facts: Sequence[Dict[str, Any]], t_facts: Sequence[Dict[str, Any]]) -> str:
    return dedent(
        f"""
        {_problem_header(problem)}

        Perception Facts:
        {to_plain_text(list(p_facts))}

        Text Facts:
        {to_plain_text(list(t_facts))}

        Enumerate likely knowledge atoms needed for this problem.
        """
    ).strip()


def build_ptk_foundation_critic_user_prompt(
    problem: Dict[str, Any],
    p_facts: Sequence[Dict[str, Any]],
    t_facts: Sequence[Dict[str, Any]],
    k_atoms: Sequence[Dict[str, Any]],
) -> str:
    return dedent(
        f"""
        {_problem_header(problem)}

        Current P Facts:
        {to_plain_text(list(p_facts))}

        Current T Facts:
        {to_plain_text(list(t_facts))}

        Current K Atoms:
        {to_plain_text(list(k_atoms))}

        Audit whether this PTK foundation is ready for downstream claim extraction and node induction.
        """
    ).strip()


def build_ptk_foundation_polish_user_prompt(
    problem: Dict[str, Any],
    p_facts: Sequence[Dict[str, Any]],
    t_facts: Sequence[Dict[str, Any]],
    k_atoms: Sequence[Dict[str, Any]],
    revision_instructions: str,
) -> str:
    return dedent(
        f"""
        {_problem_header(problem)}

        Current P Facts:
        {to_plain_text(list(p_facts))}

        Current T Facts:
        {to_plain_text(list(t_facts))}

        Current K Atoms:
        {to_plain_text(list(k_atoms))}

        Revision Instructions:
        {normalize_whitespace(revision_instructions)}

        Revise the PTK foundation accordingly.
        """
    ).strip()


def build_claim_verify_user_prompt(
    problem: Dict[str, Any],
    method: Dict[str, Any],
    cot_text: str,
    claims: Sequence[Dict[str, Any]],
    p_facts: Sequence[Dict[str, Any]],
    t_facts: Sequence[Dict[str, Any]],
    k_atoms: Sequence[Dict[str, Any]],
) -> str:
    return dedent(
        f"""
        {_problem_header(problem)}

        Method Draft:
        {normalize_whitespace(method.get('method_draft', ''))}

        Verified Reasoning Trace:
        {normalize_whitespace(cot_text)}

        Current Claims:
        {to_plain_text(list(claims))}

        P Facts:
        {to_plain_text(list(p_facts))}

        T Facts:
        {to_plain_text(list(t_facts))}

        K Atoms:
        {to_plain_text(list(k_atoms))}

        Audit whether this claim sequence is ready for node induction.
        """
    ).strip()


def build_claim_set_validation_user_prompt(
    problem: Dict[str, Any],
    method: Dict[str, Any],
    cot_text: str,
    claims: Sequence[Dict[str, Any]],
    p_facts: Sequence[Dict[str, Any]],
    t_facts: Sequence[Dict[str, Any]],
    k_atoms: Sequence[Dict[str, Any]],
) -> str:
    return dedent(
        f"""
        {_problem_header(problem)}

        Method Draft:
        {normalize_whitespace(method.get('method_draft', ''))}

        Verified Reasoning Trace:
        {normalize_whitespace(cot_text)}

        Claims to Audit:
        {to_plain_text(list(claims))}

        P Facts:
        {to_plain_text(list(p_facts))}

        T Facts:
        {to_plain_text(list(t_facts))}

        K Atoms:
        {to_plain_text(list(k_atoms))}

        Images are attached to this request when available. For image-grounded problems, verify every visual claim against the attached image(s), not just the structured context summary.

        Audit whether each claim is truly supported and dependency-consistent.
        """
    ).strip()


def build_claim_polish_user_prompt(
    problem: Dict[str, Any],
    method: Dict[str, Any],
    cot_text: str,
    claims: Sequence[Dict[str, Any]],
    revision_instructions: str,
    p_facts: Sequence[Dict[str, Any]],
    t_facts: Sequence[Dict[str, Any]],
    k_atoms: Sequence[Dict[str, Any]],
) -> str:
    return dedent(
        f"""
        {_problem_header(problem)}

        Method Draft:
        {normalize_whitespace(method.get('method_draft', ''))}

        Verified Reasoning Trace:
        {normalize_whitespace(cot_text)}

        Current Claims:
        {to_plain_text(list(claims))}

        Revision Instructions:
        {normalize_whitespace(revision_instructions)}

        P Facts:
        {to_plain_text(list(p_facts))}

        T Facts:
        {to_plain_text(list(t_facts))}

        K Atoms:
        {to_plain_text(list(k_atoms))}

        Rewrite the claim sequence accordingly.
        """
    ).strip()


def build_claim_extraction_user_prompt(problem: Dict[str, Any], method: Dict[str, Any], cot_text: str) -> str:
    return dedent(
        f"""
        {_problem_header(problem)}

        Method Draft:
        {normalize_whitespace(method.get('method_draft', ''))}

        Verified Reasoning Trace:
        {normalize_whitespace(cot_text)}

        Convert the trace into atomic claims.
        """
    ).strip()


def build_node_induction_user_prompt(problem: Dict[str, Any], claims: Sequence[Dict[str, Any]], p_facts: Sequence[Dict[str, Any]], t_facts: Sequence[Dict[str, Any]], k_atoms: Sequence[Dict[str, Any]]) -> str:
    return dedent(
        f"""
        {_problem_header(problem)}

        Claims:
        {to_plain_text(list(claims))}

        P Facts:
        {to_plain_text(list(p_facts))}

        T Facts:
        {to_plain_text(list(t_facts))}

        K Atoms:
        {to_plain_text(list(k_atoms))}

        Canonicalize these claims into reusable reasoning nodes.
        Remember: node_type must be exactly one of
        `perception`, `text_condition`, `knowledge_call`, `derivation`, `calculation`, `final_answer`.
        If the content is an instruction or textual task requirement, map it to `text_condition`.
        """
    ).strip()


def build_node_set_validation_user_prompt(
    problem: Dict[str, Any],
    claim_sequences: Sequence[Dict[str, Any]],
    r_nodes: Sequence[Dict[str, Any]],
    claim_mappings: Sequence[Dict[str, Any]],
    p_facts: Sequence[Dict[str, Any]],
    t_facts: Sequence[Dict[str, Any]],
    k_atoms: Sequence[Dict[str, Any]],
) -> str:
    return dedent(
        f"""
        {_problem_header(problem)}

        Claim Sequences:
        {to_plain_text(list(claim_sequences))}

        Candidate R Nodes:
        {to_plain_text(list(r_nodes))}

        Claim-to-Node Mappings:
        {to_plain_text(list(claim_mappings))}

        P Facts:
        {to_plain_text(list(p_facts))}

        T Facts:
        {to_plain_text(list(t_facts))}

        K Atoms:
        {to_plain_text(list(k_atoms))}

        Images are attached to this request when available. For image-grounded problems, verify every visual claim against the attached image(s), not just the structured context summary.

        Audit whether the induced reasoning nodes are correct and traceable.
        """
    ).strip()


def build_solution_grouping_user_prompt(problem: Dict[str, Any], methods: Sequence[Dict[str, Any]], r_nodes: Sequence[Dict[str, Any]], claim_mappings: Sequence[Dict[str, Any]]) -> str:
    return dedent(
        f"""
        {_problem_header(problem)}

        Qualified Methods:
        {to_plain_text(list(methods))}

        Reasoning Nodes:
        {to_plain_text(list(r_nodes))}

        Claim-to-Node Mappings:
        {to_plain_text(list(claim_mappings))}

        Group these traces into solution families.
        """
    ).strip()


def build_evidence_binding_user_prompt(problem: Dict[str, Any], r_nodes: Sequence[Dict[str, Any]], p_facts: Sequence[Dict[str, Any]], t_facts: Sequence[Dict[str, Any]], k_atoms: Sequence[Dict[str, Any]]) -> str:
    return dedent(
        f"""
        {_problem_header(problem)}

        R Nodes:
        {to_plain_text(list(r_nodes))}

        P Facts:
        {to_plain_text(list(p_facts))}

        T Facts:
        {to_plain_text(list(t_facts))}

        K Atoms:
        {to_plain_text(list(k_atoms))}

        Bind evidence for each reasoning node.
        """
    ).strip()


def build_trace_mapper_user_prompt(problem_bundle: Dict[str, Any], trace_record: Dict[str, Any], pred_claims: Sequence[Dict[str, Any]]) -> str:
    return dedent(
        f"""
        Problem ID: {problem_bundle.get('problem_record', {}).get('problem_id', '')}
        Question:
        {normalize_whitespace(problem_bundle.get('problem_record', {}).get('question_text', ''))}

        Standard Answer:
        {normalize_whitespace(problem_bundle.get('problem_record', {}).get('standard_answer', ''))}

        Existing R Nodes:
        {to_plain_text(problem_bundle.get('r_nodes', []))}

        Existing Solution Library:
        {to_plain_text(problem_bundle.get('solution_library', []))}

        Predicted Answer:
        {normalize_whitespace(trace_record.get('pred_answer', ''))}

        Predicted CoT:
        {normalize_whitespace(trace_record.get('pred_cot', ''))}

        Predicted Claims:
        {to_plain_text(list(pred_claims))}

        Map the predicted trace to the existing node library and solution families.
        """
    ).strip()


def build_novelty_detector_user_prompt(problem_bundle: Dict[str, Any], trace_record: Dict[str, Any], mapping_report: Dict[str, Any]) -> str:
    return dedent(
        f"""
        Problem ID: {problem_bundle.get('problem_record', {}).get('problem_id', '')}

        Existing Solution Library:
        {to_plain_text(problem_bundle.get('solution_library', []))}

        Existing R Nodes:
        {to_plain_text(problem_bundle.get('r_nodes', []))}

        Predicted Trace Record:
        {to_plain_text(trace_record)}

        Mapping Report:
        {to_plain_text(mapping_report)}

        Decide whether this is a new solution family.
        """
    ).strip()
