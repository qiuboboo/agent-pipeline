# qjb 索引清理 preflight（2026-04-10）

> 目的：为后续在 `qjb` policy 下执行
>
> ```bash
> git rm -r --cached outputs ready ready_problem_exports
> ```
>
> 提供一份**独立的执行前检查清单**。
>
> 本文只做 preflight，不直接执行索引清理，不删除本地文件，不假设三机切换已经发生。

关联文档：
- `docs/output_to_ready_inventory_2026-04-10.md`
- `docs/qjb_script_boundary_audit_2026-04-10.md`
- `docs/qjb_branch_sync_plan_2026-04-10.md`
- `docs/qjb_branch_execution_checklist_2026-04-10.md`

---

## 1. 这一步到底要解决什么

当前仓库已经满足两件事：

1. **文档口径已基本冻结**
   - `README.md` 已说明 `outputs/`、`ready/`、`ready_problem_exports/` 是本地派生产物
   - docs 已说明主构建链 / post-ready / export / inventory 的边界

2. **`.gitignore` 已是目标状态**
   - 默认忽略 `outputs/`
   - 默认忽略 `ready/`
   - 默认忽略 `ready_problem_exports/`

但还有一个现实问题没有解决：

> **Git 仍然在追踪这些目录里的历史文件。**

所以即使 `.gitignore` 已正确，当前工作树里仍会看到大量 `ready/...` 脏改，原因不是 ignore 失效，而是：

- 这些文件早已进入索引
- `.gitignore` 不会自动把已追踪文件移出索引

因此真正要做的高影响动作是：

```bash
git rm -r --cached outputs ready ready_problem_exports
```

这一步的本质是：

- **停止追踪历史已入索引的本地产物目录**
- **不删除磁盘上的真实目录和文件**

---

## 2. 这一步执行前，必须成立的前置条件

## 2.1 文档前置已完成
以下文档应被视为当前执行基线：

- `docs/output_to_ready_inventory_2026-04-10.md`
- `docs/qjb_script_boundary_audit_2026-04-10.md`
- `docs/qjb_branch_sync_plan_2026-04-10.md`
- `docs/qjb_branch_execution_checklist_2026-04-10.md`
- `README.md`

执行索引清理前，至少要确认：

- `build_ready_from_outputs_content_dedup.py` 已明确为 canonical 主链
- `build_review_docs.py` / `apply_manual_review_release.py` / `export_ready_to_problem_json.py` 已明确不属于 build-ready 本体
- README 与 docs 都已说明 `ready/` 是本地派生产物

---

## 2.2 `.gitignore` 前置已完成
执行前必须确认 `.gitignore` 当前至少包含：

```gitignore
outputs/
ready/
ready_problem_exports/
__pycache__/
*.pyc
*.log
.DS_Store
```

以及 outputs 内部 cache / nested `.git` 的忽略规则。

### 为什么这一步必须在前
因为如果先做 `git rm --cached`，再补 `.gitignore`，下一次本地产物刷新时，工作树又会立刻被这些目录重新污染。

---

## 2.3 分支前置要明确
理想执行环境应满足：

- 当前处于**准备承接 `qjb` policy 的分支**
- 不要在一个即将废弃或语义不清的临时分支上做最终的 policy 切换提交
- 如果后续确定仍以 `qjb` 为正式工作线，则索引清理 commit 应最终落在 `qjb`

### 当前实际情况（截至本文）
- 当前活跃工作树仍在：`temp/run-summary-only`
- 本地曾有 `qjb` 分支历史，但当前阶段主要通过文档/同 commit 工作树推进
- 因大仓库 checkout / worktree 代价高，当前不宜先为“干净目录”强行重建第二份完整 checkout

### preflight 结论
执行索引清理前，要先明确：

- 这一步究竟是在 `temp/run-summary-only` 上做一次过渡提交，还是
- 先把正式承接分支名整理好，再执行

这个分支语义问题虽然不影响命令本身是否能跑，但会影响后续三机同步和远程落点，因此不能跳过。

---

## 2.4 本地数据前置要确认
执行前必须确认：

- `outputs/` 真实目录还在磁盘上
- `ready/` 真实目录还在磁盘上
- `ready_problem_exports/` 若存在，也在磁盘上
- 当前机器里重要的本地产物不是“只有索引里有、磁盘上其实没了”这种异常状态

### 为什么要确认
因为虽然 `git rm --cached` 理论上不删本地文件，但在巨量脏工作树场景下，如果操作者对当前目录状态没有清晰认知，很容易把“索引变化”和“磁盘变化”混为一谈。

---

## 3. 真正执行时，预期会看到什么

## 3.1 命令本体
预期命令是：

```bash
git rm -r --cached outputs ready ready_problem_exports
```

这一步的语义是：

- 从 Git 索引中移除这三个目录
- 保留本地工作区文件

---

## 3.2 预期的 `git status` 变化
执行后，`git status` 很可能会出现大量：

- `deleted:`（相对于索引）
- staged for commit 的移除项

这并不等于磁盘文件被删掉。

### 正确理解
这里的“deleted”含义是：

> Git 索引里不再追踪这些文件了。

而不是：

> 你的本地 `ready/` / `outputs/` 已经没了。

---

## 3.3 执行后必须立刻检查的 3 件事
执行后不要急着 commit，先检查：

1. `ls outputs | head`
2. `ls ready | head`
3. 如存在：`ls ready_problem_exports | head`

目的是确认：

- 目录还在
- 不是误删磁盘文件
- 只是索引状态变了

---

## 4. 这一步不要和哪些动作混在一起

执行索引清理时，不要同时做下面这些事：

### 4.1 不要同时清理旧实验文件
例如：
- `tmp_*.py`
- `tmp_*.json`
- 各类本地 review 草稿
- `__pycache__/`

这些可以单独整理，但不要和索引清理混在一个 commit 里，否则后续很难分辨：

- 哪些是 policy 切换
- 哪些是杂项清扫

---

### 4.2 不要同时改主脚本行为
例如不要在同一个 commit 里再去改：
- `scripts/build_ready_from_outputs_content_dedup.py`
- `scripts/build_review_docs.py`
- `scripts/build_sample_manifest.py`

索引清理 commit 的目标应非常单一：

> 停止追踪本地产物目录。

---

### 4.3 不要同时做三机切换
先让单机上的 policy 切换 commit 稳定，再谈：
- 云服务器 A
- 云服务器 B
- 个人笔记本

否则一旦某台机器行为异常，很难判断问题是：
- 分支不同步
- 索引清理没做好
- 本地 outputs 差异
- 还是脚本边界问题

---

## 5. 执行前的人类确认项

在真正执行 `git rm --cached` 前，建议操作者对下面 5 个问题逐项回答“是”：

1. **是**：README / docs / audit / checklist 都已对齐
2. **是**：`.gitignore` 已是目标状态
3. **是**：我知道这一步是“取消追踪”，不是“删除本地文件”
4. **是**：我知道当前要把 commit 落在哪个正式工作线/分支上
5. **是**：我愿意先做一个只包含索引清理的独立 commit

只要其中有一项不能回答“是”，就不应立即执行。

---

## 6. 建议的执行后 commit 形态

建议后续真正执行时，把 commit 限制为：

- `.gitignore`（如果那时还需微调）
- `git rm --cached outputs ready ready_problem_exports` 产生的索引变化
- 可能的一两处说明文档微调

不要混入：
- 大量脚本行为修改
- review 草稿
- tmp 文件清理
- 其它 unrelated 变更

### 推荐 commit message
可以使用类似：

```text
Stop tracking local outputs and ready artifacts
```

或更明确一点：

```text
qjb: stop tracking local outputs ready artifacts
```

---

## 7. 本文给出的结论

基于当前状态，已经可以下这个结论：

- **文档阶段基本完成**
- **`.gitignore` 阶段也已事实上完成**
- 真正还没做的，是**索引清理这一高影响动作本身**

因此下一步不该再讨论“要不要把 outputs/ready 写进 ignore”，而应该明确：

1. 这一步最终落在哪个正式分支
2. 谁来执行 `git rm --cached`
3. 执行后如何验证“索引移除但本地文件还在”

---

## 8. 建议的下一步

完成本文后，建议按下面顺序继续：

1. 明确索引清理 commit 的正式落点分支
2. 在该分支执行：
   ```bash
   git rm -r --cached outputs ready ready_problem_exports
   ```
3. 立即检查本地目录仍在
4. 单独提交索引清理 commit
5. 再进入三机切换与本地重建验证
