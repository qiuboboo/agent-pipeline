# Review Release Template

用于把某个数据集的 **post-ready review 放行** 流程做成可复用模板。

## 原则

1. **先构建 canonical ready**
   - `outputs -> merge/dedup -> ready`
   - 这一步只做数据构建、去重、校验。
   - 默认不在 build 阶段把 `review` 改成 `pass`。

2. **再做候选导出**
   - 从 canonical ready 中按明确规则导出候选 bucket。
   - 候选文档只是候选，不等于已经放行。

3. **用户确认后再做 manual override**
   - 把已批准 bucket 从 `review` 改成 `pass`。
   - 必须保留 provenance，明确这是一轮 post-ready waiver / release policy。

4. **回写后刷新验证**
   - 更新 `summary.json` 的 `status_counts` 和 `write_validation`。
   - 要求 `selection_validation.ok = true` 且 `write_validation.ok = true`。

## 推荐最小回写位点

对每个被放行样本，至少同步更新：

- `problem_main_record`
  - `current_status = clean_passed`
  - `clean_decision = pass`
  - `clean_decision_reason_codes = [...]`
  - `clean_decision_rationale = ...`
  - `annotation_ready = true`
  - `qa_precheck_ready = true`
  - `release_reserved.manual_release_decision = {...}`

- `clean_problem_record`
  - `clean_decision = pass`
  - `decision_reason_codes = [...]`

- `clean_pool_entries[0]`
  - `pool_status = ready_for_annotation`
  - `clean_decision = pass`
  - `review_required = false`
  - `manual_override = {...}`

- `cleaning_records[-1]`
  - `decision = pass`
  - `decision_reason_codes = [...]`
  - `decision_rationale = ...`
  - `operator_type = manual_override`
  - `finished_at = <approved_at>`
  - `manual_override = {...}`

## Provenance object 建议字段

```json
{
  "approved_at": "2026-04-09T10:00:00Z",
  "policy_doc": "docs/review/<dataset>_review_release_candidates_YYYY-MM-DD.md",
  "approved_via": "user_confirmed_chat_policy",
  "original_clean_decision": "review",
  "original_decision_reason_codes": ["alignment_requires_review"],
  "release_bucket": "A",
  "release_basis": "..."
}
```

## 推荐分层口径

- **build-stage policy**：只负责 canonical ready 构建
- **post-ready release policy**：负责 bucket 放行 / waiver

不要把这两层混在一起，否则 provenance 和审计边界会变脏。

## 典型流程

1. 构建 canonical ready
2. 统计 review 原因分布
3. 导出候选 bucket（ledger/json）
4. 用户确认 bucket
5. 执行 manual release 写回
6. 刷新 summary / validation
7. 提交 commit
