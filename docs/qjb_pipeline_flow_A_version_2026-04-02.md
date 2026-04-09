# qjb 四阶段正式版流程图（A版）

## 1. Mermaid 总览图（严格对齐版）

```mermaid
flowchart TD
    SUP["公共支撑层<br/>types / utils / clients / logging"]

    S["0. Setup<br/>配置准备"]
    C["1. Collection<br/>采集"]
    CL["2. Cleaning<br/>清洗"]
    R["3. Report<br/>汇总输出"]

    S --> C --> CL --> R
    SUP -. support .-> S
    SUP -. support .-> C
    SUP -. support .-> CL
    SUP -. support .-> R

    classDef stage fill:#dbeafe,stroke:#2563eb,stroke-width:2px,color:#0f172a,rx:18,ry:18;
    classDef support fill:#e0f2fe,stroke:#0284c7,stroke-width:2px,color:#0f172a,rx:18,ry:18;

    class S,C,CL,R stage;
    class SUP support;

    linkStyle 0 stroke:#2563eb,stroke-width:3px;
    linkStyle 1 stroke:#2563eb,stroke-width:3px;
    linkStyle 2 stroke:#2563eb,stroke-width:3px;
    linkStyle 3 stroke:#0284c7,stroke-width:2px,stroke-dasharray: 6 4;
    linkStyle 4 stroke:#0284c7,stroke-width:2px,stroke-dasharray: 6 4;
    linkStyle 5 stroke:#0284c7,stroke-width:2px,stroke-dasharray: 6 4;
    linkStyle 6 stroke:#0284c7,stroke-width:2px,stroke-dasharray: 6 4;
```

### 图中各阶段含义

| 阶段 | 主要内容 | 对应模块 |
|---|---|---|
| 0. Setup | 参数加载（Config Load）<br>参数校验（Validation）<br>运行初始化（Run Initialization） | `pipeline_setup.py` |
| 1. Collection | 数据接入（Ingestion）<br>预处理（Preprocess）<br>信息提取（Extract）<br>初始评分 / 候选入池（Scoring / Pooling） | `pipeline_collection.py`<br>`pipeline_extraction.py` |
| 2. Cleaning | 规范化（Normalization）<br>结构 / 对齐 / 可解性分析（Semantics）<br>改写 / 转换（Rewrite / Transform）<br>判定 / 打分（Gate / Scoring） | `pipeline_normalization.py`<br>`cleaning_semantics.py`<br>`pipeline_rewrite.py`<br>`pipeline_cleaning.py` |
| 3. Report | records 写出<br>dataset summary<br>run summary<br>sample bundles / artifacts | `pipeline_reporting.py` |
| 公共支撑层 | 贯穿 0~3 全阶段的共享基础设施 | `pipeline_types.py`<br>`pipeline_utils.py`<br>`pipeline_clients.py`<br>`pipeline_logging.py` |

---

## 2. 纯文本备用版

```text
┌──────────────────────────────────────────────────────────────────────┐
│ 0. 配置准备（Setup）                                                │
│                                                                      │
│  0.1 参数加载（Config Load）                                        │
│  0.2 参数校验（Validation）                                         │
│  0.3 运行初始化（Run Initialization）                               │
│                                                                      │
│  模块：pipeline_setup.py                                             │
└──────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│ 1. 采集（Collection）                                               │
│                                                                      │
│  1.1 数据接入（Ingestion）                                          │
│  1.2 预处理（Preprocess）                                           │
│  1.3 信息提取（Extract）                                            │
│  1.4 初始评分 / 候选入池（Scoring / Pooling）                       │
│                                                                      │
│  模块：pipeline_collection.py / pipeline_extraction.py              │
└──────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│ 2. 清洗（Cleaning）                                                 │
│                                                                      │
│  2.1 规范化（Normalization）                                        │
│  2.2 结构 / 对齐 / 可解性分析（Semantics）                          │
│  2.3 改写 / 转换（Rewrite / Transform）                             │
│  2.4 判定 / 打分（Gate / Scoring）                                  │
│                                                                      │
│  模块：pipeline_normalization.py                                    │
│       cleaning_semantics.py                                         │
│       pipeline_rewrite.py                                           │
│       pipeline_cleaning.py                                          │
└──────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│ 3. 汇总输出（Report）                                               │
│                                                                      │
│  3.1 records 写出                                                   │
│  3.2 dataset summary                                                │
│  3.3 run summary                                                    │
│  3.4 sample bundles / artifacts                                     │
│                                                                      │
│  模块：pipeline_reporting.py                                        │
└──────────────────────────────────────────────────────────────────────┘

────────────────────────────────────────────────────────────────────────
公共支撑层（贯穿 0~3 全阶段）
- pipeline_types.py
- pipeline_utils.py
- pipeline_clients.py
- pipeline_logging.py
────────────────────────────────────────────────────────────────────────
```

---

## 3. 职责边界（四卡片版文案）

### 卡片 1｜Setup

**负责**
- 配置加载与合并
- CLI 参数覆盖
- 参数校验
- 运行初始化
- runtime context 建立

**不负责**
- 样本接入
- 语义分析
- rewrite / gate
- summary 写出

---

### 卡片 2｜Collection

**负责**
- 样本接入
- 资产登记
- 基本完整性检查
- 来源整理
- 稳定 ID 生成
- 初始评分 / 候选入池

**不负责**
- 深层语义纠错
- 最终答案裁决
- 最终 pass / review / reject
- 解题过程标注 / 多解法建模

---

### 卡片 3｜Cleaning

**负责**
- 文本规范化
- 字段标准化映射
- 图像质量判断
- 图文对齐
- rewrite / transform
- gate 决策

**不负责**
- 穷举全部解法
- 构建完整推理图
- 发布版数据切片

---

### 卡片 4｜Report

**负责**
- dataset bundle 累积
- dataset summary
- run summary
- records JSONL 写出
- 持久化产物整理

**不负责**
- 参数组装与运行初始化
- 样本接入与候选入池
- rewrite / gate 决策
- 语义清洗规则执行

---

## 4. 全局稳定约束图

```mermaid
flowchart LR
    subgraph COL1[" "]
        direction TB
        A["4. Schema Stable<br/>参数名 / 标签名 / 输出 schema 保持稳定<br/>"]
        B["5. Logs Preserved<br/>保留有诊断价值的日志<br/>"]
        C["6. No Behavior Drift<br/>没有明确计划与文档，不改变可观察行为<br/>"]
    end

    subgraph COL2[" "]
        direction TB
        D["1. Independently Testable<br/>每个模块应可独立测试<br/>"]
        E["2. Docs Updated with Code<br/>代码改动必须同步更新文档<br/>"]
        F["3. Contract First<br/>字段级 contract 变更必须先文档化<br/>"]
    end

    classDef card fill:#dbeafe,stroke:#2563eb,stroke-width:2px,color:#0f172a,rx:18,ry:18;
    class A,B,C,D,E,F card;
```

> 模块可以继续拆分，但 schema、日志、行为和契约不能随意漂移。

---

## 5. 最适合放进 PPT 的一句话总结

> 这套 pipeline 的正式口径是 Setup、Collection、Cleaning、Report 四大阶段；Collection 负责接入与候选入池，Cleaning 负责规范化、改写与 gate，Report 负责聚合写出，而 types / utils / clients / logging 作为公共支撑层贯穿全流程，并受到稳定契约约束。
