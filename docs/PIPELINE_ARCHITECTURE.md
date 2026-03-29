# Pipeline Architecture

## 1. 目标

本文档记录多数据集采集与清洗流水线的目标模块组织方式、依赖方向、阶段边界，以及重构时必须遵守的稳定契约。

本架构以当前主线代码与当前 LER rewrite 结果结构为基准，目标是在**不改变参数名、标签名、结果结构核心字段**的前提下完成模块化拆分。

---

## 2. 当前代码现状

当前主线组织如下：

```text
run_pipeline.py
└── multidataset_cleaning_pipeline.py
    ├── pipeline_setup.py
    ├── pipeline_collection.py
    ├── cleaning_semantics.py
    ├── pipeline_cleaning.py
    └── pipeline_reporting.py
```

### 2.1 现状说明

- `multidataset_cleaning_pipeline.py` 当前承担了总控、共享 runtime、客户端封装、agent 封装、部分 prompt 组织等多重职责。
- `pipeline_cleaning.py` 是当前最核心的业务模块，承载 rewrite、clean gate、记录构建等关键逻辑。
- `pipeline_reporting.py` 负责 records 聚合与 summary 写出。

---

## 3. 目标模块组织图

```text
run_pipeline.py
└── pipeline_orchestrator.py
    ├── pipeline_setup.py
    ├── pipeline_connectors/
    │   ├── base.py
    │   ├── dataset_x.py
    │   └── ...
    ├── pipeline_normalization.py
    ├── pipeline_extraction.py
    │   └── cleaning_semantics.py
    ├── pipeline_rewrite.py
    ├── pipeline_rewrite_compat.py
    ├── pipeline_quality.py
    ├── pipeline_decision.py
    ├── pipeline_records.py
    ├── pipeline_reporting.py
    ├── pipeline_types.py
    ├── pipeline_utils.py
    ├── pipeline_prompts.py
    ├── pipeline_logging.py
    └── pipeline_clients.py
```

---

## 4. 阶段组织图

```text
Stage 0 Setup
└── pipeline_setup.py

Stage 1 Collection
├── pipeline_connectors/
├── pipeline_normalization.py
├── pipeline_extraction.py
└── cleaning_semantics.py

Stage 2 Cleaning
├── pipeline_rewrite.py
├── pipeline_rewrite_compat.py
├── pipeline_quality.py
├── pipeline_decision.py
└── pipeline_records.py

Stage 3 Report
└── pipeline_reporting.py

Shared / Infra
├── pipeline_types.py
├── pipeline_utils.py
├── pipeline_prompts.py
├── pipeline_logging.py
└── pipeline_clients.py
```

---

## 5. 依赖方向图

```text
pipeline_orchestrator
  -> pipeline_setup
  -> pipeline_connectors
  -> pipeline_normalization
  -> pipeline_extraction
  -> cleaning_semantics
  -> pipeline_rewrite
  -> pipeline_rewrite_compat
  -> pipeline_quality
  -> pipeline_decision
  -> pipeline_records
  -> pipeline_reporting

pipeline_extraction
  -> cleaning_semantics
  -> pipeline_prompts
  -> pipeline_clients
  -> pipeline_types
  -> pipeline_utils
  -> pipeline_logging

pipeline_rewrite
  -> pipeline_prompts
  -> pipeline_clients
  -> pipeline_types
  -> pipeline_utils
  -> pipeline_logging

pipeline_quality
  -> pipeline_types
  -> pipeline_utils
  -> pipeline_logging

pipeline_decision
  -> pipeline_types
  -> pipeline_utils
  -> pipeline_logging

pipeline_records
  -> pipeline_types
  -> pipeline_utils
  -> pipeline_logging

pipeline_reporting
  -> pipeline_types
  -> pipeline_utils
  -> pipeline_logging
```

---

## 6. 禁止依赖规则

以下模块属于基础层：

- `pipeline_types.py`
- `pipeline_utils.py`
- `pipeline_prompts.py`
- `pipeline_logging.py`
- `pipeline_clients.py`

这些模块：

- 不能依赖 `pipeline_rewrite.py`
- 不能依赖 `pipeline_decision.py`
- 不能依赖 `pipeline_orchestrator.py`

另外：

- `pipeline_rewrite_compat.py` 只能作为临时兼容层存在。
- 新模块不得广泛依赖 `pipeline_rewrite_compat.py`。
- compat 调用点应尽量集中，便于后续整体删除。

---

## 7. 当前到目标的职责映射

### 7.1 `multidataset_cleaning_pipeline.py` 将拆分为

- `pipeline_orchestrator.py`
- `pipeline_clients.py`
- `pipeline_prompts.py`
- `pipeline_rewrite.py`
- `pipeline_decision.py`
- `pipeline_types.py`
- `pipeline_utils.py`
- `pipeline_logging.py`

### 7.2 `pipeline_cleaning.py` 将拆分为

- `pipeline_rewrite.py`
- `pipeline_quality.py`
- `pipeline_decision.py`
- `pipeline_records.py`

### 7.3 `pipeline_collection.py` 将拆分为

- `pipeline_connectors/`
- `pipeline_normalization.py`
- `pipeline_extraction.py`

---

## 8. 必须锁定的稳定契约

重构期间，下列字段名和结构必须保持稳定。

### 8.1 Rewrite 侧稳定契约

顶层：

- `strategy`
- `rationale`
- `variants`
- `discard_reason_codes`
- `llm_used`

`variants[*]`：

- `variant_id`
- `title`
- `rewritten_question_text`
- `expected_answer_type`
- `expected_answer`
- `split_role`

### 8.2 Decision / Gate 侧稳定契约

- `decision`
- `decision_reason_codes`
- `suggested_next_action`
- `review_required`

### 8.3 Problem Main Record 侧稳定契约

- `clean_decision`
- `clean_decision_reason_codes`
- `rewrite_strategy`
- `annotation_ready`
- `qa_precheck_ready`

### 8.4 Reporting 侧稳定契约

- `decision_counts`
- `rewrite_strategy_counts`

---

## 9. 重构顺序建议

### 第一阶段：低风险基础层拆分

- `pipeline_types.py`
- `pipeline_utils.py`
- `pipeline_prompts.py`
- `pipeline_logging.py`
- `pipeline_clients.py`

### 第二阶段：Collection 侧拆分

- `pipeline_connectors/`
- `pipeline_normalization.py`
- `pipeline_extraction.py`

### 第三阶段：Cleaning 核心拆分

- `pipeline_rewrite.py`
- `pipeline_rewrite_compat.py`
- `pipeline_quality.py`
- `pipeline_decision.py`
- `pipeline_records.py`
- `pipeline_orchestrator.py`

---

## 10. 重构硬约束

- 模块必须小
- 模块必须独立
- 参数名不乱改
- 标签名不乱改
- 结果结构不乱改
- 每个模块可单测
- 改代码必须同步改文档
- 日志必须保留，而且要有意义

---

## 11. 一句话总结

当前结构里，`multidataset_cleaning_pipeline.py` 是“大总管”，`pipeline_cleaning.py` 是“核心业务层”；目标是把总控、客户端、prompt、rewrite、decision、records 从大文件中拆出，并优先锁定 rewrite / gate / record 的字段契约。
