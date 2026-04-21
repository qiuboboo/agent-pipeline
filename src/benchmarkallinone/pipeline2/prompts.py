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
    2. `fact_text` must preserve the original question wording verbatim whenever possible: copy exact clauses/spans from the problem text instead of paraphrasing, translating, normalizing, or summarizing them.
    3. Do not merge distant clauses into one rewritten sentence; if the text contains multiple explicit conditions, keep them as separate `t_facts` using the original wording.
    4. Distinguish givens from targets.
    5. Preserve multi-part structure if the problem has multiple sub-questions.
    6. Do not copy image-derived structure, tables, map cell values, geometry relations, circuit topology, or any other visual observations into `t_facts` unless the same content is explicitly stated in the text itself.
    7. If the problem is multimodal, `t_facts` should usually be short and text-only; visual details belong in `p_facts`, not `t_facts`.
    8. Output valid JSON only.

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
    4. Do not restate visual observations or text givens as `k_atoms`; those belong in `p_facts` or `t_facts`.
    5. Avoid redundant or overlapping atoms; merge near-duplicates into a single more general reusable rule when possible.
    6. For K-map / Karnaugh-map problems, include every adjacency rule needed for valid grouping. In particular, for 5-variable K-maps split into two 4x4 planes, explicitly include that corresponding cells at the same row and column across the two planes are adjacent because they differ only in the split variable.
    7. Output valid JSON only.

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
    Convert a verified reasoning trace into the smallest sufficient sequence of verifiable claims, prioritizing correctness and support completeness over brevity.

    ## RULES
    1. Each claim should represent one atomic reasoning step.
    2. Tag the type of each claim.
    3. Explicitly mark dependencies.
    4. Prefer under-splitting only when the step is truly indivisible.
    4a. When brevity conflicts with accuracy or support completeness, prefer more claims.
    5. Preserve the original reasoning order.
    6. If one sentence contains a short local micro-chain, split it into separate claims when the substeps are independently verifiable. Typical examples include: identifying what stays constant vs. deriving an implicant, establishing coverage vs. concluding minimality, observing a mismatch vs. concluding a larger grouping is impossible, OR-ing selected implicants vs. asserting that the result is minimal, showing that enlargement fails by columns vs. showing that enlargement fails by rows, or listing several constant or varying variables in one sentence before deriving an implicant.
    7. Treat cross-object or cross-region summaries as non-atomic unless the merged statement is itself the smallest checkable unit. For example, do not write one perception claim that says "on both planes" or "in both figures" when each plane or figure can be checked separately; instead emit one claim per plane or figure. Likewise, do not merge plane-local counts into a single total-count claim when the per-plane counts can be checked separately; emit plane-local count claims first, then a short total-count claim if needed.
    8. You may add the smallest possible bridge claims only when they are directly supported by the verified CoT plus the PTK foundation and are necessary to make a later claim verifiable. Treat such bridge claims as a local unpacking of the same reasoning step, not as a new reasoning route.
    9. When the final answer explicitly claims a property such as minimum, minimal, optimal, shortest, largest, or unique, add only the shortest grounded support chain needed to justify that property if it is directly grounded in the image/PTK foundation and consistent with the verified CoT.
    10. After the two main implicants or analogous terminal derivation claims are established, place the synthesis claim immediately or nearly immediately next. Only then add a very short local bridge for the final property claim if needed.
    11. For a post-synthesis minimality bridge, keep it short but complete. A typical acceptable pattern is: one claim that the selected X=0 group covers all 1-cells on the X=0 plane, one claim that the selected X=1 group covers all 1-cells on the X=1 plane, separate X=0 and X=1 across-plane non-extension claims only if needed, and one brief minimum-cover conclusion tied specifically to those groups.
    12. Keep post-synthesis bridge claims plane-local and group-local. Do not write one claim that summarizes coverage on both planes, and do not write one claim that says both groups cannot extend across X; split those into separate X=0 and X=1 claims.
    13. Do not mix plane-local counting facts with coverage facts in the same claim. For example, do not write one claim that says a plane has four 1-cells and that a selected group covers those four 1-cells; split count from coverage, or omit the count if it is unnecessary.
    14. In group-analysis steps, keep one variable fact per claim when those facts are independently checkable. For example, emit separate claims for `Q=0`, `S=1`, and `X=0`, and separate claims for `P varies` and `R varies`, before the implicant-extraction claim.
    15. If a grouping claim relies on wrap-around between the first and last row or column, make its dependencies explicitly include the relevant header-order claim or a narrow bridge claim establishing that those labels are the first and last positions on that plane.
    16. `depends_on` may reference only earlier claim IDs from this output sequence, such as `c1` or `c7`. Do not put `p_facts`, `t_facts`, or `k_atoms` identifiers such as `p3`, `t2`, or `k5` inside `depends_on`; mention those only in `evidence_hint` or encode their use as a `knowledge_call` claim that later claims can depend on.
    17. When a bridge claim is needed, place it immediately before the claim it justifies and keep it narrowly scoped. Do not add a separate optimization proof, alternative solution path, or summary chain that goes beyond what the CoT already states or directly implies.
    18. If the verified CoT solves by direct variable elimination or plane-local activation-pattern reading, keep that route. Do not rewrite it into a K-map grouping proof, wrap-around proof, maximality proof, or across-X non-extension proof unless those steps already appear explicitly in the verified CoT.
    19. For variable-elimination traces, prefer a route like: plane-local activation-pattern claim, split constant/varying variable-status claims, implicant claim, synthesis, and only the shortest local support for a final property word if needed.
    20. For post-synthesis minimum support on variable-elimination traces, prefer the shortest literal-conflict or plane-local necessity bridge over a long contradiction proof. For example, if one plane-local cover requires `X'` and another requires `X`, prefer the short conclusion that no single product term can cover both, then conclude that at least two terms are required. Do not expand this into a longer `constant-1`, global contradiction, or all-zero-cells proof unless the verified CoT explicitly uses that route.
    21. Output valid JSON only.

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
    3. `t_facts` must cover explicit givens, goals, constraints, and subquestions from the text, and each `fact_text` should stay as close as possible to verbatim wording from the question text rather than a paraphrase.
    4. `t_facts` must not include image-derived map layouts, cell values, diagram structure, circuit connectivity, geometric relations, or other visual observations unless the same content is explicitly written in the text.
    5. `k_atoms` must be reusable knowledge atoms, not solution-specific claims.
    6. `k_atoms` should be minimal: flag duplicate, near-duplicate, or heavily overlapping rules and ask for merge/pruning when needed.
    7. For K-map / Karnaugh-map problems, treat cross-plane adjacency as essential coverage when the map is split across variable planes. For a 5-variable K-map shown as two 4x4 maps, the foundation is incomplete unless it states that corresponding cells across the two planes are adjacent because they differ only in the split variable.
    8. Flag unsupported facts, missing essentials, duplicated content, over-specific knowledge, and `t_facts` that drift away from the original wording.
    9. Prefer revision-oriented feedback over hard blocking: if the foundation is broadly usable but too verbose, duplicated, or not minimal, give concrete trim/rewrite instructions so the polish step can fix it.
    10. When revision is needed, explicitly name which section(s) must change: `p_facts`, `t_facts`, and/or `k_atoms`.
    11. Use `pass=false` only when a real blocking issue remains (for example unsupported visual facts, materially missing text conditions/goals, or solution-specific knowledge that would corrupt downstream extraction). Do not fail solely because `t_facts` need trimming, deduplication, or more verbatim wording.
    12. If `pass=true`, set `critical_issues` to `[]` and set `revision_instructions` to `No changes needed.` exactly.
    13. Output valid JSON only.

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


PTK_P_FACTS_POLISH_SYSTEM_PROMPT = dedent(
    """
    ## ROLE
    You are a PTK P-Facts Patch Agent.

    ## TASK
    Revise only the `p_facts` section of the PTK foundation according to the critic feedback.

    ## RULES
    1. Revise only `p_facts`. Do not rewrite `t_facts` or `k_atoms`.
    2. Preserve valid items when possible.
    3. Add missing grounded visual facts and remove unsupported, duplicated, or interpretive items.
    4. `p_facts` must stay objective and image-grounded.
    5. Keep IDs stable when practical, but correctness is more important than ID continuity.
    6. Return a non-empty `p_facts` list.
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
      "revision_summary": "..."
    }
    """
).strip()


PTK_T_FACTS_POLISH_SYSTEM_PROMPT = dedent(
    """
    ## ROLE
    You are a PTK T-Facts Patch Agent.

    ## TASK
    Revise only the `t_facts` section of the PTK foundation according to the critic feedback.

    ## RULES
    1. Revise only `t_facts`. Do not rewrite `p_facts` or `k_atoms`.
    2. Preserve valid items when possible.
    3. `t_facts` must cover explicit givens, goals, constraints, and subquestions from the text.
    4. Preserve question wording verbatim whenever possible: copy exact clauses/spans from the problem text instead of paraphrasing them.
    5. If trimming is needed, prefer deleting extra wording or splitting clauses over inventing new prose.
    6. `t_facts` must stay text-explicit and must not absorb visual-only content.
    7. Keep IDs stable when practical, but correctness is more important than ID continuity.
    8. Return a non-empty `t_facts` list.
    9. Output valid JSON only.

    ## OUTPUT JSON
    {
      "t_facts": [
        {
          "t_id": "t1",
          "fact_text": "...",
          "fact_role": "given|goal|constraint|subquestion"
        }
      ],
      "revision_summary": "..."
    }
    """
).strip()


PTK_K_ATOMS_POLISH_SYSTEM_PROMPT = dedent(
    """
    ## ROLE
    You are a PTK K-Atoms Patch Agent.

    ## TASK
    Revise only the `k_atoms` section of the PTK foundation according to the critic feedback.

    ## RULES
    1. Revise only `k_atoms`. Do not rewrite `p_facts` or `t_facts`.
    2. Preserve valid items when possible.
    3. `k_atoms` must stay reusable and non-solution-specific.
    4. Merge, prune, or rewrite overlapping knowledge atoms when needed, but keep only the minimum reusable set.
    5. Keep IDs stable when practical, but correctness is more important than ID continuity.
    6. Return a non-empty `k_atoms` list.
    7. Output valid JSON only.

    ## OUTPUT JSON
    {
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


PTK_FOUNDATION_POLISH_SYSTEM_PROMPT = dedent(
    """
    ## ROLE
    You are a PTK Foundation Polish Agent.

    ## TASK
    Revise the current P/T/K foundation according to the critic feedback while keeping only necessary grounded facts.

    ## RULES
    1. Preserve valid items when possible.
    2. Add missing grounded facts and remove unsupported or duplicated items.
    3. When revising `t_facts`, preserve question wording verbatim whenever possible: copy exact clauses/spans from the problem text instead of paraphrasing them.
    4. If the critic asks for trimming, prefer deleting extra wording or splitting clauses over rewriting them into new prose.
    5. `p_facts` must stay objective and image-grounded.
    6. `t_facts` must stay text-explicit.
    7. `k_atoms` must stay reusable and non-solution-specific.
    8. Keep IDs stable when practical, but correctness is more important than ID continuity.
    9. Output valid JSON only.

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
    6. Treat a narrowly scoped bridge claim as order-consistent when it only unpacks support that is already explicit or directly implied by an adjacent CoT step and is inserted immediately before the claim it justifies. Do not treat that local unpacking as a reasoning-route change.
    7. For final-answer properties such as minimum, minimal, optimal, shortest, largest, or unique, prefer sufficient support over aggressive compression. Do not fail a claim sequence merely because it adds a short, grounded support chain immediately before the final answer to justify that property.
    8. Prefer the shortest adequate support chain. If synthesis of the derived terms is already available, do not require a long counting, lower-bound, or alternate optimality proof when a shorter local bridge is sufficient.
    9. Flag bridge claims when they are too coarse, drift into a new proof path, or extend beyond the support needed for the dependent claim.
    9. If a claim mixes multiple substeps that can be checked independently, require them to be split even when the CoT states them in one sentence.
    10. Also split cross-object summaries when each object can be checked separately. For example, a claim about headers "on both planes" should usually be two claims, one per plane.
    11. Also split synthesis from optimality. A claim that ORs selected implicants into an expression should be separate from a claim that the expression is minimal, unless the minimality statement is already fully supported and indivisible in context.
    12. Also split distinct failure modes of enlargement or invalidity. For example, "cannot enlarge by adding columns" and "cannot enlarge by adding rows" should usually be separate claims, followed by a short conclusion that no larger same-plane group exists.
    13. Also split plane-local counts from global counts. For example, "the X=0 plane has four 1-cells", "the X=1 plane has four 1-cells", and "therefore the full map has eight 1-cells" should usually be three claims.
    14. If a final answer includes a property word like "minimum", do not require that property to be supported by the synthesis claim alone; accept a short, adjacent support chain grounded in plane-local coverage and PTK rules.
    15. If the verified CoT goes from the final derived terms directly to the answer, expect synthesis to appear immediately or nearly immediately after those terms. Any additional minimality bridge should be very short and should sit between synthesis and the final-answer claim, not replace synthesis or delay it by a long proof block.
    16. For a post-synthesis minimality bridge, prefer a short local block rather than a long alternate proof. A typical acceptable pattern is: the selected X=0 group covers all 1-cells on X=0; the selected X=1 group covers all 1-cells on X=1; if still needed, add separate X=0 and X=1 non-extension claims; then add one brief minimum-cover conclusion grounded in the local support and `k5`.
    17. Also reject claims that mix plane-local counting with coverage in one statement when those facts are independently checkable.
    18. Also reject post-synthesis summary claims that merge both planes or both groups into one statement, such as one cross-plane coverage claim or one combined across-X non-extension claim.
    19. In group-analysis steps, also reject bundled variable-status claims when separate constant facts or varying facts can be checked independently. For example, `Q=0, S=1, X=0` should usually be three claims, and `P varies, R varies` should usually be two claims, before the implicant claim.
    20. If a grouping claim uses wrap-around adjacency between the first and last row or column, require it to depend on the relevant header-order claim or an explicit local bridge establishing that edge adjacency.
    21. When the verified CoT is a direct variable-elimination or plane-local activation-pattern route, reject repairs that drift into a grouping/maximality proof path. In that case, prefer bridge claims that restate the plane-local activation pattern, the constant/varying variable facts, and the shortest synthesis-adjacent support chain needed for any final property word.
    22. For variable-elimination traces, also reject post-synthesis minimum bridges that expand into a long `constant-1` contradiction, global zero-cell contradiction, or other multi-step alternate proof when a shorter plane-local necessity bridge is sufficient. Prefer a short pattern like: left-plane cover requires `X'`; right-plane cover requires `X`; therefore one term cannot cover both; therefore at least two terms are required.
    23. When a post-synthesis bridge needs zero-cell support for a non-extension claim, prefer to recreate or restate that zero support immediately before the bridge instead of depending on distant earlier claims.
    24. If it fails, provide concrete rewrite instructions.
    25. If `pass=true`, set `critical_issues` to `[]` and set `revision_instructions` to `No changes needed.` exactly.
    26. Output valid JSON only.

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
    1. Keep claims minimal but sufficient, but prioritize correctness and support completeness over brevity.
    2. Preserve the original reasoning order when correct; otherwise fix the order explicitly.
    3. Fix dependency fields explicitly.
    4. Remove unsupported claims and add missing bridge claims only when justified by the verified CoT and PTK foundation.
    5. When a compound claim contains independently checkable substeps, split it into smaller claims instead of rewriting it as one broad summary.
    6. Split cross-object summaries when each object can be checked separately; for example, replace "on both planes" with one claim for the X=0 plane and one claim for the X=1 plane.
    7. Split synthesis from minimality; for example, OR-ing the selected implicants into an expression should usually be a different claim from asserting that the expression is minimal.
    8. Split distinct enlargement-failure modes into separate claims; for example, failure by adding columns and failure by adding rows should usually be two claims before concluding that no larger same-plane group exists.
    9. Split plane-local counts from global counts; for example, count 1-cells on each plane first and only then derive the total count if it is needed.
    10. When the final answer claims a property like minimum or optimal, prefer adding the smallest grounded support chain for that property over leaving the final answer under-justified.
    11. After the final derived terms are available, move synthesis to immediately or nearly immediately before the final answer. If a minimality bridge is needed, keep it extremely short and place it between synthesis and the final answer rather than inserting a long proof block earlier.
    12. Keep a post-synthesis minimality bridge short and local. Prefer a pattern like: the selected X=0 group covers all 1-cells on X=0; the selected X=1 group covers all 1-cells on X=1; if still needed, add separate X=0 and X=1 non-extension claims; then add one brief minimum-cover conclusion.
    13. Keep post-synthesis bridge claims plane-local and group-local. Do not merge both planes into one coverage claim, and do not merge both groups into one across-X non-extension claim.
    14. Do not mix plane-local counting with coverage in one claim. Split those facts, or drop the count if it is not needed.
    15. In group-analysis steps, keep one variable-status fact per claim when possible. Split bundled constants like `Q=0, S=1, X=0` into separate claims, and split bundled varying facts like `P varies, R varies` into separate claims, before deriving the implicant.
    16. If a grouping claim uses wrap-around adjacency between the first and last row or column, make it depend on the relevant header-order claim or a local bridge proving that edge adjacency on that plane.
    17. When a bridge claim is needed, keep it as the smallest local unpacking that supports the next claim, place it immediately before that claim, and avoid introducing an alternative proof route. If a post-synthesis non-extension claim needs zero-cell support, recreate that support locally near the bridge instead of relying on distant earlier claims.
    18. If the verified CoT is a variable-elimination or plane-local activation-pattern trace, preserve that route during polishing. Do not rewrite it into a grouping, wrap-around, across-X non-extension, or maximality proof unless those steps are already explicit in the verified CoT.
    19. For variable-elimination traces, prefer a repair shape like: plane-local activation-pattern claim, split constant/varying variable-status claims, implicant claim, synthesis, and only the shortest local support for a final property word if needed.
    20. For post-synthesis minimum support on variable-elimination traces, prefer the shortest literal-conflict or plane-local necessity bridge over a long contradiction proof. For example, if one plane-local cover requires `X'` and another requires `X`, prefer the short conclusion that no single product term can cover both, then conclude that at least two terms are required. Do not expand this into a longer `constant-1`, global contradiction, or all-zero-cells proof unless the verified CoT explicitly uses that route.
    21. Keep claim types semantically correct.
    22. Output valid JSON only.

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
    10. Each `canonical_nodes` item must reference exactly one source `claim_id` from the provided claim list. Never return concatenated, merged, synthetic, or grouped IDs such as `c1|c2`, `m1:c1|m2:c1`, comma-joined IDs, or array-like encodings in the `claim_id` field.
    11. Output valid JSON only.

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
        Only include content explicitly written in the problem text itself.
        Do not copy image-derived structure, cell values, diagram layout, or other visual observations into `t_facts` unless the same content appears verbatim in the text.
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
        Keep them reusable, minimal, and non-redundant.
        Do not restate P facts or T facts as knowledge atoms.
        If this is a K-map / Karnaugh-map problem, include all adjacency rules required for valid grouping; for a 5-variable map split into two 4x4 planes, explicitly include inter-plane adjacency between corresponding cells.
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


def build_ptk_p_facts_polish_user_prompt(
    problem: Dict[str, Any],
    p_facts: Sequence[Dict[str, Any]],
    t_facts: Sequence[Dict[str, Any]],
    k_atoms: Sequence[Dict[str, Any]],
    revision_instructions: str,
) -> str:
    return dedent(
        f"""
        {_problem_header(problem)}

        Target Section:
        p_facts

        Current P Facts:
        {to_plain_text(list(p_facts))}

        Reference T Facts (do not rewrite):
        {to_plain_text(list(t_facts))}

        Reference K Atoms (do not rewrite):
        {to_plain_text(list(k_atoms))}

        Revision Instructions:
        {normalize_whitespace(revision_instructions)}

        Revise only `p_facts` and keep the rest of the PTK foundation unchanged.
        """
    ).strip()


def build_ptk_t_facts_polish_user_prompt(
    problem: Dict[str, Any],
    p_facts: Sequence[Dict[str, Any]],
    t_facts: Sequence[Dict[str, Any]],
    k_atoms: Sequence[Dict[str, Any]],
    revision_instructions: str,
) -> str:
    return dedent(
        f"""
        {_problem_header(problem)}

        Target Section:
        t_facts

        Reference P Facts (do not rewrite):
        {to_plain_text(list(p_facts))}

        Current T Facts:
        {to_plain_text(list(t_facts))}

        Reference K Atoms (do not rewrite):
        {to_plain_text(list(k_atoms))}

        Revision Instructions:
        {normalize_whitespace(revision_instructions)}

        Revise only `t_facts` and keep the rest of the PTK foundation unchanged.
        """
    ).strip()


def build_ptk_k_atoms_polish_user_prompt(
    problem: Dict[str, Any],
    p_facts: Sequence[Dict[str, Any]],
    t_facts: Sequence[Dict[str, Any]],
    k_atoms: Sequence[Dict[str, Any]],
    revision_instructions: str,
) -> str:
    return dedent(
        f"""
        {_problem_header(problem)}

        Target Section:
        k_atoms

        Reference P Facts (do not rewrite):
        {to_plain_text(list(p_facts))}

        Reference T Facts (do not rewrite):
        {to_plain_text(list(t_facts))}

        Current K Atoms:
        {to_plain_text(list(k_atoms))}

        Revision Instructions:
        {normalize_whitespace(revision_instructions)}

        Revise only `k_atoms` and keep the rest of the PTK foundation unchanged.
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

        For ordering judgments, allow narrowly scoped bridge claims only when they merely unpack support that is already explicit or directly implied by the verified trace and PTK foundation. Such bridge claims should appear immediately before the claim they justify.

        Treat any `depends_on` entry that references `p#`, `t#`, `k#`, or any identifier outside the claim sequence as invalid. Dependencies must point only to earlier claim IDs in the current claim list.

        Enforce fine atomicity: split cross-plane summaries when each plane can be checked separately, split expression synthesis from minimality when they are independently checkable, split enlargement failure by columns vs. rows, split plane-local counts from global counts, and split bundled variable-status facts into one fact per claim when they can be checked independently.

        If a grouping claim uses wrap-around adjacency between the first and last row or column, require it to depend on the corresponding header-order claim or a narrow bridge that establishes that edge adjacency.

        If the final answer contains a property word such as minimum or optimal, prefer a short grounded support chain immediately before the final answer over leaving that property unsupported.

        Keep synthesis near the end of the trace: once the final derived terms are available, synthesis should come immediately or nearly immediately next, and any minimality bridge should be a short local block placed between synthesis and the final answer.

        Treat a post-synthesis minimality bridge as acceptable when it stays local and specific: plane-local coverage claims, separate plane-local non-extension claims only if needed, and one brief minimum-cover conclusion. Reject claims that mix plane-local counting with coverage in a single statement when those facts can be checked separately, and reject summary claims that merge both planes or both groups into one post-synthesis bridge claim.

        Prefer any zero-cell support used by post-synthesis non-extension claims to appear locally near that bridge instead of being pulled from much earlier in the sequence.

        If the verified CoT uses direct variable elimination or plane-local activation-pattern reading, do not approve a repaired claim sequence that drifts into a grouping/maximality proof path. In that case, prefer plane-local activation-pattern claims, split constant/varying variable facts, implicant claims, synthesis, and only the shortest local support needed for a final property word such as `minimum`.

        For variable-elimination traces, also reject post-synthesis minimum bridges that expand into a long `constant-1` contradiction, global zero-cell contradiction, or other multi-step alternate proof when a shorter plane-local necessity bridge is sufficient. Prefer a short pattern like: left-plane cover requires `X'`; right-plane cover requires `X`; therefore one term cannot cover both; therefore at least two terms are required.

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

        Audit whether each listed claim is truly supported and dependency-consistent.
        Return judgments only for the claims listed in `Claims to Audit`.
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

        When revising, split independently checkable substeps into separate claims. If a bridge claim is necessary, keep it narrowly scoped and place it immediately before the claim it supports. Also split cross-plane summaries into one claim per plane when possible, keep expression synthesis separate from minimality, split enlargement failure by columns vs. rows, split plane-local counts from global counts, and split bundled variable-status facts into one fact per claim when they can be checked independently. If the final answer includes a property word such as minimum or optimal, add the smallest grounded support chain needed for that property rather than leaving it implicit. Keep synthesis immediately or nearly immediately before the final answer, followed only by a short local minimality bridge. For that post-synthesis bridge, keep coverage and across-X non-extension plane-local, add separate X=0 and X=1 non-extension claims only if they are truly needed, include one brief minimum-cover conclusion, and recreate any needed zero-cell support locally near that bridge. If a grouping claim uses wrap-around adjacency, make sure the dependencies explicitly include the relevant header-order support. In `depends_on`, keep only earlier claim IDs from the current output sequence; move any raw `p#`, `t#`, or `k#` references into `evidence_hint` or into explicit supporting claims. If the verified CoT is a variable-elimination or plane-local activation-pattern trace, preserve that route during revision and do not drift into grouping, wrap-around, across-X non-extension, or maximality proofs unless those steps are already explicit in the CoT. For such traces, prefer a repair shape like: plane-local activation-pattern claim, split constant/varying variable facts, implicant claim, synthesis, and only the shortest local support needed for a final property word. Prefer a short plane-local necessity bridge such as `left-plane cover requires X'`, `right-plane cover requires X`, `therefore one term cannot cover both`, `therefore at least two terms are required` over a longer `constant-1` contradiction or global zero-cell contradiction chain unless the CoT explicitly uses that longer route.

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

        Convert the trace into atomic claims. Split independently checkable substeps when needed, split cross-plane summaries into one claim per plane when possible, keep expression synthesis separate from minimality, split enlargement failure by columns vs. rows, split plane-local counts from global counts, split bundled variable-status facts into one fact per claim when they can be checked independently, and only insert bridge claims when they are the smallest local support needed for a later claim. If the final answer uses a property word such as minimum or optimal, include the smallest grounded support chain needed for that property. Keep synthesis immediately or nearly immediately before the final answer, followed only by a short local minimality bridge. For that post-synthesis bridge, keep coverage and across-X non-extension plane-local, add separate X=0 and X=1 non-extension claims only if they are truly needed, include one brief minimum-cover conclusion, and recreate any needed zero-cell support locally near that bridge. If a grouping claim uses wrap-around adjacency, make sure the dependencies explicitly include the relevant header-order support. In `depends_on`, reference only earlier claim IDs from this same output sequence; never put raw `p#`, `t#`, or `k#` identifiers there. If the verified CoT is a variable-elimination or plane-local activation-pattern trace, preserve that route: prefer plane-local activation-pattern claims, split constant/varying variable facts, derive the implicants directly, put synthesis immediately after them, and do not introduce grouping, wrap-around, across-X non-extension, or maximality proofs unless the CoT itself already uses that route. For post-synthesis minimum support on such traces, prefer a short plane-local necessity bridge such as `left-plane cover requires X'`, `right-plane cover requires X`, `therefore one term cannot cover both`, `therefore at least two terms are required` over a longer `constant-1` contradiction or global zero-cell contradiction chain unless the CoT explicitly uses that longer route.
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
        For `canonical_nodes`, each output item must point to exactly one existing input `claim_id`. Do not concatenate or group claim IDs into a synthetic value.
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

        Audit whether the listed reasoning nodes are correct and traceable.
        Return judgments only for the nodes listed in `Candidate R Nodes`.
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
