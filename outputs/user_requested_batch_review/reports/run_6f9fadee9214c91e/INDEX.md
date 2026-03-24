# 批量 collection + cleaning 对照报告（run_6f9fadee9214c91e）

- pipeline 输出目录：`outputs/user_requested_batch_review/pipeline_runs/run_6f9fadee9214c91e`
- 外部对照报告目录：`outputs/user_requested_batch_review/reports/run_6f9fadee9214c91e`
- 说明：本次报告通过外部脚本生成，不改动原 pipeline 实现；运行时关闭模型网关，使用 pipeline 自带的本地 fallback / rule-based 路径保证批量稳定跑完。

## 1. 数据源可用性

| dataset_key | display_name | priority | status | detail |
| --- | --- | --- | --- | --- |
| scemqa | SCEMQA | yes | available |  |
| geometry3k | Geometry3K | yes | available |  |
| physreason | PhysReason | yes | source_unavailable | No structured data files discovered in repository |
| cmm_math | CMM-Math | yes | available |  |
| mathvision | MathVision | yes | available |  |
| multi_physics | muti- physics | no | available |  |
| eee_bench | EEE-Bench | no | available |  |

## 2. 已运行数据集

- SCEMQA：`outputs/user_requested_batch_review/reports/run_6f9fadee9214c91e/scemqa/INDEX.md`
- Geometry3K：`outputs/user_requested_batch_review/reports/run_6f9fadee9214c91e/geometry3k/INDEX.md`
- CMM-Math：`outputs/user_requested_batch_review/reports/run_6f9fadee9214c91e/cmm_math/INDEX.md`
- MathVision：`outputs/user_requested_batch_review/reports/run_6f9fadee9214c91e/mathvision/INDEX.md`
- muti- physics：`outputs/user_requested_batch_review/reports/run_6f9fadee9214c91e/multi_physics/INDEX.md`
- EEE-Bench：`outputs/user_requested_batch_review/reports/run_6f9fadee9214c91e/eee_bench/INDEX.md`