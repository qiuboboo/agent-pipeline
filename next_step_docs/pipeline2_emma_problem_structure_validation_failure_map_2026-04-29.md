# EMMA-Chemistry ProblemStructureValidation 失败项映射与最小修复方案
日期：2026-04-29

## 1. 背景

本次 5 样本 repair rerun 中，`EMMA-Chemistry` 题目 `prob_0136fbb4daaecfcbd5f105b4` 在：

- [problem_errors/prob_0136fbb4daaecfcbd5f105b4.json](/d:/Hallucination/workspace/agent-pipeline/pipeline2/outputs_tmp_ready_5samples_20260428_w5_rerun/problem_errors/prob_0136fbb4daaecfcbd5f105b4.json)

报错为：

- `PipelineDataContractError`
- `[ProblemStructureValidation] Problem 'prob_0136fbb4daaecfcbd5f105b4' failed structural verification.`

这个错误文件只保留了总失败信息，没有保留完整 `verification_audit`。因此本次细项映射来自单题 probe 输出：

- [o_emma_psv/problems/prob_0136fbb4daaecfcbd5f105b4.json](/d:/Hallucination/workspace/agent-pipeline/pipeline2/o_emma_psv/problems/prob_0136fbb4daaecfcbd5f105b4.json)

## 2. 总体结论

这题不是答案错了。

- `final_cot_validations`
  - method `1`: `pass=true`
  - method `2`: `pass=true`

真正失败的是：

- `claim_set_validation`
- `node_set_validation`

全局失败原文：

1. `Claim-set validation failed for method '1'.`
2. `Claim-set validation failed for method '2'.`
3. `Node-set validation failed.`
4. `The knowledge-call node for the rule "A valid SMILES may start at any atom in the connected structure" is unsupported by the provided K atoms or visual evidence, so that node is not fully grounded.`
5. `The method-1 node for beginning the SMILES as "*C" is not fully grounded by the provided visual facts and knowledge atoms; it relies on an unsupported starting-atom choice.`
6. `The method-1 final assembly node inherits that grounding gap because it uses the unsupported "*C" prefix, even though the resulting SMILES string is chemically correct.`

## 3. 失败项如何对应回 run 里的错误题

run 里的错误文件已经给出了本题相关 cache 路径：

- `claim_bundles/method 1`
  - `...\\claim_bundles\\8123e8323d44c0f6.json`
- `claim_bundles/method 2`
  - `...\\claim_bundles\\66ca0aa5642ae48a.json`
- `claim_bundle_progress/method 1`
  - `...\\claim_bundle_progress\\2fdc32828cd779e0.json`
- `claim_bundle_progress/method 2`
  - `...\\claim_bundle_progress\\8a9a0a09a902a9ac.json`

也就是说，run 里的错误题没有丢 claim 产物，失败项可以稳定映射回这些 claim / r_node 文本。

### 3.1 Method 1 失败 claim 映射

1. `m1__c25`
   - claim: `R1 is written as "*" in the SMILES transcription.`
   - depends_on: `m1__c8`, `m1__c24`
   - issue: `dependency_broken`

2. `m1__c26`
   - claim: `R2 is written as "*" in the SMILES transcription.`
   - depends_on: `m1__c9`, `m1__c24`
   - issue: `dependency_broken`

3. `m1__c28`
   - claim: `The down-right fragment is written as "C#N".`
   - depends_on: `m1__c16`, `m1__c27`
   - issue: `dependency_broken`

4. `m1__c31`
   - claim: `Using one wildcard substituent attached to the central carbon as the starting atom, the transcription can begin "*C".`
   - depends_on: `m1__c7`, `m1__c8`, `m1__c25`, `m1__c30`
   - issue: `dependency_broken`

5. `m1__c32`
   - claim: `The remaining wildcard substituent is written as the branch "(*)" on the central carbon.`
   - depends_on: `m1__c9`, `m1__c26`, `m1__c29`, `m1__c31`
   - issue: `dependency_broken`

6. `m1__c33`
   - claim: `The nitrile substituent is written as the branch "(C#N)" on the central carbon.`
   - depends_on: `m1__c16`, `m1__c28`, `m1__c29`, `m1__c31`
   - issue: `dependency_broken`

7. `m1__c34`
   - claim: `Combining "*C", "(*)", "(C#N)", and "NC(=O)O" gives "*C(*)(C#N)NC(=O)O".`
   - depends_on: `m1__c4`, `m1__c23`, `m1__c31`, `m1__c32`, `m1__c33`
   - issue: `dependency_broken`

结论：

- method 1 的 claim 本体多数是合理的
- 但在 `ClaimSetValidation` 按 batch 拆分后，依赖链跨 batch，导致 `dependency_closure_ok=false`

### 3.2 Method 2 失败 claim 映射

1. `m2__c14`
   - claim: `The right-side unlabeled vertex is a carbon atom.`
   - depends_on: `m2__c2`, `m2__c11`
   - issue: `dependency_broken`

2. `m2__c16`
   - claim: `The upper-right branch from the central carbon is encoded as NC(=O)O.`
   - depends_on: `m2__c9`, `m2__c10`, `m2__c11`, `m2__c12`, `m2__c13`, `m2__c14`, `m2__c15`
   - issue: `dependency_broken`

3. `m2__c17`
   - claim: `A label R1 is connected to the central carbon by a single bond on the upper-left side.`
   - depends_on: `m2__c3`
   - issue: `dependency_broken`

4. `m2__c18`
   - claim: `A label R2 is connected to the central carbon by a single bond on the lower-left side.`
   - depends_on: `m2__c3`
   - issue: `dependency_broken`

5. `m2__c22`
   - claim: `Assembling the central carbon with two wildcard branches, one C#N branch, and one NC(=O)O branch gives the SMILES C(*)(*)(C#N)NC(=O)O.`
   - depends_on: `m2__c3`, `m2__c8`, `m2__c16`, `m2__c20`, `m2__c21`
   - issue: `dependency_broken`

6. `m2__c23`
   - claim: `Equivalent SMILES strings can differ by the choice of starting atom while preserving the same connectivity and bond orders.`
   - depends_on: `[]`
   - issue: `weak_grounding`

7. `m2__c24`
   - claim: `Starting the same structure at one wildcard substituent gives the equivalent SMILES *C(*)(C#N)NC(=O)O.`
   - depends_on: `m2__c22`, `m2__c23`
   - issue: `weak_grounding`

8. `m2__c27`
   - claim: `Because the arrows are to be ignored and do not affect connectivity, the connectivity-based SMILES from c24 is the answer.`
   - depends_on: `m2__c24`, `m2__c25`, `m2__c26`
   - issue: `missing_dependency`, `unsupported`, `ungrounded`

9. `m2__c28`
   - claim: `*C(*)(C#N)NC(=O)O`
   - depends_on: `m2__c27`
   - issue: `dependency_broken`

结论：

- method 2 也有跨 batch 依赖闭包问题
- 另外还额外引入了一个当前 `k_atoms` 没显式提供的通用知识：
  - `Equivalent SMILES strings can differ by the choice of starting atom ...`

### 3.3 失败 node 映射

1. `r_43f8095cfbb0e027b6474262`
   - node_type: `knowledge_call`
   - canonical_claim: `A valid SMILES may start at any atom in the connected structure.`
   - source_claim_ids: `m1__c30`
   - issue: `unsupported_knowledge_call`, `invalid_source_support`

2. `r_f09e384522704a36ad0a2228`
   - node_type: `derivation`
   - canonical_claim: `Using one wildcard substituent attached to the central carbon as the starting atom, the transcription can begin "*C".`
   - source_claim_ids: `m1__c31`
   - issue: `unsupported`

3. `r_60c310d9716d47b0d146d9c6`
   - node_type: `derivation`
   - canonical_claim: `Combining "*C", "(*)", "(C#N)", and "NC(=O)O" gives "*C(*)(C#N)NC(=O)O".`
   - source_claim_ids: `m1__c34`
   - issue: `unsupported`

结论：

- `node_set` 的 3 个失败点都集中在同一条链上：
  - `m1__c30` 的“任意原子起写 SMILES”知识
  - `m1__c31` 的 `"*C"` 起始选择
  - `m1__c34` 的最终 assembly

## 4. 根因拆解

### 4.1 根因一：ClaimSetValidation 的 batch 太小

当前实现：

- [verification_modules.py](/d:/Hallucination/workspace/agent-pipeline/src/benchmarkallinone/pipeline2/verification_modules.py:5)
  - `CLAIM_VALIDATION_BATCH_SIZE = 12`
- [verification_modules.py](/d:/Hallucination/workspace/agent-pipeline/src/benchmarkallinone/pipeline2/verification_modules.py:446)
  - `claims` 会被按 batch 切开审
- [verification_modules.py](/d:/Hallucination/workspace/agent-pipeline/src/benchmarkallinone/pipeline2/verification_modules.py:452)
  - prompt 还明确写了：`do not assume hidden claims outside this batch`

这会直接导致：

- method 1 的后半段组装 claim 看不到前半段 perception / knowledge claim
- method 2 的后半段重线性化 claim 看不到前半段结构 claim

因此大量 `dependency_broken` 实际是“拆批审计导致的假阴性”。

### 4.2 根因二：当前 PTK/K 原子里没有显式提供 SMILES 等价重线性化知识

当前本题 `k_atoms` 包含：

- wildcard `*`
- branch parentheses
- nitrile `C#N`
- `C(=O)O`
- 忽略箭头

但没有显式包含：

- `Equivalent SMILES strings can differ by the choice of starting atom while preserving the same connectivity and bond orders.`
- 或更简化版本：
  - `A valid SMILES for the same connected structure may be written by starting from different atoms.`

因此：

- method 2 的 `m2__c23` / `m2__c24` 被判 `weak_grounding`
- method 1 的 `m1__c30` 对应 node 被判 `unsupported_knowledge_call`

## 5. 最小修复方案

### 方案 A：先修 verifier batching

这是优先级最高、改动最小、收益最大的修复。

建议：

1. 把 [verification_modules.py](/d:/Hallucination/workspace/agent-pipeline/src/benchmarkallinone/pipeline2/verification_modules.py:5) 的
   - `CLAIM_VALIDATION_BATCH_SIZE = 12`
   - 提高到至少 `48` 或 `64`
2. 同时把
   - `NODE_VALIDATION_BATCH_SIZE = 10`
   - 提高到至少 `24` 或 `32`

这样对本题的直接效果是：

- method 1 的 35 条 claim 可一次性审完
- method 2 的 28 条 claim 可一次性审完
- 跨 batch 的 `dependency_broken` 会大幅消失
- node 端也更容易拿到完整 source-claim 上下文

这是本题最小、最稳的第一步修复。

### 方案 B：补一个 chemistry/SMILES 专用 K atom

在 PTK foundation 生成或 polish 阶段，为 SMILES 题补一个显式 `k_atom`，例如：

- `Equivalent SMILES strings for the same connected structure may differ by the choice of starting atom while preserving connectivity and bond orders.`

或者更短：

- `A valid SMILES for the same connected structure may start at different atoms and still represent the same connectivity.`

这样可以直接补掉：

- `m2__c23` 的 `weak_grounding`
- `m2__c24` 的 `weak_grounding`
- `m1__c30` 对应 node 的 `unsupported_knowledge_call`

### 方案 C：如果不想补 K atom，就限制 claim 生成不要走“任意起点”这条链

这是次优方案。

可以在 chemistry/SMILES claim 生成 prompt 里约束：

- 不要额外引入“SMILES 可从任意原子起写”这类泛化知识
- 若需要给出最终字符串，优先直接基于题目标准表达或已确定的主链方向组织答案

但这个方案不如方案 B 稳，因为：

- method 2 的等价重线性化本身是合理步骤
- 只靠压 prompt，容易在别题反复出现类似 unsupported

## 6. 推荐执行顺序

1. 先做方案 A
   - 先消掉拆批造成的假阴性
2. 再做方案 B
   - 给 SMILES 等价起点补显式知识
3. 然后只重跑这题 probe
   - 看 `ProblemStructureValidation` 是否转绿
4. 若还剩失败
   - 再考虑是否需要对 chemistry claim prompt 做额外收束

## 7. 一句话结论

这题的 `ProblemStructureValidation` 失败，核心不是答案不对，而是：

1. verifier 把 claim 按小 batch 拆开，导致依赖闭包被人为打断；
2. 当前 PTK 没显式提供 `SMILES 等价重线性化 / 可换起点` 这条知识，导致 `"*C"` 起始链条被判 unsupported。
