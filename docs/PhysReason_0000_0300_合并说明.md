# PhysReason_0000_0300_合并说明

## 最终结论

PhysReason `0:300` 已完成主批跑与异常区间补跑，最终可用合并结果位于：

- `outputs/physreason_merged_0000_0300/run_merged_physreason_0000_0300`

该 merged 结果已经作为最终采用版本提交到仓库。

---

## 背景

PhysReason 主批跑按 `step=20` 执行，共覆盖 `0:300`。

主输出根目录：

- `outputs/physreason_batched_eval`

在运行过程中，`0180:0260` 区间曾出现批次级异常：上游模型服务返回 `HTTP 502 Bad Gateway`，导致该区间历史结果出现 fallback 风险，因此不适合直接作为最终 merge 来源。

异常说明见：

- `docs/PhysReason_fallback批次异常说明.md`

---

## 异常区间

历史异常区间为：

- `0180_0200`
- `0200_0220`
- `0220_0240`
- `0240_0260`

这些批次在历史主跑中曾出现：

- `successful_request_count = 0`
- `failed_request_count = 360`
- `retry_count = 240`
- `last_error = HTTP 502 Bad Gateway`

因此最终口径中不采用这些历史异常批次，而是采用后续 rerun 成功结果。

---

## 补跑情况

对 `0180:0260` 执行了按 20 一批的补跑。

补跑输出根目录：

- `outputs/physreason_batched_eval_rerun_0180_0260`

最终采用的 rerun 批次为：

- `0180_0200` → `run_612f280946d8216b`
- `0200_0220` → `run_0c6b1cdc856ee337`
- `0220_0240` → `run_9ae62d2b51063fad`
- `0240_0260` → `run_19fcdd8e59ae8685`

这些补跑批次都满足：

- `successful_request_count = 120`
- `last_error = null`

说明它们没有再出现之前那种整批 502 / fallback 崩坏。

---

## 最终 merge 规则

### 保留主跑结果的区间

- `0000_0020` → `run_75c9bb874cc91453`
- `0020_0040` → `run_591c7bfcce9db2c0`
- `0040_0060` → `run_e2e33c557a0b30e2`
- `0060_0080` → `run_345f6422c0aa8978`
- `0080_0100` → `run_07c2202fce49a2b1`
- `0100_0120` → `run_15003a01c911fca5`
- `0120_0140` → `run_a3abfb503be9c708`
- `0140_0160` → `run_6d98192f6ed56e5e`
- `0160_0180` → `run_9d9c421d41d527d7`
- `0260_0280` → `run_2cd96958623ccc52`
- `0280_0300` → `run_ba0ffe67760a268a`

### 用 rerun 替换的区间

- `0180_0200` → `run_612f280946d8216b`
- `0200_0220` → `run_0c6b1cdc856ee337`
- `0220_0240` → `run_9ae62d2b51063fad`
- `0240_0260` → `run_19fcdd8e59ae8685`

---

## 最终 merged 结果摘要

最终 merged summary：

- `requested_samples = 300`
- `processed_samples = 300`
- `pass = 118`（`39.3%`）
- `review = 182`（`60.7%`）
- `reject = 0`
- `rewrite_strategy_counts.keep_open = 300`
- `started_at = 2026-04-01T02:49:05Z`
- `finished_at = 2026-04-01T11:49:28Z`
- `elapsed_seconds = 32423`（约 `9.0` 小时）

LLM 使用统计：

- `request_count = 1800`
- `successful_request_count = 1706`
- `failed_request_count = 306`
- `retry_count = 212`
- `text_request_count = 1230`
- `multimodal_request_count = 570`
- `last_error = null`

从最终决策分布看，本次 merged 结果以 `review` 为主，未出现 `reject`。

最终 merged 结果的索引与说明文件包括：

- `outputs/physreason_merged_0000_0300/run_merged_physreason_0000_0300/summary.json`
- `outputs/physreason_merged_0000_0300/run_merged_physreason_0000_0300/datasets/physreason/summary.json`
- `outputs/physreason_merged_0000_0300/run_merged_physreason_0000_0300/records/selected_batches.json`
- `outputs/physreason_merged_0000_0300/run_merged_physreason_0000_0300/records/MERGE_SUMMARY.md`

---

## 推荐最终口径

推荐在后续汇总、上传、复核时统一使用以下口径：

> PhysReason `0:300` 已完成。由于历史主跑的 `0180:0260` 区间曾发生批次级 `HTTP 502 / fallback` 风险，最终结果采用主跑正常区间 + rerun 替换异常区间的 merged 方案。最终结果以 `outputs/physreason_merged_0000_0300/run_merged_physreason_0000_0300` 为准。
