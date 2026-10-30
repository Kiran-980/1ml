"""A delivered notebook must run from its user-facing root with valid links."""
import hashlib
import json
import os
from pathlib import Path
import stat
import tempfile
import unittest


class NotebookDeliveryTests(unittest.TestCase):
    def test_root_delivery_preserves_analysis_and_runs_without_agent_scaffolding(self):
        import nbformat
        from nbclient import NotebookClient
        from evals.harness.delivery import stage_delivery
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); source=root/'source'; delivered=root/'delivered'
            for name in ('notebooks','reports','models','inputs/data'):
                (source/name).mkdir(parents=True)
            (source/'requirements.txt').write_text('# standard-library-only fixture\n')
            (source/'model_support.py').write_text('VALUE = 42\n')
            (source/'config.json').write_text('{"seed":7}')
            (source/'inputs/data/example.txt').write_text('3')
            (source/'reports/metrics.json').write_text('{"value":45}')
            (source/'models/model.bin').write_bytes(b'fixture')
            (source/'reports/predictions.csv').write_text('id,value\n1,45\n')
            notebook=nbformat.v4.new_notebook(cells=[
                nbformat.v4.new_markdown_cell('[Metrics](../reports/metrics.json) and [source](../model_support.py)'),
                nbformat.v4.new_code_cell("import sys, subprocess, json\nfrom pathlib import Path\nsubprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])\nfrom model_support import VALUE\nanswer = VALUE + int(Path('inputs/data/example.txt').read_text())\nassert answer == 45\nPath('reports/replayed.json').write_text(json.dumps({'value': answer}))\nprint(answer)")])
            nbformat.write(notebook,source/'notebooks/example.ipynb')
            manifest={'notebook':'notebooks/example.ipynb','model':'models/model.bin','metrics':'reports/metrics.json',
                      'predictions':'reports/predictions.csv','requirements':'requirements.txt','supporting_modules':['model_support.py']}
            (source/'reports/artifact-manifest.json').write_text(json.dumps(manifest))
            before={p.relative_to(source).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in source.rglob('*') if p.is_file()}
            result=stage_delivery(source,delivered)
            self.assertTrue(result['analysis_code_and_outputs_preserved'])
            self.assertEqual(result['broken_links'],[])
            self.assertFalse((delivered/'agent').exists())
            nb=nbformat.read(delivered/'example.ipynb',as_version=4)
            NotebookClient(nb,timeout=60,resources={'metadata':{'path':str(delivered)}}).execute()
            self.assertEqual(json.loads((delivered/'reports/replayed.json').read_text()),{'value':45})
            self.assertFalse((source/'reports/replayed.json').exists())
            after={p.relative_to(source).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in source.rglob('*') if p.is_file()}
            self.assertEqual(before,after)


if __name__=='__main__': unittest.main()
