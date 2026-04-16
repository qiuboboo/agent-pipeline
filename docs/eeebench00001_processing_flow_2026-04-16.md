# eeebench00001 处理流程说明（2026-04-16）

本文只针对 `eeebench00001` 这一条样本，描述它在 `pipeline2` 中从输入到 `extract_claims` 的过程中，每一步“变成了什么样”。

## 1. ready 输入

输入样本来自：

- `tmp_pipeline2_new_ready_single/ready/circuit/eee_bench/samples/eeebench00001.json`

这一步的内容还是 ready 格式，主要包含：

- 题目文本
- 标准答案
- 图片信息
- 来源元数据

也就是说，此时它还是一个原始 ready sample，还没有变成 `pipeline2` 内部的 problem 结构。

## 2. 变成 pipeline2 的 problem

进入 `pipeline2 annotate` 后，这条 ready sample 被整理成内部 problem 对象。

在当前单样本运行里，它被标识为：

- `problem_id = prob_52fad96dad32a829290d6e8c`

到这一步，它已经不再只是 ready json，而是一个可以进入 method planning、CoT 生成、claim extraction 的标准 problem。

## 3. 变成多个 method draft

针对这个 problem，系统没有只给一种解法，而是生成了多个 method draft。

这题里最关键的是两个方法：

- `method_1`
- `method_2`

### method_1 变成了什么

`method_1` 被表述成一条标准 K-map 分组路线：

- 先看两个 `X` 平面
- 在每个平面中把 4 个 `1` 组成一个 `2x2` group
- 使用 Gray-code 邻接和 wrap-around
- 从 group 中保留不变变量
- 得到 `Q'SX'` 与 `QS'X`

也就是说，`method_1` 变成的是：

- 一条“先分组，再读常量 literal”的几何解法

### method_2 变成了什么

`method_2` 被表述成一条变量消去路线：

- 不先强调 grouping
- 直接看每个 plane 上 `1` 的分布模式
- 左 plane 中只要 `Q=0` 且 `S=1` 就激活，因此 `P`、`R` 被消去
- 右 plane 中只要 `Q=1` 且 `S=0` 就激活，因此 `P`、`R` 被消去
- 得到 `Q'SX'` 与 `QS'X`

也就是说，`method_2` 变成的是：

- 一条“先看 pattern，再消变量”的逻辑解法

## 4. 变成 verified CoT

接下来，每个 method draft 会生成自己的 CoT，并经过校验。

在这题上，`method_2` 的 verified CoT 本身是成立的，内容大致是：

- 左边 `X=0` 平面中，1 的分布对应 `Q=0`、`S=1`
- `P` 和 `R` 在这些位置中变化，因此被消去
- 所以左边得到 `Q'SX'`
- 右边 `X=1` 平面同理得到 `QS'X`
- 最终答案为 `Q'SX' + QS'X`

因此，到 verified CoT 这一步时，`method_2` 已经变成了一条“答案正确、主推理路线正确”的完整解法。

## 5. 变成 claim set 的目标形态

进入 `extract_claims` 后，系统不再满足于一整段 CoT，而是要把这条 CoT 拆成一组结构化 claim。

此时目标是把 `method_2` 变成：

- 一系列原子 claims
- 每条 claim 有自己的 `claim_id`
- 每条 claim 有自己的 `depends_on`
- 每条 claim 可以被单独检查、验证和追踪

也就是说，这一步要把“连续自然语言解法”变成“结构化可验证 claim 图”。

## 6. claim set 一开始变成了什么样

最初的问题是：`method_2` 在进入 claim extraction 后，没有老老实实保持 variable-elimination 这条路线，而是逐渐被改写成了另一种风格。

它开始变成：

- `grouping`
- `wrap-around`
- `maximality`
- `across-X non-extension`

这一版 claim set 的问题在于：

- method draft 说自己走的是 variable-elimination
- verified CoT 也确实是 variable-elimination
- 但抽出来的 claims 却越来越像 `method_1` 的 grouping 解法

所以这一步，`method_2` 实际上被“变形”成了另一条路。

## 7. route 收紧后，claim set 又变成了什么样

后来通过调整 `prompts.py`，系统被要求保留 verified CoT 原有路线，不要再漂去 grouping/wrap-around/maximality。

在这之后，claim set 的主干被拉回来了，开始更像：

- 左 plane 的激活 pattern
- 哪些变量恒定
- 哪些变量变化并被消去
- 得到 implicant
- 再合成为最终 SOP

也就是说，这一步之后，claim set 终于重新变成了一条更接近原始 `method_2` 的 variable-elimination 解法。

## 8. 后来又变成了“尾巴过长”的样子

虽然主干路线被拉回来了，但在 post-synthesis 的 `minimum` 支撑部分，claim set 又出现了另一种变形。

它开始把最后几步写得很长，例如：

- `conflicting literals`
- `forced omission`
- `reduce to 1`
- `0-cells contradiction`
- `one-term impossible`
- `minimum`

这一版的问题不是逻辑错，而是它把原本应该很短的尾部 bridge，写成了一条很长的全局反证链。

于是，这一步的 claim set 又变成了：

- 主干对了，但结尾说得太多、太绕、太不像原始 CoT 风格

## 9. 再收紧后，claim set 最新变成了什么样

在进一步限制 minimum tail 之后，最新的 claim set 已经不再主要卡在：

- route mismatch
- long tail bridge

最新状态下，它已经变成一套基本正确的 variable-elimination claim 序列，只剩最后几条 claim 的依赖接线还有问题。

也就是说，现在这套最新 claim set 已经：

- 主干路线基本正确
- 结尾长度基本收敛
- 剩下的是局部 dependency wiring bug

## 10. 最新具体问题：最后几条 claim 变成了“依赖没接好”

当前最后的核心问题集中在：

- `c22a`
- `c23a`
- `c22`
- `c23`

它们的问题不是文本主旨错，而是：

- 用到了 `X=0 plane` / `X=1 plane` 这样的前提
- 但 `depends_on` 没有正确连接到对应的 plane-label claims
- 有些地方还把左右 plane 的依赖接反了

所以在这一阶段，这个 problem 的 claim set 最终变成了：

- 一套大体正确、但最后几条 plane-label dependency 没接好的结构化 claims

## 11. 最后为什么 gate fail

`ClaimExtractionGate` 检查的不只是答案对不对，而是 claim set 是否：

- 原子化
- 路线一致
- 依赖自洽
- 支撑充分

当前 `method_2` 到最后一步时，已经从大问题收敛到小问题，但因为最后几条 claim 的 `depends_on` 仍有错误，所以它在 gate 看起来还是“不完全自洽”。

因此最终结果是：

- `failed claim validation after 3 rounds`

## 12. 一句话总结

`eeebench00001` 在 `pipeline2` 中的演化过程可以概括为：

- 从 ready sample 变成标准 problem
- 从 problem 变成多个 method draft
- 从 `method_2` 变成一条正确的 variable-elimination verified CoT
- 再从 verified CoT 变成结构化 claims 时发生路线漂移
- 收紧后又变成长尾 bridge
- 再收紧后只剩最后几条 plane-label claim 的 dependency 接线错误，最终卡在 `ClaimExtractionGate`
