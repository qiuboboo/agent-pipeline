# 两个分支工作架构图（PPT 草图）

## A. 严格贴 qjb 文档口径的正式版

### A1. 四阶段主流程

```text
┌──────────────────────────────────────────────────────────────┐
│ 0. 配置准备（Setup）                                        │
│   0.1 参数加载（Config Load）                               │
│   0.2 参数校验（Validation）                                │
│   0.3 运行初始化（Run Initialization）                      │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ 1. 采集（Collection）                                       │
│   1.1 数据接入（Ingestion）                                 │
│   1.2 预处理（Preprocess）                                  │
│   1.3 信息提取（Extract）                                   │
│   1.4 初始评分 / 候选入池（Scoring / Pooling）              │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ 2. 清洗（Cleaning）                                         │
│   2.1 规范化（Normalization）                               │
│   2.2 结构/对齐/可解性分析（Semantics）                     │
│   2.3 改写 / 转换（Rewrite / Transform）                    │
│   2.4 判定 / 打分（Gate / Scoring）                         │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ 3. 汇总输出（Report）                                       │
│   3.1 records 写出                                          │
│   3.2 dataset summary                                       │
│   3.3 run summary                                           │
│   3.4 sample bundles / artifacts                            │
└──────────────────────────────────────────────────────────────┘
```

---

### A2. 模块映射

```text
0. 配置准备（Setup）
   ├─ pipeline_setup.py
   ├─ YAML / env / CLI 参数合并
   ├─ 参数校验
   └─ run context / 输出目录初始化

1. 采集（Collection）
   ├─ pipeline_collection.py
   ├─ pipeline_extraction.py
   ├─ 数据接入（source intake / ingestion）
   ├─ 预处理（preprocess）
   ├─ 原始字段提取（extract）
   └─ 初始评分 / 候选入池（potential scoring / pooling）

2. 清洗（Cleaning）
   ├─ pipeline_normalization.py
   ├─ cleaning_semantics.py
   ├─ pipeline_rewrite.py
   ├─ pipeline_cleaning.py
   ├─ 规范化（normalization）
   ├─ 图文结构 / 对齐 / 可解性分析（semantics）
   ├─ 改写 / 转换（rewrite / transform）
   └─ pass / review / reject gate

3. 汇总输出（Report）
   ├─ pipeline_reporting.py
   └─ summary / records JSONL / sample bundles / artifacts
```

---

### A3. 公共支撑层

```text
公共支撑层（贯穿 0~3 全阶段）
├─ pipeline_types.py
├─ pipeline_utils.py
├─ pipeline_clients.py
└─ pipeline_logging.py
```

可以理解为：

- `types`：统一数据结构与稳定 dataclass
- `utils`：纯工具函数与通用 helper
- `clients`：外部模型 / 服务客户端
- `logging`：运行级与样本级结构化日志

---

### A4. 职责边界与限制

```text
Collection 负责：
- 样本接入
- 资产登记
- 基本完整性检查
- 来源整理
- 稳定 ID 生成
- 初始价值评分
- 候选入池

Collection 不负责：
- 深层语义纠错
- 最终答案裁决
- 最终 pass/review/reject
- 解题过程标注
- 多解法建模
```

```text
Cleaning 负责：
- 文本规范化
- 字段标准化映射
- 图像质量判断
- 图文对齐
- rewrite
- gate 决策

Cleaning 不负责：
- 穷举全部解法
- 构建完整推理图
- 发布版数据切片
```

```text
全局稳定约束：
- 模块应保持小而独立
- 参数名 / 标签名 / 输出 schema 保持稳定
- 没有明确计划与文档，不改变可观察行为
- 每个模块应可独立测试
- 保留有诊断价值的日志
- 代码改动必须同步更新文档
- 字段级 contract 变更必须先文档化
```

---

## B. 适合放 PPT 的蓝色流程图版（内容草图）

### B1. 主流程图文案

```text
                ┌────────────────────┐
                │ 0. Setup           │
                │ 配置准备            │
                │ 参数加载 / 校验      │
                └─────────┬──────────┘
                          │
                          ▼
                ┌────────────────────┐
                │ 1. Collection      │
                │ 采集                │
                │ 接入 / 预处理 / 提取 │
                └─────────┬──────────┘
                          │
                          ▼
                ┌────────────────────┐
                │ 2. Cleaning        │
                │ 清洗                │
                │ 规范化 / 改写 / gate│
                └─────────┬──────────┘
                          │
                          ▼
                ┌────────────────────┐
                │ 3. Report          │
                │ 汇总输出            │
                │ records / summary  │
                └────────────────────┘
```

### B2. 底部支撑层

```text
────────────────────────────────────────────────────────
支撑层：types / utils / clients / logging
────────────────────────────────────────────────────────
```

### B3. 右侧约束栏（PPT 可以单独放一列）

```text
Constraints
- schema stable
- logs preserved
- no observable behavior drift
- docs updated with code
- stage boundaries stay clear
```

---

## C. 推荐你在 PPT 里怎么画

### C1. 正式版（适合“架构说明”页）
用 A 版：
- 左到右或上到下画四个大阶段
- 每个阶段下写 3~4 个职责
- 下面单独拉一条公共支撑层
- 右侧再放“边界与限制”

### C2. 简化版（适合“总览”页）
用 B 版：
- 四个蓝色圆角框
- 中间竖箭头连接
- 底部一条浅蓝色 support bar
- 右侧一个浅灰色 constraints box

---

## D. 最适合放进 PPT 的一句话总结

> 这套 pipeline 可以抽象为 Setup、Collection、Cleaning、Report 四大阶段；其中 Collection 负责接入与候选入池，Cleaning 负责规范化、改写与 gate，Report 负责聚合写出，而 types / utils / clients / logging 作为公共支撑层贯穿全流程，并受到稳定契约约束。
