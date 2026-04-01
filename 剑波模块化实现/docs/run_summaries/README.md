# 保留的运行摘要

这里保存的是一小部分具有代表性的运行摘要，用来记录关键阶段结果；更大的未跟踪输出已经被移出仓库并归档到工作区其他位置。

## 当前保留内容

### 2026-03-28
- `2026-03-28/candidate_200_remote_rerun_analysis_2026-03-28_run_38bce3437874d962.md` —— 最新一轮完整 200 样本 rerun 分析，包含运行时长、各数据集 pass/review/reject 分布、`MM-Math`/`Multi-Physics` 深入分析，以及日志异常排查结论
- `2026-03-28/rewrite_llm_recovery_and_runlog_2026-03-28.md` —— 记录 rewrite LLM `401 Unauthorized` 根因定位、env 展开与 fail-fast 修复、以及 `run.log` 接入情况

### 已迁出的 dated reports
以下更偏“阶段分析 / benchmark 结论 / 历史进展”的文档已迁到 [docs/reports/](docs/reports/)：
- [docs/reports/progress-2026-03-23.md](docs/reports/progress-2026-03-23.md)
- [docs/reports/benchmark-200-2026-03-24.md](docs/reports/benchmark-200-2026-03-24.md)
- [docs/reports/benchmark-200-rerun-2026-03-26.md](docs/reports/benchmark-200-rerun-2026-03-26.md)
- [docs/reports/benchmark-200-comparison-2026-03-26-run-6cd93f19b5ab1d93.md](docs/reports/benchmark-200-comparison-2026-03-26-run-6cd93f19b5ab1d93.md)

- `../loader_recommendations.md` —— 数据集 → 推荐 loader 类型映射，说明 `cmm_math / physreason / mm_math` 等数据集为什么更适合 zip-member / raw-bundle 等专门 loader
- `m3cot_single_before_image_path_fix.summary.json` —— 本地图片路径修复前的结果
- `m3cot_single_after_image_path_fix.summary.json` —— 本地图片路径修复后的结果
- `all_available_v2_candidate_reject_fastpath.summary.json` —— 验证 candidate-intake reject 快速路径
- `all_available_v3_relaxed_intake.summary.json` —— 验证放宽 intake 策略后的行为
- `intake_relaxed_smoke_miniset.summary.json` —— 一个最小、可解释的 smoke 测试样本集

## 说明

原始的大型运行目录已经归档到：
`/root/.openclaw/workspace/tmp/agent-pipeline_untracked_archive_2026-03-24_0913/`
