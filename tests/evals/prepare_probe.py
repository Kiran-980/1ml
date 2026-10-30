"""Create a fresh instruction-only probe, without answer keys or research."""
import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path
from eval_paths import run_directory


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("case")
    parser.add_argument("run_name")
    args = parser.parse_args()
    for name in [args.case, args.run_name]:
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", name):
            parser.error("case and run names must be lowercase slugs")
    root = Path(__file__).resolve().parents[2]
    case_dir = root / "tests/evals" / args.case
    case = json.loads((case_dir / "case.yaml").read_text(encoding="utf-8"))
    run = run_directory(root, args.run_name)
    if run.exists():
        parser.error("run already exists; use a fresh name")
    plugin = run / "plugin"
    plugin.mkdir(parents=True)
    for folder in ["skills", "references", "tools", "rules", ".claude-plugin"]:
        shutil.copytree(root / folder, plugin / folder,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    for name in ["README.md", "requirements.txt"]:
        shutil.copy2(root / name, plugin / name)
    (run / "prompt.txt").write_text(case["execution"]["prompt"], encoding="utf-8")
    files = {p.relative_to(plugin).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in sorted(plugin.rglob("*")) if p.is_file()}
    (run / "source-manifest.json").write_text(json.dumps(files, indent=2), encoding="utf-8")
    print(run.resolve())


if __name__ == "__main__":
    main()
