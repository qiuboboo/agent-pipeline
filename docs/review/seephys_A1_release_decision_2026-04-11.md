# SeePhys review 放行方案决定（2026-04-11，A1档）

## 当前执行结论

本轮先完成 `seephys` **A1档候选审查与 provenance 建档**，尚未执行 manual release 写回。

A1档定义：

- 来源范围：`alignment_requires_review` 的 9 条样本
- 进一步限定为：仅纳入其中 **高置信度 metadata / image-reference misfire 子集**
- 本次采用 **candidate-json 手工子集**，不将该口径直接写入统一 policy config
- 不修改自动 gate
- 仅作为后续可能执行的 post-ready waiver policy 预备文档

## 本次审查范围

本次拟纳入 A1 候选的 5 条样本为：

- `prob_ed70836971fe6a4d95fd6fe1` / source `95`
- `prob_f507ee59c5cd02ece288ae97` / source `198`
- `prob_d126c8b2b5654b762edcf9f6` / source `248`
- `prob_ee96a4b7c08cafe5a4d0c742` / source `12`
- `prob_cb06ae7fc6ad04249fbea340` / source `200`

这些样本的共同特征是：

- 原始 review 信号都落在 `alignment_requires_review` 相邻区域；
- 图像资产实际存在，且文本题面已提供大部分甚至全部关键语义；
- 当前 review 更像 metadata / image-reference 记录偏差，而不像纯视觉缺失样本。

## 相邻观察样本

以下 1 条暂列相邻观察，不并入 A1 首桶：

- `prob_42a98da9e442b03ead20a6e3` / source `66`

原因：题面大体可恢复，但仍带有一定图示语义依赖，保守起见本次不混入首桶。

## 本次继续 hold 的 3 条

以下样本继续视为真视觉依赖风险，本次不纳入：

- `prob_2d7ca75d35bc56e3c74cf846` / source `64`
- `prob_9c67d428639e52917a3a0cd9` / source `74`
- `prob_e4e2d4bf30ef874bea44e29a` / source `242`

## 说明

- 本文档只记录 **2026-04-11 当次 A1 候选审查口径**。
- 当前状态是：**候选已导出，decision doc 已建档，但 manual release 尚未执行**。
- 若后续决定正式放行，应另写 ledger 并执行 `apply_manual_review_release.py`，保留完整 provenance，不覆盖本次文档。
