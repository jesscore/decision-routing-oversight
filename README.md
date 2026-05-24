# Decision Routing Oversight

**Mirrorfield Lab — AI Coherence & Intelligence Systems**

Two-layer oversight architecture for detecting decision-type misrouting before errors propagate downstream.

---

## The Problem

AI systems and human-AI teams frequently apply the wrong reasoning mode to a problem. A relational decision gets handled as a quality evaluation. An architectural decision gets routed as an operational sequence. The output appears locally coherent — but the wrong question was answered correctly.

This failure mode is structurally invisible to behavioral evaluation: it passes output-level checks while propagating error downstream. Existing evaluation approaches operate after the fact. This tool operates before.

---

## The Architecture

### `decision_classifier.py` — First-pass classification

Classifies any decision into one of eight types across three reasoning zones:

| Zone | Types |
|------|-------|
| **Reactive** — fast, bounded, local | Evaluative, Operational, Resource |
| **Strategic** — cross-domain, system-level | Directional, Architectural, Risk |
| **Field/Generative** — full contextual picture required | Relational-Strategic, Generative |

Returns: type, confidence, rationale, reasoning mode, evidence threshold, time horizon, misrouting risks, and the single most important question to ask before acting.

### `meta_observer.py` — Second-pass oversight

Hierarchical oversight layer that checks for invisible failure modes — cases where the first pass produced a confident output on the wrong decision type:

| Pattern | Misroute | Downstream risk |
|---------|----------|-----------------|
| Relational-masked-as-evaluative | Type 7 → Type 1 | Trust or relationship damaged by treating a people-context decision as a quality check |
| Architectural-as-operational | Type 5 → Type 2 | Structure-shaping decision executed without system-level thinking; compounds into technical debt |
| Generative-as-directional | Type 8 → Type 4 | Option-creation question reduced to option-selection; new option space never gets created |
| Risk-as-resource | Type 6 → Type 3 | Irreversible uncertainty treated as a scheduling problem |
| Strategic-as-evaluative | Type 4 → Type 1 | Direction question answered as a quality check |

When patterns are detected: confidence is adjusted downward, the concern is named, and human review is recommended before acting.

---

## Demonstrated Example

```
Decision: "Is this researcher a good fit to be our first rater?"

First pass:    Type 1 (Evaluative) — 78% confidence
               Rationale: assessing qualifications against a standard

Meta-Observer: ⚠ relational-masked-as-evaluative
               Adjusted confidence: 41%  (original: 78%)
               Concern: This involves relationship topology, not qualification check.
               ► HUMAN ATTENTION RECOMMENDED
               Corrected question: What is the trust and working relationship dynamic here?
```

The classifier answered the question as asked. The Meta-Observer caught that the question itself was misrouted.

---

## Installation

```bash
pip install anthropic
export ANTHROPIC_API_KEY=your_key_here
```

## Usage

```bash
# Interactive mode
python decision_classifier.py

# Single decision
python decision_classifier.py "Should we submit this paper to NeurIPS or ICLR?"

# Batch mode (JSON list of decision strings)
python decision_classifier.py --batch decisions.json

# Full pipeline: classify → meta-observe → display
python meta_observer.py "How should we approach this potential collaborator?"
```

---

## Research Background

These tools implement the hierarchical oversight architecture grounded in a preregistered empirical research program on how structured human-AI interaction shapes model representation geometry.

The decision taxonomy formalizes a specific AI failure mode — reasoning-mode misclassification — currently informal and ad-hoc in both AI labs and organizations. The hierarchical Meta-Observer layer addresses failures before downstream propagation rather than catching them in completed outputs, shifting the oversight posture from post-hoc evaluation to pre-hoc detection.

- **Preregistered research program:** [osf.io/fzjh6](https://osf.io/fzjh6) — individual phase preregistrations filed before each data collection cycle; null results reported verbatim
- **NeurIPS 2026:** under review — cross-architecture geometric consistency (Mantel ρ=0.943, preregistered)
- **ICLR 2026:** submitted — carrier-mediated symbolic token geometry (Cohen's d=2.002, preregistered)

---

## Current Status

Working prototype. Both tools run, classify correctly, and the meta-observer catches misrouting patterns on real decisions.

What hasn't been done yet: systematic empirical validation. We don't have a labeled dataset of real decisions with ground-truth type assignments, so we can't report classifier accuracy or meta-observer precision at scale. The demonstrated example (relational-masked-as-evaluative, 78% → 41%) is real and manually verified — it's a single case, not a benchmark.

This is the honest starting point. The taxonomy is grounded in a preregistered research program on how AI systems misroute reasoning, not invented from scratch. But the tools need empirical evaluation before they can make calibrated accuracy claims.

---

## What Funding Enables

Three things, in order of priority:

**1. Empirical validation.**
Build a labeled dataset of real decisions across domains — research, organizational, clinical, policy. Measure classifier accuracy by decision type. Measure meta-observer catch rate: when a misrouting pattern is present, does it fire? When it isn't, does it stay quiet? This turns the prototype into an evaluated tool with known failure modes.

**2. Taxonomy extension.**
The current 8-type taxonomy was derived from AI-research decisions. It needs stress-testing against other high-stakes domains — medical triage, institutional risk, team coordination. Some types may split; others may merge. The goal is a taxonomy that holds across contexts, not just the one it was built in.

**3. Integration with pre-hoc oversight research.**
The parent research program shows that structured interaction context produces measurable, architecturally invariant changes in model geometry (Cohen's d=2.002, Mantel ρ=0.943). The open question: does geometric signal predict decision-type misrouting? If high-entropy activation patterns correlate with misrouted classification, the meta-observer could eventually flag not just logical misrouting but geometric instability before the output arrives. That's the longer-horizon connection this work is positioned to test.

---

## License

MIT — Mirrorfield Lab, 2026
