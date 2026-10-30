"""Execute a disposable standalone delivery; never overwrite completed results."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import traceback

from .delivery import stage_delivery

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--project',type=Path,required=True); parser.add_argument('--destination',type=Path,required=True)
    parser.add_argument('--evidence-dir',type=Path)
    a=parser.parse_args(); project=a.project.resolve(); destination=a.destination.resolve()
    out=a.evidence_dir.resolve() if a.evidence_dir else project.parents[1]/'evaluator'/project.name
    evidence=out/'user-replay.json'
    if evidence.exists(): raise ValueError('Preserve existing replay evidence')
    if a.evidence_dir:
        if not out.is_relative_to(project/'evaluator'): raise ValueError('Current-project evidence must remain in its evaluator directory')
        publication=json.loads((project/'delivery-manifest.json').read_text())
        original_hashes={p:hashlib.sha256((project/p).read_bytes()).hexdigest() for p in publication['published_files'] if (project/p).is_file()}
    else:
        original_hashes=json.loads((out/'completed-sha256.json').read_text())
    delivery=stage_delivery(project,destination)
    manifest=json.loads((destination/'reports/artifact-manifest.json').read_text())
    result={'status':'failed','project':str(project),'standalone_replay':str(destination),'broken_links':delivery['broken_links'],
            'hash_scope':'published current project' if a.evidence_dir else 'completed actor project',
            'original_actor_modified':False,'purpose':'Verify the delivered notebook in an ordinary clean kernel, without evaluator scaffolding; additional verification fits are separate from the actor run.'}
    runtime=destination.parent/(destination.name+'-runtime'); runtime.mkdir()
    os.environ['TEMP']=os.environ['TMP']=os.environ['JUPYTER_RUNTIME_DIR']=str(runtime)
    os.environ['PIP_DISABLE_PIP_VERSION_CHECK']='1'
    notebook=None
    try:
        assert not delivery['broken_links']
        import nbformat
        from nbclient import NotebookClient
        notebook=nbformat.read(destination/manifest['notebook'],as_version=4)
        NotebookClient(notebook,timeout=240,kernel_name='python3',resources={'metadata':{'path':str(destination)}}).execute()
        import numpy as np
        import pandas as pd
        original=pd.read_csv(project/manifest['predictions']); replay=pd.read_csv(destination/manifest['predictions'])
        assert original.columns.tolist()==replay.columns.tolist() and original.shape==replay.shape
        for column in original:
            if pd.api.types.is_numeric_dtype(original[column]): assert np.allclose(original[column],replay[column],rtol=1e-10,atol=1e-10)
            else: assert original[column].equals(replay[column])
        def same(x,y):
            if isinstance(x,dict):
                assert x.keys()==y.keys()
                for k in x:
                    if not any(part in k.lower() for part in ('seconds','elapsed','duration')): same(x[k],y[k])
            elif isinstance(x,list):
                assert len(x)==len(y)
                for l,r in zip(x,y): same(l,r)
            elif isinstance(x,(int,float)) and not isinstance(x,bool): assert np.isclose(x,y,rtol=1e-10,atol=1e-10)
            else: assert x==y
        same(json.loads((project/manifest['metrics']).read_text()),json.loads((destination/manifest['metrics']).read_text()))
        result.update(status='passed',executed_code_cells=sum(c.cell_type=='code' for c in notebook.cells),predictions_reproduced=True,scientific_metrics_reproduced=True)
    except Exception as exc:
        result.update(error_type=type(exc).__name__,error=str(exc),traceback=traceback.format_exc())
    finally:
        if notebook is not None:
            import nbformat
            nbformat.write(notebook,out/'user-replay.ipynb')
        result['actor_files_unchanged']=all(hashlib.sha256((project/p).read_bytes()).hexdigest()==h for p,h in original_hashes.items())
        assert result['actor_files_unchanged']
        evidence.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('error','traceback')},indent=2))
    raise SystemExit(result['status']!='passed')

if __name__=='__main__': main()
