# Pipeline Architecture（当前主线）

## 1. 文档定位

本文档是 `agent-pipeline` 当前主线的**总体架构说明与导航入口**：

- 说明流水线的阶段划分、关键产物、稳定入口与“哪里看什么”。
- 不在这里重复写死各模块的硬约束与字段契约细节（那些以约束/契约文档为准）。

**权威约束来源：**
- 架构硬约束与依赖方向：
  - [docs/architecture/PIPELINE_ARCHITECTURE.md](docs/architecture/PIPELINE_ARCHITECTURE.md)
- 字段级稳定契约（records / rewrite / gate 等）：
  - [docs/contracts/PIPELINE_MODULE_CONTRACTS.md](docs/contracts/PIPELINE_MODULE_CONTRACTS.md)

---

## 2. 当前稳定入口与主代码位置

- 稳定 CLI 入口：
  - [run_pipeline.py](run_pipeline.py)
- 主实现与模块拆分后代码：
  - [benchmark/src/](benchmark/src/)

---

## 3. 当前流水线阶段划分（实现视角）

当前可将主线理解为四段：

1. **Setup**
   - 目标：装配配置、构建 run 上下文与输出目录
   - 参考：`pipeline_setup.py`
2. **Collection**
   - 目标：数据集接入 → 预处理 → 结构信号抽取（文本/视觉/对齐/可解性）
   - 参考：`pipeline_collection.py` + `cleaning_semantics.py`
3. **Cleaning**
   - 目标：rewrite（可选 LLM + fallback）→ gate 决策（pass/review/reject）→ 产出 records
   - 参考：`pipeline_cleaning.py`（rewrite runtime 由 `pipeline_rewrite.py` 承接）
4. **Report**
   - 目标：聚合写出 dataset/run summary 与 records JSONL
   - 参考：`pipeline_reporting.py`

---

## 4. 关键稳定产物（读者最常需要的“输出契约”）

本项目重构与迭代期间，以下契约被视为稳定（字段名/结构不随意改动）：

- rewrite report（`strategy / rationale / variants / discard_reason_codes / llm_used`）
- gate / decision 输出（`decision / decision_reason_codes / suggested_next_action / review_required`）
- problem main record 侧关键字段（如 `clean_decision / rewrite_strategy / annotation_ready / qa_precheck_ready`）
- dataset/run summary 统计字段（如 `decision_counts / rewrite_strategy_counts`）

具体字段与样例结构以：
- [docs/contracts/PIPELINE_MODULE_CONTRACTS.md](docs/contracts/PIPELINE_MODULE_CONTRACTS.md)
为准。

---

## 5. 主题文档索引（canonical ownership）

### 5.1 Collection / Cleaning 专项规格（工程落地视角）
- [docs/cleaning/collection-cleaning-spec.md](docs/cleaning/collection-cleaning-spec.md)

### 5.2 Rewrite 策略与分流建议
- [docs/cleaning/rewrite-policy.md](docs/cleaning/rewrite-policy.md)

### 5.3 模块导航（“代码在哪、谁负责什么”）
- [docs/architecture/pipeline-modules-reference.md](docs/architecture/pipeline-modules-reference.md)

### 5.4 Loader 建议（数据集 → 推荐加载方式）
- [docs/loader_recommendations.md](docs/loader_recommendations.md)

### 5.5 运行摘要（保留的代表性产物索引）
- [docs/run_summaries/README.md](docs/run_summaries/README.md)

### 5.6 日期型分析 / 进展 / benchmark 报告
- [docs/reports/](docs/reports/)

---

## 6. 历史与草案

- 仍在演化、尚未升格为 canonical 的草案放在：
  - [docs/plans/](docs/plans/)
- 被 superseded 的历史文档放在：
  - [docs/archive/superseded-docs/](docs/archive/superseded-docs/)
