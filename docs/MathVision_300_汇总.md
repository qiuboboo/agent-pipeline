# MathVision 300 条批跑汇总

## 1. 最终采用的 300 条结果

本次 MathVision 300 条结果由 15 个 batch（每批 20 条）组成，最终采用的是：

- 原始正常 batch：11 个
- rerun 替换 batch：4 个
  - `120:140`：`run_afdb6335893911c2` 替换 `run_c8c10507151b37aa`
  - `240:260`：`run_d831179250f6cd08` 替换 `run_759b1ad3c48cd68b`
  - `260:280`：`run_260a70729ba0035f` 替换 `run_64a7ec4ab0f8048b`
  - `280:300`：`run_0cfa422f57d82040` 替换 `run_8d7f76eb286f9842`

合并后的机器可读汇总已写入：

- [merged_summary.json](../benchmarkallinone/outputs/mathvision_300_batches/merged_summary.json)

## 2. 合并后总结果

- 总样本数：`300`
- batch 数：`15`
- 每批样本数：`20`
- 最终决策分布：`pass=178`，`review=120`，`reject=2`

对应比例约为：

- `pass ≈ 59.3%`
- `review ≈ 40.0%`
- `reject ≈ 0.7%`

## 3. 本次修复结果

本次 rerun 的核心目标是修复部分 batch 中出现的 `llm_used: false` 问题。

原问题分布：

- `120:140`：`1` 条
- `240:260`：`10` 条
- `260:280`：`20` 条
- `280:300`：`20` 条

合计：`51` 条。

rerun 后结果：

- `120:140`：`llm_used: false = 0`
- `240:260`：`llm_used: false = 0`
- `260:280`：`llm_used: false = 0`
- `280:300`：`llm_used: false = 0`

结论：

**这次需要修复的 51 条 fallback 样本已经全部清零。**

这说明此前的异常更像是运行时不稳定 / 并发压力导致的结构化输出失败，而不是这些样本天然无法走 LLM normalization。

## 4. 质量观察

### 4.1 总体可用性

从 300 条整体结果看，MathVision 已经具备继续作为可批量处理数据集使用的基础：

- `pass` 样本占比接近 60%
- `review` 样本占比约 40%
- `reject` 只有 2 条

### 4.2 review 的含义

`review` 并不等于链路失败，而更多表示：

- 图像依赖较强
- grounding 路径仍需人工复核
- 改写虽已完成，但视觉证据链还不够稳

### 4.3 reject 的情况

最终 300 条中仍保留 `2` 条 `reject`：

- `120:140` 中 1 条
- `140:160` 中 1 条

这两条不是 fallback 问题，而更像是样本本身的质量 / grounding 判定问题，不能简单通过 rerun 消除。

## 5. LLM 使用概览

合并后 300 条结果的聚合 LLM 使用量为：

- `request_count = 2281`
- `successful_request_count = 2279`
- `failed_request_count = 17`
- `retry_count = 15`
- `prompt_tokens = 2,738,239`
- `completion_tokens = 994,852`
- `total_tokens = 3,733,091`
- `multimodal_request_count = 576`
- `total_request_seconds ≈ 28,500.622`

## 6. 结论

本次 MathVision 300 条批跑在替换 4 个异常 batch 后，可以作为当前有效结果集使用。

核心结论：

- 300 条已完成合并
- 4 个异常 batch 已用 rerun 结果替换
- 原来的 `51` 条 `llm_used: false` 已全部修复为 `0`
- 最终保留 `reject=2`，但它们不属于 fallback 问题

如果后续继续扩样，建议：

- 避免多个大 batch 同时并发打同一 API
- 优先串行或低并发跑强图像依赖 split
- 对 rerun 前后都进入 `review/reject` 的样本单独做质量复核
