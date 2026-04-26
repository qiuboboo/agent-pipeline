# pipeline2 prompt differences retained in qjb (2026-04-26)

## Scope

This note records the remaining prompt differences between local `agent-pipeline` branch `qjb` and the newer upstream-style checkout at `/root/.openclaw/workspace/pipeline2` after commit `e58db85bf Harden pipeline2 PTK sanitize prompts`.

The intent is searchability: future work can decide whether to keep or remove the remaining qjb prompt guardrails without redoing the comparison.

## Already inherited from upstream

The expensive / repair-loop PTK prompt path is now upstream-aligned:

- `PTK_STRUCTURE_CRITIC_SYSTEM_PROMPT`
- `PTK_VISUAL_GROUNDING_CRITIC_SYSTEM_PROMPT`
- `PTK_P_FACTS_POLISH_SYSTEM_PROMPT`
- `PTK_T_FACTS_POLISH_SYSTEM_PROMPT`
- `PTK_K_ATOMS_POLISH_SYSTEM_PROMPT`
- `build_ptk_structure_critic_user_prompt(...)`
- `build_ptk_visual_grounding_critic_user_prompt(...)`
- `build_ptk_p_facts_polish_user_prompt(...)`
- `build_ptk_t_facts_polish_user_prompt(...)`
- `build_ptk_k_atoms_polish_user_prompt(...)`

The older qjb full-foundation critic / polish prompts and helpers were removed because they were unused after split-critic migration and carried maintenance/token cost:

- `PTK_FOUNDATION_CRITIC_SYSTEM_PROMPT`
- `PTK_FOUNDATION_POLISH_SYSTEM_PROMPT`
- `build_ptk_foundation_critic_user_prompt(...)`
- `build_ptk_foundation_polish_user_prompt(...)`

The earlier qjb section-polish user-prompt shape that sent other PTK sections as reference into every small repair call was also removed. `_polish_ptk_section(...)` now sends only the target section and `revision_instructions`; images are attached only for `p_facts` repair.

## Remaining qjb prompt differences

Only first-pass extraction prompts retain qjb-specific guardrails:

### 1. `PERCEPTION_EXTRACTION_SYSTEM_PROMPT` / `build_perception_user_prompt(...)`

**Difference:** local qjb is longer than upstream and includes visual grounding checklist / topology-chart guidance.

**Reason kept:** observed PTK failures clustered heavily in diagram/topology-heavy datasets where `p_facts` had weak grounding fidelity. This first-pass prompt is paid once per problem, but it targets the most common failure bucket directly.

**Current judgment:** keep for now unless a small smoke comparison shows upstream-only perception has equal or better `p_facts` quality.

### 2. `TEXT_CONDITION_SYSTEM_PROMPT` / `build_text_condition_user_prompt(...)`

**Difference:** local qjb keeps stronger verbatim text-grounding rules and hints around explicit textual givens/goals.

**Reason kept:** long Chinese text and chart-heavy datasets showed `t_facts` coverage / faithfulness failures. The retained guardrail is comparatively small and helps enforce that `t_facts` come from question text rather than visual interpretation or solution reasoning.

**Current judgment:** keep for now; lower priority to trim than `KNOWLEDGE`.

### 3. `KNOWLEDGE_LIBRARIAN_SYSTEM_PROMPT` / `build_knowledge_user_prompt(...)`

**Difference:** local qjb keeps anti-duplication / non-restatement guidance and a K-map adjacency note.

**Reason kept:** modeling-heavy datasets showed weak `k_atoms`, often because extracted knowledge became too solution-specific or duplicated problem givens.

**Current judgment:** weakest retained difference. If reducing token cost further, trim or revert this first and compare small smoke results.

## Compatibility boundary

Do not blindly copy newer upstream prompt call signatures into qjb until client/router compatibility is addressed:

- qjb `ModelRouter.chat_json(...)` / `chat_json_with_images(...)` do not expose upstream `response_schema=...`.
- qjb `_augment_prompt_with_ready_context(problem, base_prompt, component_name)` does not expose upstream `attach_image_requirement=...`.
- qjb keeps local cache/progress/salvage behavior, so orchestration shape in `annotation_modules.py` intentionally differs from upstream even where prompt text is aligned.

## Recommended next experiment

If the goal is strict upstream prompt inheritance, revert these six symbols next:

- `PERCEPTION_EXTRACTION_SYSTEM_PROMPT`
- `TEXT_CONDITION_SYSTEM_PROMPT`
- `KNOWLEDGE_LIBRARIAN_SYSTEM_PROMPT`
- `build_perception_user_prompt(...)`
- `build_text_condition_user_prompt(...)`
- `build_knowledge_user_prompt(...)`

Recommended selective path: revert `KNOWLEDGE` first, keep `PERCEPTION` + `TEXT_CONDITION`, then run a small smoke comparison within the current <=20-sample rule.
