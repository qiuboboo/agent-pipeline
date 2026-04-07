# mathvision 重复与疑似重复清单

- 生成时间：`2026-04-07T10:10:09Z`
- ready 包：`ready/mathvision/run_merged_mathvision_300_3040_dedup`
- dataset summary：`ready/mathvision/run_merged_mathvision_300_3040_dedup/datasets/mathvision/summary.json`

## 去重规则

- 不依赖 `source id`。
- 不直接用 `parent_problem_id` 判重。
- 先按 `problem_id` 去掉跨 run 重复。
- 再按标准化后的 `question + answer` 做严格内容去重。
- 高相似题只标记为疑似重复，不自动删除。

## 汇总

| 指标 | 值 |
| --- | --- |
| 输入样本数 | 919 |
| problem_id 去重后 | 919 |
| 严格内容去重后 | 918 |
| problem_id 删除数 | 0 |
| 严格内容重复删除数 | 1 |
| 疑似重复对数 | 0 |

## 严格重复：problem_id

无。

## 严格重复：标准化 question + answer

| 保留 problem_id | 保留样本 | 删除 problem_id | 删除样本 |
| --- | --- | --- | --- |
| prob_4c5dd5579cb671bea88d76e5 | outputs/mathvision_300_3040/run_053a22a217c324a7/datasets/mathvision/samples/prob_4c5dd5579cb671bea88d76e5.json | prob_90a5168cd21303ecc4cab579 | outputs/mathvision_300_3040/run_053a22a217c324a7/datasets/mathvision/samples/prob_90a5168cd21303ecc4cab579.json |

## 疑似重复

无。
