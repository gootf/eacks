---
name: eacks-s2-concept-alignment
description: EACKS S2 概念澄清与对齐守卫——Jingle-Jangle 检测、Correspondence 八类型判定、默认分化裁决，含 onto_merger 工具接线（方向反转适配）。Use when 对 Claim 中的概念做对齐判定（同名异义/异名同义）、建立 Correspondence 表、或裁决概念是否可合并时。
---

# EACKS S2 概念澄清与对齐守卫

配套：`eacks-execution`（骨架，本 skill 是 S2 槽位实现）。本 skill 族（`eacks-execution` + 8 个阶段守卫）即 EACKS v1.3 的完整执行形态.

**职责**：对 Claim 中的概念执行对齐判定——检测 Jingle-Jangle、建立 Correspondence（8 类型）、执行默认分化。**合并不是默认目标；无证据即分离。**

**Guard 接口**（与骨架 block-contracts S2 一致）：
- 输入：Claim 表（含概念引用）+ 概念候选对（名称归一化结果 / onto_merger 候选）
- 输出：Concept 表（含层级）+ Correspondence 表（8 类型 + 证据）+ 分化记录（unresolved 列表及原因）

---

## 一、流程概览

```
Claim 表 → 概念抽取
   → Step 1 候选对生成（三层递进）
        L1 名称归一化（词形/大小写/连字符变体 → 候选）
        L2 onto_merger 候选（lexical + embedding 匹配，工具层）
        L3 语义候选（LLM 从定义对照中发现异名同义/同名异义候选）
   → Step 2 Jingle-Jangle 检测（对每个候选对）
   → Step 3 Correspondence 类型判定（8 值规则表）
   → Step 4 默认分化裁决（门槛规则）
   → 输出 Concept 表 + Correspondence 表 + 分化记录
```

## 二、Jingle-Jangle 检测（操作化）

| 类型 | 定义 | 检测信号 | 处置 |
|---|---|---|---|
| **Jingle 陷阱**（同名异义） | 同一名称，不同定义/构念 | 两处 Claim 用同一名称但定义要素不同（内涵、外延、语境、测量至少一项冲突） | **必须分化**：拆为两个概念（加消歧后缀，规范示例：`名称[自称]`/`名称[理论定义]`，或下标 ₐ/b）；除非定义对照确证 equivalent，否则禁止以同名合并 |
| **Jangle 陷阱**（异名同义） | 不同名称，同一构念 | 两名称的定义要素一致但用词不同（术语变体、翻译差异、框架差异） | 可建立 correspondence；**不物理合并**（源概念保留），在 Correspondence 表记 equivalent 并附定义对照证据 |

**定义要素对照法**（判定依据，四项全比）：内涵（定义核心句）、外延（覆盖对象集合）、语境（所在框架/层级）、测量（操作化方式）。

**Jingle-Jangle 检查结果必须写入 Correspondence 表**：无论命中与否，每个候选对都有一条记录（含对照证据与结论），保证 S7 的 Concept Collapse 检查有对照基准。

## 三、Correspondence 八类型判定规则

| 类型 | 判定条件（须同时满足） | 典型证据 | 默认动作 |
|---|---|---|---|
| **equivalent** | 定义要素四项全部一致 + 双向蕴含 + 无已知差异 | 源定义对照、权威术语表 | 可合并（还需过 Step 4 门槛）；源概念保留。**双向蕴含判定指引**：A 的目标表述与 B 的手段清单互相覆盖（A 断言的全部内容 B 也断言，反之亦然）；仅部分覆盖（如 A 强调目标、B 强调手段清单）→ 无双向蕴含 → 降级 corresponding |
| **corresponding** | 功能/角色对应但内涵有实质差异（跨框架对应物） | 跨理论对应关系说明 | 不合并，记录类型 |
| **broader** | A 的外延 ⊇ B 的外延，且内涵包含 | 层级证据（子类/父类声明） | 不合并，记录上下位 |
| **narrower** | A 的外延 ⊆ B 的外延（与 broader 互为镜像） | 同上 | 不合并，记录上下位 |
| **overlapping** | 外延部分相交，各有独立部分 | 实例/范围对照 | 不合并，记录交集 |
| **measurement-corresponding** | 同一构念的不同测量/操作化（指标不同，构念相同） | 测量定义对照 | 不合并；防 Measurement Collapse（S7 第 9 项依赖此记录） |
| **different** | 定义要素存在实质冲突，确证不同构念 | 定义对照的冲突证据 | 记录类型；若原本同名 → 触发 Jingle 分化 |
| **unresolved** | 证据不足，无法判定任何类型 | 证据缺口说明 | **合法状态**：保留分离，记录缺口（供 S4/S8 后续处理） |

判定门槛：**证据不足时禁止猜测**——不能确证就记 unresolved（默认分化），而不是凭相似度猜 equivalent。

## 四、默认分化裁决（合并门槛）

合并（equivalent 且进入 merges）必须**全部**满足：
1. Correspondence 类型判定 = equivalent（非对应/相似/重叠）
2. 定义要素四项对照均有证据（非凭名称相似）
3. 无已知差异（无 conflicting 证据、无测量差异、无层级差异）
4. 若涉及 S 中已有的分化记录（unresolved/different），须先经 S4 或 S8 裁决解除

任一不满足 → 保持分离（Correspondence 表记录 + 分化原因）。**合并是例外，分离是默认。**

## 五、onto_merger 工具接线（方向反转适配）

工具：onto_merger（对齐引擎；位置解析见 `eacks-execution` 第八节——工作区 `candidates/onto_merger/` 或按恢复流程重下；适配调用 `eacks_om_adapter.py`）。

**适配原则——候选层直接用，决策层必须反转**：

| onto_merger 能力 | EACKS 使用方式 |
|---|---|
| nodes/mappings/hierarchies 输入模型 | 直接对应 Concept/候选对/层级——表格式转换即可 |
| 对齐引擎（lexical + 结构匹配） | **只用作候选生成层**（L2），不采用其合并决策 |
| merges 输出（默认合并最大化） | **反转**：仅当 evidence 充分的 equivalent 才进入 EACKS merges；其余全部降级为 Correspondence 记录（保持分离） |
| 源对齐优先级（seed → 逐源） | 可复用为检查顺序（优先对齐核心源） |

**适配层必须包含**：方向反转守卫（默认分化）+ 证据附着的强制（onto_merger 的 merges 不带证据 → 每条合并决策必须补证据引用才能生效）+ 输出映射（其 merges/mappings 表 → EACKS Correspondence 表）。

## 六、输出格式

**Concept 表**：`id, 名称, 定义（内涵）, 外延, 层级, 源概念引用, 消歧后缀（Jingle 分化时）`

**Correspondence 表**：`concept_a, concept_b, correspondence_type, 证据（定义要素对照 + 引用）, 默认分化标记, 状态（active/待裁决）, 来源书/章节（跨书语境记录——跨书判定依赖）`

**分化记录**：`concept_a, concept_b, 原因（unresolved 缺口 / different 冲突 / Jingle 分化）, 建议去向（S4/S8）`

## 七、与其他 guard/工具的关系

- 输入依赖：S1 的 Claim 表（概念引用）
- 输出消费：S3 候选关系（概念对可用性）、S5 非破坏性合并（merges 决策）、**S7 第 1 项 Concept Collapse 的对照基准**（合并记录 + Correspondence 表）
- 工具层：onto_merger（候选生成，方向反转）
