# agent-pipeline 仓库说明

本仓库用于多模态题目样本的抽取、清洗与候选集构建。核心目标是把不同来源的数据统一为结构化记录，并输出可用于后续标注与评测的数据。

## 目录结构（简要）

```text
agent-pipeline/
├─ run_pipeline.py                     # 主脚本（本地文件输入 -> 统一抽取/评分 -> 输出）
├─ configs/                            # 运行配置（不同场景的 YAML）
│  ├─ all_available.local.yaml
│  ├─ intake_relaxed_smoke.local.yaml
│  ├─ m3cot_mini.local.yaml
│  ├─ multi_dataset_benchmark.local.yaml
│  └─ multi_dataset_iter.local.yaml
├─ prompts/                            # LLM 提示词模板
│  ├─ extract_unified_sample.md
│  ├─ preliminary_value_scoring.md
│  ├─ extract_question_answer_image.md
│  └─ collection/
├─ m3cot/                              # 样例数据（json/jsonl + images）
├─ outputs/                            # 当前输出目录
│  └─ samples.jsonl
├─ benchmark/                          # benchmark 版本流水线与输出
│  ├─ src/
│  └─ outputs/
├─ docs/                               # 设计与说明文档
└─ logs/                               # 日志
```

## 当前 Python 结果（重点）

目前仓库中可直接看到的输出是 [outputs/samples.jsonl](outputs/samples.jsonl)：

1. 总记录数：5 条。
2. 每条包含字段：problem_id、question_text、answer_text、image_paths。
3. 样例特征：当前 answer_text 仍是选项字母（如 A/B/C），属于轻量抽取结果。

示例（节选）：

```json
{"problem_id":"m3cot_physical-commonsense-1398","question_text":"What is the likely purpose of the troll statue under the bridge?","answer_text":"B","image_paths":[".../m3cot/images/000000.png"]}
```

## run_pipeline.py 讲解

文件位置：[run_pipeline.py](run_pipeline.py)

### 1) 配置与数据结构

在 [run_pipeline.py](run_pipeline.py#L30) 到 [run_pipeline.py](run_pipeline.py#L91) 定义：

1. ModelConfig：模型地址、模型名、温度、超时。
2. ThresholdConfig：pass/review/reject 相关阈值。
3. DatasetSpec：数据集来源、字段映射、是否强制依赖图片。
4. PipelineConfig：全局运行参数（输出目录、采样策略等）。
5. UnifiedSample：统一样本结构。

### 2) 工具函数层

在 [run_pipeline.py](run_pipeline.py#L94) 到 [run_pipeline.py](run_pipeline.py#L301)：

1. 文本标准化与缺失值判断。
2. JSON/JSONL 写入。
3. 哈希与稳定 ID 生成。
4. 图片转 data URL（供多模态模型输入）。

### 3) 抽取与评分

在 [run_pipeline.py](run_pipeline.py#L316) 到 [run_pipeline.py](run_pipeline.py#L700)：

1. 有 API Key：调用 LLM，根据 prompts 进行统一字段抽取与初评分。
2. 无 API Key：走启发式抽取和启发式评分，保证可离线跑通。
3. 多选题会尝试把字母答案映射回选项文本。

### 4) 数据源连接器

在 [run_pipeline.py](run_pipeline.py#L396) 到 [run_pipeline.py](run_pipeline.py#L624)：

1. LocalFileConnector：本地 json/jsonl 输入。
2. GitHubConnector：自动 clone 仓库并发现候选数据文件。
3. HuggingFaceConnector：通过 datasets 加载公开数据集。

### 5) 清洗决策与记录构建

在 [run_pipeline.py](run_pipeline.py#L667) 到 [run_pipeline.py](run_pipeline.py#L1100)：

1. 根据评分、图文一致性、改写策略做 pass/review/reject。
2. 生成 problem_main_record、asset_records、alignment_record、rewrite_record 等结构化记录。

### 6) 主流程与命令行入口

在 [run_pipeline.py](run_pipeline.py#L1117) 到 [run_pipeline.py](run_pipeline.py#L1299)：

1. PromptExtractionPipeline 负责按数据集执行、落盘、汇总。
2. main() 解析参数并运行，支持 input、dataset-key、dataset-name、subject、limit、reset-output。

最小示例：

```bash
python run_pipeline.py m3cot/mini_test/test.json --dataset-key m3cot_mini --dataset-name M3CoT-mini --subject multimodal --limit 5
```

如果需要使用 YAML 场景化配置，请使用 benchmark 版本入口 [benchmark/src/multidataset_cleaning_pipeline.py](benchmark/src/multidataset_cleaning_pipeline.py)，该脚本支持 --config。

## 多数据集测试运行命令

推荐使用 benchmark 入口配合 YAML，一次性跑多个数据集。

### 1) 环境准备（PowerShell）

```powershell
conda activate agent
$env:OPENAI_API_KEY="你的key"
```

### 2) 多数据集快速测试（小样本）

```powershell
python benchmark/src/multidataset_cleaning_pipeline.py --config configs/multi_dataset_benchmark.local.yaml
```

### 3) 多数据集迭代测试（样本更多）

```powershell
python benchmark/src/multidataset_cleaning_pipeline.py --config configs/multi_dataset_iter.local.yaml
```

### 4) 全量可用源冒烟测试

```powershell
python benchmark/src/multidataset_cleaning_pipeline.py --config configs/all_available.local.yaml
```

### 5) 放宽策略冒烟测试

```powershell
python benchmark/src/multidataset_cleaning_pipeline.py --config configs/intake_relaxed_smoke.local.yaml
```

说明：

1. 要跑哪些数据集，修改对应 YAML 中 datasets 列表。
2. 输出目录由 runtime.output_root 控制。
3. [run_pipeline.py](run_pipeline.py) 主要用于单数据集参数模式，不是多数据集 YAML 入口。