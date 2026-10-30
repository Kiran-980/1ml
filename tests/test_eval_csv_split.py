"""Evaluation partitioning must preserve semantic CSV tokens before agent parsing."""
import csv
from pathlib import Path
import tempfile
import unittest

from evals.harness.csv_split import write_selected_rows


class CsvSplitTests(unittest.TestCase):
    def test_preserves_absence_unknown_empty_leading_zeros_and_row_order(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'source.csv'
            source.write_text('Id,kind,amount,note\n001,None,0,"a,b"\n002,NA,,unknown\n003,,12.50,empty\n', encoding='utf-8')
            target = root / 'split.csv'
            write_selected_rows(source, [2, 0, 1], target)
            with target.open(newline='', encoding='utf-8') as stream:
                self.assertEqual(list(csv.reader(stream)), [
                    ['Id', 'kind', 'amount', 'note'],
                    ['003', '', '12.50', 'empty'],
                    ['001', 'None', '0', 'a,b'],
                    ['002', 'NA', '', 'unknown'],
                ])

    def test_rejects_duplicate_or_out_of_range_rows_without_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'source.csv'
            source.write_text('Id,x\n1,None\n2,NA\n')
            for rows in ([0, 0], [-1], [2]):
                target = root / 'bad.csv'
                with self.assertRaises(ValueError):
                    write_selected_rows(source, rows, target)
                self.assertFalse(target.exists())


if __name__ == '__main__':
    unittest.main()
