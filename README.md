# agent-pipeline

这是一个 **remote-first** 的多模态数据处理流水线：优先在线下载数据集，统一抽取样本，并产出 cleaning / rewrite / review 等记录。

## 当前状态（2026-03-24）

当前仓库已经从最初的 remote-only 基础打通，进入了更完整的 **全候选数据集 remote intake** 阶段。

### 已经打通的能力

- 默认工作流已经切到 remote-first
- 当前机器上 Hugging Face 可以通过本地代理访问
- GitHub 源的数据摄取可用
- 之前卡住的几个关键连接器问题已经修好：
  - `MathVision` 图像 materialization 已修好（`decoded_image` 现在会变成真实 image asset）
  - `Multi-Physics` 已支持 GitHub JSON 顶层 `example[]` 结构
  - `MM-Math` 已支持 `MM_Math.jsonl + MM_Math.zip` 的 raw-file fallback
  - `PhysReason` 已支持 `PhysReason-mini.zip` / `PhysReason-full.zip` + `problem.json` 的 raw-zip fallback

### 全候选 smoke 状态

当前全候选 remote smoke 配置：

- `configs/all_candidates_remote.yaml`

在连接器修复后，已经完成过一轮全候选 smoke。

最新归档结果：
- `tmp/agent-pipeline_run_archive_2026-03-24_1023/outputs/all_candidates_remote_smoke/run_34f55dd2baab488b/summary.json`

小样本快照如下：

- `SCEMQA`：可接入，但当前样本以 reject 为主
- `Geometry3K`：可接入，当前是 review / reject 混合
- `CMM-Math`：可接入，review 较多，常见 `split_open`
- `MathVision`：可接入，review / reject 混合，连接器已修复
- `MM-Math`：可接入，小样本表现可用
- `SeePhys`：可接入，pass / reject 混合
- `Multi-Physics`：可接入，pass / reject 混合
- `PhysReason`：可接入，pass / reject 混合
- `EEE-Bench`：可接入，小样本表现较强
- `EMMA-Math`：可接入，小样本表现较强
- `EMMA-Physics`：可接入，小样本表现较强

### 200 样本跨学科 benchmark

已经完成一轮更大的跨学科 benchmark：

- 配置：`configs/candidate_200_remote.yaml`
- 报告：`docs/candidate_200_benchmark_report.md`
- 结果：`outputs/candidate_200_remote/run_6be16173d2403a7e/summary.json`

核心数字：
- 200 / 200 processed
- 总耗时：**195 秒**
- 平均吞吐：**0.975 秒 / 样本**
- 严格可用（`pass`）：**90 / 200 = 45.0%**
- 宽松可用（`pass + review`）：**116 / 200 = 58.0%**

当前这套设置下表现最强的几个数据集：
- `EEE-Bench`
- `PhysReason`
- `CMM-Math`

下一步最可能需要做 source-specific threshold 调整的几个数据集：
- `Geometry3K`
- `SCEMQA`
- `SeePhys`
- `MathVision` 的一部分样本

### 当前 rewrite 模式概览

从当前 smoke 和 benchmark 可以看出：

- `blank_open`
  - 常见于 `EEE-Bench`、`EMMA-*`、`Geometry3K`、`MathVision` 的一部分、`SCEMQA` 的一部分
- `keep_open`
  - 常见于 `MM-Math`、`PhysReason`、`SeePhys`、`Multi-Physics`、`MathVision` 的一部分
- `split_open`
  - 常见于 `CMM-Math`

这说明当前主要瓶颈已经不再是“能不能接上数据集”，而是：
- source-specific 的质量阈值
- 按题型做 rewrite-policy 对齐
- 更细粒度地区分“本质开放题”和“标准视觉选择题”

### 当前 prompt 文档替代 / 增强了哪些原 Python 功能

现在仓库里已经引入了一组 prompt 文档，用来替代或增强部分原本更偏硬编码的 Python 流程判断。当前主要对应关系如下：

- `prompts/extract_unified_sample.md`
  - 用于统一抽取样本里的核心字段
  - 主要替代 / 增强原来“从原始 record 里硬编码猜测 question / answer / image / choices”的逻辑
- `prompts/extract_question_answer_image.md`
  - 作为更旧的抽取 prompt fallback
  - 当统一抽取 prompt 不可用时，退回到较早版本的问答图像抽取逻辑
- `prompts/collection/asset_registry.md`
  - 用于判断一个样本的资产注册与完整性
  - 替代 / 增强原来纯 heuristic 的 asset registry 判定
- `prompts/collection/potential_scorer.md`
  - 用于做样本的初步潜力评分
  - 替代 / 增强原来纯 heuristic 的 preliminary value / potential scoring
- `prompts/collection/candidate_registrar.md`
  - 用于做 candidate intake / keep / low_priority / reject 判断
  - 替代 / 增强原来纯 heuristic 的 candidate registrar 决策

也就是说，当前 pipeline 并不是完全依赖固定的 Python 硬编码流程，而是已经逐步把：
- 字段抽取
- 资产完整性判断
- 初步价值评分
- candidate intake 决策

这些环节迁移成“prompt + Python 框架”的混合模式。

如果要继续往 reference-style pipeline 靠，这一层 prompt 文档和 Python 主流程之间的职责边界，后面还需要继续整理清楚。

## 当前默认模式

仓库默认采用 **remote-only** 工作流。

默认多数据集配置：

- `configs/multi_dataset_iter.yaml`

它会在线拉取数据，来源包括：
- GitHub
- Hugging Face

## 当前机器上的代理要求

当前机器上 GitHub 可直连，但 Hugging Face 需要本地代理：

```bash
export http_proxy=http://127.0.0.1:20171
export https_proxy=http://127.0.0.1:20171
```

然后运行：

```bash
python3 benchmark/src/multidataset_cleaning_pipeline.py --config configs/multi_dataset_iter.yaml
```

## 主要入口

### 默认 remote 迭代配置

```bash
python3 benchmark/src/multidataset_cleaning_pipeline.py --config configs/multi_dataset_iter.yaml
```

### 全候选 remote smoke 配置

```bash
python3 benchmark/src/multidataset_cleaning_pipeline.py --config configs/all_candidates_remote.yaml
```

## 当前默认数据集集合

当前默认 remote 迭代配置包含：
- `EEE-Bench`
- `CMM-Math`
- `Geometry3K`
- `MathVision`

## 输出说明

保留下来的代表性摘要在：
- `docs/run_summaries/`

运行时产生的大输出在：
- `outputs/`

一些临时或归档输出可能被移动到：
- `tmp/agent-pipeline_run_archive_*`

## 备注

- 代码内部仍然保留了 local-file 支持，但仓库默认工作流和保留配置已经切到 remote-first。
- 如果 Hugging Face 请求失败，优先检查本地代理 `127.0.0.1:20171` 是否仍然可用。
- `outputs/repo_cache/` 下的缓存目录不属于建议提交进 Git 的源码内容。
