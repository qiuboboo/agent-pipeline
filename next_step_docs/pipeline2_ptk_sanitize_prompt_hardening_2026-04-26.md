# pipeline2 PTK sanitize / prompt hardening (2026-04-26)

## Context

This patch is the qjb-compatible PTK quality hardening pass after comparing the local `qjb` line against the newer upstream `pipeline2` implementation.

The goal is not to port upstream client/fallback/router architecture. The goal is to keep the useful PTK quality behavior while reducing unnecessary qjb prompt token spend.

## What was inherited from newer upstream

- Split PTK foundation critique into:
  - text-only structure audit (`PTK_STRUCTURE_CRITIC_SYSTEM_PROMPT`);
  - image-backed visual grounding audit (`PTK_VISUAL_GROUNDING_CRITIC_SYSTEM_PROMPT`).
- Added upstream PTK normalization tolerance for common response shapes via `_coerce_object_list(...)`.
- Added deterministic text-fact recovery / sanitizer:
  - `_derive_text_facts_from_question(...)`;
  - `_sanitize_t_facts(...)`;
  - `_sanitize_ptk_foundation(...)`.
- Added heuristic PTK sanity reporting so missing explicit text facts, missing goal facts, empty visual facts, and missing reusable knowledge can be caught even when the LLM critic under-reports them.
- Adopted upstream compact, section-specific PTK polish prompts for `p_facts`, `t_facts`, and `k_atoms`.

## What qjb-specific prompt content was kept

Only the first-pass extraction prompts still keep the prior qjb additions:

- `PERCEPTION_EXTRACTION_SYSTEM_PROMPT` / `build_perception_user_prompt(...)` keep the low-token visual grounding checklist and topology/chart guidance.
- `TEXT_CONDITION_SYSTEM_PROMPT` / `build_text_condition_user_prompt(...)` keep stronger verbatim text-grounding rules.
- `KNOWLEDGE_LIBRARIAN_SYSTEM_PROMPT` / `build_knowledge_user_prompt(...)` keep the anti-duplication / non-restatement guidance and the K-map adjacency note.

These are paid once per problem, but they are short guardrails that target the observed failure buckets: diagram/topology `p_facts`, long text/chart `t_facts`, and modeling-heavy `k_atoms`.

## What qjb prompt content was removed

The older qjb full-foundation critic / polish prompt pair is no longer used. The new path uses upstream split critics and section-specific polish prompts.

The earlier qjb section-polish user prompts that included reference copies of other PTK sections were also dropped in favor of upstream compact prompts. That avoids paying extra tokens to send unchanged sections into every small repair call.

## Compatibility notes

- This patch intentionally does **not** add upstream `response_schema=...` calls because local qjb `ModelRouter.chat_json(...)` / `chat_json_with_images(...)` do not expose that interface.
- This patch intentionally does **not** add upstream `attach_image_requirement=...` because local qjb `_augment_prompt_with_ready_context(...)` does not expose that parameter.
- Image input is now limited to PTK visual critic and `p_facts` polish; text-only structure critic, `t_facts` polish, and `k_atoms` polish do not attach images.
