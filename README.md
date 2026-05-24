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

## License

MIT — Mirrorfield Lab, 2026
