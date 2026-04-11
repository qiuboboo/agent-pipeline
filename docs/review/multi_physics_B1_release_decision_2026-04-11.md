# Multi-Physics review 放行方案决定（2026-04-11，B1档）

## 当前执行结论

本次对 `multi_physics` 继续执行 **B1档** post-ready manual release。

B1档定义：

- exact `clean_decision_reason_codes == ["alignment_requires_review", "missing_grounded_visual_path", "split_variant_needs_review"]`
- 且 `quality_risk_flags == []`
- 不修改自动 gate
- 仅作为 post-ready waiver policy 执行
- 不纳入 `low_resolution`、`visual_evidence_weak`、`small_image`、`metadata.choice_field is null` 等带额外风险标记样本

## 本次执行范围

仅放行以下桶：

- `alignment_requires_review + missing_grounded_visual_path + split_variant_needs_review`
- 且无额外 `quality_risk_flags`

以下相邻桶本次仅保留观察，不执行：

- 同 reason-code 组合下仍带有额外 `quality_risk_flags` 的样本

## 说明

- 本文档用于记录 2026-04-11 当次 B1档 执行口径。
- 若后续改为放开低清晰度、弱视觉证据、缺选项文本等相邻风险桶，应另立文档，不覆盖本次 provenance。
