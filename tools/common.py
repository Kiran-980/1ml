"""Shared constants and helpers for the 1ml tools.

Every tool takes paths as arguments and never assumes the current working
directory, so the tools run from any learner project.
"""

from __future__ import annotations

import json
import sys
import os
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

# Registry order is for display, never a prerequisite chain.
STAGE_ORDER = ['frame', 'data', 'evaluation', 'explore', 'statistics', 'prepare',
               'train', 'validate', 'experiment', 'release', 'operate']
STAGE_TITLES = {stage: stage.title() for stage in STAGE_ORDER}
STAGE_ALIASES = {'metrics': 'evaluation', 'eda': 'explore', 'preprocess': 'prepare',
                 'features': 'prepare', 'model': 'train', 'deploy': 'release',
                 'monitor': 'operate', 'retrain': 'operate'}

STATE_DIR_NAME = "1ml"
STATE_FILE_NAME = "state.json"
DEFAULT_NOTEBOOK = "ml-project.ipynb"
STATE_VERSION = 2


def project_paths(project_dir: str) -> dict:
    """Return the resolved paths of one learner project."""
    root = Path(project_dir).expanduser().resolve()
    state_dir = root / STATE_DIR_NAME
    return {
        "root": root,
        "state_dir": state_dir,
        "state_file": state_dir / STATE_FILE_NAME,
    }


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def read_json(path) -> object:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path, payload) -> None:
    """Write JSON atomically so a crash never leaves a half-written file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    write_text(path, json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False) + '\n')


def write_text(path, content):
    """Replace only after the complete contents are flushed."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=path.name + '.', suffix='.tmp', dir=path.parent)
    tmp = Path(name)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        tmp.replace(path)
    finally:
        tmp.unlink(missing_ok=True)


@contextmanager
def file_lock(path):
    """Reject concurrent writers; a crash leaves an explicit recovery signal."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as handle:
        handle.write(str(os.getpid()))
    try:
        yield
    finally:
        path.unlink(missing_ok=True)


def fail(message: str, code: int = 2):
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(code)


def blank_stage() -> dict:
    """Return an empty stage record."""
    return {
        "status": "pending",
        "questions": [],
        "conclusions": [],
        "decisions": [],
        "cells": [],
        "rule_matches": [],
        "updated_at": None,
        "dependencies": [],
        "outcome": None,
        "reason": None,
        "history": [],
    }
