---
name: eacks-s3-relation-types
description: EACKS S3 候选关系守卫——Relation 类型学（12 类判定特征）、Rationale 格式、候选纪律（candidate≠事实、禁止静默类型升级）。Use when 从 Claim 集生成候选关系、为关系声明 Type 与 Rationale、或校验候选关系产物合规时。
---

# EACKS S3 候选关系守卫

配套：`eacks-execution`（骨架，本 skill 是 S3 槽位实现）。本 skill 族（`eacks-execution` + 8 个阶段守卫）即 EACKS v1.3 的完整执行形态.

**职责**：候选关系的类型学判定与 Rationale 完整性校验。**全部候选关系标记 Candidate——生成阶段不是事实认定。**

**Guard 接口**（与骨架 block-contracts S3 一致）：
- 输入：Claim 表 + Concept/Correspondence 表 + 候选关系集（agent 生成）
- 输出：类型学合规标记（每候选：Type 判定 + Rationale 完整性 + 纪律检查）+ 修订后的候选 Relation 表

---

## 一、Relation Type 判定特征（12 类）

| Type | 判定特征 | 易混辨析 |
|---|---|---|
| **causal** | X 是 Y 的原因（时序 + 机制 + 排除他因） | 仅相关/伴随 → **associational**（防 Evidence Upgrade 前置；S7 第 5 项依赖此区分） |
| **associational** | X 与 Y 共变/相关，未断言因果 | 原文用"伴随/相关/与…有关" |
| **explanatory** | X 解释 Y（为何 Y 成立） | 与 causal 重叠但弱于因果（解释可部分）；原文用"因为/由于" |
| **supports** | Evidence/Claim 支持另一 Claim | 支持≠证明（支持强度进 Strength 字段） |
| **contradicts** | 两 Claim 断言冲突 | 冲突≠错误（硬原则 3）：先检查条件/层级/测量差异 → 可能降级 Conditional Divergence（S4 处理） |
| **qualifies** | 一 Claim 限定另一 Claim 的范围/条件 | 限定内容必须保留在 condition/boundary（防压缩） |
| **correspondence** | 两概念/Claim 对应但非等价 | 对应≠等价（S2 已判定类型，此处引用） |
| **cross-level** | 跨层级断言关系（观察↔理论↔机制） | 必须标注层级（防 Level Collapse；S7 第 8 项依赖） |
| **generalizes** | 从特例到一般 | 必须带范围声明（防 Boundary Loss；S7 第 3 项依赖） |
| **specializes** | 从一般到特例 | 同上 |
| **competes** | 两理论/解释竞争（并存，未裁决） | 竞争≠折中：禁止制造第三理论（S6 检查依赖） |
| **conditional-divergence** | 表面冲突实为条件/层级/测量差异 | 由 S4 判定产生，S3 不预判 |

## 二、Rationale 格式（每候选必填）

```markdown
- 候选关系：<source_ref> --<Type>--> <target_ref>
- Rationale：
  - 依据 Claim：<claim_id>（原文引用 §位置）
  - 类型选择理由：<为什么是这个 Type，对照判定特征>
  - 证据支持：<EvidenceLink 或待补证据的说明>
  - 候选风险：<已知的备选解释/反向证据/条件限制>
```

Rationale 完整性检查：**四项缺一 → FAIL**（依据/类型理由/证据/风险）。风险字段尤其关键——候选的诚实性标记，防后续"无风险候选"被静默升级。

## 三、候选纪律

1. **全部标记 Candidate**（status=candidate，非 validated）——验证是 S4 的事
2. **Type 必填**：无类型声明 → FAIL（类型是验证路由的依据：S4 按 Type 选 guard）
3. **禁止静默类型升级**：生成阶段不得把 associational 写成 causal、supports 写成证明（与 S1 的防升级前置一致；升级只允许在 S4 验证后且证据充分时）
4. **不得预判裁决**：冲突关系标 contradicts/competes，不自行裁定（S4/S8 处理）
5. **不得制造关系**：无 Claim 依据的关系 → FAIL（S7 第 10 项 Unsupported Synthesis 的源头拦截）

## 四、输出格式

```markdown
# S3 候选关系合规报告
- 输入：N Claim / M 概念对
- 候选关系：K 条（全部 Candidate）
- 合规判定：
  - R1: PASS（Type=causal ✓ / Rationale 四项齐 ✓）
  - R2: FAIL — Type=associational 被写成 causal（依据原文"伴随"）
  - R3: FAIL — 无 Rationale（依据缺失）
- 修订后候选表：<更新 Type/Rationale>
```
