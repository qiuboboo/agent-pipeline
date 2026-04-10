# seephys 初步放行桶分析（2026-04-11）

- 数据集：`seephys`
- ready 包：`ready/seephys_000_300/datasets/seephys`
- 当前自动状态：`pass=243 / review=56 / reject=1`
- 分析时间：`2026-04-11`

## 1. 初步结构判断

对 `seephys` 的 56 条 `review` 样本做了 reason-code 拉平与边界样本核查，结论如下：

- 这一批 **不像 `physreason` 那样存在整齐、可直接 exact-set 放行的 A 桶**。
- `review` reason-code 组合非常分散：共 **56 个 review 样本，reason-code 组合数也是 56**，基本是一条一个组合。
- 平铺后的高频 reason-code 主要是：
  - `alignment_requires_review`：9
  - `missing_prior_context`：5
  - `visual_evidence_uncertain`：4
  - `answer_incomplete`：3
  - `partial_completeness`：3
  - `normalization_incomplete`：3
  - `notation_inconsistency`：3
  - `question_incomplete`：3
  - `multi_image_coordination_needed`：3

这意味着 `seephys` **第一步更适合从“对齐类误伤桶”入手，而不是从 exact reason-code 桶直接放**。

## 2. 对齐类 9 条样本的初步分桶

当前最值得优先看的，是包含 `alignment_requires_review` 的 **9 条**。对原题文本、reason-codes、risk flags、以及对应图片做了抽样核查后，先做以下粗分：

### 2.1 高置信度：文本基本自洽 / 更像 metadata 或 image-reference 误伤（5 条）

这 5 条看起来最像 `physreason B1` 那种“先放一个保守子桶”的对象：

1. `prob_ed70836971fe6a4d95fd6fe1.json` / source `95`
   - reasons: `alignment_requires_review`, `image_relevance_mismatch`
   - 判断：题面“近视小孔成像估算孔径”基本自洽，图像看起来并非解题必要核心。

2. `prob_f507ee59c5cd02ece288ae97.json` / source `198`
   - reasons: `alignment_requires_review`, `missing_grounded_visual_path`
   - 判断：题面已明确“两个等压过程 + 两个绝热过程”，图仅为标准 `p-V` 示意，文本足以恢复目标。

3. `prob_d126c8b2b5654b762edcf9f6.json` / source `248`
   - reasons: `alignment_requires_review`, `image_reference_metadata_issue`
   - 判断：虽然原题引用 Fig. 1.7，但题干本身已把 A/B/C/D/E、BC 段、磁场区域、自旋转角等要素写得很细，较像 image-reference metadata 问题。

4. `prob_ee96a4b7c08cafe5a4d0c742.json` / source `12`
   - reasons: `alignment_requires_review`, `image_reference_uncertain`
   - 判断：与上一条同属中子干涉仪题，题干对几何和物理条件描述已较完整，图像不是唯一信息源。

5. `prob_cb06ae7fc6ad04249fbea340.json` / source `200`
   - reasons: `alignment_requires_review`, `visual_grounding_incomplete`
   - 判断：题目是定性比较 metallic grating 改成 transmission grating 后是否仍辐射；图更多是背景示意，文本已给出关键设定。

### 2.2 相邻观察桶：文本大概率可恢复，但仍有一定图示语义依赖（1 条）

1. `prob_42a98da9e442b03ead20a6e3.json` / source `66`
   - reasons: `alignment_requires_review`, `visual_evidence_uncertain`
   - 判断：势阱哈密顿量已给出，图中的一维切片更像示意；但题目确实借助图来指示“越过井顶”的位置语义，保守起见先放到相邻观察桶，不并入高置信度首桶。

### 2.3 暂不放：更像真视觉依赖（3 条）

1. `prob_2d7ca75d35bc56e3c74cf846.json` / source `64`
   - reasons: `alignment_requires_review`, `visual_grounding_missing`
   - 判断：题面只有“Find the expression for the speed of the transverse elastic wave.”，几乎无法脱离图示独立成立。

2. `prob_9c67d428639e52917a3a0cd9.json` / source `74`
   - reasons: `alignment_requires_review`, `missing_grounded_visual_path`, `multi_image_coordination_needed`
   - 判断：本质上要从图/曲线读取信息，且是多图协调，不能归为 metadata 误伤。

3. `prob_e4e2d4bf30ef874bea44e29a.json` / source `242`
   - reasons: `alignment_requires_review`, `visual_grounding_uncertain`
   - 判断：题面“this system”指代强依赖图像，不能按文本自洽样本处理。

## 3. 当前判断

`seephys` 的最自然切入点不是做一个 `physreason A` 式的 exact bucket，而是：

- 先把 `alignment_requires_review` 里的 **高置信度 metadata / image-reference 误伤子桶（当前 5 条）** 单独导出；
- 把 **1 条相邻观察样本** 单独列出；
- 明确 **3 条真视觉依赖样本继续 hold**。

## 4. 建议的下一步

建议按以下顺序继续：

1. 导出 `seephys` 高置信度 5 条候选 JSON（不改统一 policy config，先走自定义 candidate-json 分支）；
2. 补写对应 decision doc / ledger，保持 provenance；
3. 如再人工复核一轮仍稳定，再执行正式 post-ready manual release；
4. `prob_42a98...` 作为相邻观察样本单列，不并入首桶；
5. 其余 3 条维持 hold。

## 5. 附注

另外还观察到少量“文本看起来可恢复，但并不属于 alignment 误伤首桶”的样本，例如：

- `prob_190214888a0a6dd9f9062df6.json` / source `85`
  - `minor_symbol_definition_gap`, `partial_completeness`
- `prob_7b264677f121fd0af0e7de75.json` / source `29`
  - `normalization_incomplete`, `notation_inconsistency`

这些更像后续第二阶段再看，不建议和首个 `alignment` 子桶混放。
