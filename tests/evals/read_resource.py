"""Read an isolated skill resource and record exactly which bytes were supplied.

This is an evaluation instrument, not a plugin runtime dependency. It cannot
detect reads made through another tool; reviewers must distinguish its audit
from a complete native host trace.
"""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    parser.add_argument("resource")
    args = parser.parse_args()
    root = (args.run / "plugin").resolve()
    path = (root / args.resource).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        parser.error("resource must be an existing file inside this run's plugin")
    content = path.read_bytes()
    record = {"at": datetime.now(timezone.utc).isoformat(),
              "path": path.relative_to(root).as_posix(), "bytes": len(content),
              "sha256": hashlib.sha256(content).hexdigest()}
    with (args.run / "reads.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record) + "\n")
    print(content.decode("utf-8-sig"))


if __name__ == "__main__":
    main()
