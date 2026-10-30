"""Source identity and immutability checks for evaluation input deduplication."""
import os
import importlib.util
import json
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch

from evals.harness.storage import intern_input, share_run_inputs, sha256


class InputStorageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.store = self.root / 'static'

    def tearDown(self):
        for path in self.root.rglob('*'):
            if path.is_file():
                path.chmod(stat.S_IREAD | stat.S_IWRITE)
        self.temp.cleanup()

    def source(self, relative, content=b'id,value\n1,2\n'):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return path

    def test_unchanged_inputs_share_storage_and_keep_bytes(self):
        first = self.source('run1/inputs/data/example.csv')
        second = self.source('run2/inputs/data/example.csv')
        expected = sha256(first)
        a = intern_input(first, self.store, self.root)
        b = intern_input(second, self.store, self.root)
        self.assertEqual(a['static'], b['static'])
        self.assertTrue(os.path.samefile(first, second))
        self.assertEqual(sha256(second), expected)
        self.assertFalse(first.stat().st_mode & stat.S_IWRITE)
        self.assertEqual(intern_input(first, self.store, self.root)['sha256'], expected)

    def test_changed_input_creates_version_without_changing_history(self):
        first = self.source('run1/data.csv', b'old')
        second = self.source('run2/data.csv', b'new')
        a = intern_input(first, self.store, self.root)
        b = intern_input(second, self.store, self.root)
        self.assertNotEqual(a['static'], b['static'])
        self.assertFalse(os.path.samefile(first, second))
        self.assertEqual(first.read_bytes(), b'old')
        self.assertEqual(second.read_bytes(), b'new')

    def test_frozen_plugin_aliases_share_bytes_without_linking_editable_source(self):
        from evals.harness.storage import share_frozen_plugin
        editable=self.source('skills/explore/SKILL.md',b'original instruction')
        first=self.source('run1/agent/plugin/skills/explore/SKILL.md',editable.read_bytes())
        second=self.source('run2/agent/plugin/skills/explore/SKILL.md',editable.read_bytes())
        share_frozen_plugin(self.root/'run1',self.store,self.root)
        share_frozen_plugin(self.root/'run2',self.store,self.root)
        self.assertTrue(os.path.samefile(first,second))
        self.assertFalse(os.path.samefile(editable,first))
        editable.write_bytes(b'updated instruction')
        self.assertEqual(first.read_bytes(),b'original instruction')
        self.assertEqual(second.read_bytes(),b'original instruction')
        self.assertTrue((self.root/'run1/agent/plugin-storage.json').is_file())

    def test_escape_rejected_before_mutation(self):
        file = self.source('safe/input.csv')
        with self.assertRaises(ValueError):
            intern_input(file, self.root.parent / 'outside-store', self.root)
        self.assertEqual(file.read_bytes(), b'id,value\n1,2\n')

    def test_failed_link_preserves_original_input(self):
        file = self.source('run/data.csv', b'original')
        with patch('evals.harness.storage.os.link', side_effect=PermissionError('link denied')):
            with self.assertRaisesRegex(PermissionError, 'link denied'):
                intern_input(file, self.store, self.root)
        self.assertEqual(file.read_bytes(), b'original')
        self.assertEqual(list(file.parent.glob('*.link')), [])

    def test_corrupt_static_version_is_rejected(self):
        file = self.source('run/data.csv', b'original')
        canonical = self.store / sha256(file) / file.name
        canonical.parent.mkdir(parents=True)
        canonical.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'identity mismatch'):
            intern_input(file, self.store, self.root)
        self.assertEqual(file.read_bytes(), b'original')

    def test_run_manifest_excludes_generated_outputs(self):
        source = self.source('run/inputs/data/train.csv')
        model = self.source('run/models/model.joblib', b'model')
        notebook = self.source('run/notebooks/example.ipynb', b'notebook')
        records = share_run_inputs(self.root / 'run', self.store, self.root)
        self.assertEqual([r['path'] for r in records], ['inputs/data/train.csv'])
        self.assertEqual(model.read_bytes(), b'model')
        self.assertEqual(notebook.read_bytes(), b'notebook')
        self.assertTrue((self.root / 'run/inputs/storage.json').exists())
        self.assertEqual(source.read_bytes(), b'id,value\n1,2\n')

    @unittest.skipUnless(importlib.util.find_spec('pandas') and importlib.util.find_spec('sklearn'), 'Optional evaluation dependencies unavailable')
    def test_prepare_shares_inputs_across_runs_even_with_readonly_sources(self):
        script = Path(__file__).resolve().parents[1] / 'evals/kaggle/titanic/prepare_eval.py'
        spec = importlib.util.spec_from_file_location('prepare_storage_test', script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        task = self.root / 'kaggle/titanic'
        for folder in ('skills', 'references', 'tools', 'rules', '.claude-plugin'):
            self.source(folder + '/fixture.txt', b'plugin fixture')
        self.source('requirements.txt', b'')
        self.source('kaggle/titanic/task.md', b'# fixture task')
        self.source('evals/harness/execute.ps1', b'# fixture helper')
        self.source('evals/harness/run_checks.py', b'# fixture helper')
        csv = 'PassengerId,Survived,Age\n' + ''.join(f'{i},{i % 2},30\n' for i in range(1, 21))
        self.source('kaggle/titanic/data/original/train.csv', csv.encode())
        test = self.source('kaggle/titanic/data/original/test.csv', b'PassengerId,Age\n21,30\n')
        test.chmod(stat.S_IREAD)
        doc = self.source('kaggle/titanic/docs/description.md', b'# source')
        doc.chmod(stat.S_IREAD)
        module.TASK, module.ROOT = task, self.root
        for name in ('first', 'second'):
            with patch('sys.argv', [str(script), '--run', name]), patch.object(module.venv.EnvBuilder,'create'):
                module.main()
        for relative in ('inputs/data/development.csv', 'inputs/data/test.csv', 'inputs/docs/description.md'):
            a, b = task / 'work/first' / relative, task / 'work/second' / relative
            self.assertTrue(os.path.samefile(a, b))
        first_config = json.loads((task / 'work/first/config.json').read_text())
        self.assertEqual(first_config['input_sha256']['test.csv'], sha256(test))
        self.assertTrue(os.path.samefile(task / 'evaluator/first/holdout.csv', task / 'evaluator/second/holdout.csv'))
        self.assertFalse((task / 'work/first/inputs/data/holdout.csv').exists())


if __name__ == '__main__':
    unittest.main()
