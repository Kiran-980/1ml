"""Optional clean-kernel integration smoke test; uses synthetic data only."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
import state
import render


@unittest.skipUnless(all(importlib.util.find_spec(p) for p in ('nbclient', 'ipykernel', 'sklearn')),
                     'optional integration dependencies: nbclient, ipykernel, scikit-learn')
class NotebookExecutionTests(unittest.TestCase):
    def test_synthetic_grouped_pipeline_executes_in_clean_kernel(self):
        import nbformat
        from nbclient import NotebookClient
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            runtime = root/'runtime'
            runtime.mkdir()
            state.init_project(root, goal='Synthetic integration check')
            notebook = root/'ml-project.ipynb'
            code = '''import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score
X, y = make_classification(n_samples=120, n_features=4, n_informative=2, random_state=7)
groups = np.repeat(np.arange(12), 10)
train, test = next(GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=7).split(X, y, groups))
assert set(groups[train]).isdisjoint(groups[test])
X[train[::5], 0] = np.nan
X[test, 0] = 9999.0
pipeline = make_pipeline(SimpleImputer(strategy='median'), StandardScaler(), LogisticRegression(max_iter=200))
pipeline.fit(X[train], y[train])
assert np.allclose(pipeline[0].statistics_, np.nanmedian(X[train], axis=0))
assert not np.allclose(pipeline[0].statistics_, np.nanmedian(X, axis=0))
baseline = DummyClassifier(strategy='prior').fit(X[train], y[train])
results = {'candidate_accuracy': accuracy_score(y[test], pipeline.predict(X[test])),
           'baseline_accuracy': accuracy_score(y[test], baseline.predict(X[test])),
           'test_rows': len(test), 'group_overlap': 0}
assert np.isfinite(list(results.values())).all()
print(results)
'''
            plan = {'stage': 'train', 'cells': [
                {'id': 'synthetic-purpose', 'type': 'markdown', 'source': 'Synthetic smoke check, not a model-quality benchmark.'},
                {'id': 'synthetic-fit', 'type': 'code', 'source': code, 'depends_on': ['synthetic-purpose']}]}
            render.render_plan(plan, notebook, root, 'train')
            nb = nbformat.read(notebook, as_version=4)
            with patch.dict(os.environ, {'JUPYTER_RUNTIME_DIR': str(runtime), 'IPYTHONDIR': str(runtime/'ipython')}):
                print('notebook-smoke: starting clean kernel', flush=True)
                executed = NotebookClient(nb, timeout=45, startup_timeout=20, kernel_name='python3',
                                          shutdown_kernel='immediate').execute(cwd=str(root))
                print('notebook-smoke: execution finished', flush=True)
            self.assertEqual(executed.cells[1].execution_count, 1)
            self.assertTrue(executed.cells[1].outputs)
            self.assertFalse(any(o.output_type == 'error' for o in executed.cells[1].outputs))
            nbformat.write(executed, notebook)
            result = render.render_plan(plan, notebook, root, 'train')
            self.assertEqual(result['added'], [])
            self.assertEqual(nbformat.read(notebook, as_version=4).cells[1].execution_count, 1)
            self.assertEqual(state.load_state(root)['stages']['train']['status'], 'pending')
            state.set_stage(root, 'train', 'complete', outcome='supported',
                            conclusions=['Clean-kernel synthetic checks verified in ml-project.ipynb; no quality claim.'])
            self.assertEqual(state.load_state(root)['stages']['train']['status'], 'complete')
