"""Regression bundles must use numeric contracts, not classification labels."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

from evals.harness.notebook_server import call_worker

AVAILABLE = all(importlib.util.find_spec(name) for name in ('sklearn', 'pandas', 'nbformat', 'IPython'))


@unittest.skipUnless(AVAILABLE, 'Optional evaluation runtime unavailable')
class RegressionBundleTests(unittest.TestCase):
    def fixture(self, root, target_transform=False):
        import joblib
        import nbformat
        import numpy as np
        import pandas as pd
        from sklearn.compose import TransformedTargetRegressor
        from sklearn.impute import SimpleImputer
        from sklearn.linear_model import LinearRegression
        from sklearn.pipeline import Pipeline
        for folder in ('reports', 'notebooks', 'inputs', 'models'):
            (root / folder).mkdir(parents=True)
        x = pd.DataFrame({'Id': [1, 2, 3, 4], 'value': [1., 2., 3., 4.]})
        y = np.array([100.25, 200.5, 300.75, 401.])
        model = Pipeline([('impute', SimpleImputer()), ('regressor', LinearRegression())])
        if target_transform:
            model = TransformedTargetRegressor(regressor=model, func=np.log, inverse_func=np.exp)
        model.fit(x, y)
        joblib.dump(model, root / 'models/model.joblib')
        x.to_csv(root / 'inputs/test.csv', index=False)
        pd.DataFrame({'Id': x.Id, 'Value': model.predict(x)}).to_csv(root / 'predictions.csv', index=False)
        nb = nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell('print("fixture")', execution_count=1)])
        nbformat.write(nb, root / 'notebooks/fixture.ipynb')
        (root / 'requirements.txt').write_text('scikit-learn\n')
        (root / 'reports/metrics.json').write_text('{"metric":"rmse"}')
        contract = {'input': 'inputs/test.csv', 'id': 'Id', 'target': 'Value',
                    'task': 'regression', 'minimum_exclusive': 0}
        (root / 'config.json').write_text(json.dumps({'prediction_contract': contract}))
        manifest = {'notebook': 'notebooks/fixture.ipynb', 'model': 'models/model.joblib',
                    'predictions': 'predictions.csv', 'metrics': 'reports/metrics.json',
                    'requirements': 'requirements.txt', 'supporting_modules': []}
        (root / 'reports/artifact-manifest.json').write_text(json.dumps(manifest))

    def verify(self, root, audit):
        return call_worker(root, audit, Path(sys.executable), 'verify_bundle')

    def test_fractional_positive_predictions_pass_fresh_process(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            self.fixture(base / 'run')
            result = self.verify(base / 'run', base / 'audit')
            self.assertEqual(result['status'], 'passed', result)
            self.assertTrue(result['fresh_process'])

    def test_transformed_target_complete_pipeline_is_supported(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            self.fixture(base / 'run', target_transform=True)
            result = self.verify(base / 'run', base / 'audit')
            self.assertEqual(result['status'], 'passed', result)

    def test_invalid_regression_outputs_fail(self):
        import pandas as pd
        for bad in (float('nan'), float('inf'), -1., 0.):
            with self.subTest(value=bad), tempfile.TemporaryDirectory() as directory:
                base = Path(directory)
                self.fixture(base / 'run')
                p = base / 'run/predictions.csv'
                frame = pd.read_csv(p)
                frame.loc[0, 'Value'] = bad
                frame.to_csv(p, index=False)
                result = self.verify(base / 'run', base / 'audit')
                self.assertEqual(result['status'], 'failed', result)
                self.assertIn('Regression', result['error'])

    def test_classification_label_contract_still_rejects_invalid_values(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            self.fixture(base / 'run')
            config = base / 'run/config.json'
            d = json.loads(config.read_text())
            d['prediction_contract'].update(task='classification', values=[0, 1])
            config.write_text(json.dumps(d))
            result = self.verify(base / 'run', base / 'audit')
            self.assertEqual(result['status'], 'failed', result)
            self.assertIn('Invalid prediction values', result['error'])

    def test_positive_but_changed_predictions_fail_reload_parity(self):
        import pandas as pd
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            self.fixture(base / 'run')
            path = base / 'run/predictions.csv'
            predictions = pd.read_csv(path)
            predictions.loc[0, 'Value'] += 1.
            predictions.to_csv(path, index=False)
            result = self.verify(base / 'run', base / 'audit')
            self.assertEqual(result['status'], 'failed', result)
            self.assertIn('Fresh-process prediction mismatch', result['error'])

    def test_declared_parser_preserves_category_tokens_for_reload(self):
        import joblib
        import pandas as pd
        from sklearn.compose import ColumnTransformer
        from sklearn.linear_model import LinearRegression
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import OneHotEncoder
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / 'run'
            self.fixture(root)
            features = pd.DataFrame({'Id': [1, 2, 3, 4], 'kind': ['None', 'NA', '', 'Stone']})
            values = [10., 20., 30., 40.]
            model = Pipeline([('encode', ColumnTransformer([('kind', OneHotEncoder(handle_unknown='ignore'), ['kind'])])),
                              ('regress', LinearRegression())]).fit(features, values)
            joblib.dump(model, root / 'models/model.joblib')
            features.to_csv(root / 'inputs/test.csv', index=False)
            pd.DataFrame({'Id': features.Id, 'Value': model.predict(features)}).to_csv(root / 'predictions.csv', index=False)
            path = root / 'reports/artifact-manifest.json'
            manifest = json.loads(path.read_text())
            manifest['input_csv_options'] = {'keep_default_na': False}
            path.write_text(json.dumps(manifest))
            result = self.verify(root, base / 'audit')
            self.assertEqual(result['status'], 'passed', result)


if __name__ == '__main__':
    unittest.main()
