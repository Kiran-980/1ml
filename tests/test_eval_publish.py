import json
from pathlib import Path
import stat
import tempfile
import unittest

from evals.harness.publish import publish

class PublishTests(unittest.TestCase):
    def test_changed_project_preserves_notebook_edits_and_replaces_only_owned_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); dataset=root/'dataset'
            def project(name):
                p=dataset/'work'/name
                for d in ('reports','models','submissions','inputs'): (p/d).mkdir(parents=True)
                (p/(name+'.ipynb')).write_text(json.dumps({'cells':[{'cell_type':'code','source':'print(1)','outputs':[]}]}))
                (p/'requirements.txt').write_text('# '+name)
                (p/'inputs/data.csv').write_text('id\n'+name)
                (p/'inputs/data.csv').chmod(stat.S_IREAD)
                (p/'models'/('model-'+name+'.joblib')).write_bytes(name.encode())
                (p/'submissions/predictions.csv').write_text('id,value\n1,2')
                (p/'reports/metrics.json').write_text(json.dumps({'run':name}))
                (p/'reports/artifact-manifest.json').write_text(json.dumps({'notebook':name+'.ipynb','model':'models/model-'+name+'.joblib','predictions':'submissions/predictions.csv','metrics':'reports/metrics.json','requirements':'requirements.txt'}))
                return p
            first=project('first'); publish(first,dataset,root/'stage1')
            self.assertEqual((first/'first.ipynb').read_bytes(),(dataset/'first.ipynb').read_bytes())
            changed=(dataset/'first.ipynb').read_text()+'\n'
            (dataset/'first.ipynb').write_text(changed)
            (dataset/'user-note.txt').write_text('keep')
            second=project('second'); publish(second,dataset,root/'stage2')
            self.assertFalse((dataset/'first.ipynb').exists())
            self.assertEqual(next((dataset/'runs').glob('*/*.ipynb')).read_text(),changed)
            self.assertFalse((dataset/'models/model-first.joblib').exists())
            self.assertEqual((dataset/'models/model-second.joblib').read_bytes(),b'second')
            self.assertEqual((dataset/'inputs/data.csv').read_text(),'id\nsecond')
            self.assertFalse(first.joinpath('inputs/data.csv').stat().st_mode & stat.S_IWRITE)
            self.assertEqual((dataset/'user-note.txt').read_text(),'keep')
            # TemporaryDirectory cleanup can clear these fixture-only attributes.
            for p in root.rglob('*'):
                if p.is_file(): p.chmod(stat.S_IREAD|stat.S_IWRITE)

if __name__=='__main__': unittest.main()
