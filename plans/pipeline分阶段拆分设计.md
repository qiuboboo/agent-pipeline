# 多数据集采集与清洗流水线分阶段拆分设计

## 1. 文档目的

本文档用于说明当前多数据集采集与清洗流水线的分阶段拆分方案，明确各阶段职责、边界、输入输出及重构方向，为后续代码重构、产物治理和调度设计提供统一依据。

本次设计聚焦于**当前代码中已经落地的采集与清洗流水线部分**，目标是将原本集中在单文件中的逻辑整理为清晰的阶段式结构，便于维护、扩展与后续接入标注、质检和格式化发布流程。

---

## 2. 背景与现状

当前流水线入口位于 [run_pipeline.py](../run_pipeline.py)，其本身仅负责导入并调用主流程；主要业务逻辑集中在 [benchmark/src/multidataset_cleaning_pipeline.py](../benchmark/src/multidataset_cleaning_pipeline.py)。

当前实现存在以下特点：

- 配置解析、参数合并、运行初始化、数据采样、样本处理、质量判定、结果写出均集中在同一主文件中
- 单个主类同时承担调度、处理、聚合和落盘职责
- 采集、清洗、输出汇总的边界在代码中隐式存在，但尚未显式化
- 中间产物已较丰富，但缺少统一的阶段归属与工件组织方式

因此，需要先完成**架构层的阶段化拆分设计**，再逐步推进代码重构。

---

## 3. 设计原则

本次拆分遵循以下原则：

### 3.1 调度与处理分离
顶层入口和主流程只负责阶段调度，不承载样本级业务处理细节。

### 3.2 阶段职责单一
每个阶段只负责自身语义明确的一类工作，避免一个阶段同时处理配置、抽取、改写、判定、落盘等多类职责。

### 3.3 输出与汇总分层
详细中间产物在各阶段内部保存；最终 `summary` / `manifest` 仅保留摘要信息和路径索引，不重复嵌套全量明细。

### 3.4 优先结构重组，暂不改业务语义
本轮拆分优先整理代码组织和阶段边界，尽可能保持当前业务逻辑、指标计算规则和输出结果不变。

### 3.5 Report 是当前流水线的最终输出层
`Report` 表示**当前采集-清洗流水线的最终输出阶段**，负责组织和写出本轮 run 的结果；它不是整个数据工程大闭环中的“最终发布”步骤，后续仍可继续进入 `Annotation / QA / Format`。

---

## 4. 总体阶段划分

当前代码所对应的流水线，建议拆分为四个一级阶段：

```text
Stage 0 Setup
  -> Stage 1 Collection
  -> Stage 2 Cleaning
  -> Stage 3 Report
```

进一步细分如下：

```text
0. 配置准备（Setup）
   0.1 参数加载（Config Load）
   0.2 参数校验（Validation）
   0.3 运行初始化（Run Initialization）

1. 采集（Collection）
   1.1 数据接入（Ingestion）
   1.2 预处理（Preprocess）
   1.3 信息提取（Extract）

2. 清洗（Cleaning）
   2.1 改写 / 转换（Rewrite / Transform）
   2.2 判定 / 打分（Prob / Scoring）

3. 汇总输出（Report）
```

其中：

- `Setup`：决定这次 run 怎么执行
- `Collection`：把样本接入并结构化
- `Cleaning`：对样本进行改写、判定和筛选
- `Report`：汇总当前流水线全部结果并形成最终输出

---

## 5. 与原始五段业务主线的关系

原始设计中的整体业务主线为：

```text
采集（Collection）
-> 清洗（Cleaning）
-> 标注（Annotation）
-> 质检（QA）
-> 格式化发布（Format）
```

本次拆分文档只针对**当前代码已经覆盖的前半段**进行细化，因此：

- `Collection` 和 `Cleaning` 对应原始主线中的前两段
- `Report` 是**当前采集/清洗代码段内部的最终输出层**
- `Report` 不等于最终对外发布
- 后续仍可在 `Report` 结果基础上继续接入：
  - `Annotation`
  - `QA`
  - `Format`

换言之，当前结构中的 `Report` 更适合理解为：

> 当前 run 的汇总与出库层，而不是整个项目生命周期的最终发布层。

---

## 6. 各阶段职责设计

## 6.1 Stage 0：配置准备（Setup）

### 6.1.1 阶段目标
负责确定“本次运行如何执行”，在正式处理数据前完成参数与运行上下文初始化。

### 6.1.2 主要职责
- 解析命令行参数
- 加载 YAML 配置
- 合并 CLI override
- 校验关键运行参数
- 创建输出根目录
- 初始化 `run_id`、`run_dir`
- 固化本次运行配置快照

### 6.1.3 输入
- CLI 参数
- YAML 配置文件
- 默认配置

### 6.1.4 输出
- 最终生效配置对象
- `run_id`
- `run_dir`
- 配置快照文件
- 运行元信息文件

### 6.1.5 建议产物
- `config.json`
- `params.json`
- `run_meta.json`

---

## 6.2 Stage 1：采集（Collection）

### 6.2.1 阶段目标
负责将样本从外部数据源引入系统，并完成进入清洗阶段前的基础规范化与结构提取。

Collection 是“将数据纳入流水线并形成结构化输入”的阶段，不承担最终清洗决策职责。

---

### 6.2.2 子阶段 1：数据接入（Ingestion）

#### 目标
从不同来源读取样本，完成统一接入。

#### 主要职责
- 按数据集类型选择 connector
- 检测数据源可用性
- 加载样本
- 执行采样策略
- 初始化 dataset 级目录

#### 输入
- 数据集配置
- connector 参数
- 抽样策略

#### 输出
- 原始样本集合
- 数据源状态信息
- 数据集级接入元信息

#### 建议产物
- 接入后的基础样本列表
- source status 信息
- ingestion 元信息

---

### 6.2.3 子阶段 2：预处理（Preprocess）

#### 目标
将原始样本转化为统一的基础规范化表示。

#### 主要职责
- 文本标准化
- 题面 / 答案清洗
- 语言识别
- 答案类型识别
- 选择项抽取
- 图片持久化
- 图像依赖性判断
- 样本处理路径初判
- 初始 collection score 计算

#### 输入
- 原始样本
- 图像资源
- 预处理规则

#### 输出
- 规范化后的 question / answer
- 基础样本元数据
- 初始采集指标
- 图像基础质量信息

#### 建议产物
- clean question / answer 中间表示
- `candidate_problem_record`
- `candidate_pool_entry`
- image quality 中间信息

---

### 6.2.4 子阶段 3：信息提取（Extract）

#### 目标
从规范化样本中抽取文本结构、视觉结构和基础可解性线索，为清洗阶段提供结构化输入。

#### 主要职责
- 文本结构解析
- 视觉结构解析
- 图文对齐分析
- 基础质量标记生成
- 可解性评估

#### 输入
- 规范化文本
- 图像及图像质量信息
- 样本元数据

#### 输出
- 文本结构记录
- 视觉结构记录
- 对齐记录
- 可解性报告
- 质量 flags

#### 建议产物
- `text_structure_records`
- `visual_structure_records`
- `alignment_records`
- `solvability_reports`

---

## 6.3 Stage 2：清洗（Cleaning）

### 6.3.1 阶段目标
负责在 Collection 产物基础上，对样本进行改写、判定和筛选，形成可进入后续标注或评估流程的高质量样本结果。

Cleaning 是“样本治理与决策”的阶段，不负责最终汇总写出。

---

### 6.3.2 子阶段 1：改写 / 转换（Rewrite / Transform）

#### 目标
对样本进行开放化改写、任务形式转换和候选变体生成。

#### 主要职责
- 调用 rewrite agent
- 生成开放题变体
- 记录改写策略与改写结果
- 构建改写报告

#### 输入
- 规范化 question / answer
- 原始题型信息
- 选项信息

#### 输出
- 改写结果
- 改写策略
- 开放题变体
- 改写报告

#### 建议产物
- `rewrite_reports`
- `open_ended_problem_variants`

---

### 6.3.3 子阶段 2：判定 / 打分（Prob / Scoring）

#### 目标
综合多模态质量、结构信息、改写结果和可解性信息，对样本进行清洗决策。

#### 主要职责
- 计算潜力分与优先级分
- 执行 clean gate 判定
- 生成 reject 记录
- 给出 `pass / review / reject` 结论

#### 输入
- 提取阶段结构化结果
- 改写结果
- 质量 flags
- 可解性报告
- 对齐结果

#### 输出
- 最终 decision
- score / priority
- reject reason
- 决策摘要

#### 建议产物
- `problem_main_record` 中的决策字段
- `reject_records`
- decision / score 汇总信息

---

## 6.4 Stage 3：汇总输出（Report）

### 6.4.1 阶段目标
负责将当前 run 中 Collection 与 Cleaning 产生的结果统一整理为标准记录、样本 bundle、数据集 summary 和 run summary。

**Report 是当前流水线的最终输出层。**
这里的“最终”指的是：

- 对于当前这段采集-清洗代码而言，它是最后一步
- 它负责形成当前 run 的可消费输出
- 它不代表整个大项目生命周期的最终发布结果

### 6.4.2 主要职责
- 构建 problem / asset / node / audit 等标准记录
- 聚合样本级 bundle
- 写出 dataset 级 records
- 生成 dataset summary
- 生成 run summary
- 维护 `manifest` 等路径索引

### 6.4.3 输入
- Collection 阶段全部中间产物
- Cleaning 阶段全部决策与评分结果
- 样本级记录对象
- 数据集级聚合统计

### 6.4.4 输出
- records jsonl
- dataset summary
- run summary
- manifest

### 6.4.5 建议产物
- `records/*.jsonl`
- `dataset/summary.json`
- `run/summary.json`
- `manifest.json`

### 6.4.6 说明
Report 的职责是“**汇总当前流水线结果并形成最终输出接口**”，因此应与 Cleaning 分离，避免将“决策逻辑”和“结果组织/落盘逻辑”混杂在同一阶段中。

---

## 7. 推荐代码组织方式

建议采用“入口层 + 调度层 + 阶段模块层”的结构：

```text
run_pipeline.py
benchmark/src/
  multidataset_cleaning_pipeline.py
  pipeline_setup.py
  pipeline_collection.py
  pipeline_cleaning.py
  pipeline_reporting.py
```

### 文件职责建议

#### `run_pipeline.py`
- 仅作为 CLI 执行入口
- 不承载样本级业务逻辑

#### `multidataset_cleaning_pipeline.py`
- 作为主 orchestrator
- 负责串联 `Setup -> Collection -> Cleaning -> Report`
- 统一收集阶段结果

#### `pipeline_setup.py`
- 负责配置加载、参数校验、运行初始化

#### `pipeline_collection.py`
- 负责 `ingestion / preprocess / extract`

#### `pipeline_cleaning.py`
- 负责 `rewrite / scoring / decision`

#### `pipeline_reporting.py`
- 负责 record build、bundle 聚合、summary / manifest 写出

---

## 8. 输出组织建议

建议后续按阶段管理输出工件，避免所有中间产物平铺在同一层级。

### 建议结构

```text
run_xxx/
  config.json
  params.json
  run_meta.json
  manifest.json
  summary.json

  collection/
    ingestion/
    preprocess/
    extract/

  cleaning/
    rewrite/
    prob/

  report/
    records/
    dataset_summary.json
    run_summary.json
```

### 组织原则
- **阶段内明细**：放对应阶段目录
- **当前最终输出**：放 `report/`
- **统一索引**：放 `manifest.json`
- **决策模块**：只保留 score / label / path / brief reason，不重复嵌套上游全量明细

---

## 9. 重构实施建议

为降低风险，建议采用渐进式重构，而非一次性重写。

### 第一步：抽出 Setup
将参数解析、配置合并、run 初始化逻辑独立成 setup 模块。

### 第二步：拆出 Collection
从 `run_single_dataset()` 与 `process_sample()` 中抽出 `ingestion / preprocess / extract` 相关逻辑。

### 第三步：拆出 Cleaning
将 rewrite、gate、score 和 reject 判定逻辑独立为 cleaning 模块。

### 第四步：拆出 Report
将 `build_*record`、bundle 聚合、summary 写出逻辑集中到 reporting 模块。

### 第五步：统一 manifest / summary
在保持原产物兼容的前提下，新增统一的路径索引和运行摘要结构。

---

## 10. 结论

当前多数据集采集与清洗流水线适合按以下结构进行显式化拆分：

```text
0. 配置准备（Setup）
1. 采集（Collection）
   1.1 数据接入（Ingestion）
   1.2 预处理（Preprocess）
   1.3 信息提取（Extract）
2. 清洗（Cleaning）
   2.1 改写 / 转换（Rewrite / Transform）
   2.2 判定 / 打分（Prob / Scoring）
3. 汇总输出（Report）
```

该方案具备以下优点：

- 与当前业务流程认知一致
- 与现有代码逻辑可自然映射
- `Report` 作为当前流水线最终输出层，职责更清晰
- 便于后续模块化重构
- 便于中间产物治理和阶段指标分散
- 便于将 `run.py` 收敛为轻量调度入口
- 便于在后续继续接入 `Annotation / QA / Format`

后续重构建议优先从**结构拆分**入手，在不改变现有业务语义的前提下，逐步完成阶段模块化。
