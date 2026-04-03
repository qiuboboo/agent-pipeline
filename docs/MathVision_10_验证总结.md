# MathVision 10 条验证总结

## 1. 运行概览

- 运行目录：`benchmarkallinone/outputs/mathvision_validation_10/run_f2f4cc8d3618cc6e`
- 数据集：MathVision
- 请求样本数：10
- 实际处理样本数：10
- 结果分布：`pass=6`，`review=4`，`reject=0`
- 改写策略分布：`keep_open=6`，`blank_open=4`

## 2. 整体结论

这 10 条样本的数据源、图像资产与清洗链路均已跑通。

从改写结果看：

- 原本已经接近开放题表达的样本，主要采用 `keep_open`，只做轻量规范化。
- 原本偏选择题表达的样本，主要采用 `blank_open`，改写成直接回答标签/答案的开放题。
- 进入 `review` 的 4 条并不是因为缺图或缺答案，而是视觉 grounding 仍偏弱，主要原因是：
  - `alignment_requires_review`
  - `missing_grounded_visual_path`

因此，这轮结果可以作为 **MathVision 可跑、可改写、可产出开放题** 的验证依据，但其中 `review` 样本仍建议人工复核。

## 3. 改写前后汇总

| source_problem_id | 策略 | 结果 | 改写前 | 改写后 | 图片名 |
| --- | --- | --- | --- | --- | --- |
| 1 | keep_open | review | Which number should be written in place of the question mark? `<image1>` | Which number should be written in place of the question mark? | `prob_562573f1741448047ddf9a5d_primary.png` |
| 2 | blank_open | pass | Which bike is most expensive? `<image1>` | Which bike is most expensive? `<image1>` | `prob_2ef5fecbeffcabb3a53c12ed_primary.png` |
| 3 | blank_open | pass | Which kite has the longest string? `<image1>` | Which kite has the longest string? `<image1>` | `prob_f02369237abcf94209081a56_primary.png` |
| 4 | keep_open | pass | How many different digits can you find in this picture? `<image1>` | How many different digits can you find in this picture? `<image1>` | `prob_4a8f5a264adc1d6d534c5550_primary.png` |
| 5 | keep_open | review | Which number do you have to write in the last daisy? `<image1>` | Which number do you have to write in the last daisy? | `prob_7e9b53fd1e9797e41cfb5247_primary.png` |
| 6 | blank_open | review | Misty the cat has five kittens ... In which picture can we see the kittens of Misty ...? `<image1>` | Which picture, labeled A to E, shows Misty's five kittens: two striped, one spotty, and the remaining ones completely white, with one kitten having ears of a different color? | `prob_2ade924e60e14f2fc742fbe0_primary.png` |
| 7 | keep_open | review | How many bricks are missing in the wall? `<image1>` | How many bricks are missing in the wall? | `prob_2829868b5411041402b3c9cf_primary.png` |
| 8 | keep_open | pass | The sums of the all the three numbers on each side of the triangle are equal. Two numbers happened to be stained with ink. How much is the sum of these two numbers? `<image1>` | The sums of all three numbers on each side of the triangle are equal. Two numbers are stained with ink. What is the sum of these two numbers? | `prob_f732438f47fa7b38775bb162_primary.png` |
| 9 | blank_open | pass | A squirrel is following the paths of labyrinth and collecting food for winter. Which stuff it will not be able to take? `<image1>` | In the labyrinth image, which labeled stuff will the squirrel not be able to take? Answer with the label. | `prob_3d78becf15a57caf11f3ca84_primary.png` |
| 10 | keep_open | pass | Four people can be seated at a square table. How many people at most could be seated if we pushed four tables of this kind together in one row? `<image1>` | Four people can be seated at a square table. How many people at most could be seated if we pushed four tables of this kind together in one row? | `prob_b5a65bdb6d9cd6b3e8ec12f9_primary.png` |

## 4. review 样本说明

以下 4 条进入 `review`：

- `source_problem_id=1`
- `source_problem_id=5`
- `source_problem_id=6`
- `source_problem_id=7`

它们的共同特点是：

- 图像依赖强
- 题面可理解，但视觉证据链不够稳
- 清洗后仍需要人工确认图像 grounding 是否充分

## 5. pass 样本说明

以下 6 条直接 `pass`：

- `source_problem_id=2`
- `source_problem_id=3`
- `source_problem_id=4`
- `source_problem_id=8`
- `source_problem_id=9`
- `source_problem_id=10`

这些样本的共同特点是：

- 改写后题意明确
- 图像与题面配合关系较清晰
- 答案形式较稳定，便于后续验证

## 6. 结论建议

MathVision 当前已经具备继续扩大样本规模的基础。

如果后续继续跑更大规模批次：

- `pass` 样本可直接进入后续链路
- `review` 样本建议单独汇总复核
- 优先关注强图像依赖但题面 grounding 偏弱的样本类型

## 7. 本次发现的问题

本次验证额外发现了一个需要后续修复的问题：**少量样本在 normalization 阶段没有成功采用 LLM 结果，而是回退到了 rule-based normalization。**

在本次 10 条验证样本中，已确认有 3 条属于这种情况：

- `source_problem_id=2`
- `source_problem_id=3`
- `source_problem_id=4`

这些样本在 `normalization_records.jsonl` 中表现为：

- `llm_used: false`
- `normalization_notes: ["rule_based_normalization"]`

其直接现象就是：题面中的 `<image1>` 没有被清掉，而是保留在改写后的问题文本里。

这说明问题不是整轮配置失效，也不是整个 MathVision 都没走 LLM；相反，其它大多数样本是正常走了 LLM normalization 的。当前更准确的判断是：**个别样本在 normalization 阶段没有拿到可用的 LLM 结构化结果，因此按代码逻辑回退到了 fallback 路径。**

后续处理建议：

- 将这类 `llm_used: false` 的样本单独汇总
- 针对这些样本做定向重跑，而不是整批重跑
- 重跑后重点检查 `<image1>` 是否被正常清理，以及 normalization 结果是否改为 `llm_used: true`
