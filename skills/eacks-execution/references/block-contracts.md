# EACKS 9 Block 详细契约（block-contracts）

配套：`SKILL.md`（骨架/路由）。本文件定义每个 block 的输入输出表字段、处理步骤、保护机制与 guard 接口签名。

---

## S0 Knowledge Ingestion

**输入**：异质知识源（TXT/PDF/EPUB/OCR 文本/网络页面），每源一个文件或引用。

**处理步骤**：
1. 规范化（行尾→LF，记录 normalization.yaml）
2. 确定性分段（per-source 边界，禁止 LLM 猜测；merged 文件按作者标记拆分）
3. 章节映射（作者 ToC + 页码锚点，优先确定性方法）
4. 来源失败分流（见下方"来源分级 × 失败分流"矩阵）
5. Completeness Gate 判定（见下）

**输出**：Source 表（`id, 标题, 类型, 路径, 规范化状态, 完整性等级`）+ 每源 provenance 坐标（`source_id→chapter→section→printed_page→ocr_page→line_range`）。

**保护机制**：
- 禁止来源幻觉（拒绝先于生成：Completeness Gate 检测残缺材料）
- Unverified 不得升为核心证据
- OCR 垃圾率量化判定（garbage_ratio < 1% 阈值，禁用命名启发式）

**来源分级判定**（Criticality，满足任一即关键）：
1. 协议交付物核心论点的唯一支撑（无其他来源可交叉验证该断言）
2. 解构后预计产生 ≥3 条结构性 Claim（下游多 Claim 依赖）
3. 用户声明为核心材料
其余为非关键（背景/外围/综述，或有可替代来源）。

**失败类型分类**：
- 可解决：文件损坏可重获、OCR 差可重扫/换工具、404 有 Wayback 存档、编码可修复 → 尝试修复 ≤1 次
- 不可解决（人工可判）：来源缺失且无法获取、权限/版权限制、语言障碍 → S8
- 根本不可核实：来源本身不存在（引用幻觉）、内容永久消失无存档、出处无法定位 → Abstain

**分流矩阵**（对应 v1.3 转移边 S0→S1 / S0→S8 / S0→Abstain）：

| 来源分级 | 可解决 | 不可解决 | 根本不可核实 |
|---|---|---|---|
| 关键 | 修复成功→继续；失败→S8 | S8 | Abstain |
| 非关键 | 标记风险继续 | 标记风险继续（记录缺口） | 标记风险继续（记录缺口） |

**Completeness Gate**：
- 完成度 = 已成功登记来源数 / 预期来源数（材料清单或用户声明）；通过条件：完成度 ≥ 90% 且全部关键来源已登记
- 未通过：暂停并列出缺失清单 → 按分流矩阵处置（缺关键来源 → S8 / Abstain）
- 单源完整性：OCR 垃圾率 < 1%；章节映射覆盖率（已映射 / ToC）≥ 95%；低于则完整性等级=partial 并显式记录缺失章节；partial 来源不得升为核心证据

**调用**：corpus-knowledge-engineering（管道）+ grounded-citations（网络来源 ledger）+ ocr-and-documents/pdf（读取）。

---

## S1 Hierarchical Claim Decomposition

**输入**：Source 表 + 文本。

**处理步骤**：
1. 粗粒度解构（章节级主张）
2. 风险驱动细拆（高 Criticality / 高歧义段落拆到最小充分单元）
3. Claim 分类（ClaimType）+ Origin 标记（source_asserted / source_inferred / cross_source_synthesized / system_derived / human_decided）
4. 坐标附着（每 Claim 带 provenance 坐标）

**输出**：Claim 表（`id, sp_subject, sp_predicate, sp_object, context, condition, boundary, level, claim_type, origin, evidence_refs, provenance_coords`）。

**保护机制**：
- 禁止无限原子化（最小充分单元：能独立验证/反驳即停）
- agent-derived 不得伪装 source-derived（硬原则 7）

**Guard 接口（eacks-s1-decomposition，✅ 已验证）**：输入 Claim 草案集 → 输出解构合规标记（每 Claim：是否最小充分 / 是否原子化过度 / Origin 是否正确）。

---

## S2 Concept Clarification & Alignment

**输入**：Claim 表。

**处理步骤**：
1. 概念抽取（Claim 的主语/宾语/谓词概念）
2. Jingle-Jangle 检查（同名异义 / 异名同义）
3. 层级对齐（上位/下位/同级）
4. Correspondence 建立（8 类型判定）
5. 默认分化：无法确证对应 → 保持分离（不可比较是合法状态）

**输出**：Concept 表（`id, 名称, 定义, 层级, 源概念引用`）+ Correspondence 表（`concept_a, concept_b, correspondence_type, evidence, 默认分化标记`）。

**Correspondence 类型**（8 值）：equivalent / corresponding / broader / narrower / overlapping / measurement-corresponding / different / unresolved。

**保护机制**：
- Correspondence ≠ Equivalence（equivalent 只是其中一型）
- 源概念永不物理删除（Canonical 仅组织层抽象）

**Guard 接口（eacks-s2-concept-alignment，✅ 已验证）**：输入概念对候选集 → 输出类型判定 + 默认分化裁决。工具接线：onto_merger 的 mappings 生成作候选层，其 merges 输出**必须反转**（默认合并→默认分化，仅 equivalent 且证据充分才合并）。

---

## S3 Candidate Relation Generation

**输入**：Claim 表 + Concept/Correspondence 表。

**处理步骤**：
1. 关系候选生成（Claim 间 + 概念间）
2. 每条候选附 Rationale（为什么建立此关系）
3. 全部标记 Candidate（非事实）
4. Relation Type 声明（causal / associational / explanatory / supports / contradicts / qualifies / correspondence / cross-level / generalizes / specializes 等）

**输出**：Relation 表（`id, source_ref, target_ref, relation_type, rationale, status=Candidate, strength, condition, scope, evidence_refs, provenance_refs`）。

**保护机制**：候选非事实；禁止静默类型升级（相关→因果即 Evidence Upgrade，属 S7 检查项）。

**Guard 接口（eacks-s3-relation-types，✅ 已验证）**：输入候选关系集 → 输出类型学合规标记 + Rationale 完整性。

---

## S4 Verification Gate

**输入**：候选 Relation 表 + Evidence 表。

**处理步骤**（Type-Specific Validation）：
1. 按 Relation Type 选验证 guard（causal 查 temporal precedence/identification/alternative explanations/robustness；definitional 查 source definition/consistency/scope；normative 用规范一致性而非实证验证）
2. 证据核对（EvidenceLink Role 汇总：supports/weakens/qualifies/contradicts/contextualizes）
3. Anti-Compression 检查（关系是否丢失了源文本的条件/边界/层级）
4. 矛盾处理：优先解释为 Conditional Divergence（条件/层级/测量差异），确证矛盾才标 Contradiction
5. 状态判定：Validated / Disputed / Rejected / Unresolved

**输出**：验证后的 Relation 表（EpistemicStatus 更新）+ 未决清单（按 Criticality 排序）。

**保护机制**：证据类型≠质量；硬约束优先；条件优先于一般化。

**Guard 接口（eacks-s4-verification-guards，✅ 已验证）**：输入（Relation, EvidenceLinks, Type 规则）→ 输出验证判定 + 未决原因分类。

---

## S5 Non-Destructive Graph Integration

**输入**：验证后的 Relation 表。

**处理步骤**：
1. 图构建（节点=Concept/Claim，边=Relation）
2. 非破坏性合并（仅 equivalent + 充分证据才合并；其余保留为 Correspondence）
3. 冲突结构化（矛盾边显式保留，标 Conditional Divergence / Genuine Contradiction / Measurement Difference / Competing Theories）
4. Canonical 节点仅作组织层（源节点永不删除）

**输出**：知识图（graphml/表形式）+ Conflict Index + Relation Matrix（Type/Status/Strength/Structurality/Criticality/Condition/Scope/EvidenceRefs/ProvenanceRefs）。

**保护机制**：源概念永不物理删除；合并必须可追溯（merge-decision-log）。

**Guard 接口（eacks-s5-artifacts，✅ 已验证）**：输入图 + 合并决策 → 输出 Relation Matrix / Conflict Index / Boundary Matrix 合规产物 + 合并违规标记。

---

## S6 Higher-Order Synthesis

**输入**：知识图。

**处理步骤**：
1. Cluster（密度聚类，参考 Leiden；轻量实现可先用连通分量 + 主题相似）
2. Hierarchy（层级组织）
3. Mechanism（机制链识别）
4. Boundary（边界矩阵：外推范围、条件边界）
5. Conflict（冲突结构显式保留）

**保护机制**：
- 禁止无依据"第三理论"（两竞争理论并存时不得自行制造折中理论）
- 新命题必须标记 Origin（cross_source_synthesized / system_derived）
- Conflict ≠ Error（矛盾保留，不强行 coherent）

**Guard 接口（eacks-s6-synthesis-guards，✅ 已验证）**：输入高阶结构草案 → 输出 No-Third-Theory 判定 + Origin 完整性 + 冲突保留检查。

---

## S7 Reconstruction & Conservativity（协议核心闸门）

**输入**：综合后体系 K̂（高阶结构 + 知识图）。

**处理步骤**：
1. 反向重建 S→K̂：从 K̂ 重述为自然语言（LLM，模板按 EACKS 对象），再从重述重建结构化表示
2. 保真度评估（fidelity = α·structure_f1 + (1−α)·ROUGE-L，α=0.7，τ_select=0.85；工具：`tools/eacks_roundtrip.py`）
3. Semantic Loss Taxonomy 十项检查（硬否决优先于软评分）
4. 判定：硬损失存在 → REJECT（回退/升级/弃权）；无硬损失 → Soft Score → Accepted / Provisional

**Semantic Loss Taxonomy**（十项）：Concept Collapse / Condition Loss / Boundary Loss / Direction Loss / Evidence Upgrade / Provenance Loss / Conflict Erasure / Level Collapse / Measurement Collapse / Unsupported Synthesis。

**保护机制**：硬否决优先于软评分；Structural 晋升的最终门槛。

**Guard 接口（eacks-s7-semantic-loss，✅ 已验证）**：输入（原始知识 S, 综合体系 K̂, 重建文本, 重建结构）→ 输出十项损失检查结果 + 硬否决判定。工具接线：round-trip 引擎已接线（`tools/eacks_roundtrip.py` 确定性部分；LLM 重述/重建通道由 agent 充当）。

---

## S8 Human-in-the-Loop Triage

**输入**：升级事项（关键来源问题 / 不可裁决关系 / Reconstruction 失败 / 迭代预算超限）。

**处理步骤**：
1. 事项分类（来源 / 概念 / 关系 / 证据 / 结构 / 综合）
2. 人工裁定（专家判断，agent 提供结构化选项与证据摘要）
3. 结构化写回（仲裁记录，append-only）
4. 回注流程（S8→S2/S4/S5/S6 或终态）

**输出**：仲裁记录（log-decisions 条目格式[本仓库内置] + EACKS 扩展字段：`ProvenanceType=human_decided, 关联对象ID, 仲裁依据引用, 裁定结果`）+ 回注转移。

**保护机制**：决策即知识资产（不丢弃）；写回可追溯；灾难性决策必须人工。

**Guard 接口（eacks-s8-arbitration-template，✅ 已验证）**：log-decisions schema + EACKS 字段扩展模板。

---

## 终态与迭代预算

- **Accepted**：硬约束全通过 + Soft Score 达标 + Risk 可接受
- **Provisional**：核心可信 + 已标注有限不确定性（附 Uncertainty Report）
- **Abstained**：核心结构不足以支持可靠统一（合法结果）
- 迭代预算：所有回环全局计数，超限 → S8 或 Abstain
- 局部未决不阻塞：仅 CoreStructure 加权触发全局 Abstain
