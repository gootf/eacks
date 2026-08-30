---
name: eacks-s1-decomposition
description: EACKS S1 Claim 解构守卫——最小充分单元判定、风险驱动细拆、禁止无限原子化、ClaimType 与 Origin 标记规则。Use when 把 Source 文本解构为 Claim 表、判定某断言是否已拆到最小充分单元、或校验解构产物合规时。
---

# EACKS S1 Claim 解构守卫

配套：`eacks-execution`（骨架，本 skill 是 S1 槽位实现）。本 skill 族（`eacks-execution` + 8 个阶段守卫）即 EACKS v1.3 的完整执行形态.

**职责**：把 Source 文本解构为 Claim 表（最小充分单元），并对解构产物做合规判定。**拆到可独立验证即停——既不欠拆（粒度太粗）也不过拆（无限原子化）。**

**Guard 接口**（与骨架 block-contracts S1 一致）：
- 输入：Source 文本（分段）+ Claim 草案集（agent 初解构结果）
- 输出：解构合规标记（每 Claim：最小充分性 PASS/WARN/FAIL + 原子化检查 + Origin 正确性）+ 修订后的 Claim 表

---

## 一、最小充分单元判定

**定义**：一个 Claim 是"最小充分单元"，当且仅当——拆开任一成分后，剩余部分无法独立验证或反驳（SPO 或条件/边界缺失导致断言不可检验）。

**判定规则**（逐条检查，全过即最小充分）：
1. **SPO 完整**：主语、谓词、宾语齐全（definitional 类允许"概念-定义"形态）
2. **可独立检验**：不依赖同段落其他句子的隐含前提（隐含前提必须显式化为 condition）
3. **单断言**：不含并列复合断言（"A 且 B"须拆为两条；"因为 X 所以 Y"须拆为因果链 Claim + 支持关系）
4. **条件/边界完整**：原文有条件限定（"仅当…""在…中"）必须进入 condition/boundary 字段，不得丢弃（S7 第 2/3 项检查依赖此字段）

**欠拆信号**（→ WARN/FAIL，需细拆）：一条 Claim 含多个可独立验证的主张；SPO 中宾语是复合列表（"A、B、C"→ 拆开或标注为集合断言并保留边界）。

## 二、风险驱动细拆

拆解深度不统一，按风险分配：
- **高风险段**（高 Criticality 概念、高歧义段落、跨理论关键断言、可能被下游合并/综合的段）→ 细拆到最小充分单元
- **低风险段**（背景叙述、历史综述、已标注的外围材料）→ 粗粒度（段级 Claim 即可，标注 granularity=coarse）
- 细拆触发信号：断言是结构性前提（下游多个 Claim 依赖）、原文含多个条件分支、术语首次定义

## 三、禁止无限原子化（停止条件）

出现以下任一信号即**停止拆解**（当前单元已是最小充分）：
1. **无独立验证价值**：拆分后任何部分都无法单独对照原文验证（纯语法碎片）
2. **上下文依赖**：部分离开整体即无意义（如代词指代、比较基准）
3. **原文原子性**：原文本身是单一断言（不可再分）
4. 过度拆解信号 → WARN：SPO 成分被继续拆分（主语内部的名词短语拆成 Claim）、条件从句被拆成独立 Claim（条件属于其断言，不是独立断言）

## 四、ClaimType 判定指引（9 类）

| Type | 判定特征 | 反例提示 |
|---|---|---|
| Descriptive | 陈述事实/状态，无因果无规范 | 含"因为"→ 非 descriptive |
| Causal | 断言因果关系（X 导致/引发/产生 Y） | 仅相关/伴随 → 应标 associational（防 Evidence Upgrade 前置） |
| Mechanistic | 描述机制链（X 通过 M 导致 Y） | 无中间机制 → causal |
| Predictive | 对未来状态的断言 | 转述他人预测 → origin=source_asserted 但语气保留推测（防升级） |
| Definitional | 概念定义（"X 是…"） | 定义须带出处（source_asserted） |
| Taxonomic | 分类/层级归属 | 归类须有依据 |
| Interpretive | 解释/解读（作者对材料的解释） | 与源文本直接陈述区分 |
| Methodological | 关于方法/程序的断言 | — |
| Normative | 应然断言（应当/必须） | 与 descriptive 严格区分 |

## 五、Origin 标记规则

- `source_asserted`：原文显式陈述
- `source_inferred`：**同一来源内部**由系统从显式文本推断（原文暗含但未明说）；必须附推断依据（原文引用 + 推断步骤）
- `cross_source_synthesized`：跨来源综合（S3 之后才可能出现）
- `system_derived`：系统推导（须 depends_on ≥1 条 source-derived Claim）
- `human_decided`：人工裁定（S8 产物）
- **规则**：source_inferred 不得伪装 source_asserted（硬原则 7）；推断必须可追溯（S7 第 6 项检查依赖）

## 六、输出格式

```markdown
# S1 解构合规报告
- 来源：<source_id> <分段>
- 总计 N Claim；细拆 M 条（风险驱动），粗粒度 K 条
- 合规判定：
  - C1: PASS（最小充分 ✓ / Type=descriptive / Origin=source_asserted）
  - C2: WARN — 含并列断言"X 导致 Y 且 Z" → 拆为 C2a/C2b
  - C3: FAIL — 条件"仅当…"未入 condition 字段
- 修订后 Claim 表：<更新字段>
```
