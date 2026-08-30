---
name: eacks-s8-arbitration-template
description: EACKS S8 人工仲裁的写回模板——log-decisions 条目格式 + EACKS 扩展字段（ProvenanceType/关联对象/仲裁依据/裁定结果），含回注转移规则。Use when 记录人工知识仲裁决策（来源/概念/关系/证据/结构/综合事项的裁定）、将 human_decided 决策结构化写回、或从 S8 回注流程时。
---

# EACKS S8 人工仲裁写回模板

配套：`eacks-execution`（骨架，本 skill 是 S8 槽位实现）；`log-decisions`（本仓库内置技能）。本 skill 族（`eacks-execution` + 8 个阶段守卫）即 EACKS v1.3 的完整执行形态.

**职责**：把人工仲裁决策**结构化写回**为可追溯的知识资产（ProvenanceType = human_decided），并驱动回注转移。**决策即知识资产，不是流程噪音。**

**Guard 接口**（与骨架 block-contracts S8 一致）：
- 输入：升级事项（分类 + 结构化选项 + 证据摘要）
- 输出：仲裁记录（append-only）+ 回注转移指令

---

## 一、升级事项分类

| 类别 | 来源转移 | 示例 |
|---|---|---|
| 来源问题 | S0→S8 | 关键来源无法核实（人工可解决）；URL/字段冲突 |
| 概念问题 | S2→S8 | 核心概念严重不可比；unresolved 需裁决 |
| 关系问题 | S4→S8 | 高风险 / Critical 关系无法裁决 |
| 证据问题 | S4→S8 | 证据不足且 Critical（人工提供证据/边界） |
| 结构问题 | S7→S8 | Reconstruction 失败；高风险未决 |
| 综合问题 | S6→S8 | 高阶框架选定 |

## 二、仲裁记录模板（log-decisions 条目 + EACKS 扩展）

记录文件：项目根 `DECISIONS.md`（append-only，`<!-- AI-maintained, append-only -->` 头；**永不编辑/重排/删除既有条目**）。编号 Q<n> 顺序递增，context 用 `eacks/<block>` 标签。

```markdown
## Q<n> — eacks/<block> — <类别>

**Question:** <仲裁事项，转述为准>
**Options considered:** <agent 提供的结构化选项，附证据摘要引用>
**Chosen:** <人工裁定结果>
**Decided-by:** human
**Justification:** <仲裁依据：引用证据/来源/领域知识，或说明推理>
**Outcome:** applied | escalated（→ 更高层裁决）| abstained（专家也无法裁决）
**Ref:** <关联对象引用：Claim/Relation/Concept/Source ID>
**Supersedes:** <仅修订时>

<!-- EACKS 扩展 -->
**ProvenanceType:** human_decided
**对象 ID:** <claim_id / relation_id / concept_id / source_id>
**裁定操作:** accept | reject | differentiate | 补充证据 | 回注 <S2/S4/S5/S6> | abstain
**回注指令:** <对知识对象的后续处理要求：如"R12 分化后回注 S4 重新验证">
```

**EACKS 扩展字段语义**：
- `ProvenanceType: human_decided`：该决策进入 provenance 链（硬原则 11：Human Judgment Is Knowledge）
- `裁定操作`：决定知识对象的去向——accept（认可当前状态）、reject（否决）、differentiate（强制分化）、补充证据、回注指定层、abstain
- `回注指令`：供骨架执行的转移描述（对应第一节的回注边）

## 三、裁定流程

```
升级事项 → 1. 分类（六类表）
        → 2. agent 结构化提交（选项 + 证据摘要 + 各选项后果）
        → 3. 人工裁定（agent 不代答；等待 human 决定）
        → 4. 写回 DECISIONS.md（模板，当场记录，不事后补记）
        → 5. 按裁定操作执行回注转移
        → 6. handoff 时列出本回合 assumed/escalated 条目（供复核）
```

**提交纪律**（来自 log-decisions，保持）：look-before-ask（搜索 spec/项目/历史/先前条目后再提交，过早升级是最常见失败）；选项须附证据引用（cite by reference，不贴原文载荷）；不记 secrets；**当场记录**（running journal，绝不 handoff 时重构）。

**硬底线**：影响不可逆的事项（删除/覆盖源材料、放弃整个体系）——即使 agent 认为可确定，也必须人工裁定。

## 四、回注转移规则

| 裁定操作 | 转移 | 说明 |
|---|---|---|
| accept | S8→终态（Accepted/Provisional） | 专家最终确认 |
| 补充证据/边界 | S8→S4 或 S8→S5 | 专家提供证据/边界后重验 |
| differentiate（分化） | S8→S2 | 专家澄清定义后重新对齐 |
| 回注 S6 | S8→S6 | 专家选定高阶框架 |
| abstain | S8→S_abstain | 专家也无法可靠裁决（合法终态） |
| 迭代预算超限 | S8 或 Abstain | 按骨架全局计数 |

## 五、与其他 guard/工具的关系

- 格式基座：`log-decisions`（本仓库内置技能，提供条目 schema、dedup/revise 规则、handoff 队列）
- 输出消费：骨架 `eacks-execution` 按 `裁定操作` + `回注指令` 执行转移
- 上游依赖：S0/S2/S4/S6/S7 的升级边（升级事项分类对齐骨架转移规则）
