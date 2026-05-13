# Gemini 网页端示意图片生成约束文档

用途：上传到 Gemini 网页端，用于约束 PPT 报告中的示意图、流程图、信息图生成。

## 1. 总体目标

请为一份学术/项目汇报 PPT 生成简洁、准确、适合 16:9 页面使用的示意图片。主题是：

> 从原始多模态题目样本，经 Pipeline1 处理、review release 质量门控，形成 ready pass 数据集，并对 ready 数据进行 taxonomy 和数据特征分析。

图片用于 PPT，不是论文正文插图。要求清晰、专业、信息密度适中。

## 2. 风格约束

- 画幅：16:9，横向。
- 风格：现代学术汇报、扁平化信息图、干净白底或极浅灰底。
- 颜色：使用蓝色、青绿色、橙色、紫色作为辅助色，但不要大面积渐变。
- 字体：无衬线风格，中文标签要清楚。
- 图形：使用流程节点、箭头、卡片、分组框、少量图标。
- 不要使用卡通人物、真实人物、夸张插画、复杂背景、科幻场景。
- 不要使用任何真实公司 Logo。
- 不要把图做成密密麻麻的数据表。
- 如果文字太多，请改成短标签，不要硬塞长段文字。

## 3. 事实约束

只能使用上传文档中出现的数据。不要编造样本数、类别数、比例、成本、耗时或结论。

必须保留的关键事实：

- ready pass 分析覆盖 21 个数据集。
- 每个数据集最终类别数为 3 至 14 类。
- 代表例题总数为 187，已补中文题意 187 条。
- 最终 taxonomy 包包含：taxonomy、sample_list、representative_examples、feature_stats、calibration_samples。
- 主要图表包括：领域分布、题长箱线图、最终类别分布、multi-step 分布、视觉类型分布、复杂度散点图。
- Pipeline1 的主线是：原始样本 → 规范化 → prompt 构造 → 模型改写/答案归一 → 图像资产收集 → 清洗与验证 → outputs。
- 从 outputs 到 ready 需要选择、合并、去重、质量门控和 review release。

如果不确定某个数字，请不要写数字，改写成“见数据表”或使用占位标签。

## 4. 禁止项

- 不要生成看起来像真实系统截图的虚假界面。
- 不要生成不存在的数据分布或伪造图表。
- 不要加入“准确率提升”“模型性能提升”等未在文档中出现的结论。
- 不要把全量 CSV 的细节塞进图片。
- 不要使用过多装饰性图案。
- 不要输出低对比度文字。

## 5. 推荐生成图片

### 图片 A：Pipeline1 到 ready 的总流程图

用途：PPT 第 1-2 页。

画面结构：

```text
Raw source samples
  → Source intake / normalization
  → Prompt construction
  → Model rewrite + answer normalization
  → Image artifact collection
  → Cleaning & validation
  → outputs/
  → selection / merge / dedup
  → review release quality gate
  → ready pass samples
```

要求：

- 用横向流程图。
- outputs 到 ready 之间用一个醒目的“Quality Gate / Review Release”关卡。
- 图中可以出现小标签：metadata、provenance、image artifacts、reason codes。
- 中文主标签优先，英文可作为小字补充。

### 图片 B：ready 数据资产结构图

用途：说明最终分析产物。

画面结构：

```text
ready pass samples
  ├─ dataset_summary
  ├─ final taxonomy package
  │   ├─ taxonomy.csv
  │   ├─ sample_list.csv
  │   ├─ representative_examples.csv
  │   ├─ feature_stats.csv
  │   └─ calibration_samples.csv
  └─ figures
      ├─ subject pie
      ├─ question length boxplot
      ├─ category bar
      ├─ multi-step histogram
      ├─ visual type bar
      └─ complexity scatter
```

要求：

- 做成“数据资产地图”。
- 不要画成真实文件管理器截图。
- 用文件卡片和图表缩略图图标表达。

### 图片 C：最终 taxonomy 和数据特征概览

用途：ready 数据分析页。

必须包含：

- 21 个数据集。
- 每个数据集 3-14 个最终类别。
- 每类代表例题均有中文题意。
- 特征维度：题长、答案长度、复杂度、multi-step、视觉类型、需图像比例。

画面结构建议：

左侧：21 datasets → taxonomy classes  
右侧：feature statistics → paper figures  
底部：representative examples with Chinese translation

要求：

- 不要把 21 个数据集全部写满，最多展示几个代表数据集名称，其余用“...”。
- 不要编造具体分布。

### 图片 D：review release 质量门控示意图

用途：讲从 outputs 到 ready 的放行逻辑。

画面结构：

```text
outputs candidates
  → validation
  → reason code analysis
  → rewrite / source resolution
  → release decision
  → ready pass
```

要求：

- 用漏斗或关卡图。
- 突出“不是所有 outputs 都直接进入 ready”。
- 可使用标签：pass、review、rewrite、reject、dedup。

### 图片 E：PPT 封面背景图

用途：封面或章节页。

画面要求：

- 抽象但专业。
- 表现“多学科视觉问答数据集分析”。
- 可以有几类简化图标：数学几何图形、电路节点、物理曲线、生物细胞、化学分子、地理地图。
- 背景留出左侧或中间空白，方便放标题。
- 不要放任何具体数字，避免误导。

## 6. 示例 Prompt 模板

把本文件和项目说明文件上传后，可以这样问：

```text
请根据我上传的约束文档和项目数据，为 PPT 生成一张 16:9 的流程示意图。
主题：Pipeline1 到 ready pass 数据集的生产流程。
请严格遵守约束文档，不要编造数字，不要使用真实 Logo。
风格：白底、现代学术汇报、扁平化信息图、中文标签为主。
图中必须包含：Raw source samples、Pipeline1 outputs、review release quality gate、ready pass samples。
请输出可直接放入 PPT 的图片。
```

如果第一版不满意，可以继续局部修改：

```text
请保留当前构图，但做以下修改：
1. 减少文字，每个节点不超过 8 个中文字符。
2. 把 review release 关卡画得更醒目。
3. 删除人物和装饰背景。
4. 增加数据资产包图标：taxonomy、sample list、representative examples、feature stats。
```

## 7. 建议上传文件

优先上传小而准的文件，不要上传全量大 CSV。

推荐上传：

1. `plans/gemini_image_generation_brief_2026-05-13.md`
2. `plans/ppt_pipeline_outputs_review_ready_plan_2026-05-13.md`
3. `plans/ready_sample_analysis_2026-05-12/最终taxonomy与图表交付说明.md`
4. `plans/ready_sample_analysis_2026-05-12/final_taxonomy_package/dataset_summary.csv`
5. `plans/ready_sample_analysis_2026-05-12/coarse_level1_taxonomy_14_2026-05-13.md`

如需让 Gemini 参考已有图表风格，再上传 1-3 张图片：

- `plans/ready_sample_analysis_2026-05-12/final_taxonomy_package/figures/paper_subject_pie.png`
- `plans/ready_sample_analysis_2026-05-12/final_taxonomy_package/figures/paper_final_category_bar.png`
- `plans/ready_sample_analysis_2026-05-12/final_taxonomy_package/figures/paper_complexity_scatter.png`

不建议上传：

- `all_samples_with_final_taxonomy.csv`
- `ready_sample_features_with_text.csv`
- 每个数据集的 `sample_list.csv`

这些文件太大，适合本地分析，不适合作为网页端图片生成约束。

