# pipeline2 eeebench00001 问题汇报（2026-04-16）

## 1. 背景

当前主线目标是跑通 `pipeline2 annotate` 的单样本正式流程，并定位/修复 `eeebench00001` 在 claim extraction 阶段的失败。

本轮关注的样本与方法为：

- dataset sample: `eeebench00001`
- problem id: `prob_52fad96dad32a829290d6e8c`
- failing method: `method_2`

正式流程中的典型失败报错为：

- `ClaimExtractionGate`
- `failed claim validation after 3 rounds`
- `Problem \`prob_52fad96dad32a829290d6e8c\` has no qualified methods; cannot continue to node extraction.`

## 2. 现象概述

`method_2` 在 verified CoT 层面并不是无效解法，但进入 `extract_claims -> ClaimExtractionGate` 后，生成出的 claim set 多轮修补后仍无法通过 validation，导致该方法被 gate 掉，进而使整题在 extraction 阶段失败。

问题并非随机波动，而是稳定可复现：

- 正式全流程重跑失败
- `method_2` 单独 claim probe 同样失败
- 多轮 prompt 调整后，失败形态发生收敛，但尚未完全通过

## 3. 根因分解

### 3.1 method_2 的正式版与旧 probe 通过版不是同一条路线

已确认昨晚 probe 通过的 `method_2` 与今天正式流程中的 `method_2` 不是同一版本。

- 旧 probe 通过版更接近：`read every 1-cell as a minterm, then factor`
- 正式流程版更接近：`variable-elimination pattern`

因此，“之前通过、现在失败”并不是随机性问题，而是 method draft 本身已经切换到另一条推理路径。

### 3.2 claim extraction 过程中出现 proof-route drift

正式版 `method_2` 的 verified CoT 主干其实是：

- `plane-local`
- `activation-pattern`
- `variable-elimination`

但在 extraction / revise / polish 过程中，claim 常被改写成另一类证明路线，例如：

- `grouping`
- `wrap-around`
- `across-X non-extension`
- `maximality`

这会导致 critic 认为：claim sequence 与 verified CoT 的原始 reasoning route 不一致，从而判定 claim set fail。

### 3.3 主干修正后，minimum 尾部 bridge 仍然过长

在 proof-route drift 被部分抑制后，新的主要问题变成：

- post-synthesis 的 `minimum` 支撑链过长
- 证明方式过于全局、过于绕
- 与 verified CoT 的局部 plane-based 证明风格不贴合

典型的长反证链包括：

- `conflicting literals`
- `forced omission`
- `reduce to 1`
- `0-cells contradiction`
- `constant-1 contradiction`
- `one-term impossible`

这条链并非逻辑错误，但它容易被 critic 视为“后缀桥太长、证明过度、偏离原 CoT 风格”。

### 3.4 最新残留问题已收敛到 dependency wiring bug

在主干 route 和 minimum tail 都收紧后，最新 probe 暴露的问题已进一步收敛为局部依赖接线错误。

核心表现：

- `c22a` / `c23a` 提到了 `X=1 plane` / `X=0 plane`
- 但没有依赖正确的 plane-label claim
- `c22` / `c23` 对 `c9` 和 `c19` 的依赖接反

因此，当前失败更像是最后几条 claim 的 `depends_on` wiring 错误，而不是主逻辑结构错误。

## 4. 已完成的修正

本轮已在 `agent-pipeline/src/benchmarkallinone/pipeline2/prompts.py` 做过两类关键修正。

### 4.1 强制 preserve verified CoT 的 variable-elimination route

已补入规则：如果 verified CoT 是 direct variable-elimination / plane-local activation-pattern route，则 extraction / revise / polish 必须保留该路线，不得无依据地改写为：

- `grouping`
- `wrap-around`
- `maximality`
- `across-X non-extension`

### 4.2 收紧 post-synthesis minimum bridge

已补入规则：对于这条 CoT，不应再偏好 `constant-1 contradiction` 一类长反证链，而应使用更短、更局部的尾部桥：

- 左 plane 覆盖需要 `X'`
- 右 plane 覆盖需要 `X`
- 单个 product term 不可能同时带 `X'` 和 `X`
- 因而单 term 不可能同时覆盖左右两边
- 所以至少需要两个 terms
- 再收束到 `minimum`

## 5. 当前状态判断

截至目前，问题已经从“大范围 reasoning route mismatch”收敛到“最后几条 claim 的 plane-label dependency 错接”。

这说明：

- 主干 variable-elimination route 基本已经拉回正轨
- minimum tail 过长的问题已经明显缓解
- 剩余故障更像最后一处接线 bug，而不是整体方案错误

## 6. 当前最关键的剩余卡点

当前最值得继续处理的是：

- 修正 `c22a` / `c23a` 对 plane-label claim 的依赖
- 修正 `c22` / `c23` 中 `c9` 与 `c19` 的反接问题
- 避免后续 repair 再次把正确的 plane-local 证明路线拉回全局反证或 grouping 风格

## 7. 建议的下一步

建议继续按以下顺序推进：

1. 优先修 plane-label dependency wiring 问题
2. 重跑 `method_2` 单独 claim probe
3. 若 probe 通过，再重跑 `tmp_run_pipeline2_new_ready_single.py` 的正式单样本 annotate 流程
4. 再确认 `ClaimExtractionGate` 是否解除，以及后续 bundle / finalize 是否能继续推进

## 8. 涉及的关键文件

- `agent-pipeline/src/benchmarkallinone/pipeline2/prompts.py`
- `agent-pipeline/tmp_probe_claim_new_ready_single.py`
- `agent-pipeline/tmp_run_pipeline2_new_ready_single.py`
- `agent-pipeline/pipeline2/outputs_new_ready_single/claim_probe_prob_52fad96dad32a829290d6e8c_method_2.json`
- `agent-pipeline/pipeline2/outputs_new_ready_single/annotation_runtime/method_runs/debug_new_ready_eeebench00001/prob_52fad96dad32a829290d6e8c/method_2.json`

## 9. 一句话结论

`eeebench00001` 当前卡在 `method_2` 的 claim extraction：最初是 reasoning route 漂移，之后是 minimum 尾桥过长，而最新状态已收敛到最后几条 plane-label claim 的 dependency 接线错误。