# PhysReason review 放行方案决定（2026-04-11，B1档）

## 当前执行结论

本次对 `physreason` 执行 **B1档** post-ready manual release。

B1档定义：

- 基础 reason-code：exact `clean_decision_reason_codes == ["alignment_requires_review", "metadata_inconsistency"]`
- 进一步限定为：仅纳入 coarse bucket = `metadata_path_only`
- 不修改自动 gate
- 仅作为 post-ready waiver policy 执行
- 不纳入带 complexity / multi-part / visual-density 标签的相邻样本

## 本次执行范围

仅放行以下桶：

- `alignment_requires_review + metadata_inconsistency`
- 且 `quality_risk_flags` 粗分层结果为 `metadata_path_only`

以下相邻桶本次仅保留观察，不执行：

- `alignment_requires_review + metadata_inconsistency + complexity-like flags`
- `alignment_requires_review + metadata_inconsistency + visual-like flags`

## 说明

- 本文档用于记录 2026-04-11 当次 B1档 执行口径。
- 若后续改为放开 complexity 相邻桶或其他分层策略，应另立文档，不覆盖本次 provenance。
