# docs index

当前与 `qjb` 分支切换、`output -> ready` 盘点、以及三机同步策略最相关的入口文档如下：

## 当前主入口
- `output_to_ready_inventory_2026-04-10.md`
  - 盘点当前仓库里与 `outputs -> ready`、review/release、导出、覆盖追踪相关的脚本和文档。
- `qjb_branch_sync_plan_2026-04-10.md`
  - 定义 `qjb` 分支下三台机器的职责、Git 与本地产物的边界，以及为什么 `outputs/ready` 应本地化。
- `qjb_branch_execution_checklist_2026-04-10.md`
  - 把 policy 落成实际执行顺序：先文档与规则、再 `.gitignore`、再索引清理、再三机切换、最后重建验证。

## 与当前 policy 直接相关的脚本
- `../scripts/build_ready_from_outputs_content_dedup.py`
  - 当前 canonical `outputs -> ready` 主链入口。
- `../scripts/build_sample_manifest.py`
  - 输出/ready 统一样本花名册与覆盖盘点。
- `../scripts/build_output_root_coverage.py`
  - 输出根覆盖情况盘点。
- `../scripts/apply_manual_review_release.py`
  - post-ready manual review/release，不属于 build-ready 本体。
- `../scripts/build_review_docs.py`
  - 基于 ready 的 review 文档生成，不属于 build-ready 本体。
- `../scripts/export_ready_to_problem_json.py`
  - ready 的下游导出，不属于 build-ready 本体。

## 口径说明
从 `qjb` 分支开始，仓库默认只同步代码、脚本、文档、规则和配置；`outputs/`、`ready/`、`ready_problem_exports/` 视为机器本地状态，不再作为 Git 同步对象。
