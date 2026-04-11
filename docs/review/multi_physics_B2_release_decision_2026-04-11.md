# Multi-Physics review 放行方案决定（2026-04-11，B2档）

## 当前执行结论

本次对 `multi_physics` 继续执行 **B2档** post-ready manual release。

B2档定义：

- exact `clean_decision_reason_codes == ["alignment_requires_review", "missing_grounded_visual_path", "split_variant_needs_review"]`
- 且 `quality_risk_flags == ["low_resolution"]`
- 不修改自动 gate
- 仅作为 post-ready waiver policy 执行
- 不纳入 `visual_evidence_weak`、`small_image`、`metadata.choice_field is null`、缺选项文本等更高不确定性风险样本

## 本次执行范围

仅放行以下桶：

- `alignment_requires_review + missing_grounded_visual_path + split_variant_needs_review`
- 且唯一额外风险标记为 `low_resolution`

以下相邻桶本次仅保留观察，不执行：

- 同 reason-code 组合下带 `visual_evidence_weak`、`small_image`、缺选项文本、metadata 不足等其他风险标记的样本

## 说明

- 本文档用于记录 2026-04-11 当次 B2档 执行口径。
- 若后续改为继续放开其它风险标记桶，应另立文档，不覆盖本次 provenance。
