# qjb docs 回收方案（2026-04-10）

> 目的：说明如何把当前 `temp/run-summary-only` 上相对 `qjb` 多出来的 **5 个 docs-only 提交**，安全地回收到正式承接分支 `qjb`。
>
> 本文只给出回收方案，不直接执行 cherry-pick / merge / reset。

关联文档：
- `docs/qjb_branch_landing_strategy_2026-04-10.md`
- `docs/qjb_index_cleanup_preflight_2026-04-10.md`
- `docs/qjb_branch_execution_checklist_2026-04-10.md`

---

## 1. 当前已确认的前提

截至本次检查：

### 当前 `qjb` worktree
- 路径：`/tmp/agent-pipeline-qjb-clean`
- 分支：`qjb`
- 状态：`git status` 干净
- 头部：`a1d7d197`

### 当前 temp 分支相对 `qjb` 的增量
`temp/run-summary-only` 相对 `qjb` 多出的提交目前是：

1. `72471dc3 docs: add qjb script boundary audit`
2. `c2b5de41 docs: clarify qjb README boundaries`
3. `36ca0b8e docs: sync qjb checklist with gitignore state`
4. `3e6c7711 docs: add qjb index cleanup preflight`
5. `de738f6b docs: define qjb landing branch strategy`

这些提交当前都属于：
- **docs-only 增量**
- 不包含索引清理
- 不包含主脚本行为修改
- 不包含本地 `ready/outputs` 数据操作

---

## 2. 为什么当前适合做“回收而不是重做”

因为当前满足三个低风险条件：

1. `qjb` worktree 是干净的
2. `temp` 相对 `qjb` 的差异非常小，而且是线性的 docs-only 提交
3. 这些提交都已经在当前工作树里落成 commit，不需要重新手改一遍

所以最自然的思路不是：
- 在 `qjb` 上重新手改一次文档

而是：
- 直接把这 5 个提交**顺序回收到 `qjb`**

---

## 3. 推荐方案

### 推荐方案：在现有 `/tmp/agent-pipeline-qjb-clean` worktree 上顺序 cherry-pick 这 5 个提交

推荐原因：

- 当前 `qjb` 已经有独立 worktree，不需要新增新的大仓库 checkout
- `qjb` worktree 当前干净，适合作为正式承接面
- 这 5 个提交是线性 docs-only 提交，按顺序 cherry-pick，语义最清晰
- 如果其中某一步出现冲突，也容易局部处理和回滚

### 推荐顺序
按原提交顺序回收：

1. `72471dc3`
2. `c2b5de41`
3. `36ca0b8e`
4. `3e6c7711`
5. `de738f6b`

### 为什么不建议打乱顺序
因为后面的文档建立在前面的文档结论之上：

- 先有 script boundary audit
- 再有 README 对齐
- 再有 checklist 对齐 `.gitignore` 现状
- 再有 index cleanup preflight
- 最后才有 landing strategy

顺序保持一致，最容易保证内容语义自洽。

---

## 4. 为什么当前不建议用别的方式

## 4.1 不建议继续把工作堆在 `temp/run-summary-only`

因为最终正式落点已经明确应是 `qjb`。
继续留在 temp 上只会把必须做的“回收动作”继续往后拖。

---

## 4.2 不建议现在新开第三份 checkout/worktree

原因很简单：
- 这台机器上大仓库 checkout / worktree 展开已有被 `SIGKILL` 的历史
- 当前已经有一个可用且干净的 `qjb` worktree
- 没必要为了这一步再新造一个成本更高的执行面

---

## 4.3 不建议现在用 squash/手工复制替代线性回收

虽然技术上可以把这 5 个提交内容重新压成 1 个新 commit，但当前不建议：

- 会丢掉已经形成的逐步决策轨迹
- 后续审计时不容易看出：
  - 先做了脚本边界
  - 再做 README 对齐
  - 再做 checklist / preflight / landing strategy

当前这 5 个提交本身就是比较干净的 docs-only 递进历史，保留它们反而更清楚。

---

## 5. 回收时要遵守的约束

在真正执行回收时，应遵守：

1. **只在 `/tmp/agent-pipeline-qjb-clean` 上操作 `qjb`**
2. **不要在当前主工作树里切分支**，避免卷入大脏工作树状态
3. **不要顺手处理 `ready/` / `outputs/` 脏改**
4. **不要把 tmp 文件清理混进回收动作**
5. **每一步都确认 `git status` 干净后再继续下一步**

---

## 6. 回收完成后的验收标准

如果后续执行回收，完成后应满足：

### 6.1 `qjb` 头部前进到最新 docs 状态
也就是 `qjb` 应吸收以下 5 个提交的内容：
- `72471dc3`
- `c2b5de41`
- `36ca0b8e`
- `3e6c7711`
- `de738f6b`

### 6.2 `qjb` worktree 仍然干净
回收完成后应检查：
- `git status` 干净
- 没有把本地运行产物卷进去

### 6.3 后续高影响动作可以直接在 `qjb` 上继续
也就是后续就不需要再说：
- “先在 temp 做，再收回 qjb”

而可以直接进入：
- `git rm -r --cached outputs ready ready_problem_exports`

---

## 7. 本文给出的建议结论

基于当前真实状态，建议采用：

> **现有 `/tmp/agent-pipeline-qjb-clean` worktree + 顺序 cherry-pick 5 个 docs-only 提交到 `qjb`**

这是当前：
- 风险最低
- 分支语义最清晰
- 最不容易卷入当前大脏工作树
- 且能直接为后续索引清理铺路

---

## 8. 建议的下一步

完成本文后，下一步就可以从“只写方案”进入“真正执行回收动作”了：

1. 在 `/tmp/agent-pipeline-qjb-clean` 上顺序回收这 5 个 docs-only 提交
2. 验证 `qjb` worktree 保持干净
3. 再进入索引清理执行
