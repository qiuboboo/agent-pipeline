# EEE-Bench / MathVision pass-only 测试集交付清单（2026-04-08）

## 交付目标
为以下两个数据集各生成 100 题测试集，并保证：
- 全部来自现有 dedup 后的 ready 数据
- 全部为 `pass` 样本
- 难度分布尽量均匀
- 配套导出格式化长 JSON 表
- 图片路径有效且文件存在

数据集：
- EEE-Bench
- MathVision

## 抽取规则
- 来源 ready 包：
  - `ready/eee_bench/run_outputs_similarity_dedup__eee_bench`
  - `ready/mathvision/run_outputs_similarity_dedup__mathvision`
- 过滤条件：
  - `cleaning_records[0].decision == "pass"`
- 抽取数量：
  - 每个数据集 100 题
- 分层方式：
  - 以 `initial_scoring_record.multi_step_score` 为主的难度代理分数
  - 按分位数分成 5 桶后均匀抽样

## 最终 Ready 测试集

### 1. EEE-Bench
- Ready 路径：
  - `ready/eee_bench/run_outputs_similarity_dedup__eee_bench_test100_pass`
- Summary：
  - `ready/eee_bench/run_outputs_similarity_dedup__eee_bench_test100_pass/datasets/eee_bench/summary.json`
- Manifest：
  - `ready/eee_bench/run_outputs_similarity_dedup__eee_bench_test100_pass/datasets/eee_bench/selection_manifest.json`
- 摘要：
  - `selected_samples = 100`
  - `pass_pool_size = 700`
  - `score_min = 0.2`
  - `score_max = 0.86`
  - `score_avg = 0.668`

### 2. MathVision
- Ready 路径：
  - `ready/mathvision/run_outputs_similarity_dedup__mathvision_test100_pass`
- Summary：
  - `ready/mathvision/run_outputs_similarity_dedup__mathvision_test100_pass/datasets/mathvision/summary.json`
- Manifest：
  - `ready/mathvision/run_outputs_similarity_dedup__mathvision_test100_pass/datasets/mathvision/selection_manifest.json`
- 摘要：
  - `selected_samples = 100`
  - `pass_pool_size = 145`
  - `score_min = 0.34`
  - `score_max = 0.9`
  - `score_avg = 0.7075`

## 导出的格式化长 JSON 表

### EEE-Bench
- `ready_problem_exports/run_outputs_similarity_dedup__eee_bench_test100_pass__eee_bench.json`

### MathVision
- `ready_problem_exports/run_outputs_similarity_dedup__mathvision_test100_pass__mathvision.json`

## 图片路径格式
长 JSON 中 `images` 字段当前使用：
- **相对 `ready/` 根目录的相对路径**

例如：
- `eee_bench/run_outputs_similarity_dedup__eee_bench_test100_pass/datasets/eee_bench/artifacts/images/...`
- `mathvision/run_outputs_similarity_dedup__mathvision_test100_pass/datasets/mathvision/artifacts/images/...`

## 文件夹结构（转交结构）
两个测试集均采用同一结构：

```text
ready/<dataset>/<package>/
└── datasets/
    └── <dataset>/
        ├── artifacts/
        │   ├── crops/
        │   └── images/
        ├── samples/
        ├── selection_manifest.json
        └── summary.json
```

## 最终质检结果
### EEE-Bench
- 样本数：100
- 非 pass：0
- 缺图片样本：0
- 长 JSON 条数：100
- 长 JSON 缺失图片路径：0

### MathVision
- 样本数：100
- 非 pass：0
- 缺图片样本：0
- 长 JSON 条数：100
- 长 JSON 缺失图片路径：0

## 本次新增脚本
- `scripts/build_test100_pass_sets.py`

## 当前状态
- 两个 pass-only 测试集已生成完成
- 两个长 JSON 已导出完成
- 最终质检已完成，当前未发现图片缺失或非 pass 混入
