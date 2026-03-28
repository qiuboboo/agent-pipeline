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

## 最新运行结果与问题总结（2026-03-28）

### 今日 200 样本 rerun 结果

本次完整 rerun 以 `outputs/candidate_200_remote/run_38bce3437874d962/summary.json` 为准。

- run id：`run_38bce3437874d962`
- Requested：`200`
- Processed：`200`
- Pass：`114`
- Review：`64`
- Reject：`22`
- 总耗时：约 **3 小时 48 分 39 秒**

各数据集结果：

- `SCEMQA`：`17 / 3 / 0`
- `Geometry3K`：`7 / 10 / 3`
- `CMM-Math`：`18 / 1 / 1`
- `MathVision`：`17 / 3 / 0`
- `MM-Math`：`2 / 17 / 1`
- `SeePhys`：`19 / 1 / 0`
- `Multi-Physics`：`4 / 0 / 16`
- `PhysReason`：`7 / 13 / 0`
- `EEE-Bench`：`13 / 6 / 1`
- `EMMA-Physics`：`10 / 10 / 0`

详细分析见：
- [`docs/run_summaries/candidate_200_remote_rerun_analysis_2026-03-28_run_38bce3437874d962.md`](docs/run_summaries/candidate_200_remote_rerun_analysis_2026-03-28_run_38bce3437874d962.md)

### 这轮暴露出的主要问题

#### 1. `MM-Math` review 过高，更像规则过保守，不像样本本身不可用

这轮 `MM-Math` 结果是：
- `2 / 17 / 1`

代表性样本：
- `prob_c11f4ea0de15f097c71f67f5`
- `rewrite_3c69d9a80d4b280babf8cd3e`

现象：
- 改写后已经是开放题
- `strategy = keep_open`
- 答案也明确
- 但仍会因为下列原因进入 `cleaning_review`：
  - `ALIGNMENT_RISKY`
  - `MAJOR_ALIGNMENT_CONFLICT`
  - `VISUAL_REFERENCE_DENSITY_MISMATCH`
  - `alignment_risky`

说明：
> 当前 `MM-Math` 的主要问题更像 **alignment 风险规则过保守**，而不是样本本身无法开放化。

#### 2. `Multi-Physics` reject 很高，更像数据类型与当前清洗目标不兼容

这轮 `Multi-Physics` 结果是：
- `4 / 0 / 16`

代表性样本：
- `prob_eabb60f1cc3409186a5d4e2f`
- `rewrite_0a78d16a7d1bb640621a7648`

现象：
- 原题强依赖图与选项语义
- 改写后仍缺 grounded reasoning path
- 最终直接 `clean_rejected`

说明：
> `Multi-Physics` 当前问题更像 **数据源与 open-ended 清洗目标不兼容**，不是简单调一条 rewrite prompt 就能解决。

#### 3. `SCEMQA` 暴露出“伪开放化”问题

在 200 样本 run 中，`SCEMQA` 的 `source_problem_id=1`：
- `problem_id = prob_d2e18289d6790272f6e58c9b`
- `rewrite_id = rewrite_387bf969e5416a40048d38e3`
- `strategy = blank_open`

实际 rewrite 结果是：
- `rewritten_question_text` 仍保留：`which of the following intervals?`
- `expected_answer_type = numeric`
- `expected_answer = 1`

这说明它虽然被标成 open rewrite，但实际上：
- 题面没有真正脱离选择题语气
- 答案没有从编号 `1` 还原成真实语义答案（如区间）

说明：
> 当前部分样本存在 **“看似开放化，实则仍保留选择题壳和编号答案”** 的问题。

#### 4. 选择题 rewrite 的边界还没有完全系统化

今天进一步确认了一条很重要的边界：

- **纯图索引题**（答案只是图中编号/位置/字母）应该直接丢弃
- **可脱离选项独立表达语义的选择题** 应改写为开放题

已有正确丢弃例子：
- `EEE-Bench`
- `prob_576407d71953067c542b419e`
- `rewrite_ab016b581953260cbe745c45`
- `rewrite_strategy = drop_image_index`
- `decision_reason_codes` 包含 `pure_image_index_choice`

但这条边界当前还没有完全沉成统一 rewrite policy，所以不同数据集、不同样本间实现仍不一致。

### 今日额外定位出的 `CMM-Math` 进展与问题

虽然 200 样本 rerun 中 `CMM-Math` 表面结果不差（`18 / 1 / 1`），但今天顺着样本链继续查，确认了两件事：

#### 已确认解决
- `ecnu-icalk/cmm-math` 的图片资源在 Hugging Face repo 的 `images.zip` 中
- 不是 repo 根目录下的裸 jpg 文件
- 目前 `HuggingFaceConnector` 已补入 zip-member 读取逻辑
- 10 样本验证 `outputs/cmm_math_fixrun_10_zipmember/run_5616b56e101d6ab8` 已证明：
  - `has_image_paths=6`
  - `with_loaded_images=6`
  - `has_image_paths_but_image_count_0=0`

#### 当前仍存在的问题
在带 LLM 的 10 样本验证 `run_71927aaf0d637bc5` 中：
- `processed=10`
- `pass=5`
- `reject=5`
- `blank_open=10`
- `llm_used=9/10`

说明当前 `CMM-Math` 已经不是“图下不来”或“LLM 不调用”的问题，而是：
- 带图题虽然能改写、能加载图
- 但仍大量因为以下原因被 reject：
  - `missing_grounded_visual_path`
  - `text_image_misaligned`
  - `implicit_visual_dependency`
  - `no_reasoning_path`
  - `bad_alignment`

也就是说：
> `CMM-Math` 当前主问题已经从 **资源加载失败** 转移到 **图文对齐 / grounded reasoning 不稳定**。

### 当前阶段结论

这轮 200 样本 rerun 说明：

- 运行链路本身已经能稳定完成 200 样本
- 当前主要问题已经从“程序能不能跑完”转成“不同数据集与当前清洗范式是否兼容”
- 其中最典型的几类问题是：
  - `MM-Math`：规则过保守，review 偏高
  - `Multi-Physics`：数据类型与当前 open-ended 目标不兼容
  - `SCEMQA`：存在伪开放化样本
  - `CMM-Math`：图片加载已修通，但多模态 grounding 仍不稳

## 常看文档

- [`docs/pipeline_python_modules_reference.md`](docs/pipeline_python_modules_reference.md)
  - Python 模块、函数职责、阶段映射说明。
- [`docs/loader_recommendations.md`](docs/loader_recommendations.md)
  - 数据集 → 推荐 loader 类型映射，说明哪些集更适合继续走通用 HF connector，哪些应切换到 zip-member / raw-bundle / GitHub-local loader。
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
