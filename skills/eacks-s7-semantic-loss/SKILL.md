---
name: eacks-s7-semantic-loss
description: EACKS S7 重建闸门的 Semantic Loss Taxonomy 检查器——十项语义损失的操作化检测（定义/信号/判定/严重度）+ round-trip 保真度评估 + 硬否决判定。Use when 对综合后的知识体系执行 S→K̂ 反向重建与保守性检查、判定体系是否发生语义失真、或生成 Reconstruction Report 时。
---

# EACKS S7 Semantic Loss Taxonomy 检查器

配套：`eacks-execution`（骨架，本 skill 是 S7 槽位实现）。本 skill 族（`eacks-execution` + 8 个阶段守卫）即 EACKS v1.3 的完整执行形态.

**职责**：判定综合后的知识体系 K̂ 相对原始知识 S 是否保守——是否存在十类语义损失、损失是否构成硬否决。**硬否决优先于软评分**。

**Guard 接口**（与骨架 block-contracts S7 一致）：
- 输入：原始知识 S（Claim/Relation/Evidence 表）、综合体系 K̂（高阶结构 + 图）、重建文本 T̂（round-trip 重述）、重建结构 R̂（从 T̂ 重建的对象表）、**Structurality 清单**（S5 产物：K̂ 中断言是否晋升 Structural——Condition Loss 升级判定依赖；缺失时按约定：K̂ 论证骨架断言默认视为 Structural）
- 输出：Reconstruction Report（十项检查结果 + round-trip fidelity + 硬否决判定 + 修复要求）

**判定约定**：同一断言可命中多项损失（如证据升级 + 测量塌缩同时发生）——报告允许重复标记，各项独立判定，不做互斥。

---

## 一、十项 Semantic Loss 操作化定义

严重度分级原则（不按类型固定，按可修复性与影响）：**FAIL（硬否决）** = 结构性破坏或关键断言真值改变，必须回退重做；**WARN（软扣分）** = 可标注修复，修复前该对象不得晋升 Structural。

| # | 损失 | 定义 | 检测信号 | 判定规则 | 默认严重度与升级条件 |
|---|---|---|---|---|---|
| 1 | **Concept Collapse** 概念塌缩 | K̂ 中两个在 S 中可区分的概念被合并为一，且无对应证据 | S 与 K̂ 的 Concept 表对照；合并记录中 correspondence_type ≠ equivalent 却被合并；等价合并但定义域被收窄 | 无 equivalent 证据的合并 → FAIL | 硬。任何无据合并即 FAIL（不可逆结构破坏） |
| 2 | **Condition Loss** 条件丢失 | K̂ 断言丢失 S 中该断言的成立条件（A\|C → A） | S 的 claim.condition 字段 vs K̂ 对应断言；重述文本条件子句缺失；round-trip 重建后 condition 为空 | 条件字段有→无且无替换说明 → 至少 WARN | 软。升级硬：丢失的是关键断言的成立前提（"仅当…"类）且该断言为 Structural |
| 3 | **Boundary Loss** 边界丢失 | K̂ 丢失 S 的适用范围/外推边界 | boundary 字段缺失；generalizes 关系缺范围声明；外推表述超出证据范围 | 有边界声明却丢失 → WARN；边界丢失导致错误外推 → FAIL | 软→硬（错误外推时） |
| 4 | **Direction Loss** 方向反转 | K̂ 中关系方向与 S 相反（A→B 变 B→A） | 机械比较 S 与 R̂ 的 relation(source,target) 对；round-trip 重建方向翻转 | 方向不一致 → FAIL | 硬。方向错误直接改变断言内容 |
| 5 | **Evidence Upgrade** 证据升级 | K̂ 提升证据强度或关系类型（correlation→causal；可能→必然） | relation_type 从 associational 变 causal；strength 提升；断言用词升级；evidence 质量与断言强度不匹配。**升级词对示例**：曙光/迹象→证明/必然、可能/或许→一定、相关/伴随→因果、推测→断言 | 类型/强度升级且无新证据 → FAIL | 硬。违背保守性原则核心（硬原则 2、8） |
| 6 | **Provenance Loss** 来源丢失 | K̂ 节点/关系失去完整来源链 | provenance 链完整性检查：High-Order Claim→…→Source 断裂；derived/synthesized 节点缺 depends_on | 任何高阶命题链断裂 → FAIL | 硬。违反可追溯性根本要求 |
| 7 | **Conflict Erasure** 冲突抹除 | S 中的矛盾在 K̂ 中被消解为一致 | S 的 Conflict Index vs K̂ 冲突结构；重述文本把矛盾双方合并为单一结论 | 原冲突消失且无 Conditional Divergence/Competing Theories 标注 → FAIL | 硬。Conflict ≠ Error（硬原则 3） |
| 8 | **Level Collapse** 层级塌缩 | 跨层断言被压到单层（观察/机制/理论层混淆） | claim.level 字段；不同层级命题被并置；cross-level 关系缺层级标注。**"实质改变断言性质"示例**：手段层命题（"采取政策 X"）与目标层命题（"达成价值 Y"）被合并为单一因果断言（"采取 X 即可达成 Y"）——手段被宣称直接达成目标 | 层级字段丢失或跨层关系无标注 → WARN；观察层断言被表述为理论层 → FAIL | 软→硬（层级混淆改变断言性质时） |
| 9 | **Measurement Collapse** 测量塌缩 | 不同测量/操作化被当成同一测量 | evidence 的 measurement 字段；不同指标被并置；measurement-corresponding 误标为 equivalent | 不同测量被合并且无 measurement-corresponding 标注 → WARN；测量差异实质改变结论 → FAIL | 软→硬（结论真值改变时） |
| 10 | **Unsupported Synthesis** 无据综合 | K̂ 出现 S 中无依据的中间理论/综合命题（"第三理论"） | 系统生成的高阶命题缺 depends_on 链；竞争理论间出现折中理论；synthesis 节点无证据 | 无 depends_on 的合成命题 → FAIL | 硬。Abstention > Unsupported Synthesis（硬原则 10） |

## 二、检测流程

```
输入：S, K̂, T̂, R̂
  │
  ├─ Step 1  round-trip 保真度评估（工具层）
  │      fidelity = α·structure_f1 + (1−α)·ROUGE-L（预处理后）
  │      fidelity < τ_select → 高风险标记，强制全项检查
  │      fidelity ≥ τ_select → 机械项全查 + 语义项抽检（Structural 级必查）
  │
  ├─ Step 2  机械检查（确定性，先跑）
  │      ① Direction Loss：S.relations vs R̂.relations 方向对照
  │      ② Concept Collapse：合并记录对照（correspondence_type ≠ equivalent 却合并）
  │      ③ Provenance Loss：provenance 链完整性扫描
  │      ④ Conflict Erasure：S Conflict Index vs K̂ 冲突结构对照
  │
  ├─ Step 3  语义检查（LLM 判定，逐项）
  │      ② Condition Loss（条件字段对照 + 重述文本条件子句扫描）
  │      ③ Boundary Loss（boundary 字段 + 外推范围声明）
  │      ⑤ Evidence Upgrade（type/strength 对照 + 用词升级扫描）
  │      ⑧ Level Collapse（level 字段 + 跨层关系标注）
  │      ⑨ Measurement Collapse（measurement 字段 + 指标并置检查）
  │      ⑩ Unsupported Synthesis（depends_on 完整性 + 折中理论检测）
  │
  └─ Step 4  判定与报告
         任一 FAIL → REJECT（回退至对应层 / 升级 S8 / Abstain，按骨架转移规则）
         仅 WARN → 通过，附修复要求清单；修复前相关对象不得晋升 Structural
```

**检查顺序原则**：机械项先跑（零成本、确定性），命中 FAIL 直接短路；语义项按"便宜优先"（字段对照先于重述文本分析）。每项检查记录证据定位（对象 ID + 字段 + 原文引用），不可只给结论。

## 三、round-trip 引擎接线（工具层）

参考实现：`tools/eacks_roundtrip.py`（纯标准库）。本 guard 的引擎约定：

```
重述模板（EACKS 对象版）：把 K̂ 的关键结构（Structural 级 Relation 及其 Claim）列表
   → 要求 LLM 用自然语言重述（禁止添加/省略/翻转）
重建模板：把重述文本 → 重建为 (source, relation_type, target, condition, boundary) 列表
保真度：fidelity = α·structure_f1 + (1−α)·ROUGE-L，α=0.7
阈值：τ_select = 0.85（低于即高风险，强制全项检查）
```

接线状态：✅ 已接线。确定性部分 = `eacks_roundtrip.py`（位置解析见 `eacks-execution` 第八节——工作区 `tools/` 或本 skill `scripts/` 副本；结构比对含方向反转/缺失/新增检出 + ROUGE-L 中文 LCS 实现 + fidelity=α·structure_f1+(1−α)·rouge + τ=0.85；纯标准库；方向反转检出已验证）。LLM 通道（重述 T̂ 生成、重建 R̂）由 agent 充当。若遇 LLM 不可用，可降级为"直接重述-重建单轮"（仅机械项检查）。

## 四、输出格式（Reconstruction Report）

```markdown
# Reconstruction Report
- 输入：S（N Claim / M Relation），K̂（H 个高阶结构）
- round-trip：fidelity 0.87 / τ_select 0.85 → PASS（结构级全查）
- 十项检查：
  1. Concept Collapse:   PASS
  2. Condition Loss:    WARN ×2 — R12（缺"仅当X"）、R34（缺条件）→ 修复要求见下
  3. Boundary Loss:     PASS
  4. Direction Loss:    PASS
  5. Evidence Upgrade:  PASS
  6. Provenance Loss:   PASS
  7. Conflict Erasure:  PASS（2 处 Conditional Divergence 已标注）
  8. Level Collapse:    PASS
  9. Measurement Collapse: PASS
  10. Unsupported Synthesis: PASS
- 硬否决：无
- Soft Score：82/100（WARN 扣分）
- 判定：Provisional —— WARN 修复前 R12/R34 不得晋升 Structural
- 修复要求：[R12 补注 condition 字段，引用 S 原文 §…；R34 同上]
```

## 五、与其他 guard/工具的关系

- 输入依赖：S2 概念表（Concept Collapse 对照基准）、S4 验证结果（Evidence Upgrade 对照基准）、S5 Conflict Index（Conflict Erasure 对照基准）
- 输出消费：骨架 eacks-execution 按报告判定转移（Accepted/Provisional/回退/S8/Abstain）
- 工具层：round-trip 引擎（重建 + fidelity）；AlignScore/factCC 方法可作语义一致性补充度量（可选）
