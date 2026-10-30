"""Profile a dataset into structured facts for the rule matcher.

The profiler answers mechanical questions about a dataset: shape, column
kinds, missingness, duplicates, target balance. It never recommends an
action. Recommendations come from the rule tables, so every recommendation
stays traceable to a rule id and a citation.

Usage:
    python data_profile.py --csv data/customers.csv --out profile.json
    python data_profile.py --sqlite data/app.db --table customers --out profile.json
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402

ID_NAME_RE = re.compile(r"(^|_)(id|uuid|guid|key)$", re.IGNORECASE)
TARGET_NAME_RE = re.compile(
    r"^(target|label|y|churn|outcome|class|response|sale|default)$", re.IGNORECASE
)
TEXT_UNIQUE_THRESHOLD = 50
HIGH_MISSING = 0.30
LOW_UNIQUE_RATIO = 0.005


def _kind_for(name: str, series: pd.Series) -> str:
    """Classify one column by dtype, name, and cardinality."""
    if ID_NAME_RE.search(name):
        return "identifier"
    if pd.api.types.is_bool_dtype(series):
        return "boolean"
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"
    if pd.api.types.is_numeric_dtype(series):
        return "numeric"
    if int(series.nunique(dropna=True)) <= TEXT_UNIQUE_THRESHOLD:
        return "categorical"
    return "text"


def _outlier_fraction(series: pd.Series) -> float:
    """Fraction of values outside Tukey's 1.5 x IQR fences."""
    clean = series.dropna()
    if len(clean) < 4:
        return 0.0
    first = clean.quantile(0.25)
    third = clean.quantile(0.75)
    spread = third - first
    if not spread:
        return 0.0
    low = first - 1.5 * spread
    high = third + 1.5 * spread
    outside = ((clean < low) | (clean > high)).sum()
    return round(float(outside) / len(clean), 6)


def _column_facts(name: str, series: pd.Series, n_rows: int, include_values=False) -> dict:
    kind = _kind_for(name, series)
    missing_count = int(series.isna().sum())
    n_unique = int(series.nunique(dropna=True))

    facts = {
        "name": name,
        "dtype": str(series.dtype),
        "kind": kind,
        "missing_count": missing_count,
        "missing_fraction": round(missing_count / n_rows, 6) if n_rows else 0.0,
        "n_unique": n_unique,
        "unique_fraction": round(n_unique / n_rows, 6) if n_rows else 0.0,
        "is_identifier": kind == "identifier",
        "is_constant": n_unique <= 1,
    }

    if kind in ("numeric",):
        clean = series.dropna()
        finite = clean.map(lambda value: math.isfinite(float(value)))
        facts['nonfinite_count'] = int((~finite).sum())
        clean = clean[finite]
        facts["numeric"] = {
            "mean": round(float(clean.mean()), 6) if len(clean) else None,
            "std": round(float(clean.std()), 6) if len(clean) > 1 else None,
            "min": round(float(clean.min()), 6) if len(clean) else None,
            "max": round(float(clean.max()), 6) if len(clean) else None,
            "skew": round(float(clean.skew()), 6) if len(clean) > 2 else None,
        }
        facts["numeric"] = {key: value if value is None or math.isfinite(value) else None
                            for key, value in facts['numeric'].items()}
        facts["outlier_fraction"] = _outlier_fraction(clean)
    if include_values and kind in ("categorical", "boolean"):
        counts = series.value_counts(dropna=True).head(20)
        facts["top_values"] = {
            str(value): int(count) for value, count in counts.items()
        }
    if include_values and kind == "text":
        sample = series.dropna().astype(str).unique()[:5]
        facts["sample"] = [str(value) for value in sample]

    return facts


def _find_target(features: list[dict], n_rows: int) -> dict | None:
    for feature in features:
        if TARGET_NAME_RE.match(feature["name"].strip()):
            return feature
    return None


def _target_facts(
    feature: dict | None,
    counts: pd.Series | None,
    n_rows: int,
    explicit: bool,
) -> dict | None:
    if feature is None:
        return None

    facts = {
        "name": feature["name"],
        "dtype": feature["dtype"],
        "kind": feature["kind"],
        "n_unique": feature["n_unique"],
        "missing_fraction": feature["missing_fraction"],
        "inferred": not explicit,
    }

    if (
        feature["kind"] in ("numeric", "categorical", "boolean")
        and feature["n_unique"] <= 20
        and counts is not None
    ):
        distribution = {
            str(value): round(count / n_rows, 6) if n_rows else 0.0
            for value, count in counts.items()
        }
        facts["class_distribution"] = distribution
        if distribution:
            raw = list(counts.to_numpy())
            facts["imbalance_ratio"] = min(raw) / max(raw) if max(raw) else None
        else:
            facts["imbalance_ratio"] = None
    else:
        facts["class_distribution"] = None
        facts["imbalance_ratio"] = None

    return facts


def profile_dataframe(
    df: pd.DataFrame, source: dict, target: str | None = None, include_values=False
) -> dict:
    """Build the facts document for one dataframe."""
    n_rows = int(len(df))
    n_columns = int(len(df.columns))

    features = [_column_facts(str(name), df[name], n_rows, include_values) for name in df.columns]

    kinds: dict[str, int] = {}
    for feature in features:
        kinds[feature["kind"]] = kinds.get(feature["kind"], 0) + 1

    missing_cells = sum(feature["missing_count"] for feature in features)
    total_cells = n_rows * n_columns
    duplicate_rows = int(df.duplicated().sum()) if n_rows else 0

    dataset = {
        "n_rows": n_rows,
        "n_columns": n_columns,
        "n_numeric": kinds.get("numeric", 0),
        "n_categorical": kinds.get("categorical", 0),
        "n_text": kinds.get("text", 0),
        "n_datetime": kinds.get("datetime", 0),
        "n_boolean": kinds.get("boolean", 0),
        "n_identifier": kinds.get("identifier", 0),
        "duplicate_rows": duplicate_rows,
        "duplicate_fraction": round(duplicate_rows / n_rows, 6) if n_rows else 0.0,
        "missing_cells": missing_cells,
        "missing_fraction": round(missing_cells / total_cells, 6) if total_cells else 0.0,
    }

    target_feature = None
    explicit = False
    if target:
        explicit = True
        for feature in features:
            if feature["name"] == target:
                target_feature = feature
                break
        if target_feature is None:
            raise ValueError(f"target column not found in dataset: {target}")
    else:
        target_feature = _find_target(features, n_rows)

    target_counts = (
        df[target_feature["name"]].value_counts(dropna=True)
        if target_feature is not None
        else None
    )
    target_facts = _target_facts(target_feature, target_counts, n_rows, explicit)
    dataset["has_target"] = target_facts is not None

    issues = []
    for feature in features:
        if feature["missing_fraction"] >= HIGH_MISSING:
            issues.append(
                {
                    "code": "HIGH_MISSING",
                    "severity": "warning",
                    "column": feature["name"],
                    "message": (
                        f"{feature['missing_fraction']:.1%} of values are missing"
                    ),
                }
            )
        if feature["is_constant"]:
            issues.append(
                {
                    "code": "CONSTANT_COLUMN",
                    "severity": "info",
                    "column": feature["name"],
                    "message": "at most one observed value in this extract; inspect missingness and schema role",
                }
            )
        if feature["kind"] == "text" and feature["unique_fraction"] > 0.5:
            issues.append(
                {
                    "code": "HIGH_CARDINALITY_TEXT",
                    "severity": "warning",
                    "column": feature["name"],
                    "message": "text column is nearly unique per row; it may be an identifier",
                }
            )
    if duplicate_rows:
        issues.append(
            {
                "code": "DUPLICATE_ROWS",
                "severity": "warning",
                "column": None,
                "message": f"{duplicate_rows} fully duplicated rows",
            }
        )
    if target_facts and target_facts.get("imbalance_ratio") is not None:
        if target_facts["imbalance_ratio"] < 0.5:
            issues.append(
                {
                    "code": "TARGET_IMBALANCE",
                    "severity": "warning",
                    "column": target_facts["name"],
                    "message": (
                        "minority class is "
                        f"{target_facts['imbalance_ratio']:.1%} of the majority class"
                    ),
                }
            )

    return {
        "source": source,
        "dataset": dataset,
        "target": target_facts,
        "features": features,
        "issues": issues,
    }


def profile_frame(
    path: str,
    table: str | None = None,
    target: str | None = None,
    max_rows: int | None = None,
    include_values: bool = False,
) -> dict:
    """Read a dataset from disk and return its facts document."""
    source_path = Path(path)
    if max_rows is not None and max_rows <= 0:
        raise ValueError('max_rows must be positive')
    if not source_path.is_file():
        raise FileNotFoundError(source_path)
    suffix = source_path.suffix.lower()

    if suffix in (".db", ".sqlite", ".sqlite3"):
        if not table:
            raise ValueError("--table is required for SQLite sources")
        import sqlite3

        connection = sqlite3.connect(source_path.resolve().as_uri() + '?mode=ro', uri=True)
        try:
            query = f'SELECT * FROM "{table.replace(chr(34), chr(34) * 2)}"'
            if max_rows is not None:
                query += ' LIMIT ?'
            frame = pd.read_sql_query(query, connection, params=[max_rows] if max_rows is not None else None)
        finally:
            connection.close()
        source = {
            "path": str(source_path),
            "kind": "sqlite",
            "table": table,
            "rows_read": int(len(frame)),
            "max_rows": max_rows,
        }
    elif suffix == ".parquet":
        if max_rows is not None:
            raise ValueError('bounded Parquet reads require an explicit batch/row-group loader; CSV-style max_rows is unsupported')
        frame = pd.read_parquet(source_path)
        source = {
            "path": str(source_path),
            "kind": "parquet",
            "table": None,
            "rows_read": int(len(frame)),
        }
    else:
        separator = "\t" if suffix in (".tsv", ".tab") else ","
        frame = pd.read_csv(source_path, sep=separator, nrows=max_rows)
        source = {
            "path": str(source_path),
            "kind": "csv",
            "table": None,
            "rows_read": int(len(frame)),
            "max_rows": max_rows,
        }

    return profile_dataframe(frame, source, target=target, include_values=include_values)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Profile a dataset into ML facts.")
    parser.add_argument("--csv", help="path to a CSV or TSV file")
    parser.add_argument("--sqlite", help="path to a SQLite database file")
    parser.add_argument("--table", help="table name inside the SQLite database")
    parser.add_argument("--target", help="name of the target column")
    parser.add_argument("--max-rows", type=int, help="read at most this many rows")
    parser.add_argument("--out", help="write the facts JSON here instead of stdout")
    parser.add_argument('--include-values', action='store_true', help='include potentially sensitive category/text examples')
    args = parser.parse_args(argv)

    if args.csv:
        source_path = args.csv
    elif args.sqlite:
        source_path = args.sqlite
    else:
        parser.error("one of --csv or --sqlite is required")

    try:
        facts = profile_frame(
            source_path,
            table=args.table,
            target=args.target,
            max_rows=args.max_rows,
            include_values=args.include_values,
        )
    except (ValueError, FileNotFoundError) as error:
        common.fail(str(error))

    if args.out:
        common.write_json(args.out, facts)
        print(f"wrote {args.out}")
    else:
        print(json.dumps(facts, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
