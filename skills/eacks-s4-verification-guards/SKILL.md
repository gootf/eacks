---
name: eacks-s4-verification-guards
description: EACKS S4 验证闸门守卫——Type-Specific Validation 矩阵、证据核对（Role 汇总/类型≠质量）、Anti-Compression 事前拦截、Conditional Divergence 判定、EpistemicStatus 状态裁决。Use when 验证候选关系（按类型选 guard）、核对证据支持、判定矛盾是条件差异还是真冲突、或裁定关系状态（Validated/Disputed/Rejected/Unresolved）时。
---

# EACKS S4 验证闸门守卫

配套：`eacks-execution`（骨架，本 skill 是 S4 槽位实现）。本 skill 族（`eacks-execution` + 8 个阶段守卫）即 EACKS v1.3 的完整执行形态.

**职责**：对候选关系执行 Type-Specific Validation，裁决 EpistemicStatus。**S4 是关系进入知识图的闸门——验证不通过的关系不得进入 S5。** 调用 `scientific-critical-thinking`（证据质量维度）+ `hypothesis-generation`（验证标准维度）作支撑。

**Guard 接口**（与骨架 block-contracts S4 一致）：
- 输入：候选 Relation 表（S3 输出）+ Evidence 表 + EvidenceLink 表 + Claim 表（条件/边界/层级字段）
- 输出：验证后的 Relation 表（EpistemicStatus 更新）+ 未决清单（按 Criticality 排序）+ 验证报告

---

## 一、验证流程

```
候选关系（S3）
  → Step 1 按 Relation Type 路由验证 guard（矩阵见下）
  → Step 2 证据核对（EvidenceLink Role 汇总 + 类型≠质量）
  → Step 3 Anti-Compression 事前检查（条件/边界/层级对照）
  → Step 4 矛盾处理（条件优先 → Conditional Divergence / 真冲突）
  → Step 5 状态裁决（Validated / Disputed / Rejected / Unresolved）
  → 输出：更新后的 Relation 表 + 未决清单
```

## 二、Type-Specific Validation 矩阵

| Relation Type | 验证 guard（检查项） | 硬失败条件 |
|---|---|---|
| **causal** | ① temporal precedence（因先于果）② identification（机制可识别）③ alternative explanations 排除——**三态**：已排除（有证据排除）→ 可判 Validated；已评估未排除 → Disputed；未评估 → 回 S3 补 Rationale 风险字段 ④ robustness（证据稳健性）⑤ 反向因果检查 | 时序反了 / 存在未排除的同等解释 / 证据仅相关 |
| **associational** | ① 共变证据存在 ② 混淆变量提示（不要求排除）③ **不得升为 causal** | 被标记为 causal |
| **mechanistic** | ① 机制链每环有 Claim 依据 ② 环节间连接类型正确 ③ 缺环必须显式标注 | 机制链缺环且未标注 |
| **definitional** | ① source definition 一致（定义出处可查）② 概念一致性（同书/跨书定义对照）③ scope 明确 | 定义无出处 / 与来源定义冲突 |
| **normative** | 规范体系内一致性（内部逻辑一致，**不做实证验证**） | 规范内部矛盾 |
| **predictive** | ① 预测可检验性 ② 条件声明完整 ③ 保持推测语气（不升级为断言） | 预测被表述为已发生事实 |
| **explanatory** | ① 解释与证据匹配 ② 与 causal 的区分保持（弱于因果） | 解释被表述为因果确证 |
| **supports/qualifies** | ① 支持关系与 EvidenceLink Role 一致 ② 支持强度进 Strength 字段 | Role 与类型矛盾 |
| **contradicts/competes** | ① 先走 Step 4 矛盾处理（条件/层级/测量差异优先）② 确证冲突才成立 | 未做差异检查直接判冲突 |
| **generalizes/specializes** | ① 范围声明存在（防 Boundary Loss）② 反例检查 | 无范围声明 |
| **cross-level** | ① 层级标注存在（防 Level Collapse）② 层级转换规则明确 | 无层级标注 |
| **correspondence** | 引用 S2 的 Correspondence 类型判定（此处不重判） | 与 S2 判定冲突 |

## 三、证据核对规则

1. **EvidenceLink Role 汇总**：对每个候选关系汇总所有 EvidenceLink——supports（+1 证据）、weakens（−1）、qualifies（限定范围，不改变支持度但进入 condition）、contradicts（反对证据，进矛盾处理）、contextualizes（语境信息，不参与支持度）
2. **Evidence Type ≠ Evidence Quality**（硬原则）：类型决定**适用性**（如描述性证据不适用于因果断言），质量（强/中/弱）决定**强度**。类型不适用 → 该证据不得计入支持度
3. **裁决门槛**：
   - 支持度 ≥ 1 且无未排除反对证据 → 可判 Validated（配合硬约束全过）
   - 存在反对证据但可标注 → Disputed
   - 硬失败条件触发 → Rejected
   - 证据不足（无支持无反对）→ Unresolved（进未决清单）

## 四、Anti-Compression 事前检查（S4 特有）

验证前对照检查（S7 第 2/3/8 项是事后，此处是**事前拦截**）：
- Relation 的 condition/boundary/level 字段 vs 其依据 Claim 的对应字段
- **压缩信号**：条件有→无（Condition Loss 前置）、边界外扩（Boundary Loss 前置）、跨层未标注（Level Collapse 前置）
- 命中 → **先修复再验证**（回 S3 修订或标注 WARN 继续但不得晋升 Validated→Structural）

## 五、矛盾处理（条件优先）

**前置区分**（在差异检查之前）：**论辩结构 ≠ 断言冲突**——
- 论辩结构：批评者立场 vs 作者回应（立场对立，双方各自成 Claim，无互相否定）→ 不建 Conflict Index 条目（或标注论辩层 competing_theories，不进入断言冲突处理）
- 断言冲突：两断言在相同条件下互相否定（A 断言 X，B 断言 ¬X）→ 进入下述差异检查

```
断言冲突（contradicts 候选）
  → 1. 条件差异检查：两 Claim 条件不同（A|C1 vs A|C2）→ Conditional Divergence（合法，双保留）
  → 2. 层级差异检查：跨层冲突（观察层 vs 理论层）→ 标注 Level 差异，双保留
  → 3. 测量差异检查：不同测量指标 → Measurement 差异，双保留（引用 S2 measurement-corresponding 记录）
  → 4. 确证冲突（同条件同层同测量仍矛盾）→ Genuine Contradiction（进 Conflict Index，双保留）
```

**规则**：矛盾优先解释为 Conditional Divergence（硬约束）；只有完成三步差异检查后仍冲突，才判真冲突。真冲突不是错误（硬原则 3）——双保留进 Conflict Index，不强行消解。

## 六、EpistemicStatus 状态裁决

| 状态 | 进入条件 | 去向 |
|---|---|---|
| **Validated** | 硬约束全过 + 支持度达标 + 无未排除反对 | S5 图整合；可晋升 Structural（需 S7 后） |
| **Disputed** | 存在实质争议（反对证据未排除 / 竞争解释并存） | 保留在图中（标 disputed）；按 Criticality 决定是否升级 S8 |
| **Rejected** | 硬失败条件触发 / 证据反驳 / 类型错误 | 不进图；记录拒绝理由（可追溯） |
| **Unresolved** | 证据不足（无支持无反对） | 进未决清单（按 Criticality 排序）；局部不阻塞（骨架规则） |

## 七、输出格式

```markdown
# S4 验证报告
- 输入：K 条候选关系 / E 条证据
- 结果：V 条 Validated / D 条 Disputed / R 条 Rejected / U 条 Unresolved
- 关键判定：
  - R1 causal: PASS（时序✓ 机制✓ 他因已排除 稳健性✓）→ Validated
  - R2 causal: FAIL — 证据仅相关（associational 被写为 causal）→ Rejected（理由：防升级）
  - R3 contradicts: → Conditional Divergence（C1 有条件 vs C2 无条件，双保留）
  - R4: 未决（证据不足）→ Unresolved（Criticality=critical → 建议 S8）
- 未决清单（按 Criticality）：...
```
