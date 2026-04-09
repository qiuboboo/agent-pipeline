# MSEarth Open Ended 0000:0120 合并说明

## 说明

- 本次将本地已存在的 `msearth_open_ended` 相关运行结果合并为一个标准输出目录。
- 其中前 20 条来自 `msearth_open_ended_head20_ler_reasoning_chain`，后续结果来自 `msearth_open_ended_batched_ler_reasoning_chain`。
- 现有批次区间在命名上存在 overlap（如 `0054_0074`、`0060_0080`），但按实际 `problem_id` 检查未发现重复样本，因此本次合并未触发 problem-level 去重冲突。

## 合并输出位置

- `outputs/msearth_open_ended_merged_0000_0120_ler_reasoning_chain/run_merged_msearth_open_ended_0000_0120_ler_reasoning_chain`

## 合并范围

- `0000_0020` / `run_749a368c3fdbf798` / source=head20 / requested=20 / processed=20 / decisions={'pass': 6, 'review': 12, 'reject': 2}
- `0020_0040` / `run_99b551815613335b` / source=batched / requested=20 / processed=20 / decisions={'pass': 4, 'review': 14, 'reject': 2}
- `0040_0060` / `run_ecaf0fae59817726` / source=batched / requested=20 / processed=20 / decisions={'pass': 12, 'review': 7, 'reject': 1}
- `0054_0074` / `run_9b786dd3a5eef29d` / source=batched / requested=20 / processed=20 / decisions={'pass': 4, 'review': 14, 'reject': 2}
- `0060_0080` / `run_3972ebc08d211496` / source=batched / requested=20 / processed=20 / decisions={'pass': 13, 'review': 7, 'reject': 0}
- `0074_0094` / `run_8509b09137a4fa1c` / source=batched / requested=20 / processed=20 / decisions={'pass': 10, 'review': 10, 'reject': 0}
- `0080_0100` / `run_360f5123b08c94cc` / source=batched / requested=20 / processed=20 / decisions={'pass': 11, 'review': 6, 'reject': 3}
- `0094_0114` / `run_41433c1c6f21f190` / source=batched / requested=20 / processed=20 / decisions={'pass': 9, 'review': 9, 'reject': 2}
- `0100_0120` / `run_0a2eafb3c8416ef5` / source=batched / requested=20 / processed=20 / decisions={'pass': 15, 'review': 5, 'reject': 0}

## 汇总结果

- 合并样本数：**180**
- requested_samples（按各批次求和）：**180**
- processed_samples（按唯一样本计）：**180**
- pass：**84**
- review：**84**
- reject：**12**
- 总耗时（按批次 elapsed_seconds 求和）：**12385.020s**（约 **3.44 小时**）
- 开始时间（最早批次）：`2026-03-31T01:20:31Z`
- 结束时间（最晚批次）：`2026-03-31T13:06:22Z`

- llm_usage.request_count: **1260**
- llm_usage.successful_request_count: **727**
- llm_usage.failed_request_count: **1607**
- llm_usage.retry_count: **1074**
- llm_usage.text_request_count: **918**
- llm_usage.multimodal_request_count: **342**
- llm_usage.prompt_tokens: **1049213**
- llm_usage.completion_tokens: **390311**
- llm_usage.total_tokens: **1439524**

## 发现的问题

### 1. batched 目录命名存在区间 overlap
- 例如 `0054_0074`、`0060_0080`、`0074_0094`、`0094_0114`。
- 本次通过实际 `problem_id` 检查，未发现重复样本，因此没有产生内容级冲突。
- 但后续如果继续追加批次，建议统一切片口径，避免目录名误导。

### 2. from20_to300 总目录当前不可直接用作正式合并源
- `outputs/msearth_open_ended_from20_to300_ler_reasoning_chain/run_44ab199af997173e` 目前缺少有效 `summary.json`，因此未纳入正式合并。

## 格式符合性说明

- 已保留并合并：
  - `datasets/msearth_open_ended/samples/*.json`
  - `datasets/msearth_open_ended/records/*.jsonl`
  - `datasets/msearth_open_ended/summary.json`
  - 顶层 `summary.json`
- 顶层 `records/` 目录按现有仓库运行产物格式保留为空目录。
