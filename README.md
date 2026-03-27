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

最新一次 200 样本长任务 benchmark：

- 配置：[`configs/candidate_200_remote.yaml`](configs/candidate_200_remote.yaml)
- 输出：[`outputs/candidate_200_remote_long/run_cf4370b4bf405a34/summary.json`](outputs/candidate_200_remote_long/run_cf4370b4bf405a34/summary.json)
- 详细分析：[`docs/run_summaries/candidate_200_remote_long_analysis_2026-03-27.md`](docs/run_summaries/candidate_200_remote_long_analysis_2026-03-27.md)

### 总体结果

- 总耗时：**约 9311 秒**（约 **155.2 分钟**，约 **2 小时 35 分**）
- 平均每个 processed sample：**约 49.0 秒 / 样本**
- Requested：**200**
- Processed：**190**
- Pass：**123**
- Review：**55**
- Reject：**12**

按本轮实际 processed=190 计算：

- **Pass rate**：**64.7%**
- **Review rate**：**28.9%**
- **Reject rate**：**6.3%**

### 简要结论

- 这轮最重要的结论是：**主流程已经能稳定跑完整轮长任务**，exit code 0，远端模型调用没有再次把整轮打死。
- 当前主要瓶颈已经从“跑不通”转成“**对高视觉依赖题偏保守**”，表现为 `review` 偏多，而不是 `reject` 大面积飙升。
- 除 `Geometry3K` 外，其余数据集都跑满了 20 个样本。
- `Geometry3K` 当时仍只 ingest 到 10 个 demo samples，因此本轮 `Geometry3K` 结果**不应作为正式评估结论**。

### 本轮各数据集表现

- 表现较健康：
  - `SeePhys`：19 / 1 / 0
  - `CMM-Math`：18 / 2 / 0
  - `SCEMQA`：17 / 2 / 1
  - `Multi-Physics`：17 / 2 / 1
  - `MathVision`：16 / 4 / 0

- 主要偏保守：
  - `MM-Math`：2 / 18 / 0
  - `PhysReason`：7 / 12 / 1
  - `EMMA-Physics`：11 / 9 / 0

- 本轮暂不采信正式结论：
  - `Geometry3K`：2 / 1 / 7（仅处理到 10 个，受旧 ingest 入口影响）

### 这轮能说明什么

- **稳定性问题基本解决**：长任务可自然结束。
- **`CMM-Math` 的 `split_open` 修复已在大样本里得到验证**。
- **`MM-Math` / `PhysReason` / `EMMA-Physics` 是下一步最值得继续拆 review 的三块**。
- **Geometry3K 需要使用修复后的官方 zip ingest 入口重新定点评估**。
- **另外已确认一个重要运行限制**：这轮 190 条 processed 样本虽然都产出了 rewrite strategy，但 `rewrite_reports` 中没有任何一条 `llm_used = True`，说明本轮实际跑到的是 fallback-only rewrite，而不是 LLM rewrite fully active；详细说明见长文档。
- **后续 `cmm_math_rewrite_debug` 定点验证已进一步钉死直接原因**：rewrite 阶段不是没进入、也不是没 choices，而是 `chat_json` 请求被接口按 `401 Unauthorized / 无效的令牌` 拒绝；高概率根因是当前 `from_yaml()` 不展开 `${OPENAI_API_KEY}`，而某些 `nohup` 进程没有带到真实环境变量，导致发出了占位符 token。
- **在补上 env 展开和 fail-fast 后，第二次 `cmm_math_rewrite_debug` 已验证修复生效**：`run_43bac1c988f5f011` 得到 `18 / 1 / 1`，且 `run.log` 连续出现 `llm_result strategy=...`，说明 rewrite LLM 已恢复正常，并开始真实影响 rewrite strategy（例如 `split_open -> direct_open`）。

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
