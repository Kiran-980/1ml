"""Behavioral checks for automatic execution feedback, not for ML answers."""
import json
import importlib.util
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch
import subprocess
from evals.harness.notebook_server import call_worker, local_path, check_notebook_requirements

ROOT = Path(__file__).resolve().parents[1]
HAS_NOTEBOOK_RUNTIME = all(importlib.util.find_spec(name) is not None for name in (
    'IPython', 'nbclient', 'ipykernel', 'sklearn', 'psutil'))


class NotebookExecutorTests(unittest.TestCase):
    @unittest.skipUnless(importlib.util.find_spec('IPython'), 'Install requirements-test.txt for notebook gates')
    def test_required_pip_and_figures_need_executed_evidence(self):
        def cell(source, outputs=None, execution_count=1):
            return {'cell_type': 'code', 'source': source, 'outputs': outputs or [], 'execution_count': execution_count}
        requirements = {'pip_setup': True, 'figures': True}
        figure = {'output_type': 'display_data', 'data': {'image/png': 'encoded-test-image'}}
        with self.assertRaisesRegex(ValueError, 'pip setup'):
            check_notebook_requirements({'cells': [cell('# pip install pandas\nimport pandas', [figure])]}, requirements)
        with self.assertRaisesRegex(ValueError, 'before the first'):
            check_notebook_requirements({'cells': [cell('import pandas'), cell('%pip install pandas', [figure])]}, requirements)
        with self.assertRaisesRegex(ValueError, 'no figure outputs'):
            check_notebook_requirements({'cells': [cell('%pip install pandas')]}, requirements)
        with self.assertRaisesRegex(ValueError, 'pip setup'):
            check_notebook_requirements({'cells': [cell('%pip install pandas', [figure], None)]}, requirements)
        with self.assertRaisesRegex(ValueError, 'pip setup'):
            check_notebook_requirements({'cells': [cell('import sys, subprocess\nresult = subprocess.run([sys.executable, "-m", "pip", "install", "pandas"])\nif result.returncode != 0:\n    print("Install failed")', [figure])]}, requirements)
        for setup in ['%pip install pandas', 'import sys, subprocess\nsubprocess.check_call([sys.executable, "-m", "pip", "install", "pandas"])',
                      'import sys, subprocess\nfor pkg in ["pandas"]:\n    result = subprocess.run([sys.executable, "-m", "pip", "install", pkg], capture_output=True)\n    if result.returncode != 0:\n        raise RuntimeError("Installation failed")']:
            result = check_notebook_requirements({'cells': [cell(setup), cell('import pandas', [figure])]}, requirements)
            self.assertEqual(result['figure_outputs'], 1)
            self.assertTrue(result['pip_setup_detected'])

    @unittest.skipUnless(HAS_NOTEBOOK_RUNTIME, 'Install requirements-test.txt for clean-kernel checks')
    def test_parallel_training_returns_feedback_and_closes_kernel(self):
        import psutil
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            project, audit = base/'actor', base/'audit'
            (project/'reports').mkdir(parents=True)
            shutil.copytree(ROOT/'tools', project/'agent/plugin/tools', ignore=shutil.ignore_patterns('__pycache__'))
            (project/'reports/artifact-manifest.json').write_text(json.dumps({
                'notebook': 'notebooks/parallel.ipynb', 'plans': ['plan.json']}))
            source = """import os
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
X, y = load_iris(return_X_y=True)
scores = cross_val_score(RandomForestClassifier(n_estimators=5, n_jobs=1, random_state=1), X, y, cv=3, n_jobs=2)
assert len(scores) == 3
print('kernel_pid:', os.getpid())
"""
            (project/'plan.json').write_text(json.dumps({'stage': 'train', 'cells': [
                {'id': 'parallel-training', 'type': 'code', 'source': source}]}))
            original_run = subprocess.run
            def bounded_run(*args, **kwargs):
                kwargs['timeout'] = 45
                return original_run(*args, **kwargs)
            with patch('evals.harness.notebook_server.subprocess.run', side_effect=bounded_run):
                result = call_worker(project, audit, Path(sys.executable), 'execute_notebook')
            worker_result = json.loads((audit/'call-01/result.json').read_text())
            self.assertEqual(worker_result['status'], 'passed', worker_result)
            self.assertEqual(result['status'], 'passed', result)
            output = result['cells'][0]['output']
            pid = int(output.split('kernel_pid:')[1].strip().split()[0])
            self.assertFalse(psutil.pid_exists(pid), f'Kernel {pid} survived completed execution')

    def test_manifest_cannot_escape_workspace(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                local_path(Path(directory), '../private.csv')
            with self.assertRaises(ValueError):
                local_path(Path(directory), str(Path(directory).resolve()/'absolute.csv'))

    @unittest.skipUnless(HAS_NOTEBOOK_RUNTIME, 'Install requirements-test.txt for clean-kernel checks')
    def test_failure_feedback_then_corrected_clean_execution_keeps_original(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            project, audit = base/'actor', base/'audit'
            (project/'reports').mkdir(parents=True)
            shutil.copytree(ROOT/'tools', project/'agent/plugin/tools', ignore=shutil.ignore_patterns('__pycache__'))
            manifest = {'notebook': 'notebooks/task-selected-name.ipynb', 'plans': ['plan.json']}
            (project/'reports/artifact-manifest.json').write_text(json.dumps(manifest))
            def plan(source):
                (project/'plan.json').write_text(json.dumps({'stage': 'data', 'cells': [
                    {'id': 'check', 'type': 'code', 'source': source}]}))
            plan("raise ValueError('observed failure boundary')")
            failed = call_worker(project, audit, Path(sys.executable), 'execute_notebook')
            self.assertEqual(failed['status'], 'failed', failed)
            self.assertIn('observed failure boundary', failed['error'])
            plan("import sys, subprocess\nsubprocess.check_call([sys.executable, '-m', 'pip', 'install', '--no-index', 'pip'])\nprint('active-kernel-pip:', sys.executable)\nassert 2 + 2 == 4")
            passed = call_worker(project, audit, Path(sys.executable), 'execute_notebook')
            self.assertEqual(passed['status'], 'passed', passed)
            self.assertIn('active-kernel-pip:', passed['cells'][0]['output'])
            self.assertEqual(passed['cells'][0]['execution_count'], 1)
            self.assertTrue((audit/'call-02/previous.ipynb').is_file())
            self.assertEqual(json.loads((audit/'call-01/result.json').read_text())['status'], 'failed')
            self.assertTrue((project/manifest['notebook']).is_file())


if __name__ == '__main__':
    unittest.main()
