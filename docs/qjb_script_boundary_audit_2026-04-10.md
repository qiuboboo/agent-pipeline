# qjb policy 脚本边界审计（2026-04-10）

> 目的：把当前仓库中与 `outputs/`、`ready/`、`ready_problem_exports/` 相关的脚本边界写清楚，明确哪些属于 **canonical `output -> ready` 主构建链**，哪些属于 **post-ready**，以及哪些脚本/文档会成为 `qjb` 本地产物 policy 落地前的高风险点。
>
> 本文只做边界审计与迁移风险说明，**不改脚本行为、不删数据、不清索引**。

关联文档：
- `docs/output_to_ready_inventory_2026-04-10.md`
- `docs/qjb_branch_sync_plan_2026-04-10.md`
- `docs/qjb_branch_execution_checklist_2026-04-10.md`

---

## 1. 审计结论先行

当前仓库里与 `qjb` local-artifact policy 最直接相关的脚本，可以拆成 4 层：

1. **主构建链（canonical）**
   - 负责：`outputs -> selection/merge/dedup -> ready`
   - 当前正式入口：`scripts/build_ready_from_outputs_content_dedup.py`

2. **盘点 / 覆盖 / 追踪层（inventory / manifest）**
   - 负责：解释哪些 `outputs` 被纳入了哪些 `ready`，以及当前本机覆盖情况
   - 代表脚本：
     - `scripts/build_sample_manifest.py`
     - `scripts/build_output_root_coverage.py`

3. **post-ready / review-release 层**
   - 负责：在 canonical ready 已存在的前提下，生成 review 文档、执行 manual release、刷新台账
   - 代表脚本：
     - `scripts/build_review_docs.py`
     - `scripts/apply_manual_review_release.py`

4. **post-ready export 层**
   - 负责：把本机现有 `ready/` 继续导出成下游 JSON 交付物
   - 代表脚本：
     - `scripts/export_ready_to_problem_json.py`

**关键结论：**
- `scripts/build_ready_from_outputs_content_dedup.py` 应继续视为 **唯一正式主链原型**。
- `scripts/build_review_docs.py` 是当前最明显的迁移风险点，因为它不是通用文档生成器，而是**硬编码依赖特定 `ready/...` 包路径**的 ready 消费脚本。
- `scripts/apply_manual_review_release.py` 与 `scripts/export_ready_to_problem_json.py` 都依赖 canonical `ready`，但都**不属于 build-ready 本体**。

---

## 2. 审计目标：`qjb` policy 想要什么边界

`qjb` 分支的目标口径是：

- **Git 负责同步**：代码、脚本、文档、规则、配置
- **机器本地负责持有**：`outputs/`、`ready/`、`ready_problem_exports/`
- `ready/` 视为**本地可重建派生产物**
- 跨机器共享时，应共享：
  - 代码版本
  - 规则文档
  - 必要时的 `outputs/`
- 不再假设 Git 保证每台机器拥有同一份 `ready/`

所以脚本边界也必须与这个目标一致：

- 主链脚本：允许显式写本机 `ready/`
- 消费脚本：可以依赖本机 `ready/`，但必须明确说明“这是本地前置条件”
- 文档/说明：不能再混淆“Git 同步 ready”和“本机构建 ready”

---

## 3. 主构建链

## 3.1 `scripts/build_ready_from_outputs_content_dedup.py`

**结论：当前 canonical 主链入口。**

### 当前职责
- 扫描本机 `outputs/`
- 识别可纳入的数据集根
- 按规则合并/去重
- 将样本与相关 assets 复制到本机 `ready/`
- 生成 `summary.json` / `selection_manifest.json` / `ready/summary.json`

### 与 `qjb` policy 的关系
这是当前与新 policy **最一致** 的脚本：
- 输入是本机 `outputs/`
- 输出是本机 `ready/`
- 不依赖 Git 来分发 ready

### 当前已知规则特征
- 普通数据集：按 range + run 新旧顺序选择
- `physreason`：保留特例选择逻辑
- 显式排除：
  - `eee_bench_merged_*`
  - `physreason_batched_eval_rerun_*`

### 迁移建议
- **保留为正式主链**
- 后续如果要改接口，应围绕它做小步重构，而不是另起一条 build-ready 正式入口
- 后续 README / docs 的主示例命令都应围绕它展开

---

## 4. 盘点 / 覆盖 / 追踪层

## 4.1 `scripts/build_sample_manifest.py`

**结论：混合型 inventory/manifest 层，不是 build-ready。**

### 当前职责
脚本头部描述就是：

> `Build a unified sample manifest from outputs/ and ready/.`

它会同时读取：
- `outputs/`
- `ready/`

并建立：
- source run -> ready package 对应关系
- 样本级 `records`
- 题目级 `canonical_records`
- dataset 级 / run 级汇总信息

### 与 `qjb` policy 的关系
它本质上是**本机状态盘点器**，这和新 policy 并不冲突；但它绝不能再被误读成：
- “ready 是 Git 保证齐全的”
- “所有机器都会看到同一份 ready package”

### 迁移建议
- **保留**
- 文档上明确它属于“本机盘点/覆盖工具”
- 后续如需增强，优先加强：
  - 缺失 ready 前置时的报错说明
  - 三机差异盘点能力
  - 对“本机只拥有部分 outputs/ready”的解释能力

---

## 4.2 `scripts/build_output_root_coverage.py`

**结论：依赖 manifest 的 coverage 报表脚本，不是 build-ready。**

### 当前职责
- 读取 `manifests/sample_roster.json`
- 统计 `outputs/` 下各 output root 的覆盖情况
- 输出 `manifests/output_root_coverage.json`

### 与 `qjb` policy 的关系
这个脚本天然适合 `qjb` 方案，因为三机 `outputs/` 允许不一致，而该脚本正好可以用来回答：
- 本机有哪些 output roots
- 哪些已被 manifest 覆盖
- 哪些还是 `not_covered`

### 迁移建议
- **保留**
- 后续可作为三机切换后的检查工具之一
- 但前提是先生成本机 manifest

---

## 5. post-ready / review-release 层

## 5.1 `scripts/build_review_docs.py`

**结论：当前第一高风险脚本。**

### 关键风险
该脚本不是“只要有 ready 就随便生成文档”的轻量工具，而是开头就写死：

- `READY_ROOT = PROJECT_ROOT / "ready"`
- `PREFERRED_DATASET_PACKAGES = {...}`

并在 `PREFERRED_DATASET_PACKAGES` 中直接硬编码一组 canonical ready 包路径，例如：
- `ready/eee_bench/run_merged_eee_bench_1000_2860_dedup/...`
- `ready/mathvision/run_merged_mathvision_300_3040_dedup/...`
- `ready/physreason/run_merged_physreason_0000_0300/...`

### 这意味着什么
它当前隐含了 3 个旧假设：

1. 本机一定已有 `ready/`
2. 本机 ready package 名称仍是旧口径
3. review 文档生成默认绑定到这些特定 ready 包

这与 `qjb` policy 并不完全冲突，但与“ready 是本地可重建、包名可能逐步演进”的新边界相比，**耦合过深**。

### 它在迁移中的角色
- 它不是主构建链
- 它是 **canonical ready 的下游消费脚本**
- 但它会成为 README / docs / `.gitignore` 落地前必须先说明清楚的“高风险硬编码点”

### 迁移建议
短期：
- **先文档化，不急着重写**
- 在 docs/README 中明确：它依赖本机已有 canonical ready 包
- 把它从“主链工具”叙述中摘出去

中期：
- 将 `READY_ROOT` / package 选择改为参数化或配置化
- 降低对固定 package 名称的硬编码

---

## 5.2 `scripts/apply_manual_review_release.py`

**结论：明确属于 post-ready manual release，不属于 build-ready。**

### 当前职责
脚本参数直接要求：
- `--dataset-root ready/.../datasets/<dataset>`
- `--candidate-json ...`
- `--policy-doc ...`
- `--ledger-out ...`

它会：
- 在已有 ready 样本上写 manual override
- 更新 `problem_main_record`
- 更新 `clean_problem_record`
- 更新 `clean_pool_entries[0]`
- 更新 `cleaning_records[-1]`
- 刷新 `summary.json`
- 生成 ledger

### 与 `qjb` policy 的关系
完全可以保留，但必须明确：
- 它消费的是**本机 canonical ready**
- 它是 release / waiver / manual override 层
- 不应被混入 `output -> ready` 主链叙述中

### 迁移建议
- **保留**
- 在 README / docs 中归类为 post-ready 工具
- 后续如增强，只做参数/文档清晰化，不改变其层级定位

---

## 6. post-ready export 层

## 6.1 `scripts/export_ready_to_problem_json.py`

**结论：ready 下游导出层，不属于 build-ready。**

### 当前职责
默认参数：
- `--ready-root ready`
- `--output-dir ready_problem_exports`

它会从本机 `ready/` 发现 dataset roots，并导出统一 problem JSON。

### 与 `qjb` policy 的关系
这与新 policy 一致：
- 输入是本机 `ready/`
- 输出是本机 `ready_problem_exports/`

但必须明确两点：
- 这一步是 **post-ready export**
- `ready_problem_exports/` 也是**本地派生产物**，不是 Git 分发对象

### 迁移建议
- **保留**
- 在 docs 中明确它不属于核心 build-ready
- 后续口径中不要再把它写成“ready 构建步骤”的一部分

---

## 7. 文档侧的边界风险

除了脚本本身，当前 docs 里也有两类内容容易在 `qjb` 迁移时造成歧义。

## 7.1 历史施工记录文档
例如：
- `docs/EEE-Bench_0000_0800_合并说明.md`
- `docs/PhysReason_0000_0300_合并说明.md`
- 大量数据集级 merge / 验证总结文档

这些文档会大量提到：
- `outputs/...`
- `ready/...`
- `ready_problem_exports/...`

### 风险
如果不加说明，后续容易被误看成“当前标准入口”。

### 建议
- **保留历史记录**
- 但应由 docs 入口明确：这些是历史说明，不等于当前 policy

---

## 7.2 直接依赖 ready 相对路径的消费文档
例如：
- `docs/review/mathvision.md`

这类文档里会直接嵌：
- `../ready/.../artifacts/...`

### 风险
它们对本机目录结构有强依赖，不适合作为“仓库一拉下来就应该通用可读”的文档假设。

### 建议
- 保留，但在 docs 口径里说明：
  - 这是本机 ready 消费文档
  - 没有本机 ready 时无法完整显示，是预期行为

---

## 8. 当前迁移顺序建议（基于本次审计）

基于这轮脚本边界审计，`qjb` policy 的低风险推进顺序应保持为：

1. **先文档化边界**
   - 先把“谁是主链、谁是 post-ready、谁有硬编码风险”写清楚

2. **先改 docs/README 口径**
   - 明确 `outputs/ready/ready_problem_exports` 是本地产物
   - 明确 `build_review_docs.py` 之类脚本依赖本机 ready

3. **再改 `.gitignore`**
   - 让本地产物默认不再进入 Git 视野

4. **最后才处理索引清理**
   - `git rm -r --cached outputs ready ready_problem_exports`
   - 这一步必须放在文档/边界说明之后

---

## 9. 这轮审计后的明确清单

### 应保留并继续作为正式组成部分的脚本
- `scripts/build_ready_from_outputs_content_dedup.py`
- `scripts/build_sample_manifest.py`
- `scripts/build_output_root_coverage.py`
- `scripts/build_review_docs.py`（但需标注为高风险消费脚本）
- `scripts/apply_manual_review_release.py`
- `scripts/export_ready_to_problem_json.py`

### 当前最需要在文档中醒目标注的风险项
- `scripts/build_review_docs.py`：硬编码 `ready` 根路径与固定 canonical package
- `docs/review/*.md`：直接依赖本机 ready 相对路径
- 各类历史 merge / 合并说明文档：容易被误解为当前标准入口

### 本阶段仍然不要做的事
- 不直接删 `outputs/`
- 不直接删 `ready/`
- 不直接清 Git 索引
- 不在边界没写清前就开始清零/整合

---

## 10. 下一步建议

完成本文后，下一步建议直接进入：

1. README / docs 入口进一步同步本审计结论
2. 为 `build_review_docs.py` 增加“本机 ready 前置条件”说明
3. 再处理 `.gitignore`
4. 最后才进入索引清理与三机切换
