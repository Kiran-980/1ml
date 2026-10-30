"""Publish a verified standalone project while preserving overwritten notebook edits.

Publication changes packaging only. Call after reviewing an agent's completed
work; it does not certify the analysis and never modifies its source project.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
from .delivery import stage_delivery, sha256
from .storage import unlink_alias


def publish(source, dataset, staging):
    source, dataset, staging = map(lambda p: Path(p).resolve(), (source, dataset, staging))
    if source.parent.name not in ('work', 'runs') or source.parent.parent != dataset:
        raise ValueError('Source must be this dataset work/run project')
    result = stage_delivery(source, staging)
    if result['broken_links']:
        raise ValueError('Resolve broken delivery links before publication')
    files = [p for p in staging.rglob('*') if p.is_file()]
    previous_path = dataset/'delivery-manifest.json'
    previous = json.loads(previous_path.read_text()) if previous_path.exists() else {}
    owned = set(previous.get('published_files', []))
    retained=[]
    def preserve(target):
        if target.suffix == '.ipynb':
            backup = dataset/'runs'/('saved-before-publication-'+sha256(target)[:12])/target.name
        elif target.relative_to(dataset).parts[0] in ('models','submissions','assignments'):
            retained.append({'path':target.relative_to(dataset).as_posix(),'sha256':sha256(target),'retention':'superseded generated output; regenerate from historical notebook'})
            return
        else:
            backup = dataset/'static/history-files'/sha256(target)/target.name
        backup.parent.mkdir(parents=True,exist_ok=True)
        if backup.exists() and sha256(backup) != sha256(target): raise ValueError('Preservation conflict')
        if not backup.exists(): shutil.copyfile(target,backup)
        retained.append({'path':target.relative_to(dataset).as_posix(),'sha256':sha256(target),'file':backup.relative_to(dataset).as_posix()})
    # Existing root notebooks can contain user-executed outputs. Preserve their
    # exact bytes before any replacement, even when cell sources are unchanged.
    for path in files:
        relative = path.relative_to(staging)
        target = dataset/relative
        if not target.resolve().is_relative_to(dataset): raise ValueError('Destination alias escapes dataset')
        if not target.exists() or sha256(target) == sha256(path):
            continue
        if target.suffix == '.ipynb' and len(relative.parts) == 1:
            preserve(target)
        elif relative.as_posix() not in owned and relative.as_posix() != 'delivery-manifest.json':
            raise ValueError(f'Unmanaged destination collision: {relative}')
        else:
            preserve(target)
    stale = owned - {p.relative_to(staging).as_posix() for p in files}
    for relative in stale:
        target=(dataset/relative).resolve()
        if not target.is_relative_to(dataset) or target==dataset: raise ValueError('Escaping managed file')
        if target.exists(): preserve(target)
    for path in files:
        relative = path.relative_to(staging)
        target = dataset/relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and sha256(target) == sha256(path):
            continue
        if target.exists():
            unlink_alias(target,dataset)
        # Inputs share immutable bytes; current results/source remain editable.
        if relative.parts[0] == 'inputs' and not os.access(path, os.W_OK):
            os.link(path, target)
        else:
            shutil.copyfile(path, target)
    for relative in stale:
        target=dataset/relative
        if target.exists(): unlink_alias(target,dataset)
    result['published_files'] = [p.relative_to(staging).as_posix() for p in files]
    result['previous_current_files'] = retained
    (dataset/'delivery-manifest.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    pointer_path = dataset/'current-run.json'
    pointer = json.loads(pointer_path.read_text()) if pointer_path.exists() else {}
    manifest = json.loads((dataset/'reports/artifact-manifest.json').read_text())
    pointer.update(run_id=source.name, notebook=manifest['notebook'], notebook_sha256=sha256(dataset/manifest['notebook']),
                   canonical_notebook=f'{source.parent.name}/{source.name}/'+json.loads((source/'reports/artifact-manifest.json').read_text())['notebook'],
                   model=manifest['model'], metrics=manifest['metrics'], predictions=manifest['predictions'],
                   execute_from='.', submission_authorized=False,
                   reading_copy_byte_identical=result['source_notebook_sha256']==result['delivered_notebook_sha256'],
                   packaging='Runnable root project; analytical code and saved outputs preserved')
    pointer_path.write_text(json.dumps(pointer, indent=2), encoding='utf-8')
    return result


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    for name in ('source','dataset','staging'): parser.add_argument('--'+name, type=Path, required=True)
    a=parser.parse_args(); r=publish(a.source,a.dataset,a.staging)
    print(json.dumps({'notebook':r['notebook'],'broken_links':r['broken_links'],'published_files':len(r['published_files'])}))
