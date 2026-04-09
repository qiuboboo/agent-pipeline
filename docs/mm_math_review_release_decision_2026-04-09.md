# MM-Math review 放行方案决定（2026-04-09）

## 背景

针对 `mm_math` 当前 merged ready 包中的 `review` 样本，之前已经明确：

- **不建议把全部 229 条 review 直接放行**；
- 风险主体虽然集中在 `alignment_requires_review`，但混有真实风险项；
- 需要采用**分层放行**，而不是全量通过。

在这次讨论中，用户最终选择采用 **方案 B（稍激进）**。

---

## 方案对比

### 方案 A（保守）

只纳入低风险候选：

- 主要是**纯 `alignment_requires_review`**；
- 不带额外视觉风险、答案风险、图文不一致信号；
- 候选规模约 **51 条**。

### 方案 B（本次采纳）

在方案 A 的基础上，**再额外纳入“只有 `metadata_inconsistency`、但没有额外视觉/答案坏信号”的样本**。

也就是说，方案 B 的目标候选池包括：

1. 纯 `alignment_requires_review` 的低风险样本；
2. `alignment_requires_review + metadata_inconsistency`，且**没有**额外视觉/答案层面坏信号的样本。

按当前统计，这样可把候选规模扩到约 **74 条**。

---

## 当前采纳结论

`mm_math` 的 review 放行策略，当前正式采用：

> **方案 B：稍激进一点。**  
> 在保留纯 `alignment_requires_review` 低风险样本的基础上，额外接受“只有 `metadata_inconsistency`、但没有额外视觉/答案坏信号”的样本，候选规模约 74 条。

---

## 明确不纳入的风险类型

即使采用方案 B，以下类型仍**不应直接纳入放行候选**：

- `visual_evidence_uncertain`
- `small_image`
- `image_reference_mismatch`
- `metadata_image_path_mismatch`
- 明显图文不一致 / diagram mismatch
- 答案冲突、答案目标不匹配、答案解释明显异常
- 其他内容层面的真实坏信号

换言之，**方案 B 不是放宽到“review 大部分都过”**，而只是把“纯 metadata inconsistency、且无其他坏信号”的一层纳入。

---

## 执行建议

即使已经采纳方案 B，执行时仍建议：

1. 先导出约 **74 条候选清单**；
2. 在候选集中做 **不超过 20 条 spot check**；
3. 若 spot check 稳定，再批量放行该候选池。

这样可以保持策略上稍激进，但执行上仍然可控。

---

## 与当前仓库状态的关系

本决策文档记录的是 **`mm_math` review 放行口径**，用于后续 merged ready 包处理与 review 样本筛选。

它本身**不等于已经执行放行**，而是后续实施时应遵循的决策基线。
