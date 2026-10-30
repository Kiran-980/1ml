"""Build a standalone current project, not a notebook-only reading copy.

Staging never edits the completed actor. Immutable inputs may share bytes;
mutable outputs and custom source files are independent at the user location.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
from urllib.parse import unquote, urlsplit


def sha256(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def confined(root, relative):
    path=(root/relative).resolve()
    if not path.is_relative_to(root) or path==root:
        raise ValueError('Delivery artifact escapes source project')
    return path


def stage_delivery(source, destination):
    source=Path(source).resolve(); destination=Path(destination).resolve()
    if destination.exists(): raise ValueError('Preserve existing delivery: destination already exists')
    manifest=json.loads((source/'reports/artifact-manifest.json').read_text(encoding='utf-8'))
    notebook_path=confined(source,manifest['notebook'])
    original=json.loads(notebook_path.read_text(encoding='utf-8'))
    notebook=copy.deepcopy(original)
    destination.mkdir(parents=True)
    copied={}

    def transfer(path):
        path=path.resolve()
        if not path.is_relative_to(source): raise ValueError('Source link escapes project')
        relative=path.relative_to(source)
        if relative.parts[0]=='agent': return
        target=destination/relative
        target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists(): return
        if relative.parts[0]=='inputs' and not (path.stat().st_mode & stat.S_IWRITE):
            os.link(path,target)
            storage='immutable input alias'
        else:
            shutil.copyfile(path,target)
            storage='current project file'
        copied[relative.as_posix()]={'sha256':sha256(path),'storage':storage}

    for folder in ('inputs','models','reports','submissions','assignments','1ml'):
        for path in (source/folder).rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts and path.suffix!='.pyc': transfer(path)
    for path in source.iterdir():
        if path.is_file() and (path.suffix=='.py' or path.name in ('requirements.txt','config.json')): transfer(path)
    for key in ('model','predictions','metrics','requirements'):
        transfer(confined(source,manifest[key]))
    for relative in manifest.get('supporting_modules',[]): transfer(confined(source,relative))

    rewritten=[]; broken=[]
    def rewrite_link(match):
        value=match.group(1)
        parsed=urlsplit(value)
        if parsed.scheme or parsed.netloc or not parsed.path: return match.group(0)
        actual=(notebook_path.parent/unquote(parsed.path)).resolve()
        if not actual.is_relative_to(source):
            broken.append(value); return match.group(0)
        relative=Path(notebook_path.name) if actual==notebook_path else actual.relative_to(source)
        if actual.is_file() and actual!=notebook_path: transfer(actual)
        if not actual.is_file() or (actual != notebook_path and not (destination/relative).is_file()): broken.append(value)
        new=relative.as_posix()+('?' + parsed.query if parsed.query else '')+('#'+parsed.fragment if parsed.fragment else '')
        if new!=value: rewritten.append({'before':value,'after':new})
        return ']('+new+')'
    for cell in notebook['cells']:
        if cell['cell_type']=='markdown':
            text=''.join(cell['source']) if isinstance(cell['source'],list) else cell['source']
            cell['source']=re.sub(r'\]\(([^)]+)\)',rewrite_link,text)
    delivered_notebook=destination/notebook_path.name
    if notebook_path.parent == source and not rewritten:
        shutil.copyfile(notebook_path,delivered_notebook)
    else:
        delivered_notebook.write_text(json.dumps(notebook,ensure_ascii=False,indent=1)+'\n',encoding='utf-8')
    code=lambda nb:[c for c in nb['cells'] if c['cell_type']=='code']
    assert code(original)==code(notebook), 'Packaging changed analytical code or outputs'
    delivered_manifest=copy.deepcopy(manifest)
    delivered_manifest['notebook']=notebook_path.name
    delivered_manifest.pop('plans',None)
    delivered_manifest['execution']='Open the root notebook with a compatible Python kernel and run all cells from this project directory.'
    (destination/'reports/artifact-manifest.json').write_text(json.dumps(delivered_manifest,indent=2),encoding='utf-8')
    result={'source_notebook_sha256':sha256(notebook_path),'notebook':notebook_path.name,
            'delivered_notebook_sha256':sha256(delivered_notebook),'analysis_code_and_outputs_preserved':True,
            'markdown_links_rebased':rewritten,'broken_links':broken,'files':copied,
            'execution_root':'.','original_actor_modified':False}
    (destination/'delivery-manifest.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--source',type=Path,required=True); parser.add_argument('--destination',type=Path,required=True)
    args=parser.parse_args(); result=stage_delivery(args.source,args.destination)
    print(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2))
    raise SystemExit(bool(result['broken_links']))
