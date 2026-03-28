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
  - 对应 prompt 入口见：[`docs/pipeline_python_modules_reference.md`](docs/pipeline_python_modules_reference.md) 末尾的“Prompt 附录（与 Agent-heavy 阶段对应）”。
- **Report**
  - 负责写出 `records/*.jsonl`、dataset summary、run summary。

## 最新运行结果

最新一次工作树改动摘要：

- 今日变更记录：[`docs/run_summaries/rewrite_llm_recovery_and_runlog_2026-03-28.md`](docs/run_summaries/rewrite_llm_recovery_and_runlog_2026-03-28.md)
- 重点包括：
  - 第一版纯文本运行日志 `run.log` 已接入，并用于 rewrite 路径排查
  - `chat_json` 已补 caller/stage 维度调试，能区分 rewrite 阶段的请求失败
  - 已确认 rewrite LLM 未生效的根因是 `${OPENAI_API_KEY}` 未展开 + 进程未继承真实环境变量，导致接口返回 `401 Unauthorized / 无效的令牌`
  - 已补上 env 展开与 fail-fast 保护
  - `cmm_math_rewrite_debug` 第二次验证已确认 rewrite LLM 恢复正常，并开始真实影响 rewrite strategy（例如 `split_open -> direct_open`）

最新一次完整 200 样本 rerun benchmark：

- 配置：[`configs/candidate_200_remote.yaml`](configs/candidate_200_remote.yaml)
- 输出：[`outputs/candidate_200_remote/run_38bce3437874d962/summary.json`](outputs/candidate_200_remote/run_38bce3437874d962/summary.json)
- 详细分析：[`docs/run_summaries/candidate_200_remote_rerun_analysis_2026-03-28_run_38bce3437874d962.md`](docs/run_summaries/candidate_200_remote_rerun_analysis_2026-03-28_run_38bce3437874d962.md)

### 总体结果

- 总耗时：**约 13719 秒**（约 **228.7 分钟**，约 **3 小时 48 分 39 秒**）
- 平均每个 processed sample：**约 68.6 秒 / 样本**
- Requested：**200**
- Processed：**200**
- Pass：**114**
- Review：**64**
- Reject：**22**

按本轮实际 processed=200 计算：

- **Pass rate**：**57.0%**
- **Review rate**：**32.0%**
- **Reject rate**：**11.0%**

### 简要结论

- 这轮最重要的结论是：**proxy-enabled 长任务已经能稳定完整跑完 200 样本 benchmark**。
- 当前主要问题已经从“运行链路是否会中断”转成“**不同数据集与当前清洗范式的兼容性差异**”。
- 表现最健康的数据集是：`SeePhys / CMM-Math / SCEMQA / MathVision`。
- 最值得继续拆解的高 review 数据集是：`MM-Math / PhysReason / EMMA-Physics`。
- 最明确应降权甚至剔除的，是：`Multi-Physics`。

### 本轮各数据集表现

- 表现较健康：
  - `SeePhys`：19 / 1 / 0
  - `CMM-Math`：18 / 1 / 1
  - `SCEMQA`：17 / 3 / 0
  - `MathVision`：17 / 3 / 0

- 可保留但 review 成本较高：
  - `EEE-Bench`：13 / 6 / 1
  - `EMMA-Physics`：10 / 10 / 0
  - `Geometry3K`：7 / 10 / 3
  - `PhysReason`：7 / 13 / 0

- 最值得重点排查 / 降权：
  - `MM-Math`：2 / 17 / 1
  - `Multi-Physics`：4 / 0 / 16

### 这轮能说明什么

- **稳定性问题在运行层面已经基本解决**：长任务自然结束，run 有完整 finished 标记。
- **`MM-Math` 的问题更像规则保守，而不是样本本身普遍不可解**：大量样本 `solvability_score=1.0`，但因 `alignment_risky / visual_reference_density_mismatch` 被压到 review。
- **`Multi-Physics` 的问题则更像数据源与当前 open-ended 清洗目标不兼容**：大量样本存在 `missing_grounded_visual_path / text_image_misaligned / low_text_completeness`。
- **这轮暴露的主要矛盾已经不是程序报错，而是策略层张力**：solvability 子系统倾向 pass，但 alignment 风险子系统在高图依赖题上更保守。


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
