# agent-pipeline

多数据集、多模态题目采集与清洗流水线。

当前主线已经完成一轮**模块拆分**，统一入口是 [run_pipeline.py](run_pipeline.py)，核心实现位于 [benchmark/src/](benchmark/src/)。当前工作重点不再是把单体脚本拆开，而是继续提高 **rewrite 质量**、补强 **运行日志**，并稳定 **LLM 调用链路**。

## 当前阶段在做什么

当前这条线主要有三件事：

1. **把 pipeline 拆成模块化结构**
   - 从大体量主流程拆成 `Setup / Collection / Cleaning / Report` 四段
   - 便于单独定位 ingestion、rewrite、decision、reporting 的问题

2. **补运行日志，缩短排查路径**
   - 已接入第一版纯文本 `run.log`
   - 已补 `SAMPLE / REWRITE / DECISION` 级别日志
   - `chat_json(...)` 已补 `caller/stage` 维度，方便定位是哪一段在请求 LLM

3. **继续追当前最难的问题：rewrite 不理想、LLM 调用不稳定**
   - 有些样本看起来 pass 了，但其实是“伪开放化”
   - 有些样本 rewrite 仍然过保守
   - LLM 链路虽然已经修过一轮 `401 Unauthorized / ${OPENAI_API_KEY}` 问题，但当前仍会出现 `chat_json returned empty`、改写质量不稳定等现象

---

## 当前结构

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

### 四段职责

- **Setup**
  - 参数解析
  - CLI override
  - run 目录与上下文初始化

- **Collection**
  - 数据集接入
  - 样本预处理
  - prompt extraction / heuristic extraction
  - 文本 / 视觉结构抽取
  - 图文对齐、可解性前置信号
  - `initial_scores / priority_score / priority_tier`

- **Cleaning**
  - rewrite
  - quality gate
  - `pass / review / reject` 判定
  - 当前最需要持续打磨的阶段

- **Report**
  - 写出 `records/*.jsonl`
  - dataset summary
  - run summary

---

## 关键代码位置

### 入口
- [run_pipeline.py](run_pipeline.py)
  - 统一运行入口
- [benchmark/src/multidataset_cleaning_pipeline.py](benchmark/src/multidataset_cleaning_pipeline.py)
  - 顶层 orchestrator，串起整条流程

### 模块
- [benchmark/src/pipeline_setup.py](benchmark/src/pipeline_setup.py)
  - Setup 模块
- [benchmark/src/pipeline_collection.py](benchmark/src/pipeline_collection.py)
  - Collection 模块
- [benchmark/src/cleaning_semantics.py](benchmark/src/cleaning_semantics.py)
  - Collection / Cleaning 共用语义分析
- [benchmark/src/pipeline_cleaning.py](benchmark/src/pipeline_cleaning.py)
  - rewrite、质量 gate、决策逻辑
- [benchmark/src/pipeline_reporting.py](benchmark/src/pipeline_reporting.py)
  - records / summary 写出

### 配置与 prompt
- [configs/](configs/)
  - 不同运行场景 YAML
- [prompts/](prompts/)
  - extraction / rewrite / scoring 相关 prompt

### 文档与输出
- [docs/](docs/)
  - 模块说明、run summary、benchmark 分析
- [outputs/](outputs/)
  - 运行输出

---

## 最近已经确认的进展

### 1. 模块拆分已经完成到可用状态
目前主线已经不再依赖单体式实现，日常排查可以沿着：

- Setup
- Collection
- Cleaning
- Report

四段往下钻，定位明显比之前直接在大脚本里找问题更快。

### 2. `run.log` 已接入，rewrite 排查路径打通
当前最小日志覆盖已包含：

- `RUN` start / finish
- `DATASET` start / finish
- `SAMPLE` 字段选择
- `REWRITE` entered / fallback / llm_result
- `DECISION` final decision

相关记录见：
- [docs/run_summaries/rewrite_llm_recovery_and_runlog_2026-03-28.md](docs/run_summaries/rewrite_llm_recovery_and_runlog_2026-03-28.md)

### 3. 一轮关键 LLM 配置问题已经确认并修过
已确认过一次真实根因：

- YAML 中 `api_key: ${OPENAI_API_KEY}` 未展开
- 某些进程环境没有继承到真实 `OPENAI_API_KEY`
- 最终 rewrite 请求带着占位符 token 发送
- 远端返回 `401 Unauthorized / 无效的令牌`

已经补了：
- env placeholder 展开
- fail-fast
- rewrite 相关 debug 日志

但这不代表当前 LLM 链路已经彻底稳定；现在仍存在：
- `chat_json returned empty`
- 单样本偶发 fallback-only rewrite
- 同类样本改写质量不一致

---

## 当前主要问题

## 1. rewrite 质量还不稳定
现在最大的问题不是“有没有 rewrite”，而是：

> **有些样本表面上完成了 rewrite，实际上并没有真正变成高质量开放题。**

典型现象：
- 题干只是轻微改写甚至几乎未改
- `strategy=blank_open`，但题目仍保留选择题语气
- `expected_answer` 仍是编号 / 索引，而不是实际语义答案

### 已暴露出的代表问题

#### SCEMQA：存在“伪开放化”
部分样本会出现：
- 题干看起来变成开放题了
- 但答案仍然是 `1 / 2 / 3` 这种编号
- 真正的选项语义并没有被还原出来

更严重的是，SCEMQA 某些样本的数据源本身只给：
- `answer = 3`
- `choices = ['a', 'b', 'c', 'd', 'e']`

这类 `choices` 只是占位符，不是真实选项文本。很多时候真正语义反而在图里。
因此当前 pipeline 可能会把这类题误当成“高质量开放题”。

#### MM-Math：更像规则过保守
`MM-Math` 在这轮 rerun 中大量进 `review`，更像：
- rewrite 已经产出开放题
- 但 alignment 风险规则过严
- 导致本可放行的样本被压到 `review`

#### Multi-Physics：更像任务目标不兼容
`Multi-Physics` 的问题不像 prompt 微调能解决，而更像：
- 数据源天然强依赖图与选项
- 不适合当前 open-ended 清洗目标

### 2. LLM 调用链路仍不够稳
虽然已经修掉一轮明确的 API key 问题，但今天的排查说明当前还存在：

- 同样的单样本，有时 `llm_result` 正常返回
- 有时又会 `chat_json returned empty`
- 前台 / 后台 / 进程环境差异会影响排查体验

所以当前现状更接近：

> **LLM 链路已经从“经常彻底失效”进展到“能跑，但仍不够稳定”。**

### 3. 部分问题已从资源加载转移到图文对齐
例如 `CMM-Math`：
- 图片 zip-member 路径问题已经基本打通
- 现在主问题不再是图下不来
- 而是 `missing_grounded_visual_path / text_image_misaligned / no_reasoning_path / bad_alignment`

也就是说：

> 资源加载问题在下降，但 grounded reasoning / alignment 问题正在变成新的主矛盾。

---

## 最新 benchmark 结果（2026-03-28）

当前完整 rerun 以：
- [outputs/candidate_200_remote/run_38bce3437874d962/summary.json](outputs/candidate_200_remote/run_38bce3437874d962/summary.json)

为准。

### 总体结果
- Requested：`200`
- Processed：`200`
- Pass：`114`
- Review：`64`
- Reject：`22`
- 总耗时：约 **3 小时 48 分 39 秒**
- 平均：约 **68.6 秒 / processed sample**

### 各数据集结果
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

详细分析：
- [docs/run_summaries/candidate_200_remote_rerun_analysis_2026-03-28_run_38bce3437874d962.md](docs/run_summaries/candidate_200_remote_rerun_analysis_2026-03-28_run_38bce3437874d962.md)

---

## loader 方向的当前判断

相关文档：
- [docs/loader_recommendations.md](docs/loader_recommendations.md)

当前推荐：

- `scemqa` → `hf_standard`
- `cmm_math` → `hf_zip_member`
- `physreason` → `hf_zip_member`
- `mm_math` → `hf_raw_bundle`
- `geometry3k` / `multi_physics` → `github_local`

这里的核心思路是：

> 不再让通用 connector 持续猜资源组织方式，而是在配置 / loader 层显式分流。

---

## 常用命令

### 默认运行
```bash
python run_pipeline.py --config configs/multi_dataset_iter.yaml
```

### 200 样本 benchmark
```bash
python run_pipeline.py --config configs/candidate_200_remote.yaml
```

### 单数据集 / 单样本排查
建议复制一份最小配置到 `logs/` 或临时路径，再单独运行：

```bash
python run_pipeline.py --config logs/scemqa_single_sample.yaml
```

### 关闭 LLM
```bash
python run_pipeline.py --config configs/multi_dataset_iter.yaml --disable-llm
```

---

## 输出结构

典型输出：

```text
outputs/<run-group>/<run_id>/
├─ summary.json
├─ logs/run.log
├─ datasets/<dataset>/summary.json
├─ datasets/<dataset>/records/*.jsonl
└─ datasets/<dataset>/samples/*.json
```

当前排查时最常看的文件：
- `logs/run.log`
- `datasets/<dataset>/records/rewrite_reports.jsonl`
- `datasets/<dataset>/records/field_audit_records.jsonl`
- `datasets/<dataset>/samples/*.json`

---

## 建议先看哪些文档

- [docs/pipeline_python_modules_reference.md](docs/pipeline_python_modules_reference.md)
  - 模块职责与阶段映射
- [docs/loader_recommendations.md](docs/loader_recommendations.md)
  - 各数据集 loader 分流建议
- [docs/run_summaries/README.md](docs/run_summaries/README.md)
  - run summary 保留规范
- [docs/run_summaries/rewrite_llm_recovery_and_runlog_2026-03-28.md](docs/run_summaries/rewrite_llm_recovery_and_runlog_2026-03-28.md)
  - run log 接入与 rewrite LLM 恢复验证
- [docs/run_summaries/candidate_200_remote_rerun_analysis_2026-03-28_run_38bce3437874d962.md](docs/run_summaries/candidate_200_remote_rerun_analysis_2026-03-28_run_38bce3437874d962.md)
  - 当前 200 样本 rerun 分析

---

## 当前一句话结论

> 这条线当前已经完成模块拆分并接入运行日志，主矛盾已经从“脚本太大不好查”和“LLM 完全不工作”逐步转向“rewrite 质量不稳定、部分样本伪开放化、以及 LLM 调用链路仍有偶发空返回/不稳定行为”。
