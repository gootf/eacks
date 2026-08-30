---
name: eacks-s5-artifacts
description: EACKS S5 图整合守卫——Relation Matrix / Conflict Index / Boundary Matrix 三类产物格式定义、非破坏性合并规则（equivalent 门槛 + merge-decision-log + Canonical 仅组织层）、冲突结构化（四类标记 + 双保留）。Use when 把验证过的关系整合为知识图、生成三类合规产物、裁决合并决策或标记合并违规时。
---

# EACKS S5 图整合守卫

配套：`eacks-execution`（骨架，本 skill 是 S5 槽位实现）。本 skill 族（`eacks-execution` + 8 个阶段守卫）即 EACKS v1.3 的完整执行形态.工具层：`onto_merger`（合并引擎，方向反转适配见第五节）。

**职责**：把验证过的关系（S4 输出）整合为知识图，产出三类合规产物，并裁决/标记合并决策。**源概念永不物理删除；Canonical 仅组织层抽象。**

**Guard 接口**（与骨架 block-contracts S5 一致）：
- 输入：验证后的 Relation 表 + Concept/Correspondence 表（S2）+ 合并候选（onto_merger 或人工提出）
- 输出：知识图（graphml/表形式）+ Relation Matrix + Conflict Index + Boundary Matrix + 合并合规报告

---

## 一、三类产物格式（核心契约）

### 1. Relation Matrix（关系矩阵）

```markdown
| relation_id | source_ref | target_ref | type | status | strength | structurality | criticality | condition | scope | evidence_refs | provenance_refs |
```

字段约束（对应架构文档第七节交付物 5）：
- `status`：candidate / validated / disputed / unresolved / rejected（S4 裁决结果直入）
- `structurality`：non_structural / structural（**structural 晋升需 S7 通过后**——S5 默认 non_structural，仅标记"候选晋升"状态）
- `condition` / `scope`：与依据 Claim 字段一致（S4 Anti-Compression 已校验）
- `evidence_refs`：EvidenceLink ID 列表（可追溯）
- `provenance_refs`：来源链引用（可追溯）

### 2. Conflict Index（冲突索引）

```markdown
| conflict_id | claim_a | claim_b | conflict_type | status | evidence | resolution_note |
```

`conflict_type` 四值（对应 S4 矛盾处理结果）：
- `conditional_divergence`：条件/语境差异（双保留，合法）
- `genuine_contradiction`：确证冲突（**双保留**，不消解——硬原则 3）
- `measurement_difference`：测量差异（引用 S2 measurement-corresponding 记录）
- `competing_theories`：竞争理论（双保留，供 S6 高阶综合识别）

`status`：active / resolved（仅当一方被 S8 人工裁决或新证据消除，且须有 resolution_note 引用裁决记录）

### 3. Boundary Matrix（边界矩阵）

```markdown
| boundary_id | subject | boundary_type | boundary_value | source_ref | status |
```

`boundary_type`：applicability（适用范围）/ extrapolation_limit（外推极限）/ condition_boundary（条件边界）/ level_boundary（层级边界）/ measurement_boundary（测量边界）
`status`：active / superseded（须有 Supersedes 引用——防边界静默变更，S7 第 3 项检查对照基准）

## 二、非破坏性合并规则

1. **合并门槛**（引用 S2 判定，不重判）：仅 Correspondence 类型 = equivalent 且证据充分（S2 四门槛全过）才允许合并
2. **合并记录（merge-decision-log）**：每次合并写入
   ```markdown
   | merge_id | concept_a | concept_b | correspondence_ref | evidence | decision | source_concepts_kept |
   ```
   `source_concepts_kept`：**必须为 true**（源概念永不物理删除，只建 Canonical 组织层节点）
3. **Canonical 节点规则**：Canonical 仅组织层抽象（指向源概念的聚合），不替代、不删除、不改变源概念内容
4. **合并违规标记**：
   - 非 equivalent 类型被合并 → FAIL（引用 S2 Correspondence 表为证）
   - 合并无证据 → FAIL
   - 源概念被删除/覆盖 → FAIL（破坏性整合，最高违规）
   - 违规合并须回滚（回 S2/S4 层），不可带病进图

## 三、冲突结构化

- S4 判定的四类冲突全部**显式入图**（双保留原则：冲突双方都是图节点，冲突以 Conflict Index 记录）
- 禁止行为：把 genuine_contradiction 合并为单方结论（= Conflict Erasure，S7 第 7 项检查的图侧对照基准）
- 禁止行为：把 conditional_divergence 强行统一（= 条件抹除）

## 四、onto_merger 接线（方向反转）

- 合并引擎（候选层）：onto_merger 的 align 流程可生成合并候选（调用方案见 `eacks_om_adapter.py`）
- **决策层反转**：其 merges 输出必须经过第二节门槛过滤——仅 equivalent + 证据充分才采纳；其余全部降级为 Correspondence 记录（保持分离）
- 输出映射：onto_merger merges/mappings 表 → EACKS merge-decision-log / Correspondence 表（字段转换 + 补证据引用——onto_merger 的 merges 不带证据，每条合并决策必须补证据才能生效）

## 五、输出格式

```markdown
# S5 图整合合规报告
- 输入：V 条 validated 关系 / C 对合并候选
- 图统计：N 节点 / E 边 / K 冲突（分类计数）
- 合并：M 条采纳（全部 equivalent+证据 ✓）/ X 条降级为 Correspondence（理由：类型非 equivalent / 证据不足）
- 违规标记：0（或列出 FAIL 项 + 回滚动作）
- 产物：Relation Matrix（V 行）/ Conflict Index（K 行）/ Boundary Matrix（B 行）已生成
```
