# EACKS Protocol — Explained

This document explains the EACKS protocol for human readers. The machine-readable, executable form lives in the skills — this is a reading path, not the authoritative spec. For the authoritative contracts, see `skills/eacks-execution/SKILL.md` and `skills/eacks-execution/references/block-contracts.md`.

## The problem: premature harmonization → spurious unification

AI models, when asked to synthesize heterogeneous sources, tend to produce a single coherent narrative. The failure mechanism is **premature harmonization** — dissolving real differences between knowledge systems before checking whether the sources support the merge. The resulting error is **spurious unification**: heterogeneous knowledge systems represented as more semantically, inferentially, conditionally, or evidentially unified than their source structures warrant.

EACKS is built on the opposite default: unification must be earned. The protocol is designed so that when the evidence does not permit unification, the differences, conditions, and conflicts survive — and "abstain" is a legal outcome.

## The four conflation types EACKS guards against

| Conflation | Description | EACKS defense |
|---|---|---|
| Semantic conflation | Two systems use the same word for different concepts | S2 Correspondence judgment (8 types); default-to-differentiate |
| Inferential conflation | Similar conclusions reached by different reasoning treated as equivalent | S4 Anti-Compression; Type-Specific Validation |
| Conditional collapse | Claims that hold only under different conditions combined into one unconditional claim | S4 Conditional Divergence checked first; conditions preserved |
| Evidential conflation | Dependent sources counted as independent confirmation | S4 Evidence Type ≠ Evidence Quality; provenance chain |

## The pipeline (S0–S8)

```
S0  Ingestion → S1  Decomposition → S2  Concept alignment → S3  Candidate relations
→ S4  Verification gate → S5  Graph integration → S6  Higher-order synthesis
→ S7  Reconstruction gate → Outcome (Accepted / Provisional / Abstained)
```

Each stage is a processing block with an input/output contract (see `references/block-contracts.md`). Stage guards (one skill per stage) enforce the rules:

| Block | Purpose | Key protection |
|---|---|---|
| S0 Ingestion | Parse sources, register metadata, preliminary evidence typing | No source hallucination; Unverified never promoted to core evidence (reference: author-built `corpus-knowledge-engineering`, [github.com/gootf/corpus-knowledge-engineering](https://github.com/gootf/corpus-knowledge-engineering)) |
| S1 Decomposition | Break sources into minimal sufficient claim units | No infinite atomization; agent-derived never masquerades as source-derived |
| S2 Concept alignment | Jingle-Jangle checks, hierarchy alignment, Correspondence (8 types) | Default-to-differentiate; incomparability is a legal state |
| S3 Candidate relations | Generate candidate relations with Rationale | Candidates are not facts; type declared explicitly |
| S4 Verification gate | Type-Specific Validation; epistemic status adjudication | Anti-Compression; conditions first; contradictions explained as Conditional Divergence |
| S5 Graph integration | Non-destructive integration + structured conflict handling | Source concepts never deleted; Canonical is an organization layer only |
| S6 Higher-order synthesis | Cluster / Hierarchy / Mechanism / Boundary / Conflict | No unsupported "third theory"; every new claim must carry an Origin |
| S7 Reconstruction gate | Reverse reconstruction S → K̂ + fidelity + Semantic Loss Taxonomy (10 items) | Hard vetoes beat soft scores; any FAIL → REJECT |
| S8 Human arbitration | Structured write-back of human decisions | Decisions become traceable knowledge assets (`human_decided`) |

## Transfer rules

- **Fallback**: S4→S2 (concept issues), S4→S4 (re-validate), S5→S2/S4, S7→S2/S4/S5/S6 (corresponding-layer problems). Each fallback counts against an iteration budget; over budget → S8 or Abstain.
- **Escalation to S8**: only when an item exceeds the algorithm's reliable adjudication boundary (Critical + human-resolvable).
- **Abstention**: S0/S4/S7/S8 can reach Abstain when core structure cannot support reliable unification — a legal outcome, not a failure.
- **Terminal states**: Accepted (all hard constraints pass + soft score OK + risk acceptable) / Provisional (core credible, limited explicitly-flagged uncertainty, requires Uncertainty Report) / Abstained (core structure insufficient for reliable unification).

## Object model (shared schema)

| Object | Key fields |
|---|---|
| Source | id, metadata, provenance coordinates |
| Concept | id, name, level, source references |
| Claim | SPO + Context/Condition/Boundary/Level + ClaimType + Origin |
| Evidence | Type/Design/Identification/Quality/Robustness/Replication/ExternalValidity/Limitations |
| EvidenceLink | Evidence ↔ Claim/Relation + Role (supports/weakens/qualifies/contradicts/contextualizes) |
| Relation | Type + EpistemicStatus + Strength + Structurality + Criticality + Condition + Scope + EvidenceRefs + ProvenanceRefs |
| Arbitration record | log-decisions entry (built-in: `skills/log-decisions`) + ProvenanceType + linked object IDs + basis |

## Design principles

1. **Conservativity as goal**: K ⪯ S — the higher-order system is a conservative extension of the source knowledge. New semantic commitments require explicit provenance; derived claims never masquerade as source claims; evidence strength never upgraded.
2. **Workflow/truth separation**: EFSM orchestrates what to do next, never what is true.
3. **Validated guards**: each of the 8 stage guards was exercised against implanted violations before shipping.
4. **Shippable**: S7 round-trip engine is pure Python stdlib (zero deps); the S2/S5 onto_merger adapter is optional (L1 zero-dep, L2 needs onto_merger + networkit).

## Verification benchmark

Jingle-Jangle, False Unification, Conditional Contradiction, Evidence Upgrade, Reconstruction Fidelity, Competing Theories.

## License

MIT — see [LICENSE](../LICENSE).
