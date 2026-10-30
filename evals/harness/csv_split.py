"""Subset CSV records without assigning missing-value or dtype semantics."""
import csv
from pathlib import Path


def write_selected_rows(source, row_indices, destination):
    with Path(source).open(newline='', encoding='utf-8-sig') as stream:
        records = list(csv.reader(stream))
    if not records or not records[0] or len(set(records[0])) != len(records[0]):
        raise ValueError('Expected a nonempty CSV with unique headers')
    header, rows = records[0], records[1:]
    indices = list(row_indices)
    if (any(type(i) is not int or i < 0 or i >= len(rows) for i in indices)
            or len(set(indices)) != len(indices)):
        raise ValueError('Row indices must be unique, in-range integers')
    if any(len(row) != len(header) for row in rows):
        raise ValueError('CSV row width differs from header')
    with Path(destination).open('x', newline='', encoding='utf-8') as stream:
        writer = csv.writer(stream)
        writer.writerow(header)
        writer.writerows(rows[i] for i in indices)
