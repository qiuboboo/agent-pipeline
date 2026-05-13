# Gemini 直接生成 PPT 的输入包

目标：让 Gemini 按固定页序、固定内容和固定设计生成组会 PPT，避免自由发挥导致页面重点偏移。

## 1. 最重要的使用方式

优先上传并要求 Gemini 严格执行：

1. `plans/gemini_ppt_strict_page_spec_2026-05-13.md`

这份文件是逐页施工图，优先级最高。Gemini 不应自行改页序、改标题、改主线或增删页面。

## 2. 上传文件清单

核心文档：

1. `plans/gemini_ppt_strict_page_spec_2026-05-13.md`
2. `plans/ppt_template_style_summary_2026-05-13.md`
3. `plans/ppt_with_production_data_insert_plan_2026-05-13.md`
4. `plans/ppt_pipeline_outputs_review_ready_plan_2026-05-13.md`
5. `plans/ready_sample_analysis_2026-05-12/最终taxonomy与图表交付说明.md`
6. `ready/ready_dataset_layout.md`

图像素材：

1. `plans/ready_sample_analysis_2026-05-12/final_taxonomy_package/figures/paper_subject_pie.png`
2. `plans/ready_sample_analysis_2026-05-12/final_taxonomy_package/figures/paper_final_category_bar.png`
3. `plans/ready_sample_analysis_2026-05-12/final_taxonomy_package/figures/paper_question_length_boxplot.png`
4. `plans/ready_sample_analysis_2026-05-12/final_taxonomy_package/figures/paper_complexity_scatter.png`
5. `plans/ready_sample_analysis_2026-05-12/final_taxonomy_package/figures/paper_multistep_histogram.png`
6. `plans/ready_sample_analysis_2026-05-12/final_taxonomy_package/figures/paper_visual_type_bar.png`

如果上传数量有限，图像素材优先级：

1. `paper_subject_pie.png`
2. `paper_final_category_bar.png`
3. `paper_question_length_boxplot.png` 或 `paper_complexity_scatter.png`

不要上传：

- `ready_sample_features_with_text.csv`
- `all_samples_with_final_taxonomy.csv`
- 任何全量 `sample_list.csv`

## 3. 口径提醒

全局 ready 资产：

- `29,966` candidates
- `21,555` ready pass
- `21` datasets
- `6` domains
- `14` coarse taxonomy classes

5 月 7 日以来生产子集：

- `47` production runs
- `12,114` processed samples
- `88,169` requests
- `19,113` final ready

这两个口径必须分开写，不能放进同一个总览数字里。

## 4. 可直接复制给 Gemini 的提示词

```text
请根据我上传的“Gemini 直接生成 PPT 严格逐页规格书”生成一份 8 页组会 PPT。

你必须逐页执行规格书，不要自行改页序、改标题、改主线或增删页面。

硬性规则：
1. 只使用上传文档中的数字和结论，不要编造任何数据。
2. 全局 ready 资产与 5 月 7 日以来生产子集必须分开。
3. 不要出现内部文件名、路径、CSV、json、字段名。
4. 每页必须有一句核心结论。
5. 第 2 页必须用表格或领域分组矩阵完整列出 21 个真实数据集名称，并嵌入真实统计图。
6. 第 3 页必须做成思维导图式框架：左侧完整列出 21 个真实数据集名称，中间 taxonomy 分类流程，右侧特征分析维度；不能使用 Dataset A/B/C 占位。
7. 第 4 页必须是节点加上下交错对话框的横向 pipeline。
8. 如果某个图像素材无法嵌入，请用同样数据重绘简洁论文风格图表；不要用图标或文字占位代替真实图表。

风格必须参考我上传的 PPT 模板风格总结：
- 16:9 横版
- 白底
- 深绿色 #005825 作为主强调色
- 中山大学学术组会风格
- 简洁、克制、论文汇报感
- 页面顶部有深绿色细横线
- 标题左侧有深绿色竖线
- 右上角有页码，例如 03 / FRAMEWORK
```

## 5. 如果 Gemini 仍然跑偏

不要让它一次生成完整 PPT，改成两步：

1. 先要求它逐页复述 `8` 页结构，每页只输出“标题 + 核心结论 + 主图类型”。
2. 你确认无误后，再让它按严格规格书生成 PPT。
