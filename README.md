# EACKS — Evidence-Aware Conservative Knowledge Synthesis

**English** | [简体中文](README.zh-CN.md)

![License](https://img.shields.io/github/license/gootf/eacks)
![Release](https://img.shields.io/github/v/release/gootf/eacks)
![Stars](https://img.shields.io/github/stars/gootf/eacks)

**EACKS stops AI agents from prematurely harmonizing heterogeneous knowledge sources into a single, falsely unified story.**

Ask an AI to synthesize two books on the same topic, and it will usually hand back one clean narrative — conflicts smoothed away, conditional claims made unconditional, dependent sources presented as independent. The result *looks* coherent. That is the problem.

EACKS is a knowledge-synthesis protocol that treats unification as something to be **earned, not assumed**: it preserves differences, keeps conditions explicit, makes conflicts visible, and refuses to produce a unified result when the sources do not warrant one.

## What goes wrong without it

| The failure | Without EACKS | With EACKS |
|---|---|---|
| **Semantic conflation** — two systems use the same word for different concepts | Merged into one concept | Eight-type Correspondence judgment (S2); default-to-differentiate |
| **Inferential conflation** — two systems reach a similar conclusion by different reasoning | Treated as equivalent | Anti-Compression + Type-Specific Validation (S4) |
| **Conditional collapse** — a claim holds only under condition X, another only under Y | Combined into one unconditional claim | Conditional Divergence checked first; conditions preserved (S4) |
| **Evidential conflation** — sources that quote each other counted as independent confirmation | Reported as "3 sources support this" | Evidence Type ≠ Evidence Quality; provenance chain enforced (S4) |
| **Uncertainty hidden or faked** — the model cannot decide, so it pretends it did | A confident answer with no basis | Three legal outcomes: Accepted / Provisional / Abstained |
| **Sources erased by canonicalization** — original concepts disappear into a merged vocabulary | Source concepts gone, no way to verify | Source concepts are never physically deleted; Canonical is an organizational layer only (S5) |
| **Synthesis distortion invisible to the reader** | A coherent story with no checkable relation to its sources | S7 reverse reconstruction (S → K̂) + ten-item Semantic Loss Taxonomy; hard vetoes beat soft scores |
| **High-order claims with no chain back to sources** | An abstraction that cannot be audited | Mandatory trace: High-Order Claim → Structural Relation → Validated Relation → Claim → Evidence → Source |

## The core term: Spurious Unification

> **Spurious unification** — the erroneous representation of heterogeneous knowledge systems as more semantically, inferentially, conditionally, or evidentially unified than their source structures warrant.

The failure mechanism that produces it is **premature harmonization**: the model, aiming for a fluent, coherent, answerable whole, dissolves real differences between systems too early — before checking whether the sources actually support the merge.

```
Source A: "Freedom means X" ──┐
                             ├──→  One Unified Theory   ←  spurious unification
Source B: "Freedom means Y" ──┘

Actually:
Source A: "Freedom means X" ──┐
                             ├──→  Correspondence + unresolved divergence,
Source B: "Freedom means Y" ──┘     conditional relations, preserved conflicts
```

EACKS exists to make the bottom path the default.

## Who this is for

| You are | Your situation | What EACKS does |
|---|---|---|
| **Knowledge engineer** | Building RAG or knowledge-graph pipelines over many sources | Typed object model (Concept / Claim / Evidence / Relation / EvidenceLink) whose provenance survives integration |
| **AI agent developer** | Multi-source synthesis in agent workflows | One guard skill per pipeline block (S0–S8): spurious unification, false causality, and silent compression are rejected *before* they enter the graph |
| **Researcher** | Synthesizing literature with conflicting findings | An EFSM workflow with explicit verification gates, a reconstruction gate, and structured human arbitration (S8) |
| **LLM output quality engineer** | Governing model-generated synthesis | Every derived claim carries explicit provenance; every higher-order structure must survive reverse reconstruction |

## Why this protocol

1. **Conservativity is the goal, not a constraint.** K ⪯ S: the higher-order system is a *conservative extension* of the source knowledge. New semantic commitments require explicit provenance; derived claims must never masquerade as source claims; evidence strength must never be upgraded.
2. **Workflow and truth are separated.** An EFSM (Layer 4) orchestrates *what to do next* — fallback, escalation, abstention — and never decides *what is true*. The typed knowledge model, the inference & validation engine, and the source & provenance layer each stay in their own layer.
3. **Guard behavior is validated, not aspirational.** Each of the 8 stage guards was exercised against implanted violations (missing conditions, hidden type upgrades, forced unification) before shipping; the machine-executable workflow (`skills/eacks-execution/templates/eacks.workflow.yaml`, 10 nodes / 30 edges) is the EFSM made runnable.
4. **Shippable pieces.** The S7 round-trip engine is pure Python stdlib (zero dependencies) and self-tests in one command. The S2/S5 `onto_merger` adapter is optional — the lightweight L1 channel runs with zero dependencies, the L2 channel only needs `onto_merger` + `networkit`.

## Quick start

```bash
git clone https://github.com/gootf/eacks.git

# copy the skills into your agent's skills directory
# (e.g. ~/.hermes/skills/ — each directory under skills/ is a self-contained skill)

# self-check the round-trip engine (pure stdlib, no install):
python skills/eacks-execution/scripts/eacks_roundtrip.py
# expect: 正常重建: 1.0 PASS / 方向反转: 0.5 HIGH_RISK / ... / ROUGE-L: 1.0 0.0
```

Then start with `eacks-execution` — it defines the 9 block contracts, the transition rules, and the shared object schema, and routes to the stage guards. A synthesis run flows S0 → S1 → S2 → S3 → S4 → S5 → S6 → S7 → Outcome (Accepted / Provisional / Abstained), with fallback, escalation, and abstention edges between stages.

**All dependencies ship inside this repo** under `skills/` — clone, copy, run:

| Skill | Purpose |
|---|---|
| `log-decisions` | Decision journal for S8 arbitration write-back (built-in) |
| `grounded-citations` | Web-source ledger for S0 (MIT) |
| `hypothesis-generation` | Candidate discipline for S3/S4 (MIT, K-Dense) |
| `scientific-critical-thinking` | Evidence evaluation for S4 (MIT, K-Dense) |
| `ocr-and-documents` | Document reading for S0 (MIT) |
| `corpus-knowledge-engineering` | Ingestion/decomposition/integration discipline (author-built, [standalone repo](https://github.com/gootf/corpus-knowledge-engineering)) |

Optional tool: `onto_merger` (AstraZeneca, Apache-2.0) + `networkit` for the L2 adapter channel.

## What it deliberately does NOT do

- **No fact-checking.** EACKS preserves provenance; it does not arbitrate which source is right.
- **No promise of a more unified result.** Unification happens only where evidence, definitions, conditions, and logical structure jointly allow it — sometimes the honest output is less unified than the input.
- **No fully-automated pipeline.** S8 is a structured, write-back human arbitration channel (`human_decided` decisions become traceable knowledge assets); some decisions are deliberately kept out of the algorithm's hands.
- **No LLM-free reconstruction.** S7's narrative channel needs an LLM to restate K̂; when unavailable, it degrades to mechanical structure checks only.

## Structure

```
skills/                    the protocol itself — 9 self-contained agent skills:
  eacks-execution/              Layer-4 orchestrator: 9 block contracts, transition
                                rules, shared object schema, tool wiring
                                (SKILL.md + references/ + templates/ + scripts/)
  eacks-s1-decomposition … eacks-s8-arbitration-template
                                8 stage guards, one per processing block (S1–S8)
docs/protocol.md           the protocol explained: EFSM, block contracts, object
                           model, transition rules (for readers, not just agents)
LICENSE                    MIT
README.md / README.zh-CN.md
```

## License

MIT — see [LICENSE](LICENSE).
