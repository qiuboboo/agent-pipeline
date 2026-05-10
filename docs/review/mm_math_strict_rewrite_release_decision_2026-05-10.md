# MM-Math 严格改写题放行决策记录（2026-05-10）

## 适用范围

本记录适用于当前本地 `outputs` 中按 `source_problem_id` 全局去重后选中的 MM-Math 样本。

本次判断的核心问题是：大量 `mm_math` 样本被自动标成 `review`，并不是因为题目不可用，而是因为图片分辨率、metadata 路径、alignment 风险或轻度视觉证据不足触发了保守 gate。参照 GeoQA-Plus 的处理方式，本次只放行“改写后开放题本身完整、答案可验证、图文能共同支持、数学逻辑自洽”的严格候选子集。

## 放行策略

本次新增显式候选桶，而不是按 reason code 一刀切：

- 候选文件：`docs/review/mm_math_strict_rewrite_release_candidates_2026-05-10.json`
- 候选 key：`strict_rewrite_usable_review_candidates`
- policy bucket：`mm_math.release_buckets.strict_rewrite_release`

候选样本必须满足：

- 原始 decision 为尚未通过既有 policy 放行的 `review`。
- 存在 open-ended variant，且有明确题干和 expected answer。
- `solvability_score` 达到可解，答案可验证，目标清楚，改写完整。
- cleaning agent 判断为 `complete` 且 `understandable`。
- 图片如有低清、小图、轻度裁切或 metadata 路径不一致，必须仍然能支持题意理解，或题目本身不依赖该风险字段。
- 数学结论和答案需要自洽，不能依赖错误原题答案或不可见条件。

以下情况继续不放行：

- 题干关键条件缺失，必须靠图、解析或隐含上下文补出。
- 图文语义冲突、图片不可用、图片缺失或目标图无法定位。
- 答案不一致、存在多答案歧义，或标准答案与推理明显冲突。
- 相似三角形对应顺序、角/边命名等会改变答案的轻度但实质性歧义。
- answer format 非最小答案、答案嵌在完整解析中、解析文本有明显不一致等格式/语义边界风险。

## 数量统计

当前 MM-Math 去重选中样本：

- release 前选中：`4000`
- 原始 pass：`1291`
- 原始 review：`2702`
- 原始 reject：`7`
- 已有 A 桶释放 review：`849`
- 本次严格改写候选桶行数：`1610`
- 预计 release 后可进入 ready：`3750`
- 预计仍丢弃 review：`243`
- reject 仍不放行：`7`

候选桶生成时排除项统计：

- `already_released_by_existing_policy`：`849`
- `strict_quality_or_semantic_bad`：`81`
- `agent_complete` 未通过：`140`
- `agent_understandable` 未通过：`137`

候选桶内 rewrite strategy 分布：

- `keep_open`：`1609`
- `blank_open`：`1`

## 抽样例子

### `prob_278dd6a0c9280c8387a950cf` / `51402984.png`

- 自动状态：`review`
- 风险标记：`alignment_requires_review`, `low_image_resolution`
- 题目：三角形周长为 `20cm`，`BC=6cm`，内切圆切线 `MN` 分别交 `AB`、`CA` 于 `M`、`N`，求 `△AMN` 周长。
- 答案：`8 cm`
- 判断：图片低清是轻度风险，但题干、图形关系和切线等长推理完整；答案可由周长关系验证，因此放行。

### `prob_8ea9ed1a4a659de2a0dc6c04` / `52914187.png`

- 自动状态：候选集中按当前去重结果作为 review 评估。
- 风险标记：metadata/image path 不一致、answer manifest schema 非标准。
- 题目结论：角度答案为 `70°`。
- 判断：主要问题是元数据和 schema 记录不一致，不是数学题干或答案错误；候选检查中 agent 判断为 `understandable`，因此纳入严格候选。

### `prob_e90c781839ea2588c73e906e` / `52914191.png`

- 自动状态：候选集中按当前去重结果作为 review 评估。
- 风险标记：`visual_evidence_weak`
- 题目结论：面积答案为 `13.5`。
- 判断：视觉证据偏弱，但图文仍能支持题意，题目目标和答案自洽；属于可放行的轻度视觉风险。

### `prob_186b9aa7645e8a7fce717d1b` / `52836781.png`

- 自动状态：`review`
- 风险标记：`alignment_requires_review`, `minor_visual_risk`, `minor_label_cropping`
- 题目：`C` 在 `BG` 上，以 `BC`、`CG` 为边作正方形，`S1+S2=40`，`BG=8`，求阴影面积。
- 答案：`6`
- 判断：标签轻度裁切不影响读题，代数关系 `a+b=8`、`a^2+b^2=40` 可推出 `ab=12`，阴影面积 `6`；放行。

### `prob_058b31137a099ef50d6c1c57` / `55403711.png`

- 自动状态：`review`
- 风险标记：`alignment_requires_review`, `visual_evidence_uncertain`, `low_resolution_but_usable`
- 题目：直角三角形中，`CD` 为斜边 `AB` 上的高，`∠ACD=40°`，求 `∠B`。
- 答案：`40°`
- 判断：图片低清但可用，题干条件足够，角度关系清楚；放行。

### 边界样本：`prob_41318e803047adf162775cf4` / `51351735.png`

- 风险标记：`minor_similarity_order_ambiguity`
- 判断：相似三角形对应顺序可能实质影响比例关系和答案，虽然题面看起来可解，但属于会改变数学语义的边界风险。本次严格桶不放行。

### 边界样本：`prob_bee246b065dde8e9d0379e49` / `51435251.png`

- 风险标记：`answer_format_nonminimal`
- 判断：题目本身能算出 `OD=3`，但 answer text 是完整解析而不是最小答案。为保持严格候选桶边界，本次不纳入 `strict_rewrite_release`。

## 执行结论

本次可以放行 `strict_rewrite_usable_review_candidates` 中的 `1610` 条。它们不是“所有 review 直接放行”，而是经过严格候选文件显式列出的子集。对于关键条件缺失、语义冲突、不可用图片、答案不一致以及会影响答案的轻度歧义样本，继续保持不放行。
