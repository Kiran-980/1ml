"""Tests for the deterministic 1ml tools.

Run from the plugin root:
    python -m unittest discover -s tests -t .
"""

from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parents[1] / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import pandas as pd  # noqa: E402


def sample_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "customer_id": list(range(100)),
            "age": [20, 25, None, 30, 35] * 20,
            "city": ["a", "b", "c", "a", "b"] * 20,
            "notes": [f"free text number {i}" for i in range(100)],
            "churn": [0, 1] * 50,
        }
    )


class ProfileTests(unittest.TestCase):
    def test_reports_column_kinds_missingness_and_dataset_totals(self):
        import data_profile as profile

        facts = profile.profile_dataframe(
            sample_frame(), {"path": "customers.csv", "kind": "csv"}
        )

        self.assertEqual(facts["dataset"]["n_rows"], 100)
        self.assertEqual(facts["dataset"]["n_columns"], 5)

        by_name = {col["name"]: col for col in facts["features"]}
        self.assertEqual(by_name["age"]["kind"], "numeric")
        self.assertEqual(by_name["age"]["missing_count"], 20)
        self.assertAlmostEqual(by_name["age"]["missing_fraction"], 0.2)
        self.assertEqual(by_name["city"]["kind"], "categorical")
        self.assertEqual(by_name["notes"]["kind"], "text")
        self.assertTrue(by_name["customer_id"]["is_identifier"])

    def test_counts_duplicate_rows(self):
        import data_profile as profile

        frame = sample_frame()
        frame = pd.concat([frame, frame.iloc[[0]]], ignore_index=True)

        facts = profile.profile_dataframe(frame, {"path": "customers.csv", "kind": "csv"})

        self.assertEqual(facts["dataset"]["duplicate_rows"], 1)
        self.assertAlmostEqual(facts["dataset"]["duplicate_fraction"], 1 / 101)

    def test_infers_target_by_name_and_flags_imbalance(self):
        import data_profile as profile

        frame = sample_frame()
        frame["churn"] = [0] * 90 + [1] * 10

        facts = profile.profile_dataframe(frame, {"path": "customers.csv", "kind": "csv"})

        self.assertEqual(facts["target"]["name"], "churn")
        self.assertTrue(facts["target"]["inferred"])
        self.assertAlmostEqual(facts["target"]["imbalance_ratio"], 10 / 90)

    def test_explicit_target_wins_over_inference(self):
        import data_profile as profile

        facts = profile.profile_dataframe(
            sample_frame(),
            {"path": "customers.csv", "kind": "csv"},
            target="age",
        )

        self.assertEqual(facts["target"]["name"], "age")
        self.assertFalse(facts["target"]["inferred"])

    def test_reads_sqlite_table(self):
        import data_profile as profile

        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "app.db"
            connection = sqlite3.connect(db_path)
            sample_frame().to_sql("customers", connection, index=False)
            connection.close()

            facts = profile.profile_frame(db_path, table="customers")

        self.assertEqual(facts["source"]["kind"], "sqlite")
        self.assertEqual(facts["dataset"]["n_rows"], 100)

    def test_cli_writes_profile_json(self):
        import data_profile as profile

        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "customers.csv"
            sample_frame().to_csv(csv_path, index=False)
            out_path = Path(tmp) / "profile.json"

            result = subprocess.run(
                [
                    sys.executable,
                    str(TOOLS_DIR / "data_profile.py"),
                    "--csv",
                    str(csv_path),
                    "--out",
                    str(out_path),
                ],
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(out_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["dataset"]["n_rows"], 100)


class MatchRulesTests(unittest.TestCase):
    def setUp(self):
        import data_profile as profile

        self.facts = profile.profile_dataframe(
            sample_frame(), {"path": "customers.csv", "kind": "csv"}
        )

    def test_matches_rule_and_collects_citations(self):
        import match_rules

        rules = {
            "rules": [
                {
                    "id": "MISS-002",
                    "title": "Moderate missingness",
                    "scope": "column",
                    "applies_when": {
                        "kind": "numeric",
                        "missing_fraction": {"gte": 0.05, "lt": 0.30},
                    },
                    "recommend": {"action": "impute_median_with_indicator"},
                    "rationale": "Median is robust to outliers.",
                    "cite": [{"url": "https://example.org/impute", "section": "Indicators"}],
                    "confidence": "high",
                }
            ]
        }

        result = match_rules.match_rules(self.facts, rules)

        self.assertIn("MISS-002", result["matched"])
        self.assertFalse(result["no_match"])
        subjects = [detail["subject"] for detail in result["details"]]
        self.assertIn("age", subjects)
        self.assertEqual(result["citations"][0]["rule_id"], "MISS-002")

    def test_returns_no_match_contract_when_nothing_applies(self):
        import match_rules

        rules = {
            "rules": [
                {
                    "id": "NOPE-001",
                    "title": "Never",
                    "scope": "column",
                    "applies_when": {"kind": "numeric", "missing_fraction": {"gte": 0.99}},
                }
            ]
        }

        result = match_rules.match_rules(self.facts, rules)

        self.assertEqual(result["matched"], [])
        self.assertTrue(result["no_match"])
        self.assertIn("note", result)

    def test_flags_escalation_when_escalate_if_matches(self):
        import match_rules

        rules = {
            "rules": [
                {
                    "id": "MISS-002",
                    "title": "Moderate missingness",
                    "scope": "column",
                    "applies_when": {"kind": "numeric"},
                    "escalate_if": {"missing_fraction": {"gte": 0.10}},
                    "escalate_note": "Missingness is high enough to need a human call.",
                }
            ]
        }

        result = match_rules.match_rules(self.facts, rules)

        age_detail = [d for d in result["details"] if d["subject"] == "age"][0]
        self.assertTrue(age_detail["escalate"])
        self.assertIn("human call", age_detail["escalate_note"])

    def test_dataset_scope_rules_read_dataset_facts(self):
        import match_rules

        rules = {
            "rules": [
                {
                    "id": "ROW-001",
                    "title": "Enough rows to model",
                    "scope": "dataset",
                    "applies_when": {"n_rows": {"gte": 100}},
                }
            ]
        }

        result = match_rules.match_rules(self.facts, rules)

        self.assertIn("ROW-001", result["matched"])
        self.assertEqual(result["details"][0]["subject"], "dataset")

    def test_dataset_scope_rule_does_not_match_when_condition_fails(self):
        import match_rules

        rules = {
            "rules": [
                {
                    "id": "DUP-001",
                    "title": "Duplicate rows present",
                    "scope": "dataset",
                    "applies_when": {"duplicate_fraction": {"gte": 0.001}},
                }
            ]
        }

        result = match_rules.match_rules(self.facts, rules)

        self.assertNotIn("DUP-001", result["matched"])
        self.assertTrue(result["no_match"])

    def test_loads_rules_from_yaml_file(self):
        import match_rules

        with tempfile.TemporaryDirectory() as tmp:
            rules_path = Path(tmp) / "data.yaml"
            rules_path.write_text(
                "rules:\n"
                "  - id: MISS-002\n"
                "    title: Moderate missingness\n"
                "    scope: column\n"
                "    applies_when:\n"
                "      kind: numeric\n",
                encoding="utf-8",
            )

            rules = match_rules.load_rules(rules_path)

        self.assertEqual(rules["rules"][0]["id"], "MISS-002")


class StateTests(unittest.TestCase):
    def test_init_creates_visible_state_folder(self):
        import state

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            root.mkdir()
            state.init_project(root, name="churn", goal="predict churn")

            self.assertTrue((root / "1ml" / "state.json").exists())
            saved = json.loads((root / "1ml" / "state.json").read_text(encoding="utf-8"))
            self.assertEqual(saved["project"]["goal"], "predict churn")

    def test_next_stage_requires_a_requested_task(self):
        import state

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            root.mkdir()
            state.init_project(root, name="churn", goal="predict churn")

            first = state.next_stage(root)
            self.assertIsNone(first["stage"])
            self.assertEqual(first['status'], 'needs_request')
            self.assertFalse(first["blocked"])

    def test_cannot_complete_a_stage_before_declared_prerequisites(self):
        import state

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            root.mkdir()
            state.init_project(root, name="churn", goal="predict churn")

            state.configure_stage(root, 'train', ['evaluation'])
            with self.assertRaises(state.GateError):
                state.set_stage(root, "train", "complete", conclusions=['Candidate fitted.'])

    def test_records_conclusions_questions_and_decisions(self):
        import state

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            root.mkdir()
            state.init_project(root, name="churn", goal="predict churn")

            state.set_stage(
                root,
                "frame",
                "done",
                conclusions=["Retention is the business goal."],
                questions=["What counts as a churned account?"],
                decisions=[
                    {
                        "id": "DEC-001",
                        "summary": "Use monthly churn label",
                        "rationale": "Matches the billing cycle.",
                        "citations": ["https://example.org/billing"],
                    }
                ],
            )

            saved = state.load_state(root)
            frame = saved["stages"]["frame"]
            self.assertEqual(frame["status"], "complete")
            self.assertEqual(frame["conclusions"], ["Retention is the business goal."])
            self.assertEqual(frame["questions"], ["What counts as a churned account?"])
            self.assertEqual(frame["decisions"][0]["id"], "DEC-001")
            self.assertIsNone(state.next_stage(root, 'frame')["stage"])

    def test_add_source_records_dataset_path(self):
        import state

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            root.mkdir()
            state.init_project(root, name="churn", goal="predict churn")

            state.add_source(root, "data/customers.csv", kind="csv")

            saved = state.load_state(root)
            self.assertEqual(saved["sources"][0]["path"], "data/customers.csv")


class RenderTests(unittest.TestCase):
    def make_plan(self) -> dict:
        return {
            "stage": "data",
            "cells": [
                {
                    "id": "data-load-001",
                    "type": "markdown",
                    "source": "## Load the data",
                    "teaches": "why we load before deciding",
                },
                {
                    "id": "data-missing-002",
                    "type": "code",
                    "source": "df.isna().mean()",
                    "depends_on": ["data-load-001"],
                    "expected_output": "missing fraction per column",
                },
            ],
            "conclusions": ["`age` is 20% missing."],
            "questions": ["Is `customer_id` unique per row?"],
        }

    def test_appends_cells_and_keeps_notebook_valid(self):
        import render

        with tempfile.TemporaryDirectory() as tmp:
            notebook = Path(tmp) / "ml-project.ipynb"
            result = render.render_plan(self.make_plan(), notebook)

            self.assertEqual(result["added"], ["data-load-001", "data-missing-002"])
            notebook_text = notebook.read_text(encoding="utf-8")
            self.assertIn("data-load-001", notebook_text)

    def test_is_idempotent_for_already_rendered_cells(self):
        import render

        with tempfile.TemporaryDirectory() as tmp:
            notebook = Path(tmp) / "ml-project.ipynb"
            render.render_plan(self.make_plan(), notebook)
            second = render.render_plan(self.make_plan(), notebook)

            self.assertEqual(second["added"], [])
            self.assertEqual(second["skipped"], ["data-load-001", "data-missing-002"])

    def test_rejects_plan_that_fails_schema(self):
        import render

        bad_plan = {"stage": "data", "cells": [{"id": "Bad Id", "type": "code", "source": "x=1"}]}

        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(render.PlanError):
                render.render_plan(bad_plan, Path(tmp) / "ml-project.ipynb")

    def test_rejects_dependency_on_unknown_cell(self):
        import render

        plan = self.make_plan()
        plan["cells"][1]["depends_on"] = ["does-not-exist"]

        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(render.PlanError):
                render.render_plan(plan, Path(tmp) / "ml-project.ipynb")

    def test_records_rendered_cells_in_project_state(self):
        import render
        import state

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            root.mkdir()
            state.init_project(root, name="churn", goal="predict churn")
            notebook = root / "ml-project.ipynb"

            render.render_plan(self.make_plan(), notebook, project_root=root, stage="data")

            saved = state.load_state(root)
            data_stage = saved["stages"]["data"]
            self.assertEqual(
                data_stage["cells"], ["data-load-001", "data-missing-002"]
            )
            self.assertIn("`age` is 20% missing.", data_stage["conclusions"])


class RuleTableTests(unittest.TestCase):
    RULES_DIR = Path(__file__).resolve().parents[1] / "rules"
    STAGE_FILES = {
        "frame": "frame.yaml",
        "metrics": "metrics.yaml",
        "data": "data.yaml",
        "eda": "eda.yaml",
        "preprocess": "preprocess.yaml",
        "features": "features.yaml",
        "model": "model.yaml",
        "validate": "validate.yaml",
    }

    def test_packaged_investigation_tables_exist(self):
        for stage, filename in self.STAGE_FILES.items():
            self.assertTrue(
                (self.RULES_DIR / filename).exists(), f"missing rule table for {stage}"
            )

    def test_rules_are_well_formed_and_cited(self):
        import match_rules

        for stage, filename in self.STAGE_FILES.items():
            rules = match_rules.load_rules(self.RULES_DIR / filename)
            self.assertTrue(rules.get("rules"), f"{filename} has no rules")
            for rule in rules["rules"]:
                self.assertRegex(rule["id"], r"^[A-Z]+-\d{3}$")
                self.assertTrue(rule.get("title"), f"{rule['id']} has no title")
                self.assertIn(
                    rule.get("scope"), ("column", "dataset", "target"), rule["id"]
                )
                self.assertIsInstance(rule.get("applies_when"), dict)
                self.assertIsInstance(rule.get("recommend"), dict)
                self.assertTrue(rule.get("recommend", {}).get("action"))
                self.assertTrue(rule.get("rationale"), f"{rule['id']} has no rationale")
                self.assertTrue(rule.get("cite"), f"{rule['id']} has no citation")
                for cite in rule["cite"]:
                    self.assertTrue(cite.get("url", "").startswith("https://"))
                    self.assertTrue(cite.get("section"), f"{rule['id']} cite has no section")

    def test_rule_ids_are_unique_across_all_tables(self):
        import match_rules

        seen: dict[str, str] = {}
        for filename in self.STAGE_FILES.values():
            rules = match_rules.load_rules(self.RULES_DIR / filename)
            for rule in rules["rules"]:
                self.assertNotIn(rule["id"], seen, f"{rule['id']} duplicated")
                seen[rule["id"]] = filename

    def test_rules_only_use_known_fact_fields(self):
        """A rule must not reference a field the profiler never produces."""
        import match_rules

        allowed = {
            "name",
            "dtype",
            "kind",
            "missing_count",
            "missing_fraction",
            "n_unique",
            "unique_fraction",
            "is_identifier",
            "is_constant",
            "numeric.mean",
            "numeric.std",
            "numeric.min",
            "numeric.max",
            "numeric.skew",
            "outlier_fraction",
            "n_rows",
            "n_columns",
            "n_numeric",
            "n_categorical",
            "n_text",
            "n_datetime",
            "n_boolean",
            "n_identifier",
            "duplicate_rows",
            "duplicate_fraction",
            "missing_cells",
            "has_target",
            "inferred",
            "class_distribution",
            "imbalance_ratio",
        }
        allowed_operators = {
            "eq",
            "ne",
            "gt",
            "gte",
            "lt",
            "lte",
            "in",
            "not_in",
            "contains",
            "exists",
        }

        for filename in self.STAGE_FILES.values():
            rules = match_rules.load_rules(self.RULES_DIR / filename)
            for rule in rules["rules"]:
                for field, condition in rule.get("applies_when", {}).items():
                    self.assertIn(field, allowed, f"{rule['id']} uses unknown field {field}")
                    if isinstance(condition, dict):
                        for operator in condition:
                            self.assertIn(
                                operator,
                                allowed_operators,
                                f"{rule['id']} uses unknown operator {operator}",
                            )


if __name__ == "__main__":
    unittest.main()
