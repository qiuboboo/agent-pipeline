# eee_bench 重复与疑似重复清单

- 生成时间：`2026-04-07T10:10:05Z`
- ready 包：`ready/eee_bench/run_merged_eee_bench_1000_2860_dedup`
- dataset summary：`ready/eee_bench/run_merged_eee_bench_1000_2860_dedup/datasets/eee_bench/summary.json`

## 去重规则

- 不依赖 `source id`。
- 不直接用 `parent_problem_id` 判重。
- 先按 `problem_id` 去掉跨 run 重复。
- 再按标准化后的 `question + answer` 做严格内容去重。
- 高相似题只标记为疑似重复，不自动删除。

## 汇总

| 指标 | 值 |
| --- | --- |
| 输入样本数 | 956 |
| problem_id 去重后 | 956 |
| 严格内容去重后 | 956 |
| problem_id 删除数 | 0 |
| 严格内容重复删除数 | 0 |
| 疑似重复对数 | 2 |

## 严格重复：problem_id

无。

## 严格重复：标准化 question + answer

无。

## 疑似重复

| 左 problem_id | 右 problem_id | 问题相似度 | 左样本 | 右样本 |
| --- | --- | --- | --- | --- |
| prob_350b4202e59ce721a2949a47 | prob_9ff075df188a754f561a4a68 | 0.994819 | outputs/eee_bench_1000_2860/run_9ab7b7c008590714/datasets/eee_bench/samples/prob_350b4202e59ce721a2949a47.json | outputs/eee_bench_1000_2860/run_9ab7b7c008590714/datasets/eee_bench/samples/prob_9ff075df188a754f561a4a68.json |
| prob_1b27c8acf27f87809a0c1b33 | prob_34d1bd37d1a8479c2007d427 | 0.973568 | outputs/eee_bench_1000_2860/run_9ab7b7c008590714/datasets/eee_bench/samples/prob_1b27c8acf27f87809a0c1b33.json | outputs/eee_bench_1000_2860/run_9ab7b7c008590714/datasets/eee_bench/samples/prob_34d1bd37d1a8479c2007d427.json |
