"""Freeze and inspect a finished actor delivery without changing its files.

Run only after the actor reports completion. Scientific and history-restoration
review remain separate from these mechanical checks.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--trial', type=Path, required=True)
    args = parser.parse_args()
    trial = args.trial.resolve()
    project, evaluator = trial/'project', trial/'evaluator'
    snapshot = evaluator/'actor-completed-sha256.json'
    if snapshot.exists():
        raise ValueError('Preserve existing completion evidence')
    # Environment/cache files are not delivered analysis. Preserve their path
    # inventory separately so excluded directories cannot hide history clutter.
    runtime = {'.venv', 'venv', '__pycache__', '.ipynb_checkpoints', '.runtime'}
    all_files = sorted(p for p in project.rglob('*') if p.is_file())
    files = {p.relative_to(project).as_posix(): digest(p) for p in all_files
             if not runtime.intersection(p.relative_to(project).parts)}
    snapshot.write_text(json.dumps(files, indent=2), encoding='utf-8')
    (evaluator/'completed-inventory.json').write_text(json.dumps(
        [p.relative_to(project).as_posix() for p in all_files], indent=2), encoding='utf-8')
    manifest = json.loads((project/'reports/artifact-manifest.json').read_text(encoding='utf-8'))
    failures = []
    def check(condition, message):
        if not condition:
            failures.append(message)
    def artifact(relative):
        target = (project/relative).resolve()
        if not target.is_relative_to(project):
            raise ValueError('Artifact escapes actor project: '+str(relative))
        return target
    keys = ['notebook', 'requirements', 'model', 'predictions', 'metrics', 'test_results', 'history_manifest']
    for key in keys:
        check(key in manifest and artifact(manifest[key]).is_file(), 'Missing artifact: '+key)
    for name in manifest.get('supporting_modules', []):
        check(artifact(name).is_file(), 'Missing supporting module: '+name)
    notebook = artifact(manifest['notebook'])
    check(notebook.parent == project, 'Current notebook is not at project root')
    check(artifact(manifest['requirements']).parent == project, 'Requirements are not at project root')
    # The task requires appropriate project child folders, not fixed basenames.
    # Preserve conventional-name differences as observations, not false failures.
    layout_notes = []
    for key, folder in [('model','models'),('predictions','submissions'),('metrics','reports'),('test_results','reports')]:
        path = artifact(manifest[key])
        check(path.parent != project and not path.is_relative_to(project/'runs'),
              key+' must be in a current output folder outside notebook history')
        if not path.is_relative_to(project/folder):
            layout_notes.append(key+' uses '+path.relative_to(project).parts[0]+' instead of '+folder)
    history = [p for p in all_files if p.is_relative_to(project/'runs')]
    check(bool(history), 'Notebook history is empty')
    check(all(p.suffix == '.ipynb' for p in history), 'Non-notebook files in runs history')
    current = json.loads(notebook.read_text(encoding='utf-8'))
    code = [c for c in current['cells'] if c['cell_type'] == 'code']
    check(bool(code) and all(c.get('execution_count') is not None for c in code), 'Current code cells are not all executed')
    check(not any(o.get('output_type') == 'error' for c in code for o in c.get('outputs', [])), 'Current notebook retains error outputs')
    current_source = [(c['cell_type'], ''.join(c['source'])) for c in current['cells']]
    earlier = []
    for path in history:
        if path.suffix != '.ipynb':
            continue
        previous = json.loads(path.read_text(encoding='utf-8'))
        source = [(c['cell_type'], ''.join(c['source'])) for c in previous['cells']]
        previous_code = [c for c in previous['cells'] if c['cell_type'] == 'code']
        if source != current_source and previous_code and all(c.get('execution_count') is not None for c in previous_code):
            earlier.append(path.relative_to(project).as_posix())
    check(bool(earlier), 'No distinct executed earlier notebook revision')
    links = [link for c in current['cells'] if c['cell_type'] == 'markdown'
             for link in re.findall(r'\]\(([^)]+)\)', ''.join(c['source']))
             if not re.match(r'(?:https?://|#|mailto:)', link)]
    missing = [link for link in links if not (notebook.parent/unquote(link.split('#')[0])).exists()]
    check(not missing, 'Broken current notebook links: '+repr(missing))
    for manifest_name, base in [('materials-before.json',trial/'materials'),
                                ('existing-results-before.json',Path(__file__).resolve().parents[4])]:
        baseline = json.loads((evaluator/manifest_name).read_text())
        check(all((base/name).is_file() and digest(base/name) == sha for name, sha in baseline.items()),
              'Protected files changed: '+manifest_name)
    result = {'status': 'passed' if not failures else 'failed', 'failures': failures, 'layout_notes': layout_notes,
              'frozen_analysis_files': len(files), 'all_project_files': len(all_files),
              'executed_code_cells': len(code), 'relative_links': len(links),
              'earlier_executed_revisions': earlier, 'manifest': manifest,
              'scope': 'Mechanical inspection only; scientific review, standalone replay and history reconstruction remain required.'}
    (evaluator/'structure-check.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
