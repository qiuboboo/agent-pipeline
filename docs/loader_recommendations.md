# Dataset → Recommended Loader Type

本文档整理当前 `agent-pipeline` 各 benchmark 数据集更适合走哪类资源加载器（loader），目的是减少通用 `HuggingFaceConnector` 的“猜路径/猜资源组织方式”行为，把明显需要特化的资源链路显式分流出来。

## Loader 类型定义

### 1. `hf_standard`
适用于典型 Hugging Face 数据集：
- row 中直接提供可用 `image` / `decoded_image` / bytes / path
- 不需要额外 raw bundle、zip-member、repo 特化资源发现

### 2. `hf_zip_member`
适用于图片资源被打包在 zip 中的数据集：
- row 中常给出 zip 内成员名，如 `9171.jpg`
- repo 中真实资源是 `images.zip` / `image.zip`
- loader 需要支持：下载 zip、建立成员名索引、按 basename 读取图片

### 3. `hf_raw_bundle`
适用于原始资源由 json/jsonl + zip 等成套文件组成的数据集：
- 不适合继续只靠通用 row/image 字段推断
- 需要专门入口加载原始 bundle，再组装 `UnifiedSample`

### 4. `github_local`
适用于 GitHub / 本地文件资源逻辑：
- 不走 Hugging Face image loader
- 资源发现和文件定位应由 GitHub connector / 本地路径逻辑负责

## Dataset → Loader mapping

| Dataset | Source | Recommended loader | Why |
|---|---|---|---|
| `scemqa` | Hugging Face | `hf_standard` | 当前没有证据显示其图片资源组织需要 zip/raw 特化；现阶段主要问题在 rewrite / LLM 链路而非资源加载 |
| `geometry3k` | GitHub | `github_local` | 资源来自 GitHub / 本地文件，不属于 Hugging Face image loader 范畴 |
| `cmm_math` | Hugging Face | `hf_zip_member` | 已确认 repo 中存在 `images.zip`，而 row 中给出的是 `9171.jpg` 这类成员名，不适合继续假设 repo 中存在裸 jpg 文件 |
| `mathvision` | Hugging Face | `hf_standard` | 目前尚无证据表明其需要 zip/raw 级特化 |
| `mm_math` | Hugging Face | `hf_raw_bundle` | 代码中已经存在 `sample_from_mm_math_raw_files()`，说明其更适合走 raw/jsonl+zip 成套入口 |
| `seephys` | Hugging Face | `hf_standard` | 当前运行结果稳定，未暴露 loader 级结构性问题 |
| `multi_physics` | GitHub | `github_local` | 核心问题是数据类型与清洗目标不兼容，不是 HF 资源组织问题 |
| `physreason` | Hugging Face | `hf_zip_member` | 配置 note 已标明 `zip fallback`，明显更适合 zip-member / zip-fallback 路线 |
| `eee_bench` | Hugging Face | `hf_standard` | 当前主要问题更像内容质量 / 裁剪，不是资源加载器结构问题 |
| `emma_physics` | Hugging Face | `hf_standard` | review 高主要由 alignment 风险驱动，目前没有 loader 级证据说明必须特化 |

## Recommended grouping

### A. Continue using `hf_standard`
- `scemqa`
- `mathvision`
- `seephys`
- `eee_bench`
- `emma_physics`

这些数据集当前更适合继续走通用 Hugging Face image loader，后续若再暴露出 zip/raw 资源组织问题，再考虑升级为专门 loader。

### B. Prioritize `hf_zip_member`
- `cmm_math`
- `physreason`

这类数据集的典型特征是：
- repo 中存在 zip 资源包
- row 中给的是 zip 内成员名或可映射文件名
- 通用 `HuggingFaceConnector` 继续按单文件路径猜测，容易持续失败

### C. Keep / formalize `hf_raw_bundle`
- `mm_math`

这类数据集已经实际证明更适合：
- 显式下载 raw json/jsonl
- 显式下载 zip bundle
- 再由特化 loader 组装样本

### D. Keep outside HF loader family
- `geometry3k`
- `multi_physics`

这两类不应混入 Hugging Face image loader 讨论，应继续由 GitHub / 本地文件逻辑维护。

## Why `cmm_math` failed while other zip-like datasets could still run

`cmm_math` 的特殊之处在于它同时踩中了三层误导：

1. row 中给出了看起来像裸文件路径的成员名（如 `9171.jpg`）
2. 本地 datasets cache 中并没有实际图片实体文件
3. 真实图片资源位于 `images.zip`，而通用 loader 初始假设是 repo 中存在单文件 jpg

因此它不像已经有专门 raw/zip 入口的数据集那样直接走正确路径，而是先被误当成“普通 HF image/path 数据集”处理，导致长时间停留在错误资源假设上。

## Engineering recommendation

建议在配置层显式引入 loader 类型，而不是继续让 connector 猜测：

```yaml
loader_type: hf_standard        # 普通 HF image loader
loader_type: hf_zip_member      # zip 内成员名取图
loader_type: hf_raw_bundle      # json/jsonl + zip/raw bundle
loader_type: github_local       # GitHub / 本地文件资源
```

这样可以把：
- 数据集级资源组织
- 资源发现方式
- 图片提取策略

从通用 `HuggingFaceConnector` 里抽出来，减少“能跑但总在边缘失效”的隐式假设。

## Immediate priorities

### Highest priority
1. `cmm_math`
2. `physreason`

### Secondary priority
3. `mm_math`

原因是：
- `cmm_math` 已明确验证 `images.zip` 路线
- `physreason` 在配置上已明示 `zip fallback`
- `mm_math` 虽已有特化入口，但仍值得抽象进统一 `hf_raw_bundle` 设计中
