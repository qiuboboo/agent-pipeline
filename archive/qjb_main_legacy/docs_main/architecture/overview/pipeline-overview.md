# Pipeline Overview

## 目标

该流水线从多个来源采集多模态 benchmark 样本，将其归一化为统一样本表示，评估图像与文本可用性，把符合条件的题目改写为开放式变体，做出清洗决策，并写出标准化输出记录。

## 重构原则

以下原则对本次重构具有约束力：

1. 模块应保持小而独立。
2. 保持参数名、标签名与输出结果 schema 稳定。
3. 除非有明确计划且文档已记录，否则不要改变可观察行为。
4. 确保每个模块都可以被独立测试。
5. 保留有意义的日志，不要删除有诊断价值的运行日志。
6. 代码变更时，必须在同一轮同步更新对应文档。
7. 文档必须说明模块目的、输入、输出、依赖关系与测试预期。

## 当前端到端流程

1. **加载配置**
   - 读取 YAML、环境变量与 CLI 覆盖项。
   - 构建 `PipelineConfig`。
2. **发现并加载源样本**
   - 根据来源使用本地、Hugging Face、GitHub 或 unavailable connector。
   - 将源记录转换为 `UnifiedSample`。
3. **提取原始字段**
   - 提取题干文本、答案文本、选项映射、图片路径与提取元数据。
4. **规范化文本与答案语义**
   - 规范化题干与答案文本。
   - 在可能时，将选择题标签或数字索引解析为语义答案。
5. **分析图像质量与结构信号**
   - 计算图像质量摘要与多模态可用性信号。
   - 提取文本结构、视觉结构、alignment 与 solvability 前置信号。
6. **改写为开放式变体**
   - 产出 rewrite strategy、rationale、variants 与 discard reason codes。
7. **评估 / 决策**
   - 综合文本、图像、rewrite、alignment 与 solvability 信号。
   - 生成 pass / review / reject 决策。
8. **构建输出记录**
   - 写出样本级记录、rewrite records、asset records、audits 与 summaries。
9. **持久化运行产物**
   - 保存日志、JSON/JSONL 输出、run summary 与 sample bundles。

## 当前最小可用模块化架构

当前已落地的稳定主线为：

- `run_pipeline.py`
- `multidataset_cleaning_pipeline.py`
- `pipeline_setup.py`
- `pipeline_collection.py`
- `cleaning_semantics.py`
- `pipeline_cleaning.py`
- `pipeline_reporting.py`
- `pipeline_types.py`
- `pipeline_utils.py`
- `pipeline_clients.py`
- `pipeline_logging.py`
- `pipeline_normalization.py`
- `pipeline_extraction.py`
- `pipeline_rewrite.py`

## 当前最小可用重构状态

当前已落地的是一轮保持契约的最小重构：
- `run_pipeline.py` 仍然是稳定的 CLI 入口。
- `multidataset_cleaning_pipeline.py` 充当当前 orchestrator shell，并暂时承载尚未完全拆出的 decision runtime 与部分兼容接线。
- `pipeline_setup.py` 负责 CLI 覆盖项合并与运行上下文创建。
- `pipeline_collection.py` 负责预处理、collection scoring，以及与 `cleaning_semantics.py` 的结构提取交接。
- `cleaning_semantics.py` 负责文本结构、视觉结构、alignment 与 solvability 分析。
- `pipeline_cleaning.py` 负责 rewrite orchestration、gate 与输出记录构建。
- `pipeline_reporting.py` 负责 dataset/run summary 生成与 JSONL 写出。
- `pipeline_types.py`、`pipeline_utils.py`、`pipeline_clients.py`、`pipeline_logging.py`、`pipeline_normalization.py`、`pipeline_extraction.py` 与 `pipeline_rewrite.py` 已承接一部分原先嵌在 orchestrator-host 文件中的共享基础设施与 rewrite runtime。

上一轮 contract alignment 前的 orchestrator 快照已归档于：
- `archive/refactor-2026-03-29/multidataset_cleaning_pipeline.pre_contract_alignment.py`

共享基础设施抽取前的 orchestrator 快照已归档于：
- `archive/refactor-2026-03-29/multidataset_cleaning_pipeline.pre_shared_infra_extraction.py`

提取逻辑拆分前的 orchestrator 快照已归档于：
- `archive/refactor-2026-03-29/multidataset_cleaning_pipeline.pre_extraction_split.py`

rewrite runtime 拆分前的 orchestrator 快照已归档于：
- `archive/refactor-2026-03-29/multidataset_cleaning_pipeline.pre_rewrite_runtime_split.py`

当前状态仍不是最终目标架构。后续轮次仍需继续把 connectors、decision runtime 以及其余 shared infra 从 `multidataset_cleaning_pipeline.py` 中抽离出去。
