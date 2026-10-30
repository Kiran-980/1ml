"""Prepare an empty-project delivery trial, never an actor-authored solution."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys

CASE = Path(__file__).resolve().parent
ROOT = CASE.parents[3]
sys.path.insert(0, str(ROOT))
from evals.harness.storage import share_run_inputs, share_frozen_plugin

def hashes(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', required=True)
    args = parser.parse_args()
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', args.run):
        raise ValueError('Expected run slug')
    trial = ROOT / 'evals/skills/trials/autonomous-delivery' / args.run
    if trial.exists():
        raise ValueError('Preserve existing trial')
    materials, project, evaluator = trial/'materials', trial/'project', trial/'evaluator'
    project.mkdir(parents=True)
    evaluator.mkdir()
    source = ROOT/'evals/kaggle/titanic/inputs'
    for name in ('data', 'docs'):
        shutil.copytree(source/name, materials/'inputs'/name, copy_function=shutil.copyfile)
    share_run_inputs(materials, ROOT/'evals/kaggle/titanic/static/inputs', ROOT)
    for name in ('skills', 'references', 'tools', 'rules', '.claude-plugin'):
        shutil.copytree(ROOT/name, materials/'agent/plugin'/name,
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    shutil.copyfile(ROOT/'requirements.txt', materials/'agent/plugin/requirements.txt')
    share_frozen_plugin(materials, ROOT/'evals/static/plugin-files', ROOT)
    shutil.copyfile(CASE/'task.md', trial/'task.md')
    (evaluator/'materials-before.json').write_text(json.dumps(hashes(materials), indent=2), encoding='utf-8')
    protected = {}
    for dataset in ('titanic', 'house-prices', 'store-item-demand', 'wholesale-customers'):
        folder = ROOT/'evals/kaggle'/dataset
        publication = json.loads((folder/'delivery-manifest.json').read_text())
        paths = publication['published_files'] + ['current-run.json', 'README.md', 'delivery-manifest.json']
        for relative in paths:
            path = folder/relative
            if path.is_file():
                protected[path.relative_to(ROOT).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    (evaluator/'existing-results-before.json').write_text(json.dumps(protected, indent=2), encoding='utf-8')
    criteria = {
        'model': 'gpt-6-astra', 'reasoning_effort': 'medium', 'initial_project_files': [],
        'scope': 'One fresh-agent instruction-following trial; no statistical reliability guarantee',
        'gates': [
            'Agent creates complete current root delivery without parent publication or repairs',
            'Notebook dependencies, source, model, predictions, metrics and tests are present and linked',
            'Notebook-only runs history contains a genuine earlier executed revision',
            'Changed source/dependencies have recoverable versions outside runs; unchanged data is shared',
            'Historical weights and full environment/project copies are not retained as history',
            'Current notebook replays from delivered location without authoring scaffolding',
            'Clean regeneration reproduces outputs without relying on retained weights or computation caches',
            'Lifecycle reasoning, relevant EDA/figures and evaluation claims match actual evidence',
            'Frozen materials and existing accepted dataset results remain unchanged',
            'No parent messages, edits or repairs after dispatch; no Kaggle submission']}
    (evaluator/'criteria.json').write_text(json.dumps(criteria, indent=2), encoding='utf-8')
    print(json.dumps({'trial': str(trial), 'project_initially_empty': not any(project.iterdir()),
                      'materials_files': len(hashes(materials))}, indent=2))

if __name__ == '__main__':
    main()
