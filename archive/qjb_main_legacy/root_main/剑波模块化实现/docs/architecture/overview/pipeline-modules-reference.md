# Pipeline Modules Reference（当前主线）

> 本文档是 **代码模块职责导航** 的 canonical owner。
>
> - 总体架构与阶段关系请看：[docs/architecture/pipeline-architecture.md](docs/architecture/pipeline-architecture.md)
> - 架构硬约束与依赖方向请看：[docs/architecture/PIPELINE_ARCHITECTURE.md](docs/architecture/PIPELINE_ARCHITECTURE.md)
> - 字段级稳定契约请看：[docs/contracts/PIPELINE_MODULE_CONTRACTS.md](docs/contracts/PIPELINE_MODULE_CONTRACTS.md)

本文面向当前采集/清洗流水线的代码结构，回答两个问题：

1. 代码主要在哪些模块里。
2. 每个模块负责哪一段，不负责哪一段。

## 1. 总览：模块与阶段映射

| 模块 | 主要阶段 | 角色 | 自动化类型 |
| --- | --- | --- | --- |
| `pipeline_setup.py` | Setup | 参数解析、配置覆盖、run 目录初始化 | 纯脚本 |
| `pipeline_collection.py` | Collection | 样本接入、预处理、初步评分、结构提取编排 | 纯脚本 |
| `cleaning_semantics.py` | Collection / Cleaning 支撑 | 文本结构解析、视觉结构解析、对齐、可解性判断 | 纯脚本 |
| `pipeline_cleaning.py` | Cleaning | rewrite、quality gate、清洗记录构建 | 混合 fallback |
| `pipeline_reporting.py` | Report | records 聚合、dataset/run summary 写出 | 纯脚本 |
| `multidataset_cleaning_pipeline.py` | Orchestrator / shared runtime | dataclass、connector、agent、主流程编排 | 混合 fallback |

## 2. 阶段关系图

```text
run_pipeline.py
    │
    ▼
multidataset_cleaning_pipeline.py
    │
    ├── Setup
    │   └── pipeline_setup.py
    │
    ├── Collection
    │   ├── pipeline_collection.py
    │   └── cleaning_semantics.py
    │
    ├── Cleaning
    │   └── pipeline_cleaning.py
    │
    └── Report
        └── pipeline_reporting.py
```

## 3. 各模块职责边界

### 3.1 `pipeline_setup.py`

职责：
- 解析 CLI 参数
- 合并 CLI override 到配置
- 初始化 run 目录与 `SetupContext`

不负责：
- 数据集接入
- rewrite / gate
- report 聚合

### 3.2 `pipeline_collection.py`

职责：
- 选择 connector 并拉取样本
- 预处理 question / answer / image
- 计算初步评分与优先级
- 编排文本结构、视觉结构、对齐、可解性提取

不负责：
- 最终 `pass / review / reject`
- run summary 落盘

### 3.3 `cleaning_semantics.py`

职责：
- 提供文本结构解析、视觉结构解析、alignment、solvability 等规则层能力
- 作为 Collection / Cleaning 共用的非 Agent 语义支撑层

不负责：
- 顶层编排
- 最终 report 写出

### 3.4 `pipeline_cleaning.py`

职责：
- 执行 rewrite
- 执行 `clean_gate()`
- 生成 cleaning record / reject record / problem main record 等最终清洗结果

关键边界：
- **`pass / review / reject` 在这里决定**
- Report 阶段只消费这里的结果，不重新裁决

### 3.5 `pipeline_reporting.py`

职责：
- 汇总单样本结果
- 写出 `records/*.jsonl`
- 写出 `datasets/<dataset>/summary.json`
- 写出 run 级 `summary.json`

关键边界：
- **不负责决定** `pass / review / reject`
- 只负责汇总与序列化

### 3.6 `multidataset_cleaning_pipeline.py`

职责：
- 作为总 orchestrator 和共享 runtime
- 定义配置 dataclass、connector、client、agent
- 初始化 parser / analyzer / agent / connector class
- 串联 Setup → Collection → Cleaning → Report

它本身不是单独一个业务阶段，而是装配点和编排点。

## 4. 自动化类型怎么理解

### 4.1 纯脚本

关闭 LLM 后仍正常运行：
- Setup 参数解析与目录初始化
- connector 选择与数据读取主流程
- 文本归一化、choice 解析、answer type 推断
- 图像质量分析
- 文本/视觉结构解析
- text-image alignment
- solvability 判定
- report 聚合与写出

### 4.2 可选 LLM / Agent

增强项，不是主流程硬依赖：
- `OpenAICompatibleClient.chat_json()`
- `DecisionAgent.review_override()`

### 4.3 混合 fallback

优先尝试模型，但存在脚本回退：
- 记录字段抽取
- rewrite
- review 边界 override

## 5. 两个最重要的定位结论

### `pass / review / reject` 在哪里决定？

在 Cleaning 阶段，核心位置是：
- `pipeline_cleaning.clean_gate()`
- `pipeline_cleaning.finalize_cleaning_sample()`

### 这是不是“全 Agent 化”流水线？

不是。当前主线是：
- **脚本主导的采集/清洗流水线**
- 在少数点位接入 **可选 LLM 增强**
- 关闭 LLM 后仍可跑通 deterministic pipeline

## 6. 说明

当前主线请以本文档为准。
