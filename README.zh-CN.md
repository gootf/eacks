# EACKS — 证据感知型保守知识综合协议（Evidence-Aware Conservative Knowledge Synthesis）

**English** | [简体中文](README.zh-CN.md)

![License](https://img.shields.io/github/license/gootf/eacks)
![Release](https://img.shields.io/github/v/release/gootf/eacks)
![Stars](https://img.shields.io/github/stars/gootf/eacks)

**EACKS 阻止 AI agent 在综合异质知识源时"过早协调"（premature harmonization）——把本不该统一的体系，揉成一个虚假统一（spurious unification）的整体。**

让 AI 综合两本同一主题的书，它通常会还给你一个干净利落的故事：冲突被磨平、有条件的主张被说成无条件的、相互引用的来源被当成独立佐证。结果**看起来**自洽——这正是问题所在。

EACKS 是一套知识综合协议，它把"统一"当作一件**需要挣得（earned）而非默认拥有**的事：保留差异、显式标注条件、让冲突可见，当来源本身不支持统一时，拒绝产出统一的结果。

## 没有它会发生什么

| 失败模式 | 没有 EACKS | 有 EACKS |
|---|---|---|
| **语义混同（Semantic conflation）**——两个体系用同一词指不同概念 | 被合并为一个概念 | 八类 Correspondence 判定（S2）；默认分化 |
| **推理混同（Inferential conflation）**——两个体系以不同推理得出相似结论 | 被当作等价 | Anti-Compression + 类型专属验证（S4） |
| **条件坍缩（Conditional collapse）**——一个主张仅在条件 X 下成立，另一个仅在 Y 下成立 | 被合并成一条无条件主张 | 先查 Conditional Divergence；条件被保留（S4） |
| **证据混同（Evidential conflation）**——相互引用的来源被当作独立佐证 | 报告为"3 个来源支持此说" | 证据类型 ≠ 证据质量；强制溯源链（S4） |
| **不确定性被隐藏或伪造**——模型无法裁决，于是假装裁决了 | 一个没有依据的自信答案 | 三种合法结果：Accepted / Provisional / Abstained |
| **规范化抹掉来源**——原始概念消失在合并词汇里 | 源概念消失，无从核验 | 源概念永不物理删除；Canonical 仅是组织层（S5） |
| **综合失真对读者不可见** | 一个与来源关系无法核查的自洽故事 | S7 反向重建（S → K̂）+ 十项语义损失清单；硬否决优先于软评分 |
| **高阶主张没有回溯链** | 一个无法审计的抽象 | 强制链路：高阶主张 → 结构关系 → 已验证关系 → 主张 → 证据 → 来源 |

## 核心术语：虚假统一（Spurious Unification）

> **虚假统一（spurious unification）**——异质知识体系被表示为具有超出其源结构所支持的语义、推理、条件或证据一致性，这是一种综合错误。

产生它的失败机制是**过早协调（premature harmonization）**：模型为了得到一个流畅、连贯、可回答的整体，在核查来源是否真的支持合并之前，就过早地消解了体系之间的真实差异。

```
来源 A："自由意味着 X" ──┐
                       ├──→  一个统一理论   ←  虚假统一
来源 B："自由意味着 Y" ──┘

实际应该是：
来源 A："自由意味着 X" ──┐
                       ├──→  Correspondence + 未消解的分歧 +
来源 B："自由意味着 Y" ──┘     条件关系 + 保留的冲突
```

EACKS 的存在，就是让下面那条路成为默认。

## 适合谁

| 你是谁 | 你的处境 | EACKS 给你什么 |
|---|---|---|
| **知识工程师** | 构建多源 RAG 或知识图谱管线 | 带溯源的类型对象模型（Concept / Claim / Evidence / Relation / EvidenceLink），溯源在整合后依然存活 |
| **AI agent 开发者** | Agent 工作流中的多源综合 | 每个管线块一个守卫技能（S0–S8）：虚假统一、假因果、静默压缩在进入图谱*之前*就被拒绝 |
| **研究者** | 综合结论相互冲突的文献 | 带显式验证门、重建门、结构化人工仲裁（S8）的 EFSM 工作流 |
| **LLM 输出质量工程师** | 治理模型生成的综合结果 | 每个推导主张携带显式溯源；每个高阶结构必须经受反向重建 |

## 为什么是这套协议

1. **保守性是目标，不是约束。** K ⪯ S：高阶体系是源知识的*保守扩展*。新的语义承诺需要显式溯源；推导主张不得伪装成源主张；证据强度不得被升级。
2. **工作流与真相分离。** EFSM（第四层）只编排*下一步做什么*——回退、升级、弃权——从不下判断*什么是真*。类型化知识模型、推理与验证引擎、来源与溯源层各自独立。
3. **守卫行为经验证，而非空想。** 8 个阶段守卫在发布前都经受了对植入违规（缺失条件、隐蔽类型升级、强制统一）的实战检验；机器可执行工作流（`skills/eacks-execution/templates/eacks.workflow.yaml`，10 节点 / 30 边）是 EFSM 的可运行形态。
4. **可交付的组件。** S7 回溯引擎是纯 Python 标准库（零依赖），一条命令自测。S2/S5 的 `onto_merger` 适配器可选——轻量 L1 通道零依赖，L2 通道仅需 `onto_merger` + `networkit`。

## 快速开始

```bash
git clone https://github.com/gootf/eacks.git

# 把 skills/ 下每个目录复制到你的 agent 技能目录
#（如 ~/.hermes/skills/——每个目录都是自包含技能）

# 自测 round-trip 引擎（纯标准库，无需安装）：
python skills/eacks-execution/scripts/eacks_roundtrip.py
# 预期输出：正常重建: 1.0 PASS / 方向反转: 0.5 HIGH_RISK / ... / ROUGE-L: 1.0 0.0
```

然后从 `eacks-execution` 开始——它定义 9 个处理块契约、转移规则与共享对象 Schema，并路由到各阶段守卫。一次综合运行按 S0 → S1 → S2 → S3 → S4 → S5 → S6 → S7 → 结果（Accepted / Provisional / Abstained）流动，阶段之间带回退、升级与弃权边。

**全部依赖随仓库提供**，位于 `skills/` 下——clone 即用：

| 技能 | 用途 |
|---|---|
| `log-decisions` | S8 仲裁写回的决策日志（内置） |
| `grounded-citations` | S0 网络来源台账（MIT） |
| `hypothesis-generation` | S3/S4 候选纪律（MIT, K-Dense） |
| `scientific-critical-thinking` | S4 证据评估（MIT, K-Dense） |
| `ocr-and-documents` | S0 文档读取（MIT） |
| `corpus-knowledge-engineering` | 摄取/解构/整合纪律（作者自研，[独立仓库](https://github.com/gootf/corpus-knowledge-engineering)） |

可选工具：`onto_merger`（AstraZeneca, Apache-2.0）+ `networkit`（L2 适配通道）。

## 它刻意不做什么

- **不做事实核查。** EACKS 保留溯源，不裁决哪个来源正确。
- **不承诺"更统一"的结果。** 统一只发生在证据、定义、条件与逻辑结构共同允许的地方——有时诚实的产出反而比输入更不统一。
- **不是全自动管线。** S8 是结构化、写回式的人工仲裁通道（`human_decided` 决策成为可追溯的知识资产）；有些决策刻意留在算法能力之外。
- **无法脱离 LLM 重建。** S7 的叙事通道需要 LLM 重述 K̂；不可用时降级为纯机械结构检查。

## 结构

```
skills/                    协议本体——9 个自包含 agent 技能：
  eacks-execution/             Layer 4 编排器：9 个处理块契约、转移规则、
                               共享对象 Schema、工具布线
                               （SKILL.md + references/ + templates/ + scripts/）
  eacks-s1-decomposition … eacks-s8-arbitration-template
                               8 个阶段守卫，每个处理块一个（S1–S8）
docs/protocol.md           协议详解：EFSM、处理块契约、对象模型、转移规则
                           （写给读者，不只写给 agent）
LICENSE                     MIT
README.md / README.zh-CN.md
```

## License

MIT — 见 [LICENSE](LICENSE)。
