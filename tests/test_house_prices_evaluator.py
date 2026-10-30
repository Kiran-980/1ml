"""Exercise the local evaluator's freeze and one-shot scoring boundaries."""
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('house_verifier', ROOT / 'evals/kaggle/house-prices/verify_eval.py')
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding='utf-8')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class HouseEvaluatorTests(unittest.TestCase):
    def fixture(self, task):
        import joblib
        import nbformat
        import pandas as pd
        from sklearn.linear_model import LinearRegression
        from sklearn.pipeline import Pipeline
        run = task / 'runs/fixture'
        evaluator = task / 'evaluator/fixture'
        for folder in ('inputs/data', 'notebooks', 'models', 'reports'):
            (run / folder).mkdir(parents=True)
        (task / 'data/original').mkdir(parents=True)
        evaluator.mkdir(parents=True)
        frame = pd.DataFrame({'Id': [1, 2, 3, 4], 'value': [1., 4., 2., 8.], 'SalePrice': [10., 40., 20., 80.]})
        dev, holdout = frame.iloc[:2], frame.iloc[2:]
        frame.to_csv(task / 'data/original/train.csv', index=False)
        dev.to_csv(run / 'inputs/data/development.csv', index=False)
        holdout.to_csv(evaluator / 'holdout.csv', index=False)
        from sklearn.compose import ColumnTransformer
        model = Pipeline([('select', ColumnTransformer([('value', 'passthrough', ['value'])])),
                          ('regressor', LinearRegression())]).fit(dev.drop(columns='SalePrice'), dev.SalePrice)
        joblib.dump(model, run / 'models/model.joblib')
        holdout[['Id', 'SalePrice']].to_csv(run / 'predictions.csv', index=False)
        notebook = nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell('1 + 1', execution_count=1)])
        nbformat.write(notebook, run / 'notebooks/fixture.ipynb')
        (run / 'requirements.txt').write_text('scikit-learn\n')
        write(run / 'reports/metrics.json', {'development_log_rmse': 0})
        manifest = {'notebook': 'notebooks/fixture.ipynb', 'model': 'models/model.joblib',
                    'predictions': 'predictions.csv', 'metrics': 'reports/metrics.json',
                    'requirements': 'requirements.txt', 'supporting_modules': []}
        hashes = {manifest[key]: digest(run / manifest[key]) for key in
                  ('notebook', 'model', 'predictions', 'metrics', 'requirements')}
        write(run / 'reports/artifact-manifest.json', manifest)
        write(run / 'reports/verify_bundle-feedback.json', {'status': 'passed', 'rows': 2, 'artifact_sha256': hashes})
        write(run / 'reports/execute_notebook-feedback.json', {'status': 'passed', 'notebook_sha256': hashes[manifest['notebook']]})
        write(run / 'config.json', {'input_sha256': {}, 'plugin_sha256': {}})
        write(evaluator / 'review.json', {'status': 'accepted', 'approved_sha256': hashes})
        write(evaluator / 'split.json', {'development_ids': [1, 2], 'holdout_ids': [3, 4],
              'source_sha256': digest(task / 'data/original/train.csv'), 'holdout_sha256': digest(evaluator / 'holdout.csv')})
        return run, evaluator

    def execute(self, task):
        with patch.object(verifier, 'TASK', task), patch('sys.argv', ['verify_eval', '--run', 'fixture']), contextlib.redirect_stdout(io.StringIO()):
            verifier.main()

    def test_scores_reviewed_bundle_once_and_preserves_first_result(self):
        import math
        with tempfile.TemporaryDirectory() as directory:
            task = Path(directory)
            run, evaluator = self.fixture(task)
            actor_before = {p.relative_to(run).as_posix(): digest(p) for p in run.rglob('*') if p.is_file()}
            self.execute(task)
            actor_after = {p.relative_to(run).as_posix(): digest(p) for p in run.rglob('*') if p.is_file()}
            self.assertEqual(actor_before, actor_after, 'Independent scoring must not change actor outputs')
            path = evaluator / 'verification.json'
            result = json.loads(path.read_text())
            self.assertAlmostEqual(result['holdout_log_rmse'], 0.)
            self.assertAlmostEqual(result['constant_baseline_prediction'], 20.)
            self.assertAlmostEqual(result['constant_baseline_log_rmse'], math.log(4) / math.sqrt(2))
            original_result = path.read_bytes()
            with self.assertRaisesRegex(ValueError, 'scoring already started'):
                self.execute(task)
            self.assertEqual(path.read_bytes(), original_result)
            self.assertTrue((evaluator / 'scoring-started.json').exists())

    def test_changed_artifacts_stop_before_label_access(self):
        with tempfile.TemporaryDirectory() as directory:
            task = Path(directory)
            run, evaluator = self.fixture(task)
            (run / 'requirements.txt').write_text('changed\n')
            # Removing labels demonstrates the integrity gate fails before trying to read them.
            (evaluator / 'holdout.csv').unlink()
            with self.assertRaisesRegex(AssertionError, 'Artifacts changed after review'):
                self.execute(task)
            self.assertFalse((evaluator / 'scoring-started.json').exists())


if __name__ == '__main__':
    unittest.main()
