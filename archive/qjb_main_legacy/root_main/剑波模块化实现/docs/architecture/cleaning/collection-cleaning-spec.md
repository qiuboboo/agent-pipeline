# Collection / Cleaning Spec（当前主线）

> 本文档是 **Collection / Cleaning 工程规格** 的 canonical owner。
>
> - 总体阶段划分、入口与文档导航请看：[docs/architecture/pipeline-architecture.md](docs/architecture/pipeline-architecture.md)
> - 字段级稳定契约请看：[docs/contracts/PIPELINE_MODULE_CONTRACTS.md](docs/contracts/PIPELINE_MODULE_CONTRACTS.md)
> - rewrite 分流建议请看：[docs/cleaning/rewrite-policy.md](docs/cleaning/rewrite-policy.md)

本文档只负责回答：

1. Collection 阶段采什么、怎么入池。
2. Cleaning 阶段洗什么、怎么 gate。
3. 这些阶段为后续标注 / QA / 发布准备什么前置底座对象。

不在这里重复整条 pipeline 的总体架构叙述，也不在这里写死字段级 schema 全量定义。

## 1. 适用范围与设计目标

适用范围：
- 多模态题目数据集
- 图文联合推理题
- 带图题、图表题、几何题、科学图示题、流程图题、读图题
- 已有原始答案、但未必有结构化解析的数据集
- 不同来源、不同格式、不同质量等级的候选题源

核心目标不是“尽可能多保留题”，而是：
- **稳定筛出适合后续深标和多解法建模的高价值样本**

因此设计上同时追求：
- **可扩展**：继续接更多数据源时不必推翻 schema
- **可审计**：字段来源、改写原因、淘汰原因可追溯
- **可门控**：每一步都有明确通过 / 复核 / 淘汰规则
- **可衔接**：产物可以直接喂给后续标注、QA、发布

## 2. Collection / Cleaning 的边界

### 2.1 Collection 负责什么

Collection 负责把不同来源的原始题目接入系统，形成统一候选题池。

重点包括：
- 样本接入
- 资产登记
- 基本完整性检查
- 来源信息整理
- 稳定 ID 生成
- 初始价值评分
- 候选入池

Collection 不负责：
- 深层语义纠错
- 最终答案规范化裁决
- 最终 `pass / review / reject`
- 解题过程标注
- 多解法建模

### 2.2 Cleaning 负责什么

Cleaning 负责把候选题池转成适合后续标注的标准化样本池。

重点包括：
- 文本规范化
- 字段标准化映射
- 单位统一 / 变量形式统一
- 图像质量判断与模糊图剔除
- 图像区域标准化
- 图文对齐
- 字段缺失补救或淘汰
- rewrite
- 保留 / 复核 / 淘汰 gate

Cleaning 不负责：
- 穷举全部解法
- 构建完整推理图
- 做发布版数据切片

## 3. 阶段接口要求

Cleaning 结束后，后续阶段至少应能直接知道：

1. 题目的唯一主键。
2. 有哪些图、哪些文本、哪些答案资产。
3. 哪些文本是原始文本，哪些是清洗修订文本。
4. 哪些图像区域重要。
5. 图文之间有哪些显式对齐关系。
6. 当前题目的风险点（如文本缺失、图像模糊、答案歧义）。
7. 该题是否允许进入正式标注。

当前主线至少会稳定产出这些前置对象：
- `clean_problem_record`
- `normalized_assets`
- `text_structure_record`
- `visual_structure_record`
- `alignment_record`
- `solvability_report`
- `rewrite_report`
- `open_ended_problem_variants`
- `cleaning_record`
- `reject_record`
- `field_audit_record`

具体稳定字段请以 [docs/contracts/PIPELINE_MODULE_CONTRACTS.md](docs/contracts/PIPELINE_MODULE_CONTRACTS.md) 为准。

## 4. 自动化架构（Collection → Cleaning）

```text
外部数据源
  → 样本接入
  → 资产登记
  → 完整性校验
  → 初始价值评分
  → 候选入池
  → 规范化
  → 图像质量检测
  → 图文解析与对齐
  → 字段缺失处理
  → Cleaning gate
      → pass: 标准化样本池
      → review: 复核队列
      → reject: 淘汰记录库
```

实现视角下可对应到：
- Collection：`pipeline_collection.py` + `cleaning_semantics.py`
- Cleaning：`pipeline_cleaning.py`

## 5. 设计原则

### 5.1 原始数据与生成数据严格分层

必须能区分：
- 原始提供字段
- 自动抽取得到字段
- 模型推断字段
- 规则计算字段
- 人工修订字段

### 5.2 先保留证据，再保留结论

优先保留：
- 原图
- 原始题干文本
- 原始答案文本
- 区域框
- 图文对齐证据
- 清洗日志
- 评分依据

而不是只保留一个脱离来源的“最终文本”。

### 5.3 一切 gate 必须可解释

每次 gate / reject / review 都应能追溯：
- 决策规则
- 阈值
- 命中的信号
- 最终处理动作

### 5.4 Collection 广覆盖，Cleaning 强约束

- Collection 允许高召回，只要候选价值足够即可入池
- Cleaning 必须收紧标准，只保留适合后续深度标注的数据

## 6. 数据对象设计总览

为支撑后续标注 / QA / 发布，Collection / Cleaning 至少围绕以下对象组织：

主表对象：
1. `problem_main_record`
2. `asset_record`
3. `node_record`
4. `cleaning_record`
5. `reject_record`

辅助对象：
6. `normalized_assets`
7. `text_structure_record`
8. `visual_structure_record`
9. `alignment_record`
10. `solvability_report`
11. `rewrite_report`
12. `open_ended_problem_variants`
13. `field_audit_record`

其中：
- 主表对象承载后续消费入口
- 辅助对象负责中间结构、证据与审计轨迹

## 7. 字段来源与可信度分层

建议关键字段至少保留以下维度：
- `value`
- `confidence`
- `field_origin`
- `evidence_refs`
- `last_updated_by`
- `last_updated_at`

`field_origin` 推荐统一理解为以下几类：
- `source_provided`
- `source_derived`
- `rule_generated`
- `model_generated`
- `human_corrected`
- `system_reserved`

这样后续 QA / 人工复核可以直接判断字段是怎么来的。

## 8. 当前主线下的职责落点

### 8.1 Collection 侧

主要由 [benchmark/src/](benchmark/src/) 中的以下模块承担：
- `pipeline_collection.py`：接入、预处理、初步评分、结构提取编排
- `cleaning_semantics.py`：文本结构、视觉结构、对齐、可解性规则层

### 8.2 Cleaning 侧

主要由：
- `pipeline_cleaning.py`：rewrite、gate、records 构建

注意：
- `pass / review / reject` 的最终脚本决策发生在 Cleaning
- Report 只做聚合与写出，不重新裁决

## 9. 与 rewrite policy 的分工

本文档不重复维护完整 rewrite 策略表。

如果你想看：
- 哪类题更适合 `blank_open`
- 哪类题更适合 `keep_open`
- 哪类题更适合 `split_open`
- 哪些数据集只该作为弱 prior

请直接看：[docs/cleaning/rewrite-policy.md](docs/cleaning/rewrite-policy.md)

## 10. 旧文档指针

较早的工作文档位于：[docs/plans/数据采集与清洗自动化搭建文档.md](docs/plans/数据采集与清洗自动化搭建文档.md)。当前主线请以本文档配合 contracts / policy 文档一起阅读。
