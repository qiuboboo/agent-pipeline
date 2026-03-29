# Rewrite Migration Notes

## 当前状态

rewrite 路径当前正朝着更独立的 runtime 迁移，同时保持现有 pipeline 契约不变。

在第四轮最小契约对齐重构之后：
- `pipeline_cleaning.py` 继续作为 rewrite orchestration、gate 决策与下游记录组装的主责任模块。
- `pipeline_rewrite.py` 已正式落地，并承接 `BaseStructuredAgent`、`RewriteAgent`、rewrite fallback、LLM 改写调用，以及临时 rewrite 兼容清洗逻辑。
- `pipeline_normalization.py` 提供 `TextNormalizer` 与 `ImageQualityAnalyzer`，作为 rewrite / cleaning runtime 共享依赖的一部分。
- `pipeline_types.py`、`pipeline_utils.py`、`pipeline_clients.py`、`pipeline_logging.py` 与 `pipeline_extraction.py` 继续提供 rewrite/runtime 所需的共享依赖。
- `multidataset_cleaning_pipeline.py` 不再保留 rewrite runtime 的主实现，只保留受控导入、兼容别名与实例化接线；decision runtime 仍暂时留在该文件中。
- 独立的 `pipeline_rewrite_compat.py` 仍未正式落地，因此 compat 逻辑当前仍集中在 `pipeline_rewrite.py` 内部，避免扩散回 reporting 或 orchestrator shell。

## 迁移原则

1. 保持 rewrite report schema 与下游记录预期稳定。
2. 持续向更小、更独立的模块推进。
3. 保留有意义的日志。
4. 将临时兼容层明确视为“临时”。
5. 只要 rewrite 行为或结构发生变化，就必须同步更新文档。

## 当前临时兼容层

当前临时 helper：
- `normalize_rewrite_variants_temp(...)`

当前位置：
- `benchmark/src/pipeline_rewrite.py`

用途：
- 在迁移期间规范化 rewrite 输出变体
- 在 rewrite 内部重构过程中维持下游字段稳定

规则：
- 当 rewrite 输出可以被下游直接消费、无需兼容清洗时，就应移除此 helper
- 在独立 `pipeline_rewrite_compat.py` 落地前，不得把 compat 调用点重新扩散回 `multidataset_cleaning_pipeline.py`、`pipeline_cleaning.py` 之外的外围模块

## 目标终态

目标终态为：
- `pipeline_rewrite.py` 承载稳定的 rewrite agent 与 rewrite fallback 逻辑
- `pipeline_rewrite_compat.py` 为空或被删除
- rewrite 输出可被下游模块直接消费
- rewrite 路径诊断所需日志仍然保留

## 必须同步更新的文档

任何 rewrite 内部变更，都必须同步保持以下文档一致：
- `docs/architecture/pipeline-overview.md`
- `docs/architecture/pipeline-modules.md`
- `docs/contracts/intermediate-artifacts.md`
- 本文件
