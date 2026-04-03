# Pipeline Modules

本文档定义当前主线下各个 pipeline 模块的职责边界，优先描述**已落地模块**，不再把尚未落地的目标文件当成现状。

---

## `pipeline_types.py`
**目的**
- 定义跨模块复用的稳定 dataclass 与类型化产物。

**负责**
- `ModelConfig`
- `ThresholdConfig`
- `DatasetSpec`
- `PipelineConfig`
- `UnifiedSample`
- 后续 preprocess / rewrite / decision 相关的类型化契约

**不得负责**
- 业务逻辑
- IO 逻辑
- LLM 调用

---

## `pipeline_utils.py`
**目的**
- 提供不归属于某个 pipeline stage 的纯工具函数。

**负责**
- JSON helpers
- hash helpers
- whitespace / text helpers
- env placeholder helpers
- directory / file helpers

**不得负责**
- 数据集特定规则
- rewrite 逻辑
- connector 逻辑

---

## `pipeline_clients.py`
**目的**
- 封装外部模型 / 服务客户端。

**负责**
- `OpenAICompatibleClient`

---

## `pipeline_logging.py`
**目的**
- 提供运行级与样本级的结构化日志。

**负责**
- `RunLogger`
- 日志格式规则
- stage 日志约定

**日志规则**
- 日志是必需的，并且应保持有意义、简洁且具备诊断价值。

---

## `pipeline_normalization.py`
**目的**
- 提供文本规范化、答案规范化与图像质量分析规则。

**负责**
- `TextNormalizer`
- `ImageQualityAnalyzer`
- `resolve_multiple_choice_answer_text`
- 数据集特定的答案索引规则

**输入**
- 原始或已规范化文本
- choice map
- 数据集答案索引元数据

**输出**
- 规范化文本
- 规范化后的语义答案
- answer type 判断
- image quality 摘要
- rewrite 辅助判断

---

## `pipeline_extraction.py`
**目的**
- 从原始 source row 中提取题目 / 答案 / 图片 / 选项信息。

**负责**
- heuristic extraction
- prompt-based extraction
- field-selection helpers
- image-path normalization helpers
- choice parsing helpers

---

## `pipeline_rewrite.py`
**目的**
- 将符合条件的问题改写为开放式变体。

**负责**
- `BaseStructuredAgent`
- `RewriteAgent`
- rewrite fallback policy
- rewrite LLM interaction
- `normalize_rewrite_variants_temp`

**契约**
- 必须保持 rewrite report 字段稳定：
  - `strategy`
  - `rationale`
  - `variants`
  - `discard_reason_codes`
  - `llm_used`

---

## `pipeline_setup.py`
**目的**
- 组装运行配置、CLI override 与输出目录上下文。

**负责**
- CLI 参数覆盖
- run 目录初始化
- config merge 与 runtime context 建立

---

## `pipeline_collection.py`
**目的**
- 承担 collection 阶段的样本接入、预处理、基础评分与结构提取编排。

**负责**
- 数据集接入后的样本预处理
- collection scoring
- prompt / heuristic extraction 编排
- 与 `cleaning_semantics.py` 的结构信号交接

---

## `cleaning_semantics.py`
**目的**
- 承担 collection / cleaning 共用的语义分析层。

**负责**
- 文本结构分析
- 视觉结构分析
- 图文 alignment 分析
- solvability 前置信号

---

## `pipeline_cleaning.py`
**目的**
- 承担 cleaning 阶段的 rewrite orchestration、gate 决策与记录组装。

**负责**
- rewrite runtime 调用
- pass / review / reject gate
- decision reason code 组装
- clean problem / rewrite / audit 等记录构建

---

## `pipeline_reporting.py`
**目的**
- 聚合 dataset / run 级结果并写出持久化产物。

**负责**
- dataset bundle 累积
- dataset summary
- run summary
- records JSONL 写出

---

## `multidataset_cleaning_pipeline.py`
**目的**
- 充当当前 orchestrator shell，并作为尚未完全抽离逻辑的临时宿主。

**负责**
- 运行顺序编排
- stage 调用接线
- 当前残留的 decision runtime
- 与已拆分共享模块之间的兼容别名 / 实例化接线

**不得负责**
- 长期持有大块 rewrite runtime 实现
- 长期持有应下沉到专属模块的 shared infra

---

## 当前已落地映射

仓库当前已落地的最小映射为：

- `pipeline_types.py` -> 稳定共享 dataclass 与 config/sample types
- `pipeline_utils.py` -> 纯工具函数，以及 JSON/hash/text/path helpers
- `pipeline_clients.py` -> 外部模型客户端封装
- `pipeline_logging.py` -> run logger
- `pipeline_normalization.py` -> 文本规范化、答案规范化、图像质量分析
- `pipeline_extraction.py` -> 原始字段提取、字段选择、图片路径归一化与 prompt 提取辅助逻辑
- `pipeline_rewrite.py` -> rewrite runtime、rewrite fallback、LLM 改写调用与临时 rewrite 兼容清洗逻辑
- `pipeline_setup.py` -> CLI override、config merge、run context 初始化
- `pipeline_collection.py` -> 预处理、collection scoring、中间 collection 产物、结构提取交接
- `cleaning_semantics.py` -> 文本 / 视觉 / 对齐 / 可解性语义分析
- `pipeline_cleaning.py` -> rewrite、gate、持久化记录构建、最终样本结果组装
- `pipeline_reporting.py` -> dataset bundle 累积、dataset summary、run summary
- `multidataset_cleaning_pipeline.py` -> 当前 orchestrator shell，以及剩余 decision runtime 与部分兼容接线的临时宿主

重构前的 orchestrator-host 快照已归档于：
- `archive/refactor-2026-03-29/multidataset_cleaning_pipeline.pre_contract_alignment.py`
- `archive/refactor-2026-03-29/multidataset_cleaning_pipeline.pre_shared_infra_extraction.py`
- `archive/refactor-2026-03-29/multidataset_cleaning_pipeline.pre_extraction_split.py`
- `archive/refactor-2026-03-29/multidataset_cleaning_pipeline.pre_rewrite_runtime_split.py`

上述映射是当前保持契约的中间状态；后续重构仍应继续把 decision runtime、connectors 与其余 shared infra 进一步从 `multidataset_cleaning_pipeline.py` 中抽离出去。
