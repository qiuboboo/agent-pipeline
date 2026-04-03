# Pipeline Architecture Constraints

## 1. 目标

本文件定义当前 pipeline 重构期间必须遵守的模块边界、依赖方向与稳定契约。

目标不是一次性把所有代码拆完，而是在保留现有入口与结果契约的前提下，逐轮把 `multidataset_cleaning_pipeline.py` 中的职责拆分出去。

---

## 2. 当前稳定入口

当前稳定入口保持不变：

- `run_pipeline.py`

要求：
- 不改变入口角色
- 不改变 CLI 使用方式
- 不改变主流程可导入路径

---

## 3. 当前主流程边界

当前主流程采用如下责任分布：

- `pipeline_setup.py`：CLI 覆盖项合并、配置装配、运行上下文创建
- `pipeline_collection.py`：样本预处理、collection scoring、结构提取编排
- `cleaning_semantics.py`：文本 / 视觉 / 对齐 / 可解性语义分析
- `pipeline_cleaning.py`：rewrite orchestration、gate、记录构建、最终样本结果组装
- `pipeline_reporting.py`：dataset/run 级汇总与写出
- `pipeline_types.py`：稳定类型与 dataclass
- `pipeline_utils.py`：纯工具函数
- `pipeline_clients.py`：模型客户端
- `pipeline_logging.py`：运行日志
- `pipeline_normalization.py`：文本与答案规范化、图像质量分析
- `pipeline_extraction.py`：原始字段提取与提取辅助逻辑
- `pipeline_rewrite.py`：rewrite runtime、rewrite fallback、LLM 改写调用与临时 rewrite compat
- `multidataset_cleaning_pipeline.py`：当前 orchestrator shell，以及 remaining decision runtime / shared infra 的临时宿主

---

## 4. 当前已落地模块集合

当前代码库里已落地并应优先作为现状理解的模块为：

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
- `multidataset_cleaning_pipeline.py`

说明：
- `pipeline_quality.py`
- `pipeline_rewrite_compat.py`
- `pipeline_decision.py`
- `pipeline_records.py`
- `pipeline_orchestrator.py`

这些仍可作为**目标拆分方向**讨论，但当前主线代码并未独立落地，不应被写成“当前已经存在的正式模块”。

---

## 5. 当前依赖方向

当前推荐依赖方向如下：

```text
run_pipeline
  -> multidataset_cleaning_pipeline

multidataset_cleaning_pipeline
  -> pipeline_setup
  -> pipeline_collection
  -> pipeline_cleaning
  -> pipeline_reporting
  -> pipeline_types
  -> pipeline_utils
  -> pipeline_clients
  -> pipeline_logging
  -> pipeline_normalization
  -> pipeline_extraction
  -> pipeline_rewrite

pipeline_collection
  -> pipeline_types
  -> pipeline_utils
  -> pipeline_normalization
  -> pipeline_extraction
  -> cleaning_semantics
  -> pipeline_logging

pipeline_cleaning
  -> pipeline_types
  -> pipeline_utils
  -> pipeline_rewrite
  -> cleaning_semantics
  -> pipeline_logging

pipeline_rewrite
  -> pipeline_types
  -> pipeline_utils
  -> pipeline_clients
  -> pipeline_normalization
  -> pipeline_extraction
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
- `pipeline_logging.py`
- `pipeline_clients.py`

这些模块：
- 不能依赖业务 stage 模块
- 不能反向依赖 `pipeline_cleaning.py`
- 不能反向依赖 `multidataset_cleaning_pipeline.py`

另外：
- rewrite compat 逻辑当前虽然留在 `pipeline_rewrite.py` 内部，但仍只能被视为临时过渡实现。
- 新逻辑不得继续把 compat 处理扩散回 reporting 或基础层模块。
- `multidataset_cleaning_pipeline.py` 可以暂时保留剩余 runtime，但不应重新吸纳已经拆出的 rewrite 实现。

---

## 7. 当前到目标的职责映射

### 7.1 `multidataset_cleaning_pipeline.py`
当前角色：
- orchestrator shell
- stage 调用接线
- remaining decision runtime / shared infra 的临时宿主

后续目标：
- 继续缩小壳层职责
- 让更多 runtime 下沉到专属模块

### 7.2 `pipeline_cleaning.py`
当前角色：
- rewrite orchestration
- gate 决策
- records 组装

后续目标：
- 继续拆薄内部大块逻辑
- 但在独立模块正式落地前，仍以当前文件为 cleaning 主责任模块

### 7.3 `pipeline_collection.py`
当前角色：
- 预处理
- collection scoring
- 结构提取编排

后续目标：
- 继续把更纯的 extraction / normalization / connector 逻辑向专属模块集中

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
- `pipeline_logging.py`
- `pipeline_clients.py`

### 第二阶段：Collection / Cleaning 共用能力拆分
- `pipeline_normalization.py`
- `pipeline_extraction.py`
- `pipeline_rewrite.py`

### 第三阶段：继续缩小 orchestrator-host
- 把 `multidataset_cleaning_pipeline.py` 中 remaining runtime 逐轮移出
- 在真正落地前，不把目标模块名写成现状

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

## 11. 当前落地状态一句话总结

当前结构里，`multidataset_cleaning_pipeline.py` 仍是 orchestrator shell，但 rewrite runtime 已先行迁入 `pipeline_rewrite.py`；后续应继续把 remaining runtime 逐轮拆出，而不是把未落地模块当成既成事实。
