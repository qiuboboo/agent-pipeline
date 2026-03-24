# 批量 collection + cleaning 对照报告（run_637ca3432da6ddfb）

- pipeline 输出目录：`outputs/user_requested_batch_review/pipeline_runs/run_637ca3432da6ddfb`
- 外部对照报告目录：`outputs/user_requested_batch_review/reports/run_637ca3432da6ddfb`
- 说明：本次报告通过外部脚本生成，不改动原 pipeline 实现；运行时关闭模型网关，使用 pipeline 自带的 fallback / rule-based 路径保证批量稳定跑完。
- 功能报告：[`采集清洗功能报告.md`](outputs/user_requested_batch_review/reports/run_637ca3432da6ddfb/采集清洗功能报告.md)

## 1. 数据源可用性

| 数据集 | 状态 | 处理条数 | detail |
| --- | --- | ---: | --- |
| SCEMQA | available | 20 | - |
| Geometry3K | available | 20 | - |
| PhysReason | source_unavailable | 0 | No structured data files discovered in repository |
| CMM-Math | available | 20 | - |
| MathVision | available | 20 | - |
| EEE-Bench | available | 20 | - |
| EMMA | source_unavailable | 0 | No stable programmatic public source configured |
| GeoSQA | source_unavailable | 0 | No stable programmatic public source configured |
| MM-Math | source_unavailable | 0 | An error occurred while generating the dataset |
| muti- physics | available | 20 | - |
| Seephy | source_unavailable | 0 | No stable programmatic public source configured |

## 2. 已运行数据集

- SCEMQA：[`INDEX.md`](outputs/user_requested_batch_review/reports/run_637ca3432da6ddfb/scemqa/INDEX.md)
- Geometry3K：[`INDEX.md`](outputs/user_requested_batch_review/reports/run_637ca3432da6ddfb/geometry3k/INDEX.md)
- PhysReason：[`SKIPPED_physreason.md`](outputs/user_requested_batch_review/reports/run_637ca3432da6ddfb/SKIPPED_physreason.md)
- CMM-Math：[`INDEX.md`](outputs/user_requested_batch_review/reports/run_637ca3432da6ddfb/cmm_math/INDEX.md)
- MathVision：[`INDEX.md`](outputs/user_requested_batch_review/reports/run_637ca3432da6ddfb/mathvision/INDEX.md)
- EEE-Bench：[`INDEX.md`](outputs/user_requested_batch_review/reports/run_637ca3432da6ddfb/eee_bench/INDEX.md)
- EMMA：[`SKIPPED_emma.md`](outputs/user_requested_batch_review/reports/run_637ca3432da6ddfb/SKIPPED_emma.md)
- GeoSQA：[`SKIPPED_geosqa.md`](outputs/user_requested_batch_review/reports/run_637ca3432da6ddfb/SKIPPED_geosqa.md)
- MM-Math：[`SKIPPED_mm_math.md`](outputs/user_requested_batch_review/reports/run_637ca3432da6ddfb/SKIPPED_mm_math.md)
- muti- physics：[`INDEX.md`](outputs/user_requested_batch_review/reports/run_637ca3432da6ddfb/multi_physics/INDEX.md)
- Seephy：[`SKIPPED_seephy.md`](outputs/user_requested_batch_review/reports/run_637ca3432da6ddfb/SKIPPED_seephy.md)
