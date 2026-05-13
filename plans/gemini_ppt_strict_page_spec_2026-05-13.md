# Gemini 直接生成 PPT 严格逐页规格书

生成时间：2026-05-13

用途：把本次 ready pass / production subset / taxonomy analysis 汇报做成一份可直接用于组会的 PPT。本文档不是资料说明，而是 Gemini 生成 PPT 时必须逐页执行的施工图。

## 0. 总体要求

### 0.1 汇报主线

整份 PPT 只讲一条主线：

> 数据不是简单堆进 ready，而是经过 production pipeline、outputs-to-ready 门控、review release 策略和 taxonomy/feature analysis 后，形成可分析、可汇报、可用于论文附录的数据资产。

### 0.2 页数

生成 8 页内容页。不需要封面，不需要感谢页。

页码与章节必须固定：

1. `01 / SCOPE`：数据口径与汇报主线
2. `02 / ASSETS`：Ready Pass 数据资产结构
3. `03 / FRAMEWORK`：Taxonomy 与数据特征分析框架
4. `04 / PIPELINE`：生产子集 Pipeline1 处理流程与成本
5. `05 / FUNNEL`：Outputs 到 Ready 的转化漏斗
6. `06 / RELEASE`：Review release 质量门控
7. `07 / TAXONOMY`：Ready 数据题型分布
8. `08 / DIAGNOSIS`：Review 原因诊断与结论

### 0.3 统一视觉风格

必须贴近“中山大学学术组会 PPT”风格：

- 16:9 横版。
- 白底为主。
- 页面最上方放 5-7 px 深绿色横线，颜色 `#005825`。
- 每页左上标题前放一条竖向深绿色短线。
- 右上角放页码，例如 `03 / FRAMEWORK`，小号浅绿色。
- 主标题 28-34 pt，黑色或深灰，加粗。
- 小标题 16-20 pt，深绿色，加粗。
- 正文 12-15 pt，深灰。
- 数据数字可以 22-32 pt，加粗，深绿色。
- 卡片圆角不要超过 8 px。
- 卡片背景使用白色或极浅灰 `#F7F9F8`，边框用浅灰 `#E4E9E6`。
- 一页只使用深绿色、黑/深灰、浅灰，最多少量琥珀色用于 warning/hold。
- 不要卡通人物，不要 3D，不要大面积渐变，不要科技大屏，不要暗色背景。

### 0.4 页面文字禁令

PPT 页面上禁止出现内部文件名、目录名、扩展名和字段名。下面这些只能作为事实来源或素材定位，不能出现在页面文字中：

- `dataset_summary`
- `taxonomy.csv`
- `sample_list.csv`
- `representative_examples.csv`
- `feature_stats.csv`
- `calibration_samples.csv`
- `paper_subject_pie.png`
- `paper_final_category_bar.png`
- `paper_complexity_scatter.png`
- `paper_question_length_boxplot.png`
- `Final Taxonomy Package`
- `Ready Pass Samples`
- `CSV`
- `json`
- `outputs/`
- `ready/`

如果必须引用数据来源，只写“统计口径：全局 ready 资产”或“统计口径：5 月 7 日以来生产子集”，不要写文件名。

注意：本节是生成约束，不是 PPT 页面内容；不要把这份禁令列表复制到任何页面上。

### 0.5 数据口径硬约束

必须分清两个口径，不能混写到同一张总览卡里：

全局 ready 资产：

- `29,966` candidates
- `21,555` ready pass
- `21` datasets
- `6` domains
- `14` coarse taxonomy classes
- pass rate `71.93%`

5 月 7 日以来生产子集：

- `47` production runs
- `12,114` processed samples
- `88,169` requests
- `77,290` successful requests
- `65,589` text requests
- `22,580` multimodal requests
- `7.28` requests/sample
- `91.95` sec/sample
- `12.63` sec/request
- final ready `19,113`

## 1. 第 1 页：数据口径与汇报主线

### 标题

> Pipeline1 到 Ready Pass：数据生产、门控与分析

右上角页码：`01 / SCOPE`

### 核心结论

> 本次汇报分开说明“全局 ready 资产”和“5 月 7 日以来生产子集”：前者回答最终数据规模与结构，后者回答数据如何被生产、筛选和放行。

### 版式

使用左右双栏。不要做成普通三张卡片。

左栏标题：`全局 ready 资产`

左栏用 4 个纵向指标：

- `29,966` candidates
- `21,555` ready pass
- `21` datasets
- `14` taxonomy classes

左栏底部一句：

> 用于最终数据结构、领域覆盖和题型特征分析。

右栏标题：`生产子集`

右栏用 4 个纵向指标：

- `47` production runs
- `12,114` processed samples
- `88,169` requests
- `19,113` final ready

右栏底部一句：

> 用于解释 Pipeline1 成本、outputs-to-ready 转化和 review release。

中间用一条细竖线分隔，并在两栏之间放一个小标签：

> 两个口径分开汇报，不混合求和

### 设计要求

- 左栏标题和右栏标题都用深绿色。
- 数字要大，说明文字要短。
- 页面底部放一条浅灰注释条：

> 本 PPT 的重点不是展示文件目录，而是解释数据资产如何形成、如何过滤、最终具有什么结构。

### 禁止

- 不要放代码图标。
- 不要写内部路径。
- 不要把 `29,966` 和 `19,113` 写成同一个总量。

## 2. 第 2 页：Ready Pass 数据资产结构

### 标题

> Ready Pass 数据资产结构图

右上角页码：`02 / ASSETS`

### 核心结论

> 最终 ready pass 资产覆盖 6 个主领域、21 个核心数据集，不是单一数学或单一物理集合；它已经具备领域覆盖、题型 taxonomy 和特征统计三层分析结构。

### 版式

使用“上方结论 + 下方数据集矩阵表 + 右侧真实图表”的布局。第 2 页重点是把 21 个数据集名字完整展示出来，最好用紧凑表格或领域分组矩阵，不要只写概念框。

#### 左侧：规模锚点

左侧放一个深绿色竖向大卡片，卡片标题写：

> Ready Pass

卡片中放 3 个大数字：

- `21,555` samples
- `6` domains
- `21` datasets

卡片底部小字：

> 全局 ready pass 口径

#### 中间：21 个数据集矩阵表

中间放一个紧凑表格或领域分组矩阵，必须完整写出 21 个数据集名称。推荐用 6 个领域分组，每组包含“数据集 / 样本数 / 类别数”三列。不要使用 Dataset A、Dataset B 这样的占位符。

表格内容如下：

| 领域 | 数据集 | 样本数 | 类别数 |
| --- | --- | ---: | ---: |
| 数学 | mm_math | 4,229 | 8 |
| 数学 | geoqa_plus | 2,766 | 14 |
| 数学 | mathvision | 1,879 | 11 |
| 数学 | geometry3k | 879 | 11 |
| 数学 | scemqa_math | 189 | 10 |
| 数学 | cmm_math | 142 | 5 |
| 物理 | seephys | 1,499 | 9 |
| 物理 | phyx | 1,139 | 11 |
| 物理 | physreason | 905 | 6 |
| 物理 | multi_physics | 525 | 9 |
| 物理 | emma_physics | 266 | 7 |
| 物理 | sciverse_physics | 239 | 8 |
| 化学 | emma_chemistry | 864 | 3 |
| 化学 | sciverse_chemistry | 247 | 11 |
| 化学 | scemqa_chemistry | 111 | 10 |
| 生物 | ai2d_biology | 1,315 | 8 |
| 生物 | sciverse_biology | 219 | 9 |
| 生物 | scemqa_biology | 64 | 8 |
| 地理 | geosqa | 1,757 | 9 |
| 地理 | ai2d_geography | 298 | 8 |
| 电子电路 | eee_bench | 2,023 | 12 |

如果表格太密，可以改为“领域分组矩阵”：每个领域一个浅灰分组块，块内逐行写 `数据集名  样本数  类别数`，但 21 个名字必须全部出现。

领域总量可作为每组标题右侧小标签：

- 数学 `10,084`
- 物理 `4,573`
- 化学 `1,222`
- 生物 `1,598`
- 地理 `2,055`
- 电子电路 `2,023`

#### 右侧：真实统计图

必须嵌入真实统计图，不要只画图标，不要只写“统计图”。

放两张图即可，避免拥挤：

1. 领域分布图，图题写：`领域分布`
2. 题型结构柱状图，图题写：`题型结构`

如果空间不足，优先保留领域分布图和题型结构柱状图，不放复杂度散点图。

### 底部声明

页面底部放一条浅绿色结论条：

> 数据资产已经从“样本集合”整理为“领域覆盖 + 题型 taxonomy + 特征统计”的分析对象。

### 禁止

- 不要出现“文件包”“目录”“CSV”“dataset_summary”“taxonomy.csv”。
- 不要放代表例题。
- 不要用一个大文件夹图标概括全部内容。
- 不要使用 Dataset A/B/C 占位，必须写真实数据集名称。
- 不要只写抽象词，例如“Statistical Figures”“Complexity Analysis”，必须放真实图。

## 3. 第 3 页：Taxonomy 与数据特征分析框架

### 标题

> Taxonomy 与数据特征分析框架

右上角页码：`03 / FRAMEWORK`

### 核心结论

> 这一步不是简单“打标签”，而是把 21 个数据集统一到可比较的题型结构和特征矩阵中，使后续能够回答：题型是否多样、哪些领域占主导、哪些数据集偏科、哪些样本复杂。

### 版式

使用“思维导图式框架”：左侧完整列出 21 个数据集，中间是 taxonomy 分类流程，右侧是数据特征分析维度；底部是代表例题与统计图输出。这个页面可以参考用户给出的 Gemini 示例图，但必须把 Dataset A/B/C 占位替换为真实数据集名称。

#### 左侧：21 个 Ready 数据集

标题：

> 21 个 Ready 数据集

左侧用按领域分组的紧凑列表或小表格完整写出 21 个数据集名称。不要把 21 条做成过长单列导致拥挤；建议分为数学、物理、化学、生物、地理、电子电路 6 个小组。不要只写“21 个数据集”。

必须出现：

1. mm_math
2. geoqa_plus
3. mathvision
4. geometry3k
5. scemqa_math
6. cmm_math
7. seephys
8. phyx
9. physreason
10. multi_physics
11. emma_physics
12. sciverse_physics
13. eee_bench
14. emma_chemistry
15. sciverse_chemistry
16. scemqa_chemistry
17. ai2d_biology
18. sciverse_biology
19. scemqa_biology
20. geosqa
21. ai2d_geography

左侧 6 个领域小组各用 1 条细灰色连线汇入中间流程框，形成“多领域数据集输入 → taxonomy 统一”的视觉关系。不要为 21 个数据集各画一条长线，否则页面会太乱。

左侧底部小字：

> 规模范围：64 - 4,229 samples；覆盖 6 个主领域

底部小标签：

> 输入层：样本与领域覆盖

#### 中间：Taxonomy 分类流程

标题：

> Taxonomy 分类流程

中间用一个浅绿色大框，内部画 4 步纵向流程：

```text
规则初稿
    ↓
高 Other 数据集细分
    ↓
抽样校准
    ↓
最终 Taxonomy
```

每一步旁边放短指标：

- 规则初稿：自动规则标签
- 高 Other 数据集细分：7 个重点数据集
- 抽样校准：每类 20-50 条
- 最终 Taxonomy：3-14 类/数据集，14 个一级类

必须点名 high-other 深分数据集：

> eee_bench、geometry3k、geoqa_plus、scemqa_math、multi_physics、phyx、seephys

从“最终 Taxonomy”节点向下连接到底部“代表例题”模块。

底部小标签：

> 分类层：从局部题型到统一 taxonomy

#### 右侧：数据特征分析维度

标题：

> 数据特征统计

右侧使用竖向图标按钮或小卡片，写 6 个特征维度：

- 题长
- 答案长度
- 复杂度
- Multi-step
- 视觉类型
- 需图像比例

从中间“最终 Taxonomy”节点向右连到这 6 个维度，形成“taxonomy 输出 → feature analysis”的视觉关系。

底部小标签：

> 特征层：从题目文本到复杂度结构

#### 下方：代表例题与统计图输出

下方可以放一个“代表例题（中英文题意）”模块，但不要放具体长题干。只写：

> 187 类代表题均已补中文题意

旁边放 3 个小图输出模块：

1. 领域分布
2. 题长箱线图
3. 复杂度散点图

### 推荐页面结构草图

```text
标题

[21个真实数据集列表]  ──多条灰线──>  [Taxonomy分类流程]  ──>  [6个特征维度]
                                            │
                                            ↓
                          [187类代表题中文题意] [领域分布] [题长箱线图] [复杂度散点图]

底部一句结论：统一 taxonomy 让不同数据集可以横向比较。
```

### 底部结论

> 该框架把 pass 样本转化为可比较的数据结构：能看整体分布，也能定位单个数据集的题型偏向。

### 禁止

- 不要只写“Taxonomy 分类逻辑”“数据多维特征分析”这种空标题。
- 不要使用 Dataset A/B/C 占位。
- 不要放长英文原题示例。
- 不要放黄色大引用框。
- 不要把三张大卡片做得很空，左侧必须完整出现 21 个真实数据集名称。

## 4. 第 4 页：生产子集 Pipeline1 处理流程与成本

### 标题

> Pipeline1：从原始样本到结构化 outputs

右上角页码：`04 / PIPELINE`

### 核心结论

> 生产子集显示 Pipeline1 是多节点加工流程：每个样本平均触发约 7.28 次请求，累计请求耗时约 91.95 秒。

### 版式

中间放一条横向流程线，每个节点向上或向下连接一个小对话框。不要放底部大指标条。

流程节点固定为：

```text
原始样本 → 规范化 → Prompt 构造 → 模型改写 → 图像资产 → 清洗验证 → outputs
```

节点气泡：

| 节点 | 位置 | 气泡短句 | 指标 |
| --- | --- | --- | --- |
| 原始样本 | 上 | 生产窗口子集 | 12,114 processed |
| 规范化 | 下 | 统一字段和元数据 | 47 runs |
| Prompt 构造 | 上 | 多轮 LLM 请求 | 7.28 requests/sample |
| 模型改写 | 下 | 文本与多模态处理 | 88,169 requests |
| 图像资产 | 上 | 保留视觉 grounding | 22,580 multimodal |
| 清洗验证 | 下 | 通过质量门控 | 77,290 successful |
| outputs | 上 | 进入 ready 转化 | 91.95 sec/sample |

左下角放小注：

> 统计口径：5 月 7 日以来生产子集。

### 禁止

- 不要写“这就是全局 ready 总量”。
- 不要把 `12,114 processed` 和 `32,292 processed` 放在同一气泡里。
- 不要用花哨 AI/机器人插画。

## 5. 第 5 页：Outputs 到 Ready 的转化漏斗

### 标题

> Outputs → Ready：选择、去重与质量门控

右上角页码：`05 / FUNNEL`

### 核心结论

> 生产子集里的 ready 不是简单复制 outputs，而是经过 pass/review/reject 判断、review release、去重和风险过滤后形成。

### 版式

使用横向漏斗或阶梯图，不要只写列表。

主漏斗数字：

- `32,292` processed
- `16,495` pass
- `12,744` review
- `2,618` released review
- `10,126` dropped review
- `2,667` dedup removed
- `19,113` final ready

右侧放 3 个比例小卡：

- review rate `39.5%`
- review release rate `20.5%`
- final ready / processed `59.2%`

底部流程规则：

```text
pass → ready
review → only if matched release policy
reject → dropped
```

### 设计

- 漏斗主体用深绿色渐浅，但不要大面积渐变背景。
- `final ready 19,113` 用深绿色实心块突出。
- `dropped review 10,126` 用浅灰或琥珀色，不能比 final ready 更醒目。

## 6. 第 6 页：Review release 质量门控

### 标题

> Review release：释放非致命工程风险，保留语义风险

右上角页码：`06 / RELEASE`

### 核心结论

> review 不是默认放行；只有命中结构化 release policy 或显式候选子集的样本才进入 ready。

### 版式

左右双栏。

左栏：规则图

```text
pass   → ready
review → policy matched → ready
review → policy not matched → hold/drop
reject → dropped
```

左栏下方写“不放行边界”：

- 关键条件缺失
- 答案冲突
- 图文冲突
- split variant 未确认
- rewrite 不完整或不可理解

右栏：实际放行条形图

必须画成横向条形图，不要只写列表。

数据：

- mm_math A：`1,114`
- ai2d A：`751`
- geoqa_plus A：`305`
- multi_physics A/B：`389`
- physreason A：`52`
- seephys A1：`7`

底部一句：

> release policy 的作用是释放 alignment/grounding path 等非致命工程风险，而不是降低语义质量标准。

## 7. 第 7 页：Ready 数据题型分布

### 标题

> Ready taxonomy：14 类粗粒度题型

右上角页码：`07 / TAXONOMY`

### 核心结论

> 最终 ready 集以视觉数学、物理力学、电磁电路为主体，同时覆盖化学结构、生命科学和地理类题目。

### 版式

左侧放真实 taxonomy 类别柱状图或按下列数据重绘横向条形图。右侧放三条结论。

Top taxonomy：

- 几何与空间推理：`40.9%`
- 电磁、电路与电子系统：`12.7%`
- 力学与运动：`12.3%`
- 地球空间、气候与自然地理：`5.9%`
- 代数、离散数学与应用数学：`5.5%`
- 化学结构与分子表示：`4.4%`
- 生态、生理与生命系统：`3.9%`
- 生命分子、细胞与遗传：`3.4%`

右侧三条结论：

1. 几何与空间推理是最大主轴，主要来自视觉数学数据集。
2. 电路与力学构成物理侧的两条主线。
3. 化学、生物、地理保留跨学科覆盖，适合后续做能力分层分析。

底部放一个小标签：

> taxonomy 支撑采样平衡、能力覆盖分析和低覆盖领域补齐。

## 8. 第 8 页：Review 原因诊断与结论

### 标题

> Review 原因：不只是视觉问题

右上角页码：`08 / DIAGNOSIS`

### 核心结论

> review 原因是混合信号，既包含 alignment/metadata，也包含答案可解性、视觉 grounding 和改写结构问题，因此必须用细分 release policy 处理。

### 版式

左侧放原因分布图。右侧放“原因解释 + 处理策略”。

原因分布：

- alignment / metadata consistency：`22,643`，`32.1%`
- other：`20,285`，`28.7%`
- answer / target solvability：`11,594`，`16.4%`
- visual grounding / image quality：`9,359`，`13.3%`
- rewrite / structure / options：`6,699`，`9.5%`

右侧解释：

| 原因 | 处理策略 |
| --- | --- |
| alignment / metadata | 可通过结构化规则部分释放 |
| answer / solvability | 保守 hold，防止语义错误 |
| visual grounding | 只释放低风险 grounding path 问题 |
| rewrite / structure | 需验证题干完整和答案可验 |

底部最终结论：

> 当前数据链路已经形成“生产统计 + ready 转化 + release policy + taxonomy 分析”的闭环；下一步可以围绕低覆盖领域、复杂样本和 review 高发原因继续补齐。

## 9. 上传给 Gemini 的文件

优先上传：

1. 本文件：`gemini_ppt_strict_page_spec_2026-05-13.md`
2. PPT 模板风格总结：`ppt_template_style_summary_2026-05-13.md`
3. 数据口径说明：`ready_dataset_layout.md`
4. 生产统计说明：`ppt_with_production_data_insert_plan_2026-05-13.md`
5. taxonomy 交付说明：`最终taxonomy与图表交付说明.md`

同时上传这些图像素材：

1. 领域分布图
2. taxonomy 类别柱状图
3. 题长箱线图
4. 复杂度散点图
5. multi-step 分布图
6. 视觉类型分布图

如果 Gemini 限制上传数量，优先上传：

1. 领域分布图
2. taxonomy 类别柱状图
3. 题长箱线图或复杂度散点图

## 10. 可直接复制给 Gemini 的生成提示词

```text
请根据我上传的“Gemini 直接生成 PPT 严格逐页规格书”生成一份 8 页组会 PPT。

你必须逐页执行规格书，不要自行改页序、改标题、改主线或增删页面。

风格要求：
- 16:9 横版
- 白底
- 深绿色 #005825 作为主强调色
- 中山大学学术组会风格
- 简洁、克制、论文汇报感
- 页面顶部有深绿色细横线
- 标题左侧有深绿色竖线
- 右上角有页码，例如 03 / FRAMEWORK

内容要求：
- 只使用上传文档中的数字和结论
- 全局 ready 资产与 5 月 7 日以来生产子集必须分开
- 不要出现内部文件名、路径、CSV、json、字段名
- 第 2 页必须列出 6 个领域下的 21 个数据集，并嵌入真实统计图
- 第 3 页必须详细展示 taxonomy 与数据特征分析框架，不能只写空泛标题
- 第 4 页必须是节点加上下交错对话框的横向 pipeline
- 每页必须有一句核心结论

如果某个图像素材无法嵌入，请用同样数据重绘简洁论文风格图表；不要用图标或文字占位代替真实图表。
```
