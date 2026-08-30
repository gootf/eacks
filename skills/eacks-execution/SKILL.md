---
name: eacks-execution
description: EACKS v1.3 协议执行骨架——9 个处理块（S0–S8）的输入/输出契约、调用映射与转移规则；guard 槽位逐块填充。Use when 执行知识综合流程（异质知识源→可追溯高阶知识体系）、按 EACKS 协议编排 S0–S8、或为某 block 挂接 guard/工具层时。
---

# EACKS 执行骨架（v1.3 Final）

本 skill 族（`eacks-execution` + 8 个阶段守卫）即 EACKS v1.3 的完整执行形态。本 skill 是 **Layer 4 编排层**：定义 9 个处理块的契约、调用映射与转移规则；协议守卫（guard）逐块填充，槽位状态见第五节。工具层（onto_merger / round-trip 引擎 / log-decisions）见第六节。

**最高原则**：先判断知识是否允许被统一，再判断如何组织统一；统一不是默认目标。

## 一、EFSM 概览

```
S0 摄取 → S1 解构 → S2 概念对齐 → S3 候选关系 → S4 验证闸门 → S5 图整合 → S6 高阶综合 → S7 重建闸门 → Outcome
```

- **回退边**：S4→S2（语义/层级/定义问题）、S4→S4（降级/分化/条件化后重验）、S5→S2（概念问题）、S5→S4（关系/证据问题）、S7→S2/S4/S5/S6（对应层问题）
- **升级边**：S0→S8（关键来源无法核实且人工可解决）、S2→S8（核心概念严重不可比）、S4→S8（高风险 Critical 关系无法裁决）、S7→S8（高风险未决/Reconstruction 失败）
- **弃权边**：S0→Abstain（来源根本不可核实）、S4→Abstain（证据严重不足且 Critical）、S7→Abstain（Critical 结构无法重建）、S8→Abstain（专家也无法裁决）
- **终态**：Accepted / Provisional / Abstained（判定规则见第三节）

## 二、9 Block 契约与调用映射

| Block | 输入 | 处理 | 输出 | 保护机制 | 调用映射 | Guard 槽位 |
|---|---|---|---|---|---|---|
| **S0** Ingestion | 异质知识源（书籍/文本/PDF/OCR/网络） | 来源解析、元数据、初步证据类型；来源失败按 Criticality 与可解决性分流 | Source 登记表（唯一 ID + 元数据 + provenance 坐标） | 禁止来源幻觉；Unverified 不得升为核心证据；Completeness Gate | `corpus-knowledge-engineering`（L0–L2）+ `grounded-citations`（网络来源）+ `ocr-and-documents`/`pdf` | — 已就绪 |
| **S1** Claim 解构 | Source 文本 | 最小充分单元解构（粗粒度 + 风险驱动细拆） | Claim 表（SPO + Context/Condition/Boundary/Level + ClaimType + Origin） | 禁止无限原子化；agent-derived 不得伪装 source-derived | `corpus-knowledge-engineering`（claim 三层分类 + 坐标） | ✅ `eacks-s1-decomposition`·本仓库 |
| **S2** 概念对齐 | Claim 中的概念 | Jingle-Jangle 检查、层级对齐、Correspondence 建立 | Concept 表 + Correspondence 表（8 类型） | 默认分化；不可比较是合法状态；Correspondence ≠ Equivalence | `onto_merger`（工具层，方向反转适配） | ✅ `eacks-s2-concept-alignment`·本仓库 |
| **S3** 候选关系 | Claim 集 | 生成带 Rationale 的候选关系 | Relation 表（全部标记 Candidate + Rationale） | 候选非事实；类型声明 | `hypothesis-generation`（候选纪律） | ✅ `eacks-s3-relation-types`·本仓库 |
| **S4** 验证闸门 | 候选关系 + 证据 | Type-Specific Validation（不同 Relation Type 不同 Guard） | Validated / Disputed / Rejected 关系 | Anti-Compression；条件优先；证据类型≠质量；矛盾优先解释为 Conditional Divergence | `scientific-critical-thinking` + `hypothesis-generation` | ✅ `eacks-s4-verification-guards`·本仓库 |
| **S5** 图整合 | 验证过的关系 | 非破坏性整合 + 冲突结构化 | 知识图 + Conflict Index | 源概念永不删除；Canonical 仅组织层 | `corpus-knowledge-engineering`（合并纪律）+ `onto_merger`（合并引擎） | ✅ `eacks-s5-artifacts`·本仓库 |
| **S6** 高阶综合 | 知识图 | Cluster / Hierarchy / Mechanism / Boundary / Conflict 生成 | 高阶结构（Boundary Matrix 等） | 禁止无依据"第三理论"；新命题必须标 Origin | 可选轻量聚类；Synthadoc 生命周期范式 | ✅ `eacks-s6-synthesis-guards`·本仓库 |
| **S7** 重建闸门 | 综合后体系 K̂ | S→K̂ 反向重建 + 保真度评估 + 损失检查 | Reconstruction 报告 + 通过/否决 | Semantic Loss Taxonomy 硬否决优先于软评分 | round-trip 引擎（工具层，已接线：`eacks_roundtrip.py`，位置解析见第八节） | ✅ `eacks-s7-semantic-loss`·本仓库 |
| **S8** 人工仲裁 | 算法无法裁决事项 | 人工裁定 + 结构化写回 | 仲裁记录（ProvenanceType = human_decided） | 决策即知识资产；写回可追溯 | `log-decisions`（本仓库内置） | ✅ `eacks-s8-arbitration-template`·本仓库 |

## 三、转移规则与终态判定

- **进入**：前序 block 输出表通过契约校验（必填字段齐全、provenance 完整）。
- **回退**：触发条件见第一节；每次回退计入迭代预算，超限 → S8 或 Abstain。
- **升级 S8**：仅当事项超出算法可靠裁决边界（Critical + 人工可解决）。
- **终态判定**：
  - **Accepted**：硬约束全部通过 + Soft Score 达标 + Risk 可接受
  - **Provisional**：核心可信，存在已显式标注的有限不确定性（须附 Uncertainty Report）
  - **Abstained**：核心结构不足以支持可靠统一（合法结果，非失败）
- **局部 vs 全局弃权**：单个 Unresolved Relation 不自动阻塞；仅当未决对象触及 CoreStructure（按 Criticality、Structurality、Propagation 加权）才全局 Abstain。

## 四、共享对象 Schema（跨 block 契约）

| 对象 | 字段 | 说明 |
|---|---|---|
| Source | id, 元数据, provenance 坐标 | 唯一 ID，禁止幻觉 |
| Concept | id, 名称, 层级, 源引用 | 可被多个 Claim 引用；源概念永不删除 |
| Claim | SPO + Context/Condition/Boundary/Level + ClaimType + Origin | ClaimType：Descriptive/Causal/Mechanistic/Predictive/Definitional/Taxonomic/Interpretive/Methodological/Normative；Origin：source_asserted（同源显式）/source_inferred（同源推断）/cross_source_synthesized/system_derived/human_decided |
| Evidence | Type/Design/Identification/Quality/Robustness/Replication/ExternalValidity/Limitations | Evidence Type ≠ Evidence Quality |
| EvidenceLink | Evidence ↔ Claim/Relation + Role | Role：supports/weakens/qualifies/contradicts/contextualizes |
| Relation | Type + EpistemicStatus + Strength + Structurality + Criticality + Condition + Scope + EvidenceRefs + ProvenanceRefs | 四维正交；Type：causal/associational/…/correspondence/cross-level/generalizes/specializes |
| 仲裁记录 | log-decisions 条目 + ProvenanceType + 关联对象 ID + 仲裁依据 | S8 产物（字段模板待 eacks-s8 填充） |

详细字段约束与校验规则：`references/block-contracts.md`

## 五、Guard 槽位清单（填充状态）

| 槽位 | 内容 | 状态 |
|---|---|---|
| eacks-s1-decomposition | 解构规则：风险驱动细拆 + 禁止无限原子化 | ✅ 已验证（规则检出欠拆、3 植入案例全过） |
| eacks-s2-concept-alignment | Correspondence 类型学（equivalent/corresponding/broader/narrower/overlapping/measurement-corresponding/different/unresolved）+ Jingle-Jangle 检测 + 默认分化守卫 | ✅ 已验证（6 案例全过，3 修正已落） |
| eacks-s3-relation-types | Relation 类型学应用 + Rationale 格式 | ✅ 已验证（3 合规 + 3 植入全过；提示引用 S2 防错候选） |
| eacks-s4-verification-guards | Anti-Compression + Conditional Divergence + Type×Status×Strength 矩阵 | ✅ 已验证（3 植入全过，2 修正已落：他因三态/论辩结构区分） |
| eacks-s5-artifacts | Relation Matrix / Conflict Index / Boundary Matrix 产物格式 | ✅ 已验证（3 产物样例 + 4 植入违规全过） |
| eacks-s6-synthesis-guards | No-Third-Theory 判定 + Origin 强制 + Conflict 保留 | ✅ 已验证（现成案例 FAIL + 合规提案 PASS，与 S7 防线一致） |
| eacks-s7-semantic-loss | Semantic Loss Taxonomy 十项操作化定义 + 硬否决判定 | ✅ 已验证（10/10 检出、0 误报，4 修正已落） |
| eacks-s8-arbitration-template | log-decisions schema + EACKS 字段扩展 | ✅ 已验证（完整仲裁记录产出，字段 8+4 齐全、回注闭合） |

填充方式：每个 guard 独立成 skill（`eacks-<block>-<name>`），骨架的调用映射表在 guard 完成后更新状态并给出调用约定。

## 六、工具层索引

| 工具 | 位置 | 用途 | 接线状态 |
|---|---|---|---|
| onto_merger | 位置解析见第八节（工作区 `candidates/onto_merger/` 或重下恢复） | S2 概念对齐引擎 / S5 合并引擎 | ✅ 可用（调用方案：`eacks_om_adapter.py` 内建；须加方向反转 guard：默认合并 → EACKS 默认分化） |
| round-trip 引擎 | 位置解析见第八节（工作区 `tools/` 或本 skill `scripts/`） | S7 重建引擎（结构比对含方向反转/缺失/新增检出 + ROUGE-L + fidelity + τ 判定；纯标准库） | ✅ 已接线（LLM 重述/重建通道由 agent 充当；方向反转检出与全链路实测通过） |
| log-decisions | `skills/log-decisions`（本仓库内置） | S8 决策写回格式基座 | ✅ 可用 |
| AlignScore / factCC / TRUE | 远程参考 | S7 文本级一致性度量方法 | 📎 参考（eacks-s7 时评估） |

## 八、资产备份与恢复

本 skill 内保存 EACKS 工具层与工作流图的持久副本——工作区被清理后资产不丢失：

| 资产 | 本 skill 内置副本 | 工作区位置（重建后） |
|---|---|---|
| 工作流图（机器可执行 EFSM） | `templates/eacks.workflow.yaml` | 工作区根 `workflow.yaml`（用 workflow-definition 的 `validate-workflow.py` 校验，已 VALID：10 节点/30 边） |
| round-trip 引擎 | `scripts/eacks_roundtrip.py` | 工作区 `tools/eacks_roundtrip.py` |
| onto_merger 适配层 | `scripts/eacks_om_adapter.py` | 工作区 `tools/eacks_om_adapter.py` |
| log-decisions 决策日志 | `../../log-decisions/SKILL.md` | 工作区根 `DECISIONS.md`（按恢复流程重建） |

**工具位置解析规则**（执行时查找，不写死路径）：
1. 工作区内优先：`<工作区根>/tools/eacks_roundtrip.py`、`<工作区根>/candidates/onto_merger/`（已按恢复流程重建时）
2. 回退：本 skill `scripts/` 下同名文件（内置副本，天然存在）

**恢复流程**（工作区被清理后）：
1. 复制 `scripts/*` → 工作区 `tools/`、`templates/eacks.workflow.yaml` → 工作区根
2. `candidates/onto_merger/` 从 GitHub 重新获取（AstraZeneca/onto_merger，Apache-2.0）；装回 networkit（`pip install networkit`）
3. 适配器 L1 通道零依赖，L2 通道需以上两项就位

## 九、执行入口

1. 按 S0→S7 顺序执行；每 block 完成后用契约校验输出表（必填字段 + provenance）。
2. Guard 槽位为 ⬜ 的 block：以最小规则运行（仅保留协议硬约束），输出标注 `guard_pending`，不阻塞流程但禁止该 block 的产物晋升 Structural。
3. 触及转移条件时按第三节规则回退/升级/弃权；迭代预算全局计数。
4. 骨架验证基准（Benchmark）：Jingle-Jangle、False Unification、Conditional Contradiction、Evidence Upgrade、Reconstruction Fidelity、Competing Theories。
