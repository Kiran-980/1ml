"""Retain notebooks and content-versioned reproduction evidence, not run clones.

Preparation is read-only with respect to the original project. Pruning is a
separate explicit operation after reviewing the exact retained/pruned manifest.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil

from .delivery import sha256

CACHE_PARTS = {'environment', 'runtime', '__pycache__', '.ipynb_checkpoints', 'cache'}
GENERATED_PARTS = {'models', 'submissions', 'assignments'}


def prepare_history(project, dataset):
    project, dataset = Path(project).resolve(), Path(dataset).resolve()
    if project.parent.parent != dataset or project.parent.name not in ('work', 'runs'):
        raise ValueError('Expected a direct dataset work/run project')
    evidence = dataset/'evaluator'/project.name
    archive = evidence/'notebook-history'
    archive.mkdir(parents=True, exist_ok=True)
    store = dataset/'static/history-files'
    records = {}
    for path in sorted(project.rglob('*')):
        if not path.is_file(): continue
        rel = path.relative_to(project)
        if set(rel.parts).intersection(CACHE_PARTS) or path.suffix == '.pyc': continue
        if not path.resolve().is_relative_to(project): raise ValueError('Escaping source alias')
        digest = sha256(path)
        record = {'sha256':digest, 'bytes':path.stat().st_size}
        if rel.parts[0] in GENERATED_PARTS or path.suffix in ('.joblib','.pkl','.pickle'):
            record['retention'] = 'regenerate from notebook; current published output retained separately'
        elif rel.parts[0] == 'reports' and path.suffix in ('.csv','.png','.svg','.parquet'):
            record['retention'] = 'generated diagnostic output; regenerate from notebook'
        elif path.suffix == '.ipynb':
            # Preserve distinct intermediate notebooks without full project clones.
            target = archive/path.name
            if target.exists() and sha256(target) != digest:
                target = archive/(path.stem+'-'+digest[:12]+path.suffix)
            if not target.exists(): shutil.copyfile(path,target)
            record.update(retention='notebook history', file=target.relative_to(dataset).as_posix())
        else:
            if rel.parts[:2] == ('agent','plugin'):
                target = dataset.parents[1]/'static/plugin-files'/digest/path.name
            elif rel.parts[0] == 'inputs':
                target = dataset/'static/inputs'/digest/path.name
            else:
                target = store/digest/path.name
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists(): shutil.copyfile(path,target)
            if sha256(target) != digest: raise ValueError('Archive identity conflict')
            record.update(retention='content version', file=os.path.relpath(target,dataset).replace('\\','/'))
        records[rel.as_posix()] = record
    result = {'project':str(project), 'dataset':str(dataset), 'state':'prepared; original project not removed',
              'restore':'Use retained file mappings to reconstruct a historical project. Models and generated tables require notebook execution.',
              'files':records, 'notebooks':str(archive)}
    (evidence/'history-manifest.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result


if __name__ == '__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--project',type=Path,required=True); parser.add_argument('--dataset',type=Path,required=True)
    a=parser.parse_args(); r=prepare_history(a.project,a.dataset)
    print(json.dumps({'project':r['project'],'files':len(r['files']),'state':r['state']}))
