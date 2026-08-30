---
name: eacks-s6-synthesis-guards
description: EACKS S6 高阶综合守卫——五类高阶结构（Cluster/Hierarchy/Mechanism/Boundary/Conflict）的建立判定、No-Third-Theory 裁决、Origin 强制、冲突保留检查与候选晋升生命周期。Use when 从知识图生成高阶结构、裁决是否可制造综合理论、或校验高阶综合产物合规时。
---

# EACKS S6 高阶综合守卫

配套：`eacks-execution`（骨架，本 skill 是 S6 槽位实现）。本 skill 族（`eacks-execution` + 8 个阶段守卫）即 EACKS v1.3 的完整执行形态.生命周期范式参考：Synthadoc（candidate staging）；聚类参考：GraphRAG Leiden（可选轻量实现）。

**职责**：判定高阶结构（Cluster/Hierarchy/Mechanism/Boundary/Conflict）何时可建立、裁决综合命题是否构成"无据第三理论"、强制 Origin 标注与冲突保留。**S6 是组织结构，不是发明结构。**

**Guard 接口**（与骨架 block-contracts S6 一致）：
- 输入：知识图 + Relation Matrix + Conflict Index + Boundary Matrix（S5 产物）+ 高阶结构草案（agent 生成的 Cluster/Hierarchy/Mechanism 提案）
- 输出：高阶结构合规报告（No-Third-Theory 判定 + Origin 完整性 + 冲突保留检查）+ 修订后的高阶结构

---

## 一、五类结构建立判定

| 结构 | 建立条件 | 禁止行为 |
|---|---|---|
| **Cluster** | 节点间有可引用的相似/共现/主题证据 | 用聚类**替代**概念（Cluster 仅组织层，源节点不删除——与 S5 Canonical 规则一致） |
| **Hierarchy** | 引用 S2 的 broader/narrower 判定（不重判）；跨层必须有层级标注 | 无证据的层级指派；跨层未标注（防 Level Collapse 前置） |
| **Mechanism** | 机制链每环有 Validated 关系依据（S4 产物）；缺环显式标注 | 缺环不标注的机制链（防 Unsupported Synthesis 前置） |
| **Boundary** | **引用 S5 的 Boundary Matrix**（不重造） | 新建边界不登记（边界必须进 Boundary Matrix） |
| **Conflict** | **引用 S5 的 Conflict Index**（不重造）；竞争理论显式识别 | 抹除/统一冲突（防 Conflict Erasure 前置） |

**总原则**：S6 的每一类结构都必须**引用下游产物**（S2 层级判定 / S4 验证关系 / S5 Matrix/Index），不是凭空生成。

## 二、No-Third-Theory 裁决（核心）

**定义**：两个（或多个）理论/解释处于竞争状态（Conflict Index 标 competing_theories）时，综合者不得自行制造"第三理论"将其整合——除非满足下列豁免条件。

**豁免条件**（全部满足才允许"第三理论"存在）：
1. **独立证据链**：第三理论有完整 depends_on 链（每条核心断言追溯到 Claim/Evidence）
2. **双方证据均被引用**：整合命题同时引用了竞争双方的证据（不是只取一方）
3. **候选标记**：该理论被标记为 `synthesis_candidate`（未经 S7 重建验证不得晋升 Structural）
4. **无覆盖**：不覆盖/不消解原冲突（原 competing_theories 记录保持 active）

**判定流程**：
```
综合提案 → 1. 是否与既有竞争理论相关？（查 Conflict Index）
         → 2. 是 → 逐条检查豁免条件（1-4）
         →    全过 → 允许（标记 synthesis_candidate）
         →    任一不过 → FAIL（No-Third-Theory 违规）→ 降级为"竞争理论注释"（不建理论节点）
         → 3. 否（新综合，非整合竞争理论）→ 走第三节 Origin 强制检查
```

**FAIL 处置**：违规综合命题不得入图；降级为 evidence 注释或进 S8 人工裁决（若用户坚持该理论）。

## 三、Origin 强制

S6 生成的每个新命题（高阶结构、综合节点）必须：
1. 标记 Origin：`cross_source_synthesized`（跨源综合）或 `system_derived`（系统推导）
2. 附 depends_on 列表（≥1 条源 Claim/Relation）
3. **检查规则**：缺 Origin → FAIL；有 Origin 无 depends_on → FAIL（S7 第 6/10 项检查依赖此字段）

## 四、Conflict 保留检查

- 综合产物不得使 S5 Conflict Index 中的 active 冲突消失（对照检查）
- 竞争理论在 Hierarchy/Cluster 中必须显式并列（不合并、不选边）
- 综合论述提及冲突时，双立场都呈现（禁止单方结论式综合）

## 五、候选晋升生命周期（candidate staging）

借鉴 Synthadoc：高阶结构提案不直接入体系——
```
提案（staging）→ 评审（本 guard 合规检查）→ promote（入图，标记 synthesis_candidate）
                                          → discard（降级 evidence 注释）
                                          → escalate（重大理论争议 → S8 人工）
```
- promote 后的结构在 S7 重建验证通过前**不得晋升 Structural**
- 每次状态变更写入不可变事件日志（记录提案/评审/promote/discard 的时间与依据——可审计）

## 六、输出格式

```markdown
# S6 高阶综合合规报告
- 输入：N 节点 / E 边 / K 冲突 / 提案 P 项
- 结构判定：
  - Cluster C1: PASS（有共现证据 ✓ 源节点保留 ✓）
  - Hierarchy H1: FAIL — 无 S2 层级判定依据
  - Mechanism M1: PASS（每环有 Validated 依据 ✓）
  - 综合提案 T1: PASS（豁免 1-4 全过 → synthesis_candidate）
  - 综合提案 T2: FAIL — 无 depends_on（No-Third-Theory 违规）→ 降级 evidence 注释
- Origin 检查：新命题 12/12 有 Origin + depends_on ✓
- 冲突保留：Conflict Index active 冲突 5/5 保持 ✓
- 生命周期：P 项提案 → promote X / discard Y / escalate Z
```
