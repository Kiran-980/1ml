"""Forecast bundles may encapsulate history without being sklearn Pipelines."""
import json
from pathlib import Path
import tempfile
import unittest

from tests import test_eval_regression as regression


@unittest.skipUnless(regression.AVAILABLE, 'Optional evaluation runtime unavailable')
class ForecastBundleTests(unittest.TestCase):
    def fixture(self, root):
        import joblib
        import pandas as pd
        from sklearn.dummy import DummyRegressor
        helper = regression.RegressionBundleTests()
        helper.fixture(root)
        x = pd.read_csv(root / 'inputs/test.csv')
        # A complete fitted feature-free forecaster is a valid baseline bundle.
        model = DummyRegressor(strategy='mean').fit(x, [10., 20., 30., 40.])
        joblib.dump(model, root / 'models/model.joblib')
        pd.DataFrame({'Id': x.Id, 'Value': model.predict(x)}).to_csv(root / 'predictions.csv', index=False)
        config = json.loads((root / 'config.json').read_text())
        config['prediction_contract']['task'] = 'forecasting'
        (root / 'config.json').write_text(json.dumps(config))
        return helper

    def test_complete_nonpipeline_forecaster_reloads_with_numeric_parity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            helper = self.fixture(root / 'run')
            result = helper.verify(root / 'run', root / 'audit')
            self.assertEqual(result['status'], 'passed', result)
            self.assertEqual(result['prediction_task'], 'forecasting')
            self.assertIsInstance(result['parity_tolerance'], dict)

    def test_forecast_artifact_without_predict_is_rejected(self):
        import joblib
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            helper = self.fixture(root / 'run')
            joblib.dump({'history': [1, 2, 3]}, root / 'run/models/model.joblib')
            result = helper.verify(root / 'run', root / 'audit')
            self.assertEqual(result['status'], 'failed', result)
            self.assertIn('predict', result['error'])


if __name__ == '__main__':
    unittest.main()
