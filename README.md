# agent-pipeline

多数据集、多模态题目采集与清洗流水线。

当前主线采用四段结构：**Setup → Collection → Cleaning → Report**。统一入口是 [`run_pipeline.py`](run_pipeline.py)，核心实现位于 [`benchmark/src/`](benchmark/src/)。

## 当前结构与功能

```text
run_pipeline.py
    ↓
multidataset_cleaning_pipeline.py
    ├─ Setup       -> pipeline_setup.py
    ├─ Collection  -> pipeline_collection.py + cleaning_semantics.py
    │                 ├─ ingestion / preprocess
    │                 ├─ initial collection scoring
    │                 └─ structure extract
    ├─ Cleaning    -> pipeline_cleaning.py
    └─ Report      -> pipeline_reporting.py
```

- **Setup**
  - 负责参数解析、配置覆盖、run 目录和上下文初始化。
- **Collection**
  - 负责数据集接入、样本预处理、文本/视觉结构抽取、图文对齐与可解性分析。
  - 其中结尾单独整理了一小段 **initial collection scoring**，用于计算 `initial_scores`、`priority_score`、`priority_tier`。
- **Cleaning**
  - 负责 rewrite、质量 gate、最终 `pass / review / reject` 判定。
  - **这是当前最需要 Agent 的阶段**：prompt extraction、rewrite、solvability / reasoning support 都主要集中在这里。
- **Report**
  - 负责写出 `records/*.jsonl`、dataset summary、run summary。

## 最新运行结果

最新一次工作树改动摘要：

- 今日变更记录：[`docs/run_summaries/geometry3k_ingest_ranking_fix_2026-03-27.md`](docs/run_summaries/geometry3k_ingest_ranking_fix_2026-03-27.md)
- 重点包括：
  - Geometry3K ingest 排序修复，避免 Collection 阶段误扫大型辅助 CSV
  - Collection 末尾的 initial collection scoring 显式拆块
  - Cleaning gate 从硬 reject 短路改为统一风险原因记录
  - 远端模型 API key 改为优先走环境变量，且补充 chat_json 调试能力
  - 后续 smoke 还记录了三个代表性案例：CMM-Math 的 `split_open` 误伤已修复；MM-Math 有一个应当保留为 `review` 的高视觉密度几何题样本；SCEMQA 的隐式函数图题通过弱视觉锚点补偿从 reject 提升到 pass

最新一次 200 样本 benchmark：

- 配置：[`configs/candidate_200_remote.yaml`](configs/candidate_200_remote.yaml)
- 输出：[`outputs/candidate_200_remote/run_6cd93f19b5ab1d93/summary.json`](outputs/candidate_200_remote/run_6cd93f19b5ab1d93/summary.json)
- 对比记录：[`docs/candidate_200_benchmark_comparison_2026-03-26_run_6cd93f19b5ab1d93.md`](docs/candidate_200_benchmark_comparison_2026-03-26_run_6cd93f19b5ab1d93.md)

### 运行时间（这是非agent提取内容版的）

- 总耗时：**约 602.1 秒**（约 **10.0 分钟**）
- 平均每个 processed sample：**约 3.01 秒 / 样本**
- 说明：这里按本次实际启动与 summary 写出时间近似计算

### 总体结果

- Requested：**200**
- Processed：**200**
- Pass：**61**
- Review：**48**
- Reject：**91**
- **严格可用率**：**30.5%**
- **宽松可用率**：**54.5%**

### 与上一轮复跑结果对比

上一轮基线见 [`docs/candidate_200_benchmark_report_rerun_2026-03-26.md`](docs/candidate_200_benchmark_report_rerun_2026-03-26.md)：

| 指标 | 上一轮 | 本轮 | 变化 |
|---|---:|---:|---:|
| Pass | 63 | 61 | **-2** |
| Review | 49 | 48 | **-1** |
| Reject | 88 | 91 | **+3** |
| 严格可用率 | 31.5% | 30.5% | **-1.0pt** |
| 宽松可用率 | 56.0% | 54.5% | **-1.5pt** |

### 本轮数据集表现

表现较强：
- `CMM-Math`：13 / 6 / 1，宽松 **95.0%**
- `EEE-Bench`：12 / 6 / 2，宽松 **90.0%**
- `MathVision`：11 / 3 / 6，宽松 **70.0%**
- `Multi-Physics`：10 / 0 / 10，严格 **50.0%**

需要继续调优：
- `Geometry3K`：0 / 0 / 20，严格/宽松都 **0.0%**
- `SCEMQA`：2 / 0 / 18，宽松 **10.0%**
- `SeePhys`：3 / 1 / 16，宽松 **20.0%**
- `MM-Math`：0 / 10 / 10，严格 **0.0%**，宽松 **50.0%**
- `PhysReason`：4 / 11 / 5，review 偏多
- `EMMA-Physics`：6 / 11 / 3，review 偏多

## 项目结构

```text
agent-pipeline/
├─ run_pipeline.py
├─ benchmark/
│  └─ src/
│     ├─ multidataset_cleaning_pipeline.py
│     ├─ pipeline_setup.py
│     ├─ pipeline_collection.py
│     ├─ cleaning_semantics.py
│     ├─ pipeline_cleaning.py
│     └─ pipeline_reporting.py
├─ configs/
├─ prompts/
├─ docs/
├─ outputs/
├─ benchmarkallinone/
└─ archive/
```

## 目录与文件说明

### 入口与主线
- [`run_pipeline.py`](run_pipeline.py)
  - 统一运行入口。
- [`benchmark/src/multidataset_cleaning_pipeline.py`](benchmark/src/multidataset_cleaning_pipeline.py)
  - 顶层 orchestrator，串联整条流水线。

### 四个阶段模块
- [`benchmark/src/pipeline_setup.py`](benchmark/src/pipeline_setup.py)
  - Setup：参数解析、配置覆盖、run 目录与上下文初始化。
- [`benchmark/src/pipeline_collection.py`](benchmark/src/pipeline_collection.py)
  - Collection：数据集接入、样本预处理、结构化中间结果生成。
  - 内部现在把 Collection 末尾的 **initial collection scoring** 单独整理成了一个小块：先产出 `initial_scores`，再生成 `priority_score` / `priority_tier`。
- [`benchmark/src/cleaning_semantics.py`](benchmark/src/cleaning_semantics.py)
  - Collection/Cleaning 支撑：文本结构、视觉结构、对齐、可解性分析。
- [`benchmark/src/pipeline_cleaning.py`](benchmark/src/pipeline_cleaning.py)
  - Cleaning：rewrite、质量 gate、`pass/review/reject` 判定。
- [`benchmark/src/pipeline_reporting.py`](benchmark/src/pipeline_reporting.py)
  - Report：写出 records、dataset summary、run summary。

### 其他目录
- [`configs/`](configs/)
  - 不同运行场景的 YAML 配置。
- [`prompts/`](prompts/)
  - 抽取、评分、改写相关提示词。
- [`docs/`](docs/)
  - 模块说明、benchmark 报告、运行摘要文档。
- [`outputs/`](outputs/)
  - 运行产物输出目录。
- [`benchmarkallinone/`](benchmarkallinone/)
  - 旧整合实现，当前作为对照保留。
- [`archive/`](archive/)
  - 历史主线归档。

## 常用命令

### 默认运行

```bash
python run_pipeline.py --config configs/multi_dataset_iter.yaml
```

### 200 样本 benchmark

```bash
python run_pipeline.py --config configs/candidate_200_remote.yaml
```

### 关闭 LLM / agent

```bash
python run_pipeline.py --config configs/multi_dataset_iter.yaml --disable-llm
```

## 常看文档

- [`docs/pipeline_python_modules_reference.md`](docs/pipeline_python_modules_reference.md)
  - Python 模块、函数职责、阶段映射说明。
- [`docs/run_summaries/README.md`](docs/run_summaries/README.md)
  - 运行摘要保留规范。
- [`docs/candidate_200_benchmark_report_rerun_2026-03-26.md`](docs/candidate_200_benchmark_report_rerun_2026-03-26.md)
  - 200 样本 benchmark 复跑报告。
- [`docs/candidate_200_benchmark_comparison_2026-03-26_run_6cd93f19b5ab1d93.md`](docs/candidate_200_benchmark_comparison_2026-03-26_run_6cd93f19b5ab1d93.md)
  - 本次最新复跑与上一轮结果对比。

## 输出位置

典型输出结构：

```text
outputs/<run-group>/<run_id>/
├─ summary.json
├─ datasets/<dataset>/summary.json
├─ datasets/<dataset>/records/*.jsonl
└─ datasets/<dataset>/samples/*.json
```

## 备注

- 当前以 [`benchmark/src/`](benchmark/src/) 为主线实现。
- [`benchmarkallinone/`](benchmarkallinone/) 和 [`archive/`](archive/) 不是当前首页重点，只作历史对照保留。
- 若 Hugging Face 拉取失败，优先检查本地网络/代理环境。
