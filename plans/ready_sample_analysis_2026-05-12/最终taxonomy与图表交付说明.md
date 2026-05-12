# ready pass 样本最终 taxonomy 与图表交付说明

生成时间：2026-05-12

## 交付入口

最终包目录：

`plans/ready_sample_analysis_2026-05-12/final_taxonomy_package/`

总览文件：

- `final_taxonomy_package/README.md`：21 个数据集的样本数、类别数、最大类别和目录索引。
- `final_taxonomy_package/dataset_summary.csv`：可直接用于论文表格的数据集级摘要。
- `final_taxonomy_package/all_samples_with_final_taxonomy.csv`：所有 pass 样本的最终类别标签。
- `final_taxonomy_package/figures/`：论文风格统计图。

每个数据集目录均包含：

- `taxonomy.csv`：最终类别、中文名、数量、占比、类别定义、来源规则。
- `sample_list.csv`：全量样本清单，含最终类别、题目、答案、题长、复杂度、multi-step、视觉类型。
- `representative_examples.csv`：每类一道代表例题，已补中文题意。
- `feature_stats.csv`：按类别聚合的题长、答案长度、复杂度、multi-step、视觉实体、需图像比例等统计。
- `calibration_samples.csv`：每类抽样校准清单，默认每类最多 20 条。
- `README.md`：该数据集的 taxonomy、代表例题、特征统计三块合并展示。

## 最终 taxonomy 概况

共处理 21 个数据集。每个数据集最终类别数为 3 至 14 类，满足“每个数据集约 10-15 类以内”的要求；小型或高度单一的数据集保留较少类别。

| 数据集 | 样本数 | 最终类别数 | 最大类 | 最大类占比 |
| --- | ---: | ---: | --- | ---: |
| biology\ai2d_biology | 1315 | 8 | 细胞、分子与遗传 | 43.65% |
| biology\scemqa_biology | 64 | 8 | 细胞、分子与遗传 | 43.75% |
| biology\sciverse_biology | 219 | 9 | 细胞、分子与遗传 | 57.53% |
| chemistry\emma_chemistry | 864 | 3 | 过渡态结构与 SMILES 选择 | 97.92% |
| chemistry\scemqa_chemistry | 111 | 10 | 化学计量与反应计算 | 28.83% |
| chemistry\sciverse_chemistry | 247 | 11 | 化学计量与反应计算 | 24.70% |
| circuit\eee_bench | 2023 | 12 | 直流/交流电路网络分析 | 34.85% |
| geography\ai2d_geography | 298 | 8 | 地球、太阳与月相 | 39.60% |
| geography\geosqa | 1757 | 9 | 气候、天气与季节 | 21.17% |
| math\cmm_math | 142 | 5 | 线性规划与约束最值 | 38.03% |
| math\geometry3k | 879 | 11 | 几何角度追踪 | 56.88% |
| math\geoqa_plus | 2766 | 14 | 几何角度追踪 | 51.88% |
| math\mathvision | 1879 | 11 | 几何角度追踪 | 48.32% |
| math\mm_math | 4229 | 8 | 几何角度追踪 | 83.00% |
| math\scemqa_math | 189 | 10 | 代数方程与不等式 | 25.40% |
| physics\emma_physics | 266 | 7 | 力学、运动学与动力学 | 62.03% |
| physics\multi_physics | 525 | 9 | 力学、运动学与动力学 | 54.86% |
| physics\physreason | 905 | 6 | 力学、运动学与动力学 | 87.07% |
| physics\phyx | 1139 | 11 | 力学、运动学与动力学 | 44.42% |
| physics\sciverse_physics | 239 | 8 | 力学、运动学与动力学 | 61.09% |
| physics\seephys | 1499 | 9 | 力学、运动学与动力学 | 51.17% |

## 高 other 数据集细分

已对 `*_other` 比例较高的数据集进行二次细分和合并：

- `circuit\eee_bench`：细分出节点电压/电流与等效网络、数字逻辑、信号系统、模拟电子、控制、电力电子、电机电力、电磁场、测量仪表等，最终 12 类。
- `math\geometry3k`：把原 math_other 拆成几何线段测量、四边形与多边形、图形通用量测等，最终 11 类。
- `math\geoqa_plus`：把原 math_other 拆成数学谜题与逻辑推理、比例配方应用、数据表统计推断等，最终 14 类。
- `math\scemqa_math`：细分为代数、统计、数据表、概率组合、几何量测、坐标变换、逻辑推断等，最终 10 类。
- `physics\multi_physics`：补充分为物理概念判断、物理电路应用等，最终 9 类。
- `physics\phyx`：补充分为热机/制冷、物理电路应用、高级力学与振动、概念判断等，最终 11 类。
- `physics\seephys`：补充分为物理电路应用、高级力学与振动、概念判断等，最终 9 类。

## 代表例题中文翻译

`representative_examples.csv` 中每个类别都保留原题 `question`，并新增中文题意 `question_zh`。

核验结果：

- 代表例题总数：187
- 已补中文题意：187
- `translation_status`：全部为 `human_curated_zh`

说明：全量 `sample_list.csv` 中，原本就是中文的问题会填入 `question_zh`；英文全量样本暂不做逐条翻译，以避免把论文附录主文件膨胀得过大。需要逐条全量翻译时，可在最终类别稳定后单独生成扩展版。

## 图表

图表目录：

`plans/ready_sample_analysis_2026-05-12/final_taxonomy_package/figures/`

已生成 6 张论文风格图：

- `paper_subject_pie.png`：领域分布饼图。
- `paper_question_length_boxplot.png`：各数据集题长箱线图。
- `paper_final_category_bar.png`：最终类别分布柱状图。
- `paper_multistep_histogram.png`：multi-step 分布直方图。
- `paper_visual_type_bar.png`：视觉类型分布柱状图。
- `paper_complexity_scatter.png`：题长与复杂度散点图。

## 复现脚本

主要脚本：

- `scripts/analyze_ready_samples.py`：抽取全量 pass 样本特征。
- `scripts/deepen_ready_analysis.py`：生成数据集级深度分析和 outlier。
- `scripts/export_ready_category_examples.py`：导出早期题型代表例题。
- `scripts/build_ready_final_taxonomy_package.py`：生成最终 taxonomy 包和图表。
- `scripts/apply_ready_representative_translations.py`：为代表例题写入人工校准中文题意。
- `scripts/translate_ready_representatives.py`：在线翻译辅助脚本，当前不作为最终结果依赖。

已通过：

```powershell
python -m py_compile scripts\build_ready_final_taxonomy_package.py scripts\apply_ready_representative_translations.py scripts\translate_ready_representatives.py scripts\export_ready_category_examples.py scripts\plot_ready_analysis.py scripts\deepen_ready_analysis.py scripts\analyze_ready_samples.py
```

