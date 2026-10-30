"""Keep generated native workspaces out of recursive case discovery."""
from pathlib import Path
import re


def run_directory(root: Path, slug: str) -> Path:
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
        raise ValueError("run must be a lowercase slug")
    root = root.resolve()
    target = (root / "tests/eval-runs" / slug).resolve()
    if not target.is_relative_to(root) or target.is_relative_to(root / "tests/evals"):
        raise ValueError("run directory must stay in the project, outside case discovery")
    if any(char in str(target) for char in "()[]{}*?!#"):
        raise ValueError("native evaluation requires a path without permission-pattern metacharacters")
    return target
