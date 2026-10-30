"""Reconstruct retained historical source in a new folder; never restore weights."""
import argparse
import json
from pathlib import Path
import shutil

from .delivery import sha256


def restore(manifest_path, destination):
    manifest_path=Path(manifest_path).resolve(); destination=Path(destination).resolve()
    record=json.loads(manifest_path.read_text(encoding='utf-8-sig'))
    dataset=Path(record['dataset']).resolve()
    if destination.exists(): raise ValueError('Restore destination must be new')
    # Verify every retained source before creating the destination.
    sources=[]
    for relative,item in record['files'].items():
        if 'file' not in item: continue
        target=(destination/relative).resolve()
        if not target.is_relative_to(destination) or target==destination: raise ValueError('Escaping restore target')
        source=(dataset/item['file']).resolve()
        if not source.is_relative_to(dataset.parents[1]): raise ValueError('Evidence outside evaluation area')
        if sha256(source)!=item['sha256']: raise ValueError('Historical file identity mismatch')
        sources.append((source,target))
    destination.mkdir(parents=True)
    for source,target in sources:
        target.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(source,target)
    for folder in ('models','reports','submissions','assignments'): (destination/folder).mkdir(exist_ok=True)
    return {'restored_files':len(sources),'destination':str(destination),'weights_restored':False,
            'next':'Use a compatible kernel, install retained requirements, and run the notebook from this restored project root. Evaluator runtime environments are not retained.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--manifest',type=Path,required=True); parser.add_argument('--destination',type=Path,required=True)
    args=parser.parse_args(); print(json.dumps(restore(args.manifest,args.destination),indent=2))
