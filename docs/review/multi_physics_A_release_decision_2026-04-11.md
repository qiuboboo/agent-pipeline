# Multi-Physics review 放行方案决定（2026-04-11，A档）

## 当前执行结论

本次对 `multi_physics` 仅执行 **A档** post-ready manual release。

A档定义：

- exact `clean_decision_reason_codes == ["alignment_requires_review", "missing_grounded_visual_path"]`
- 不修改自动 gate
- 仅作为 post-ready waiver policy 执行
- 不纳入 `split_variant_needs_review`、`visual_evidence_uncertain`、`visual_grounding_uncertain` 等相邻复杂桶

## 本次执行范围

仅放行以下桶：

- `alignment_requires_review + missing_grounded_visual_path`

以下相邻桶本次仅保留观察，不执行：

- `alignment_requires_review + missing_grounded_visual_path + split_variant_needs_review`

## 说明

- 本文档用于记录 2026-04-11 当次 A档 执行口径。
- 若后续改为放开 `split_variant` 相邻桶或其他视觉不确定性桶，应另立文档，不覆盖本次 provenance。
