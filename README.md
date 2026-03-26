# agent-pipeline

这是一个 **remote-first** 的多模态数据处理流水线：优先在线下载数据集，统一抽取样本，并产出 cleaning / rewrite / review 等记录。

## 接下来的计划

下一阶段主要做三件事：

### 1) 检查高 reject 数据集

优先抽查以下数据集的 `reject_records` / `problem_main_records`：

- `SCEMQA`
- `Geometry3K`
- `SeePhys`
- `MM-Math`

重点看：

- 是否存在明显误杀
- 是图像质量、文本完整性、图文对齐还是 rewrite / gate 导致 reject
- 哪些 reject 模式是 source-specific 的稳定问题

### 2) 修改 prompt

优先检查和调整：

- `prompts/extract_unified_sample.md`
- `prompts/collection/asset_registry.md`
- `prompts/collection/potential_scorer.md`
- `prompts/collection/candidate_registrar.md`

重点目标：

- 减少本应 `pass` 的样本被推到 `review`
- 降低高 reject 数据集上的保守偏差
- 让 source-specific 的题型判断与 rewrite-policy 更贴合真实分布

### 3) 小规模样本质量检测

针对当前已经接入成功的数据集，按学科和题型抽取更小规模样本做人工检查，重点看：

- `pass / review / reject` 的真实质量分布
- 不同数据源上的误判模式
- 哪些数据集需要单独调 threshold 或 rewrite policy

## 分支说明

当前主要关注三个分支：

- `main`
  - 当前主要存放 qiuboboo 这边的阶段性进度、仓库说明、稳定运行入口和对外展示内容。
- `feat/multi-dataset-iter`（qiuboboo）
  - 当前共同开发的主分支，由当前 GitHub 账号负责上传和同步，主要承载多数据集 remote-first intake、连接器修复、rewrite / review 流程迭代，以及 benchmark / smoke 配置更新。
- `ler`（LERFOE）
  - LERFOE 侧的进度分支，主要用于记录对应方向的阶段性进展；当前不是主开发入口。

目前主仓库的实际开发重心在 `main`，并已将 `ler` 中的 `benchmarkallinone` 实现吸收到当前主线。

## 当前主仓库结构

```text
agent-pipeline/
├─ benchmark/
│  ├─ src/                              # 多数据集流水线主入口与核心逻辑
│  └─ outputs/                          # benchmark 相关输出
├─ benchmarkallinone/                   # 从 ler 导入的整合实现，当前作为对照保留
├─ configs/                             # 不同运行场景的 YAML 配置
├─ docs/                                # 报告、设计说明、阶段性总结
├─ plans/                               # 下一步计划与设计草案
├─ outputs/                             # 当前保留的运行输出
├─ prompts/                             # 抽取、评分、改写等提示词模板
├─ run_pipeline.py                      # 当前正式入口
└─ archive/                             # 历史主线归档
```

结构上可以分成五层：

1. **运行入口层**：`run_pipeline.py` 与 `benchmark/src/`
2. **配置层**：`configs/`
3. **文档层**：`docs/` 与 `plans/`
4. **提示词层**：`prompts/`
5. **历史与过渡层**：`archive/`、`benchmarkallinone/`

## 当前进度（2026-03-26）

项目已经完成从旧主线到 `benchmarkallinone` 主线实现的切换，并在新主线上复跑了一轮 200 样本 benchmark。

### 已完成的环境与能力

- 已完成 `ler` 中 `benchmarkallinone` 实现导入
- 已归档旧主线 Python / prompt / 核心配置到：
  - `archive/pre-ler-main-python-2026-03-25/`
- 已将当前正式主线切到：
  - `run_pipeline.py`
  - `benchmark/src/multidataset_cleaning_pipeline.py`
  - `benchmark/src/cleaning_semantics.py`
- 已验证新主线：
  - Python 语法编译通过
  - `--help` 正常
  - 本地 1-sample 验证通过
  - 200 样本 remote benchmark 可完整跑通
- 当前机器上 Hugging Face 需要本地代理访问

### 当前已经得到的结果

#### 1) 已完成新主线最小运行验证

- 本地示例配置在 `--disable-llm` 下已成功处理 1 个样本
- 说明当前新主线在入口、配置读取、本地样本处理链路上已经可运行

#### 2) 已完成新主线 200 样本跨学科 benchmark 复跑

- 配置：[configs/candidate_200_remote.yaml](configs/candidate_200_remote.yaml)
- 报告：[docs/candidate_200_benchmark_report_rerun_2026-03-26.md](docs/candidate_200_benchmark_report_rerun_2026-03-26.md)
- 结果：`outputs/candidate_200_remote/run_1dbbbab6d8b51fd6/summary.json`

核心结果：
- 200 / 200 processed
- 严格可用（`pass`）：**63 / 200 = 31.5%**
- 宽松可用（`pass + review`）：**112 / 200 = 56.0%**

### 与旧 200 样本 benchmark 的差异

旧结果（README 中记录的 `run_6be16173d2403a7e`）：
- pass：90
- review：26
- reject：84
- strict usable：45.0%
- lenient usable：58.0%

新主线复跑结果（`run_1dbbbab6d8b51fd6`）：
- pass：63
- review：49
- reject：88
- strict usable：31.5%
- lenient usable：56.0%

### 当前阶段判断

目前的主要瓶颈已经不是“主线能不能跑通”，而是：

- 高 reject 数据集为什么持续偏弱
- 新主线为什么把更多样本打到 `review`
- source-specific 的 prompt / threshold / rewrite-policy 是否仍需调整

### 当前表现较强的数据集

- `CMM-Math`
- `EEE-Bench`
- `MathVision`
- `Multi-Physics`

### 当前更需要继续调优的数据集

- `SCEMQA`
- `Geometry3K`
- `SeePhys`
- `MM-Math`
- `PhysReason`（review 偏多）
- `EMMA-Physics`（review 偏多）

## 当前默认模式

仓库默认采用 **remote-only** 工作流。

默认多数据集配置：
- [configs/multi_dataset_iter.yaml](configs/multi_dataset_iter.yaml)

它会在线拉取数据，来源包括：
- GitHub
- Hugging Face

## 当前机器上的代理要求

当前机器上 GitHub 可直连，但 Hugging Face 需要本地代理：

```bash
export http_proxy=http://127.0.0.1:20171
export https_proxy=http://127.0.0.1:20171
```

运行命令：

```bash
python3 run_pipeline.py --config configs/multi_dataset_iter.yaml
```

## 主要入口

### 默认 remote 迭代配置

```bash
python3 run_pipeline.py --config configs/multi_dataset_iter.yaml
```

### 200 样本 benchmark 配置

```bash
python3 run_pipeline.py --config configs/candidate_200_remote.yaml
```

### 全候选 remote smoke 配置

```bash
python3 run_pipeline.py --config configs/all_candidates_remote.yaml
```

## 输出说明

保留下来的代表性摘要在：
- [docs/run_summaries/](docs/run_summaries/)

阶段性 benchmark / 分析报告在：
- [docs/](docs/)

运行时产生的大输出在：
- [outputs/](outputs/)

## 备注

- 如果 Hugging Face 请求失败，优先检查本地代理 `127.0.0.1:20171` 是否仍然可用。
- `outputs/repo_cache/` 下的缓存目录不属于建议提交进 Git 的源码内容。
- `benchmarkallinone/` 当前仍作为迁移对照保留，后续可继续收敛进正式主线结构。
