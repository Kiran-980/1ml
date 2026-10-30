"""Append cells from a cell plan to a Jupyter notebook.

Writes are append-only: existing cells, learner edits, and cell outputs are
never rewritten. Re-running the same plan is a no-op because every cell
carries a stable id in its notebook metadata.
"""

from __future__ import annotations

from pathlib import Path

import nbformat as nbf
import common

META_KEY = "1ml"


def cell_id(cell) -> str | None:
    """Return the 1ml cell id of a notebook cell, or None when absent."""
    metadata = cell.get("metadata", {}) or {}
    block = metadata.get(META_KEY) or {}
    return block.get("cell_id")


def load_notebook(path) -> nbf.NotebookNode:
    """Load a notebook, or return an empty one when the file does not exist."""
    path = Path(path)
    if not path.exists():
        return nbf.v4.new_notebook()
    return nbf.read(str(path), as_version=4)


def build_cell(spec: dict) -> nbf.NotebookNode:
    """Build one notebook cell from a cell-plan entry."""
    if spec["type"] == "markdown":
        cell = nbf.v4.new_markdown_cell(spec["source"])
    else:
        cell = nbf.v4.new_code_cell(spec["source"])

    block: dict = {"cell_id": spec["id"]}
    for key in ("teaches", "expected_output", "cites", "rule_ids", "depends_on"):
        value = spec.get(key)
        if value:
            block[key] = value
    cell.metadata[META_KEY] = block
    return cell


def append_plan(notebook_path, plan: dict) -> dict:
    """Append the plan's cells to the notebook, skipping ids already present.

    Returns the ids that were added and the ids that were skipped.
    """
    notebook = load_notebook(notebook_path)
    seen = {cell_id(cell): cell for cell in notebook.cells if cell_id(cell)}

    added: list[str] = []
    skipped: list[str] = []
    for spec in plan["cells"]:
        cid = spec["id"]
        if cid in seen:
            existing = seen[cid]
            expected = build_cell(spec)
            if (existing.source != expected.source or existing.cell_type != expected.cell_type
                    or dict(existing.metadata.get(META_KEY, {})) != dict(expected.metadata[META_KEY])):
                raise ValueError(f'cell {cid} differs from the plan; preserve edits and use a new correction ID')
            skipped.append(cid)
            continue
        notebook.cells.append(build_cell(spec))
        seen[cid] = notebook.cells[-1]
        added.append(cid)

    if added:
        path = Path(notebook_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        nbf.validate(notebook)
        common.write_text(path, nbf.writes(notebook))

    return {"added": added, "skipped": skipped}
