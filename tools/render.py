"""Render a validated cell plan into a notebook and the project state.

This is the only path that changes a learner notebook. A plan is validated
against ``plan_schema.json`` first, dependency ids are checked, then cells are
appended. Writes are append-only and idempotent: a plan that is rendered
twice leaves the notebook unchanged the second time.

Usage:
    python render.py --plan plan.json --notebook ml-project.ipynb \
        --project . --stage data
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

sys.path.insert(0, str(Path(__file__).resolve().parent))
import append_cells  # noqa: E402
import common  # noqa: E402
import state as state_tool  # noqa: E402

SCHEMA_PATH = Path(__file__).resolve().parent / "plan_schema.json"


class PlanError(ValueError):
    """Raised when a cell plan is invalid and must not be rendered."""


def load_schema() -> dict:
    with open(SCHEMA_PATH, "r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_plan(plan: dict) -> None:
    """Validate a plan against the schema, raising PlanError on any violation."""
    validator = Draft202012Validator(load_schema())
    errors = sorted(validator.iter_errors(plan), key=lambda error: list(error.path))
    if errors:
        first = errors[0]
        location = "/".join(str(part) for part in first.path) or "plan"
        raise PlanError(f"{location}: {first.message}")


def check_dependencies(plan: dict, notebook_path) -> None:
    """Every depends_on id must exist in the plan or already in the notebook."""
    known = set()
    ids = [cell['id'] for cell in plan['cells']]
    if len(ids) != len(set(ids)):
        raise PlanError('duplicate cell IDs in plan')
    notebook = append_cells.load_notebook(notebook_path)
    known |= {
        append_cells.cell_id(cell)
        for cell in notebook.cells
        if append_cells.cell_id(cell)
    }

    for cell in plan["cells"]:
        for dependency in cell.get("depends_on", []):
            if dependency not in known:
                raise PlanError(
                    f"cell '{cell['id']}' depends on '{dependency}', which is "
                    "neither in this plan nor in the notebook"
                )
        known.add(cell['id'])


def render_plan(
    plan: dict,
    notebook_path,
    project_root=None,
    stage: str | None = None,
) -> dict:
    """Validate and render a plan, then record it in the project state."""
    path = Path(notebook_path)
    with common.file_lock(path.with_suffix(path.suffix + '.lock')):
        return _render_locked(plan, notebook_path, project_root, stage)


def _render_locked(plan, notebook_path, project_root=None, stage=None):
    validate_plan(plan)
    if stage is not None and state_tool.canonical(stage) != state_tool.canonical(plan['stage']):
        raise PlanError('plan stage does not match requested task')
    if project_root is not None:
        state_tool.load_state(project_root)
        stage = stage or plan['stage']
    check_dependencies(plan, notebook_path)

    result = append_cells.append_plan(notebook_path, plan)

    if project_root is not None and stage is not None:
        state_tool.record_stage(
            project_root,
            stage,
            conclusions=plan.get("conclusions", []),
            questions=plan.get("questions", []),
            decisions=plan.get("decisions", []),
            cells=[cell['id'] for cell in plan['cells']],
            rule_matches=sorted(
                {
                    rule_id
                    for cell in plan["cells"]
                    for rule_id in cell.get("rule_ids", [])
                }
            ),
        )

    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render a cell plan into a notebook.")
    parser.add_argument("--plan", required=True, help="path to the cell-plan JSON")
    parser.add_argument("--notebook", required=True, help="path to the notebook")
    parser.add_argument("--project", help="project root holding the 1ml state folder")
    parser.add_argument("--stage", help="stage this plan belongs to")
    args = parser.parse_args(argv)

    try:
        plan = common.read_json(args.plan)
    except (OSError, ValueError) as error:
        common.fail(str(error))
        return 2

    try:
        result = render_plan(
            plan, args.notebook, project_root=args.project, stage=args.stage
        )
    except (ValueError, OSError) as error:
        print(f"error: invalid plan: {error}", file=sys.stderr)
        return 2

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
