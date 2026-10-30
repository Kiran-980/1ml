"""Replay clustering labels without pretending transductive models predict new rows."""
import json
from pathlib import Path
import tempfile
import unittest
from tests import test_eval_regression as regression
from evals.harness.notebook_server import digest


@unittest.skipUnless(regression.AVAILABLE, 'Optional evaluation runtime unavailable')
class ClusteringBundleTests(unittest.TestCase):
    def fixture(self, root, mode='predict'):
        import joblib
        import pandas as pd
        from sklearn.cluster import KMeans, DBSCAN
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import StandardScaler
        helper=regression.RegressionBundleTests(); helper.fixture(root)
        x=pd.read_csv(root/'inputs/test.csv')
        estimator=KMeans(n_clusters=2,n_init=5,random_state=1) if mode=='predict' else DBSCAN(eps=.2,min_samples=2)
        model=Pipeline([('scale',StandardScaler()),('cluster',estimator)]).fit(x)
        labels=model.predict(x) if mode=='predict' else model[-1].labels_
        joblib.dump(model,root/'models/model.joblib')
        pd.DataFrame({'Id':x.Id,'Value':labels}).to_csv(root/'predictions.csv',index=False)
        config=json.loads((root/'config.json').read_text())
        config['prediction_contract']={'input':'inputs/test.csv','id':'Id','target':'Value','task':'clustering'}
        (root/'config.json').write_text(json.dumps(config))
        manifest=json.loads((root/'reports/artifact-manifest.json').read_text())
        manifest.update(assignment_mode=mode,fit_input_sha256=digest(root/'inputs/test.csv'))
        (root/'reports/artifact-manifest.json').write_text(json.dumps(manifest))
        return helper

    def test_predictive_clustering_replays_labels(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); helper=self.fixture(p/'run')
            result=helper.verify(p/'run',p/'audit')
            self.assertEqual(result['status'],'passed',result)
            self.assertEqual(result['assignment_mode'],'predict')
            self.assertTrue(result['predict_api_checked'])
            self.assertFalse(result['new_row_prediction_checked'])

    def test_transductive_noise_replays_only_fitted_population(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); helper=self.fixture(p/'run','transductive')
            result=helper.verify(p/'run',p/'audit')
            self.assertEqual(result['status'],'passed',result)
            self.assertEqual(result['assignment_mode'],'transductive')
            self.assertFalse(result['new_row_prediction_checked'])

    def test_fractional_cluster_labels_are_rejected(self):
        import pandas as pd
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); helper=self.fixture(p/'run')
            frame=pd.read_csv(p/'run/predictions.csv'); frame['Value']=frame.Value.astype(float)+.25
            frame.to_csv(p/'run/predictions.csv',index=False)
            result=helper.verify(p/'run',p/'audit')
            self.assertEqual(result['status'],'failed',result)
            self.assertIn('Cluster labels',result['error'])

    def test_transductive_input_fingerprint_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); helper=self.fixture(p/'run','transductive')
            path=p/'run/reports/artifact-manifest.json'; m=json.loads(path.read_text()); m['fit_input_sha256']='wrong'; path.write_text(json.dumps(m))
            result=helper.verify(p/'run',p/'audit')
            self.assertEqual(result['status'],'failed',result)
            self.assertIn('Transductive input fingerprint',result['error'])

    def test_changed_valid_labels_fail_parity(self):
        import pandas as pd
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); helper=self.fixture(p/'run')
            frame=pd.read_csv(p/'run/predictions.csv'); frame['Value']=1-frame.Value
            frame.to_csv(p/'run/predictions.csv',index=False)
            result=helper.verify(p/'run',p/'audit')
            self.assertEqual(result['status'],'failed',result)
            self.assertIn('Fresh-process prediction mismatch',result['error'])


if __name__=='__main__': unittest.main()
