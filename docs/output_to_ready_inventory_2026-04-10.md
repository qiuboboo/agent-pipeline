# output -> ready 全链路脚本 / 文档盘点（2026-04-10）

> 目的：为后续 **清零 + 整合** 做准备。
>
> 本文只做盘点、分类、职责澄清与保留建议，**不做删除、不改数据、不改口径**。

---

## 1. 结论先行

当前仓库里与 `output -> ready` 相关的内容，实际可以拆成 5 层：

1. **主构建链（核心）**
   - 从 `outputs/` 选择样本，按规则合并，写入 `ready/`
   - 当前核心脚本：`scripts/build_ready_from_outputs_content_dedup.py`

2. **ready 盘点 / 追踪链（辅助）**
   - 用于回答“哪些 output 被纳入 ready、哪些 run 被覆盖、哪些样本在 ready 里”
   - 关键脚本：`scripts/build_sample_manifest.py`、`scripts/build_output_root_coverage.py`

3. **review / release 链（post-ready）**
   - 不是 `output -> ready` 构建本身，而是 **canonical ready 构建完成后** 的人工放行/台账刷新
   - 关键脚本：`scripts/apply_manual_review_release.py`
   - 关键模板：`docs/review/review_release_template.md`

4. **历史特例链（旧分支/特殊导出）**
   - 在主链统一之前，为少数数据集单独做的 ready 导出或 merge
   - 关键脚本：`scripts/export_special_outputs_to_ready.py`、`scripts/build_physreason_merged_full.js`、`scripts/build_physreason_merged_summary.js`

5. **ready 下游消费链（不是 build ready 本身）**
   - ready 构建完成后，用于导出 problem json、分析文档、review 文档
   - 关键脚本：`scripts/export_ready_to_problem_json.py`、`scripts/build_review_docs.py`

**建议的未来目标：**
- 把 **主构建链** 收敛为 1 条正式口径；
- 把 **review/release** 明确为独立后处理层，不再混进 build 逻辑；
- 把 **历史特例链** 归档；
- 把 **下游导出链** 与 build ready 解耦，作为纯消费层。

---

## 2. 当前正式理解的流程边界

结合 `docs/qjb_pipeline_flow_A_version_2026-04-02.md` 与当前脚本实现，可以把范围定义为：

### 上游
`Setup -> Collection -> Cleaning -> Report`
- 上游 pipeline 负责把样本跑到 `outputs/<dataset...>/run_xxx/datasets/<dataset>/...`
- 这一步产出样本 JSON、records、artifacts、summary

### 本文关注的中段
`outputs -> selection/merge/dedup -> ready`
- 从多个 `outputs` 目录里选取候选样本
- 按 `source_problem_id` / 特例规则去重与合并
- 把选中样本和相关资产复制到 `ready/...`
- 产出 `summary.json` / `selection_manifest.json` / 顶层 `ready/summary.json`

### 下游
`ready -> review docs / manifests / exports / manual release`
- 从 ready 生成分析文档
- 从 ready 导出下游 problem json
- 对 ready 中的 review 样本做候选放行与 manual override

**重要边界：**
- `apply_manual_review_release.py` **不属于 output -> ready 构建阶段**，而属于 **post-ready**。
- `export_ready_to_problem_json.py` 也 **不属于 output -> ready 构建阶段**，而属于 ready 的下游导出。

---

## 3. 主链：当前真正负责 `outputs -> ready` 的核心脚本

## 3.1 `scripts/build_ready_from_outputs_content_dedup.py`

**当前地位：主线核心脚本**

**脚本描述（原文）**
> Build ready datasets from outputs only. No similarity dedup. Within each dataset range folder (dataset_aaa_bbb), traverse runs newest to oldest, keep the first sample for each source_problem_id, then merge all ranges.

### 它做什么

- 扫描 `outputs/` 下的 run dataset roots
- 识别 output root 是否匹配某个数据集范围
- 将样本按 `dataset_key + range_key` 分组
- 在每个 range 内按 **run 新到旧** 扫描
- 对同一 `source_problem_id` 只保留首个样本
- 再把各个 range 合并成一个 ready package
- 复制样本 JSON 与相关 images/crops/assets 到 `ready/`
- 写出每个 dataset 的：
  - `datasets/<dataset>/summary.json`
  - `datasets/<dataset>/selection_manifest.json`
- 最后写出总：
  - `ready/summary.json`

### 它的关键规则

#### 普通数据集默认规则
- `dedup_rule = latest_to_oldest_within_range_by_source_problem_id_then_merge_ranges`
- `selection_rule = Use only outputs folders whose names contain dataset_key_start_end ...`

#### `physreason` 特例
- 若存在 `physreason_full_*`，则走：
  - `physreason_full_global_newest_to_oldest_by_source_problem_id`
- 这是当前主线里唯一明确保留的“正式特例”

#### 显式排除/特判
- `eee_bench_merged_*` 不作为该脚本普通输入
- `physreason_batched_eval_rerun_*` 被排除
- `emma_chemistry_full` / `emma_chemistry_validation_*` 被专门识别为同一 family

### 关键输出位点

对每个 dataset：
- `ready/<dataset>/<package_name>/datasets/<dataset>/samples/*.json`
- `ready/<dataset>/<package_name>/datasets/<dataset>/artifacts/images/*`
- `ready/<dataset>/<package_name>/datasets/<dataset>/artifacts/crops/*`
- `ready/<dataset>/<package_name>/datasets/<dataset>/summary.json`
- `ready/<dataset>/<package_name>/datasets/<dataset>/selection_manifest.json`

顶层：
- `ready/summary.json`

### 内建验证
- `selection_validation`
- `write_validation`

这两个校验现在是 canonical ready 可信度的核心依据。

### 后续整合建议
- **必须保留**
- 应视为未来唯一正式的 `outputs -> ready` 主链原型
- 后续可以改名，但语义上应成为统一入口

---

## 4. 历史主链/旧版本/替代脚本

## 4.1 `scripts/build_ready_from_outputs_content_dedup.fdefb72.py`

**当前地位：历史版本 / 旧策略备份**

**脚本描述（原文）**
> Build ready datasets from outputs only. Deduplicate while adding by comparing the incoming sample's question content against already accepted question content.

### 与现主链的核心区别
- 这个版本含 **内容相似去重/加入时对比** 逻辑
- 当前主脚本已改为：
  - **不做 similarity dedup**
  - 只按 `source_problem_id` 规则与 range/runs 规则构建 ready

### 后续整合建议
- **不要继续作为生产主链使用**
- 作为“历史口径对照”保留到归档区即可
- 后续清零时，优先从主工作区移走，避免误用

---

## 5. 历史特例 ready 构建链

这些脚本本质上都做过 “特殊数据集 / 特殊口径 -> ready” 的工作，但不是当前统一主链。

## 5.1 `scripts/export_special_outputs_to_ready.py`

**当前地位：历史特例导出链**

### 它做什么
- 内置 `CONFIG`
- 针对少数数据集直接从指定 `source_runs` 导出 ready package
- 显式合并 records、样本、artifacts
- 生成：
  - ready package
  - dataset summary / top summary
  - selection file
  - duplicate manifest
  - suspected duplicates

### 当前已识别配置
- `eee_bench`
  - `run_merged_eee_bench_1000_2860_dedup`
- `mathvision`
  - `run_merged_mathvision_300_3040_dedup`

### 这个脚本的特征
- 带有强 dataset-specific config
- 使用 `problem_id` 去重 + `normalized question+answer` 精确内容去重
- 另外还检测高相似样本，只做 suspected duplicate 标记
- 写 `filtered_from`、`dedupe` 等 metadata

### 它和当前主链的关系
- 它是主链统一前的 **专项 ready 构建工具**
- 现在与 `build_ready_from_outputs_content_dedup.py` 并存，容易造成口径混乱

### 后续整合建议
- **归档候选**
- 保留其“曾用于特殊数据集的去重策略说明”价值
- 但不要再让它承担正式 canonical ready 构建职责
- 若其中某些去重能力仍需保留，应抽成可配置模块，而不是继续维持 dataset-specific 总脚本

---

## 5.2 `scripts/build_physreason_merged_full.js`

**当前地位：PhysReason 历史专项 merge 工具**

### 它做什么
- 按 `selected_batches.json` 把多个 source package 合并到一个 `mergeRoot`
- 复制：
  - samples
  - images
  - crops
  - records
- 生成 `FULL_MERGE_MANIFEST.json`

### 问题
- 完全是 `physreason` 专项逻辑
- 独立于当前 Python 主链之外
- 容易与当前 `physreason_full_global_newest_to_oldest_by_source_problem_id` 主线特例重复或冲突

### 后续整合建议
- **归档候选**
- 不应继续作为正式主构建工具
- 若要保留，应只保留其历史 provenance 价值

---

## 5.3 `scripts/build_physreason_merged_summary.js`

**当前地位：PhysReason 历史专项 summary 工具**

### 它做什么
- 汇总 selected batches 的 summary
- 生成 merged `datasets/physreason/summary.json`
- 生成顶层 `summary.json`

### 后续整合建议
- **归档候选**
- 不应继续和主链并行写 summary

---

## 6. ready 盘点 / 覆盖 / 追踪辅助链

这些脚本不是直接构建 ready，但对于后续“清零 + 整合”非常重要，因为它们能回答：
- 哪些 output root 已被纳入 ready？
- 哪些 ready package 来自哪些 source run？
- 同一问题在 outputs 与 ready 中是怎样流转的？

## 6.1 `scripts/build_sample_manifest.py`

**当前地位：主辅助盘点工具**

**脚本描述（原文）**
> Build a unified sample manifest from outputs/ and ready/.

### 它做什么
- 同时扫描 `outputs/` 与 `ready/`
- 构建统一 sample roster / canonical records
- 建立：
  - output 样本 -> ready package 的对应关系
  - dataset 级状态统计
  - source run 级覆盖情况
  - canonical sample 记录

### 关键用途
- 做仓库盘点
- 做 ready coverage / provenance 核对
- 后续做清零时，判断哪些 ready 包还依赖哪些 output run

### 后续整合建议
- **保留**
- 它适合成为以后所有整合动作前的标准盘点入口

---

## 6.2 `scripts/build_output_root_coverage.py`

**当前地位：辅助覆盖率报告**

### 它做什么
- 读取 `manifests/sample_roster.json`
- 扫描 `outputs/*`
- 产出 `manifests/output_root_coverage.json`
- 标识哪些 output root：
  - `covered`
  - `ignored`
  - `empty_shell`
  - `not_covered`

### 关键用途
- 非常适合做“清零前盘点”
- 帮你识别哪些 output 根目录仍未被主线纳入

### 后续整合建议
- **保留**
- 作为 `build_sample_manifest.py` 的补充报表

---

## 7. review / release（post-ready，不属于 build ready 主链）

## 7.1 `scripts/apply_manual_review_release.py`

**当前地位：post-ready 手工放行执行器**

**脚本描述（原文）**
> Apply post-ready manual review release to a candidate bucket and refresh summary/ledger.

### 它做什么
- 输入某个 canonical ready dataset root
- 读取候选 candidate json
- 对指定 bucket 样本执行 manual override
- 将 `review -> pass`
- 回写样本内部 provenance 字段
- 重算 `status_counts`
- 刷新 `write_validation`
- 输出 ledger markdown

### 它修改的关键字段
- `problem_main_record.release_reserved.manual_release_decision`
- `clean_pool_entries[0].manual_override`
- `cleaning_records[-1].manual_override`
- `problem_main_record.clean_decision`
- `clean_problem_record.clean_decision`
- `summary.json.status_counts`
- `summary.json.write_validation`

### 重要边界
- 它明确是 **canonical ready 之后** 的人工政策放行层
- 不应该被混入 `build_ready_from_outputs_content_dedup.py`
- 未来整合时应作为 **独立命令层** 保留

### 后续整合建议
- **保留，但独立分层**
- 后续命名上建议明确成：
  - `ready_postprocess_manual_release.py`
  - 或 `ready_release_apply.py`
- 核心原则：**不把 manual release 混到 build stage**

---

## 7.2 `docs/review/review_release_template.md`

**当前地位：review release 制度模板**

### 它定义了什么
- 先构建 canonical ready
- 再导出候选 bucket
- 用户确认后再做 manual override
- 回写后刷新 `summary.json`
- 要求 `selection_validation.ok = true` 且 `write_validation.ok = true`

### 后续整合建议
- **必须保留**
- 这是 review/release 分层边界的制度文档
- 后续整合时，它应成为“release policy”章节的母文档

---

## 8. ready 文档生成链（消费层）

## 8.1 `scripts/build_review_docs.py`

**当前地位：ready 文档生成器，但仍绑着旧 package 口径**

### 它做什么
从 ready dataset package 生成三类文档：
- `docs/review/*.md`
- `docs/manifests/*.md`
- `docs/analysis/*.md`

### 当前问题
- 内置 `PREFERRED_DATASET_PACKAGES`
- 里面很多仍指向旧包，例如：
  - `run_merged_eee_bench_1000_2860_dedup`
  - `run_merged_mathvision_300_3040_dedup`
  - `run_filtered_emma_physics_safe`
  - `run_filtered_multi_physics_safe`
  - `run_merged_physreason_0000_0300`
  - `run_merged_msearth_open_ended_0000_0120_ler_reasoning_chain`
  - `seephys_000_300`
  - `mm_math_000_300`

这说明：
- 文档层当前还没有完全切到新的 canonical ready 包口径
- 它会把旧 ready 包继续固化进文档产物

### 后续整合建议
- **保留功能，重构入口**
- 不应继续硬编码 `PREFERRED_DATASET_PACKAGES`
- 后续应该改成：
  - 默认读 `ready/summary.json`
  - 或读“当前 canonical package registry”

---

## 8.2 `scripts/export_ready_to_problem_json.py`

**当前地位：ready 下游统一导出器**

**脚本描述（原文）**
> Export ready datasets into unified problem JSON files.

### 它做什么
- 从 `ready/` 发现 dataset roots
- 读取 ready sample / records / variants
- 导出统一的 problem JSON 到 `ready_problem_exports/`

### 边界判断
- 它是 **ready 的消费层**
- 不是 `output -> ready` 主链本身

### 后续整合建议
- **保留**
- 但应明确归类到“downstream export”而不是“ready build”

---

## 9. 质量审计 / 小样本切片 / 旁路工具

这些和 `output -> ready` 有关系，但不是主链构建器。

## 9.1 `scripts/audit_pass_samples.py`

**当前地位：ready/output 质量审计辅助工具**

### 它做什么
- 审计 run outputs，重点检查 pass 样本
- 生成 `analysis/pass_sample_audit.json/md`

### 后续整合建议
- **保留为 QA 工具**
- 不应放进主链

---

## 9.2 `scripts/build_test100_pass_sets.py`

**当前地位：测试切片工具**

### 它做什么
- 从特定 ready package 中抽取 100 个 pass 样本
- 生成 `*_test100_pass` 包
- 同时导出 problem json

### 后续整合建议
- **保留到 tools / experiments 区**
- 不属于正式主链

---

## 10. 上游运行脚本（不是 output -> ready 本身，但属于前置）

这些脚本产出 `outputs/.../run_*`，是 `output -> ready` 的上游来源。

### 已识别脚本
- `scripts/eee_bench_batch_launcher.py`
- `scripts/msearth_open_ended_batch_launcher.py`
- `scripts/physreason_batch_launcher.py`
- `scripts/run_eee_bench_20_batches.sh`
- `scripts/run_eee_bench_range.sh`
- `scripts/run_multidataset_validation_20.command`
- `scripts/run_multidataset_validation_20.sh`
- `scripts/run_scemqa_full_pipeline.sh`
- `scripts/watch_and_continue_eee_bench_0500_0700.sh`

### 边界判断
- 这些是 **生成 outputs 的上游工具**
- 后续清零时需要纳入“输入来源”章节，但不应与 `outputs -> ready` 主链混写

### 后续整合建议
- 统一放到“upstream collection / cleaning runners”分类
- 不纳入 ready 主链文件集合

---

## 11. 文档盘点

下面按用途分类列出现有文档。

## 11.1 流程 / 架构文档

### 核心
- `docs/qjb_pipeline_flow_A_version_2026-04-02.md`
  - 上游 pipeline 四阶段正式版流程
  - 用来定义 `outputs` 的来源背景

### 相关背景
- `docs/branch_architecture_diagram_2026-04-02.md`
- `docs/qjb_branch_summary.md`
- `docs/qjb_ler_branch_report_2026-04-02.md`

### 后续整合建议
- **保留**，但与 ready 主链文档分开
- 这些属于“pipeline 上游背景”，不是 ready build 细则

---

## 11.2 当前 ready 口径/状态文档

### 核心
- `docs/current_ready_dataset_status_2026-04-09.md`

### 它的重要性
- 直接记录当前 canonical ready 包
- 明确 `selection_validation.ok = true`
- 明确 `write_validation.ok = true`
- 可视作“当前 ready 正式口径声明”

### 后续整合建议
- **保留**
- 未来可以升级成长期维护文档，而不是日期快照

---

## 11.3 review / release 文档

### 通用模板 / 规则
- `docs/review/review_release_template.md`

### 数据集台账
- `docs/review/eee_bench.md`
- `docs/review/emma_physics.md`
- `docs/review/mathvision.md`
- `docs/review/mm_math.md`
- `docs/review/msearth_open_ended.md`
- `docs/review/multi_physics.md`
- `docs/review/physreason.md`
- `docs/review/seephys.md`

### 特定 release 候选 / 决策文档
- `docs/review/mm_math_A_bucket_candidates_2026-04-09.json`
- `docs/review/mm_math_A_bucket_candidates_2026-04-09.md`
- `docs/review/mm_math_adjacent_text_sufficient_manual_review_2026-04-09.md`
- `docs/review/mm_math_review_release_candidates_2026-04-09.md`
- `docs/review/seephys_review_release_candidates_2026-04-09.md`
- `docs/mm_math_review_release_decision_2026-04-09.md`

### 后续整合建议
- **保留，但重新分层**
- 建议未来拆成：
  - `docs/review/ledger/`：各 dataset 台账
  - `docs/review/policies/`：模板与放行规则
  - `docs/review/decisions/`：具体日期决策

---

## 11.4 ready 消费层文档（由 `build_review_docs.py` 生成）

### manifests
- `docs/manifests/eee_bench.md`
- `docs/manifests/mathvision.md`

### analysis
- `docs/analysis/eee_bench.md`
- `docs/analysis/emma_physics.md`
- `docs/analysis/mathvision.md`
- `docs/analysis/mm_math.md`
- `docs/analysis/msearth_open_ended.md`
- `docs/analysis/multi_physics.md`
- `docs/analysis/physreason.md`
- `docs/analysis/seephys.md`

### 后续整合建议
- **保留功能，重做生成入口**
- 当前文档不是问题，问题在于生成脚本绑了旧 package 选择逻辑

---

## 11.5 历史 ready merge / validation / 说明文档

### 已识别
- `docs/EEE-Bench_0000_0300_合并说明.md`
- `docs/EEE-Bench_0000_0800_合并说明.md`
- `docs/EEE-Bench_0010_0300_合并说明.md`
- `docs/EEE-Bench_visual_structure_records_口径不一致问题记录.md`
- `docs/EEE-Bench_前10题改写前后对照.md`
- `docs/MathVision_0000_0300_filtered_safe_说明.md`
- `docs/MathVision_10_验证总结.md`
- `docs/MathVision_300_汇总.md`
- `docs/MSEarth_open_ended_0000_0120_合并说明.md`
- `docs/MSEarth_Open_Ended_10_验证总结.md`
- `docs/MSEarth_Open_Ended_汇总说明.md`
- `docs/PhysReason_0000_0300_合并说明.md`
- `docs/PhysReason_10_验证总结.md`
- `docs/PhysReason_fallback批次异常说明.md`
- `docs/PhysReason_前10题改写前后逐字对照.md`
- `docs/emma_physics_validation_summary_2026-04-04.md`
- `docs/mm_math_validation_summary_2026-04-04.md`
- `docs/multi_physics_validation_summary_2026-04-04.md`
- `docs/ler_reasoning_chain_msearth_detailed_report_2026-04-02.md`
- `docs/testset_delivery_checklist_pass_only_2026-04-08.md`

### 后续整合建议
- **归档候选**
- 这些文档有历史价值，但不应继续被误认为当前正式主链文档
- 建议后续统一移入：
  - `docs/archive/merge-notes/`
  - `docs/archive/validation-notes/`

---

## 12. 文件级保留建议总表

| 分类 | 文件 | 当前角色 | 后续建议 |
| --- | --- | --- | --- |
| 主链 | `scripts/build_ready_from_outputs_content_dedup.py` | canonical ready 构建主脚本 | **保留，作为统一主入口** |
| 历史主链 | `scripts/build_ready_from_outputs_content_dedup.fdefb72.py` | 旧版 similarity dedup 方案 | **归档** |
| 特例构建 | `scripts/export_special_outputs_to_ready.py` | eee_bench / mathvision 专项导出 | **归档或拆能力后淘汰总脚本** |
| 特例构建 | `scripts/build_physreason_merged_full.js` | physreason 专项 merge | **归档** |
| 特例构建 | `scripts/build_physreason_merged_summary.js` | physreason 专项 summary | **归档** |
| 辅助盘点 | `scripts/build_sample_manifest.py` | outputs/ready 样本级总清单 | **保留** |
| 辅助盘点 | `scripts/build_output_root_coverage.py` | output root 覆盖率报告 | **保留** |
| review/release | `scripts/apply_manual_review_release.py` | post-ready 手工放行 | **保留，但明确为后处理层** |
| ready 消费 | `scripts/build_review_docs.py` | 生成 review/manifests/analysis 文档 | **保留功能，重构入口** |
| ready 消费 | `scripts/export_ready_to_problem_json.py` | ready 下游导出 | **保留** |
| QA 工具 | `scripts/audit_pass_samples.py` | pass 审计 | **保留到 QA/tools** |
| QA/切片 | `scripts/build_test100_pass_sets.py` | test100 pass 切片 | **保留到 tools/experiments** |
| 上游 runner | `scripts/*launcher*`, `scripts/run_*` | 生成 outputs | **保留，但移到 upstream 分类** |

---

## 13. 推荐的未来目录收敛方式

如果接下来要做“清零 + 整合”，建议按下面的目标结构收敛：

```text
scripts/
  ready/
    build_ready.py                  # 统一主链（由当前 build_ready_from_outputs_content_dedup.py 演化）
    build_sample_manifest.py        # 保留
    build_output_root_coverage.py   # 保留
    apply_manual_release.py         # 由 apply_manual_review_release.py 演化
    export_problem_json.py          # 由 export_ready_to_problem_json.py 演化
    build_ready_docs.py             # 由 build_review_docs.py 演化

  upstream/
    ... batch launchers / run scripts ...

  qa/
    audit_pass_samples.py
    build_test100_pass_sets.py

  archive/
    build_ready_from_outputs_content_dedup.fdefb72.py
    export_special_outputs_to_ready.py
    build_physreason_merged_full.js
    build_physreason_merged_summary.js
```

文档建议收敛成：

```text
docs/
  ready/
    architecture.md
    current_status.md
    output_to_ready_inventory.md

  review/
    policies/
    ledgers/
    decisions/

  archive/
    merge-notes/
    validation-notes/
    branch-notes/
```

---

## 14. 本次清零整合前，建议先不要动的东西

在真正执行“清零 + 整合”前，建议先 **冻结** 以下文件作为参照物：

### 必须保留作基线
- `scripts/build_ready_from_outputs_content_dedup.py`
- `scripts/build_sample_manifest.py`
- `scripts/build_output_root_coverage.py`
- `scripts/apply_manual_review_release.py`
- `scripts/export_ready_to_problem_json.py`
- `docs/review/review_release_template.md`
- `docs/current_ready_dataset_status_2026-04-09.md`
- `docs/qjb_pipeline_flow_A_version_2026-04-02.md`

### 建议保留到归档区再动
- `scripts/export_special_outputs_to_ready.py`
- `scripts/build_ready_from_outputs_content_dedup.fdefb72.py`
- `scripts/build_physreason_merged_full.js`
- `scripts/build_physreason_merged_summary.js`
- 各类 `*_合并说明.md` / `*_验证总结.md`

---

## 15. 我建议的下一步

后续如果你要我继续推进，我建议按这个顺序做：

1. **先做“统一目录与责任边界”方案**
   - 不删代码，先改分组与命名方案

2. **再做“主链最小闭环”确认**
   - 明确未来唯一主脚本
   - 明确 review/release 是后处理层
   - 明确旧特例脚本全部退场或归档

3. **再执行真正清零**
   - 迁移旧脚本到 archive
   - 更新 docs 入口
   - 改文档生成脚本的 canonical package 读取逻辑

4. **最后做一次 repo 级验证**
   - 用 manifest / coverage / ready summary 再核一次

---

## 16. 本文涉及到的关键文件清单

### 核心脚本
- `scripts/build_ready_from_outputs_content_dedup.py`
- `scripts/build_ready_from_outputs_content_dedup.fdefb72.py`
- `scripts/build_sample_manifest.py`
- `scripts/build_output_root_coverage.py`
- `scripts/apply_manual_review_release.py`
- `scripts/build_review_docs.py`
- `scripts/export_ready_to_problem_json.py`
- `scripts/export_special_outputs_to_ready.py`
- `scripts/build_physreason_merged_full.js`
- `scripts/build_physreason_merged_summary.js`

### 核心文档
- `docs/qjb_pipeline_flow_A_version_2026-04-02.md`
- `docs/current_ready_dataset_status_2026-04-09.md`
- `docs/review/review_release_template.md`
- `docs/mm_math_review_release_decision_2026-04-09.md`

### 现有 review / analysis / manifest 文档目录
- `docs/review/`
- `docs/analysis/`
- `docs/manifests/`

---

如果后面要继续，我建议下一步直接做一版：
**“清零 + 整合执行方案”**，把每个文件变成明确动作：`保留 / 合并 / 改名 / 归档 / 删除候选`。
