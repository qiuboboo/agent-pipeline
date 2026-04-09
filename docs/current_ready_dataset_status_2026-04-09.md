# 当前 ready 数据集汇总（2026-04-09）

## 结论

截至 `2026-04-09`，本轮 `outputs -> merge/dedup -> ready` 清理任务关注的 9 个目标数据集都已经有 **canonical ready 包**，且均满足：

- `selection_validation.ok = true`
- `write_validation.ok = true`

当前没有遗漏数据集。

## 统计口径

本页只记录 **当前正式汇总口径**：

- 优先使用 `ready/<dataset>/run_outputs_merged_by_source_problem_id__*`
- `physreason` 使用其 special merged package
- 不再把历史 `similarity_dedup` / `filtered` / 旧 `run_merged_*` 包作为当前对外汇报口径

## 各数据集当前状态

| dataset | canonical ready package | scanned | duplicates | unique | pass | review | reject | dedup rule |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `mm_math` | `ready/mm_math/run_outputs_merged_by_source_problem_id__mm_math` | 300 | 0 | 300 | 71 | 229 | 0 | `latest_to_oldest_within_range_by_source_problem_id_then_merge_ranges` |
| `physreason` | `ready/physreason/run_outputs_merged_by_source_problem_id__physreason_full` | 499 | 212 | 287 | 188 | 90 | 9 | `physreason_full_global_newest_to_oldest_by_source_problem_id` |
| `seephys` | `ready/seephys/run_outputs_merged_by_source_problem_id__seephys` | 601 | 1 | 600 | 458 | 126 | 16 | `latest_to_oldest_within_range_by_source_problem_id_then_merge_ranges` |
| `msearth_open_ended` | `ready/msearth_open_ended/run_outputs_merged_by_source_problem_id__msearth_open_ended` | 307 | 7 | 300 | 82 | 189 | 29 | `latest_to_oldest_within_range_by_source_problem_id_then_merge_ranges` |
| `emma_physics` | `ready/emma_physics/run_outputs_merged_by_source_problem_id__emma_physics` | 468 | 0 | 468 | 266 | 180 | 22 | `latest_to_oldest_within_range_by_source_problem_id_then_merge_ranges` |
| `emma_chemistry` | `ready/emma_chemistry/run_outputs_merged_by_source_problem_id__emma_chemistry` | 1177 | 1 | 1176 | 864 | 262 | 50 | `latest_to_oldest_within_range_by_source_problem_id_then_merge_ranges` |
| `mathvision` | `ready/mathvision/run_outputs_merged_by_source_problem_id__mathvision` | 3183 | 143 | 3040 | 1879 | 1150 | 11 | `latest_to_oldest_within_range_by_source_problem_id_then_merge_ranges` |
| `multi_physics` | `ready/multi_physics/run_outputs_merged_by_source_problem_id__multi_physics` | 587 | 87 | 500 | 56 | 431 | 13 | `latest_to_oldest_within_range_by_source_problem_id_then_merge_ranges` |
| `eee_bench` | `ready/eee_bench/run_outputs_merged_by_source_problem_id__eee_bench` | 2216 | 0 | 2216 | 1541 | 670 | 5 | `latest_to_oldest_within_range_by_source_problem_id_then_merge_ranges` |

## 特殊说明

### 1. `physreason`

`physreason` 不是普通 range merge 口径，而是：

- `physreason_full_*` 视为全局 `source_problem_id` 空间
- 使用 `physreason_full_global_newest_to_oldest_by_source_problem_id`

这和普通数据集的“同 range 内 dedup，再 merge ranges”规则不同。

### 2. `emma_chemistry`

`emma_chemistry` 已从旧的 similarity-dedup 特例切换为当前 merged 主线口径。

当前 canonical package 为：

- `ready/emma_chemistry/run_outputs_merged_by_source_problem_id__emma_chemistry`

本次 merge 的关键点：

- 输入 family 为 `outputs/emma_chemistry_full` 与 `outputs/emma_chemistry_validation_*`
- 两边只发生了 1 个 `source_problem_id` 冲突
- 最终结果为：`1177 scanned / 1 duplicate / 1176 unique`

因此，后续对外汇报时应以这版 merged package 为准，而不是旧的 `run_outputs_similarity_dedup__emma_chemistry`（69 条）口径。

## 使用建议

如果后续需要汇报、交付或继续核对，请默认引用本页中的 canonical ready package，而不是 `ready/` 下仍保留的历史包。
