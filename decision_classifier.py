#!/usr/bin/env python3
"""
Decision Intelligence Classifier — Pathway A MVP
Mirrorfield Lab — AI Coherence & Intelligence Systems

Classifies decisions by type and generates routing metadata.
Eight types: Evaluative / Operational / Resource / Directional /
             Architectural / Risk / Relational-Strategic / Generative

Usage:
  python decision_classifier.py                          # interactive mode
  python decision_classifier.py "Should we pre-register now?"  # single decision
  python decision_classifier.py --batch decisions.json   # batch mode
"""

import json
import os
import sys
import argparse
from anthropic import Anthropic

SYSTEM_PROMPT = """You are a Decision Intelligence classifier for an AI coherence research lab.

Your job: classify any decision by type and generate routing metadata.

THE EIGHT DECISION TYPES:

REACTIVE ZONE (fast, local, bounded):
1. Evaluative    — Is this good/ready/true enough? Assess quality against a standard.
2. Operational   — What is the next sequence? Process, order, logistics.
3. Resource      — What gets time, money, energy, or compute? Allocating finite capacity.

STRATEGIC ZONE (slower, cross-domain, system-level):
4. Directional   — Which path under uncertainty? Strategic judgment required.
5. Architectural — What system/container makes future decisions easier?
6. Risk          — What uncertainty do we accept, hedge, test, or avoid?

FIELD/GENERATIVE ZONE (creative, option-expanding):
7. Relational-Strategic — Navigate people, institutions, trust, timing, incentives.
                          Analysis + social/contextual sensing. NOT softer — wider input set.
8. Generative    — What new option space should we create before anyone asks?

IMPORTANT ROUTING RULES:
- If a decision could be Type 1-3 OR Type 4-6, err toward the higher type (more deliberation)
- Type 7-8 decisions require the full organizational/contextual picture before acting
- Misrouting risk: operational thinking for architectural problems is the most common failure

Return ONLY a valid JSON object with these exact fields:
{
  "type": "exact type name from the list above",
  "type_number": integer 1-8,
  "zone": "Reactive" or "Strategic" or "Field/Generative",
  "reasoning_mode": "short description of required cognitive posture",
  "evidence_threshold": "low" or "medium" or "high" or "very_high",
  "time_horizon": "immediate" or "short" or "medium" or "long" or "indefinite",
  "suggested_agents": ["list of 2-4 relevant capability domains"],
  "risk_tolerance": "low" or "medium" or "high",
  "confidence": float 0.0-1.0,
  "rationale": "one clear sentence explaining the classification",
  "misrouting_risks": ["2-3 common ways this specific decision gets misrouted"],
  "first_question": "the single most important question to ask before acting on this"
}"""


def classify(decision_text: str, client: Anthropic) -> dict:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Classify this decision:\n\n{decision_text}"}]
    )
    text = response.content[0].text
    start = text.find('{')
    end = text.rfind('}') + 1
    if start == -1 or end == 0:
        raise ValueError(f"No JSON found in response:\n{text}")
    return json.loads(text[start:end])


def format_result(decision: str, r: dict) -> str:
    zone_colors = {"Reactive": "⬡", "Strategic": "⬢", "Field/Generative": "◈"}
    zone_icon = zone_colors.get(r.get("zone", ""), "◆")

    lines = [
        "",
        "─" * 64,
        f"  {decision[:72]}{'…' if len(decision) > 72 else ''}",
        "─" * 64,
        f"  TYPE      {zone_icon}  {r['type']}  (Type {r['type_number']} — {r.get('zone', '')} zone)",
        f"  CONFIDENCE   {r['confidence']:.0%}",
        f"  RATIONALE    {r['rationale']}",
        "",
        "  ROUTING",
        f"    Reasoning mode      {r['reasoning_mode']}",
        f"    Evidence threshold  {r['evidence_threshold']}",
        f"    Time horizon        {r['time_horizon']}",
        f"    Risk tolerance      {r['risk_tolerance']}",
        f"    Agents              {', '.join(r.get('suggested_agents', []))}",
        "",
        f"  FIRST QUESTION",
        f"    {r['first_question']}",
        "",
        "  MISROUTING RISKS",
    ]
    for risk in r.get("misrouting_risks", []):
        lines.append(f"    ⚠  {risk}")
    lines.append("─" * 64)
    lines.append("")
    return "\n".join(lines)


def interactive_mode(client: Anthropic):
    print("\nDecision Intelligence Classifier")
    print("Type a decision to classify. 'quit' to exit.\n")
    while True:
        try:
            decision = input("Decision: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not decision:
            continue
        if decision.lower() in ("quit", "exit", "q"):
            break
        try:
            result = classify(decision, client)
            print(format_result(decision, result))
        except Exception as e:
            print(f"  Error: {e}\n")


def batch_mode(path: str, client: Anthropic):
    with open(path) as f:
        decisions = json.load(f)
    if not isinstance(decisions, list):
        decisions = [decisions]
    results = []
    for item in decisions:
        text = item if isinstance(item, str) else item.get("decision", str(item))
        print(f"Classifying: {text[:60]}…")
        result = classify(text, client)
        results.append({"decision": text, "classification": result})
        print(format_result(text, result))
    out_path = path.replace(".json", "_classified.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Decision Intelligence Classifier")
    parser.add_argument("decision", nargs="*", help="Decision text to classify")
    parser.add_argument("--batch", metavar="FILE", help="JSON file of decisions to classify")
    args = parser.parse_args()

    client = Anthropic()

    if args.batch:
        batch_mode(args.batch, client)
    elif args.decision:
        decision = " ".join(args.decision)
        result = classify(decision, client)
        print(format_result(decision, result))
    else:
        interactive_mode(client)


if __name__ == "__main__":
    main()
