import json
from pathlib import Path
import tempfile
import unittest

from evals.harness.history import prepare_history


class HistoryTests(unittest.TestCase):
    def test_history_keeps_notebooks_and_versions_without_deleting_source(self):
        with tempfile.TemporaryDirectory() as directory:
            dataset=Path(directory)/'evals/kaggle/example'
            for name in ('one','two'):
                project=dataset/'work'/name
                for folder in ('models','inputs','agent/environment','reports'):
                    (project/folder).mkdir(parents=True)
                (project/'analysis.ipynb').write_text('{"cells":[]}')
                (project/'requirements.txt').write_text('numpy==2.0\n')
                (project/'inputs/source.csv').write_text('x\n1\n')
                (project/'models/model.joblib').write_bytes(b'weights')
                (project/'reports/metrics.json').write_text('{"score":0.5}')
                (project/'agent/environment/disposable.txt').write_text('cache')
                result=prepare_history(project,dataset)
                self.assertTrue((project/'models/model.joblib').exists())
                self.assertNotIn('agent/environment/disposable.txt',result['files'])
                self.assertNotIn('file',result['files']['models/model.joblib'])
                self.assertTrue((dataset/result['files']['analysis.ipynb']['file']).is_file())
                self.assertEqual(list((dataset/'evaluator'/name/'notebook-history').iterdir())[0].suffix,'.ipynb')
            first=json.loads((dataset/'evaluator/one/history-manifest.json').read_text())
            second=json.loads((dataset/'evaluator/two/history-manifest.json').read_text())
            self.assertEqual(first['files']['requirements.txt']['file'],second['files']['requirements.txt']['file'])
            self.assertEqual(first['files']['inputs/source.csv']['file'],second['files']['inputs/source.csv']['file'])
            from evals.harness.restore_history import restore
            restored=Path(directory)/'restored'
            restore(dataset/'evaluator/one/history-manifest.json',restored)
            self.assertEqual((restored/'requirements.txt').read_text(),'numpy==2.0\n')
            self.assertEqual((restored/'inputs/source.csv').read_text(),'x\n1\n')
            self.assertTrue((restored/'analysis.ipynb').is_file())
            self.assertFalse((restored/'models/model.joblib').exists())
            self.assertFalse((restored/'agent/environment').exists())

    def test_refuses_project_outside_named_dataset(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError): prepare_history(Path(directory)/'unrelated',Path(directory)/'dataset')


if __name__=='__main__': unittest.main()
