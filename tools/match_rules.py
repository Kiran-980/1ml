"""Match a rule table against profiled dataset facts.

A rule table is YAML with a top-level ``rules`` list. Every rule states the
conditions under which it applies, the action it recommends, the rationale
behind that action, and the primary sources that justify it. Matching is
deterministic: the same facts and the same table always produce the same
result, and every match carries its rule id.

Usage:
    python match_rules.py --rules rules/data.yaml --profile profile.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402

MISSING = object()


def _get(container, path: str):
    """Look up a dotted path in a nested mapping, returning MISSING when absent."""
    current = container
    for part in path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return MISSING
    return current


def _compare(value, operator: str, expected) -> bool:
    if operator == "exists":
        present = value is not MISSING and value is not None
        return present == bool(expected)
    if value is MISSING:
        return False

    if operator == "eq":
        return value == expected
    if operator == "ne":
        return value != expected
    if operator == "gt":
        return value is not None and value > expected
    if operator == "gte":
        return value is not None and value >= expected
    if operator == "lt":
        return value is not None and value < expected
    if operator == "lte":
        return value is not None and value <= expected
    if operator == "in":
        return value in expected
    if operator == "not_in":
        return value not in expected
    if operator == "contains":
        try:
            return expected in value
        except TypeError:
            return False
    raise ValueError(f"unknown rule operator: {operator}")


def _matches_condition(subject, condition) -> bool:
    """Evaluate one field condition against a subject mapping."""
    if isinstance(condition, dict):
        return all(
            _compare(_get(subject, field), operator, expected)
            for field, operators in condition.items()
            for operator, expected in operators.items()
        )
    return _compare(_get(subject, "value"), "eq", condition)


def _matches_conditions(subject, conditions: dict) -> bool:
    """Evaluate a whole ``applies_when`` block: every field must pass."""
    if not conditions:
        return True
    for field, condition in conditions.items():
        if isinstance(condition, dict):
            passed = all(
                _compare(_get(subject, field), operator, expected)
                for operator, expected in condition.items()
            )
        else:
            passed = _compare(_get(subject, field), "eq", condition)
        if not passed:
            return False
    return True


def _subjects(facts: dict, scope: str):
    """Yield (subject_name, subject_mapping) pairs for a rule scope."""
    if scope == "dataset":
        yield "dataset", facts.get("dataset", {})
    elif scope == "target":
        target = facts.get("target")
        if target:
            yield target.get("name", "target"), target
    elif scope == "column":
        for feature in facts.get("features", []):
            yield feature["name"], feature
    else:
        raise ValueError(f"unknown rule scope: {scope}")


def match_rules(facts: dict, rules: dict) -> dict:
    """Match every rule in the table against the profiled facts."""
    matched_ids: list[str] = []
    details: list[dict] = []
    citations: list[dict] = []

    for rule in rules.get("rules", []):
        rule_id = rule["id"]
        scope = rule.get("scope", "column")
        applies_when = rule.get("applies_when", {})
        escalate_if = rule.get("escalate_if")

        for subject_name, subject in _subjects(facts, scope):
            if not _matches_conditions(subject, applies_when):
                continue

            detail = {
                "rule_id": rule_id,
                "subject": subject_name,
                "title": rule.get("title", ""),
                "recommend": rule.get("recommend", {}),
                "rationale": rule.get("rationale", ""),
                "confidence": rule.get("confidence", "medium"),
                "citations": rule.get("cite", []),
                "escalate": False,
                "reference": rule.get('reference'),
            }

            if escalate_if and _matches_conditions(subject, escalate_if):
                detail["escalate"] = True
                detail["escalate_note"] = rule.get("escalate_note", "")

            if rule_id not in matched_ids:
                matched_ids.append(rule_id)
            details.append(detail)

            for cite in rule.get("cite", []):
                citations.append(
                    {
                        "rule_id": rule_id,
                        "url": cite.get("url", ""),
                        "section": cite.get("section", ""),
                    }
                )

    if not matched_ids:
        return {
            "matched": [],
            "no_match": True,
            "note": (
                "No rule matched the observed data. Treat this as a judgment "
                "call, state the reasoning, and ask the learner when the "
                "choice is not reversible."
            ),
            "details": [],
            "citations": [],
        }

    return {
        "matched": matched_ids,
        "no_match": False,
        "details": details,
        "citations": citations,
    }


def load_rules(path) -> dict:
    """Load a rule table from YAML."""
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {"rules": []}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Match rule tables against dataset facts.")
    parser.add_argument("--rules", required=True, help="path to the rule YAML file")
    parser.add_argument("--profile", required=True, help="path to the profile JSON file")
    parser.add_argument("--out", help="write the match result here instead of stdout")
    args = parser.parse_args(argv)

    try:
        facts = common.read_json(args.profile)
        rules = load_rules(args.rules)
    except (OSError, ValueError, yaml.YAMLError) as error:
        common.fail(str(error))
        return 2

    result = match_rules(facts, rules)

    if args.out:
        common.write_json(args.out, result)
        print(f"wrote {args.out}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
