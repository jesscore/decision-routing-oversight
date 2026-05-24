#!/usr/bin/env python3
"""
Meta-Observer — Second-pass oversight layer for Decision Intelligence
Mirrorfield Lab — AI Coherence & Intelligence Systems

Wraps decision_classifier.py. Takes a classification output and runs
a second-pass check for invisible failure modes:
  - Relational decision masked as evaluative
  - Architectural decision routed as operational
  - Generative decision collapsed to directional
  - False precision (high confidence on ambiguous decision)
  - Strategic-over-operational ambiguity

Usage:
  from meta_observer import observe
  result = observe(decision_text, classification_dict, client)

  python meta_observer.py "How do we approach EleutherAI?"  # runs full pipeline
"""

import json
import sys
from anthropic import Anthropic
from decision_classifier import classify, format_result

INVISIBLE_FAILURE_PATTERNS = [
    {
        "name": "relational-masked-as-evaluative",
        "condition": "classified as Type 1 (Evaluative) but involves a person, institution, relationship, or trust",
        "correct_type": "Type 7 (Relational-Strategic)",
        "danger": "Logically correct answer to the wrong question. Relationship or trust damaged.",
    },
    {
        "name": "architectural-routed-as-operational",
        "condition": "classified as Type 2 (Operational) but the decision shapes future capability or system structure",
        "correct_type": "Type 5 (Architectural)",
        "danger": "Execution without structural thinking. Compounds into technical debt and strategic incoherence.",
    },
    {
        "name": "generative-collapsed-to-directional",
        "condition": "classified as Type 4 (Directional) but the real question is what option spaces should exist",
        "correct_type": "Type 8 (Generative)",
        "danger": "Choosing between options when creating new options was the actual task. The new option space never gets created.",
    },
    {
        "name": "risk-routed-as-resource",
        "condition": "classified as Type 3 (Resource) but involves accepting or rejecting irreversible uncertainty",
        "correct_type": "Type 6 (Risk)",
        "danger": "Uncertainty treated as a scheduling problem. Commitment asymmetry ignored.",
    },
    {
        "name": "strategic-compressed-to-evaluative",
        "condition": "classified as Type 1 (Evaluative) but involves significant uncertainty about direction",
        "correct_type": "Type 4 (Directional)",
        "danger": "Direction question answered as quality check. Wrong question answered correctly.",
    },
]

META_OBSERVER_PROMPT = """You are a Meta-Observer for a Decision Intelligence classifier.

Your job: review a decision classification for invisible failure modes — cases where the classifier
produced a confident-seeming output but may have classified the wrong type.

The five dangerous invisible failure patterns are:
1. RELATIONAL-MASKED-AS-EVALUATIVE: Decision involves a person, institution, trust, or relationship
   but was classified as Type 1 (Evaluative). Should be Type 7 (Relational-Strategic).

2. ARCHITECTURAL-AS-OPERATIONAL: Decision shapes future capability or system structure but was
   classified as Type 2 (Operational). Should be Type 5 (Architectural).

3. GENERATIVE-AS-DIRECTIONAL: The real question is what option spaces should be created, but
   classified as Type 4 (Directional). Should be Type 8 (Generative).

4. RISK-AS-RESOURCE: Involves accepting irreversible uncertainty but classified as Type 3 (Resource).
   Should be Type 6 (Risk).

5. STRATEGIC-AS-EVALUATIVE: Involves significant directional uncertainty but classified as Type 1.
   Should be Type 4 (Directional).

Also check for FALSE PRECISION: a high confidence score on a decision that is genuinely
ambiguous between two adjacent types.

Given the decision and its classification, return ONLY a valid JSON object:
{
  "flags": ["list of invisible failure pattern names detected, empty if none"],
  "human_needed": boolean,
  "confidence_adjusted": float (0.0-1.0, your adjusted confidence in the original classification),
  "type_stable": boolean (true if you agree with the original type),
  "suggested_type": "original type if stable, or your suggested correction",
  "suggested_type_number": integer,
  "concern": "one sentence describing the concern, or 'none' if clean",
  "override_first_question": "better first question if type should be corrected, or null if original is fine"
}

Be skeptical of high-confidence Type 1-2 classifications on complex decisions.
Be especially watchful for relational context that got stripped out."""


def observe(decision: str, classification: dict, client: Anthropic) -> dict:
    """Run meta-observer second pass on a classification."""
    review_input = f"""Decision: {decision}

Classification received:
- Type: {classification['type']} (Type {classification['type_number']})
- Confidence: {classification['confidence']:.0%}
- Rationale: {classification['rationale']}
- First question generated: {classification['first_question']}

Check for invisible failure modes."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=META_OBSERVER_PROMPT,
        messages=[{"role": "user", "content": review_input}],
    )

    text = response.content[0].text
    start = text.find('{')
    end = text.rfind('}') + 1
    meta = json.loads(text[start:end])

    # Attach meta review to original classification
    result = classification.copy()
    result["meta_review"] = meta
    return result


def format_meta_result(decision: str, result: dict) -> str:
    meta = result.get("meta_review", {})
    flags = meta.get("flags", [])
    human_needed = meta.get("human_needed", False)
    confidence_adjusted = meta.get("confidence_adjusted", result["confidence"])
    type_stable = meta.get("type_stable", True)
    concern = meta.get("concern", "none")
    override_q = meta.get("override_first_question")

    # Show original classification
    lines = [format_result(decision, result)]

    # Add meta-observer review
    lines.append("  META-OBSERVER REVIEW")

    if not flags and type_stable:
        lines.append(f"  ✓  Classification stable. No invisible failure patterns detected.")
        lines.append(f"     Adjusted confidence: {confidence_adjusted:.0%}")
    else:
        status = "⚠  FLAGS RAISED" if flags else "○  Note"
        lines.append(f"  {status}")

        if not type_stable:
            lines.append(f"     Suggested correction: {meta.get('suggested_type')} (Type {meta.get('suggested_type_number')})")

        if concern != "none":
            lines.append(f"     Concern: {concern}")

        for flag in flags:
            # Find the pattern description
            pattern = next((p for p in INVISIBLE_FAILURE_PATTERNS if p["name"] == flag), None)
            if pattern:
                lines.append(f"     Pattern: {flag}")
                lines.append(f"     Danger:  {pattern['danger']}")

        lines.append(f"     Adjusted confidence: {confidence_adjusted:.0%}  (original: {result['confidence']:.0%})")

        if override_q:
            lines.append(f"")
            lines.append(f"  CORRECTED FIRST QUESTION")
            lines.append(f"     {override_q}")

    if human_needed:
        lines.append(f"")
        lines.append(f"  ► HUMAN ATTENTION RECOMMENDED before acting on this classification")

    lines.append("─" * 64)
    lines.append("")
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python meta_observer.py \"decision text\"")
        print("Runs full pipeline: classify → meta-observe → display")
        sys.exit(1)

    decision = " ".join(sys.argv[1:])
    client = Anthropic()

    print("\nClassifying…")
    classification = classify(decision, client)

    print("Running meta-observer…")
    result = observe(decision, classification, client)

    print(format_meta_result(decision, result))


if __name__ == "__main__":
    main()
