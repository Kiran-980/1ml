"""Prepare the local actor workspace and separately held evaluator labels."""
import hashlib
import argparse
import json
from pathlib import Path
import shutil
import sys
import venv

import pandas as pd
from sklearn.model_selection import train_test_split

TASK = Path(__file__).resolve().parent
ROOT = next(p for p in TASK.parents if (p / '.claude-plugin/plugin.json').is_file())
sys.path.insert(0, str(ROOT))
from evals.harness.storage import share_run_inputs, intern_input, share_frozen_plugin
RUN_ID = '2026-10-27-001'
RUN = TASK / 'work' / RUN_ID
EVALUATOR = TASK / 'evaluator' / RUN_ID


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2), encoding='utf-8')


def main():
    global RUN_ID, RUN, EVALUATOR
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', required=True)
    args = parser.parse_args()
    import re
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', args.run):
        parser.error('run must be a lowercase slug')
    RUN_ID = args.run
    RUN = TASK / 'work' / RUN_ID
    EVALUATOR = TASK / 'evaluator' / RUN_ID
    if RUN.exists() or EVALUATOR.exists():
        raise SystemExit('Preserve existing evidence: run or evaluator directory already exists')
    RUN.mkdir(parents=True)
    EVALUATOR.mkdir(parents=True)
    for folder in ('inputs/data', 'inputs/docs', 'agent/plans', 'models', 'submissions', 'reports'):
        (RUN / folder).mkdir(parents=True)
    train = pd.read_csv(TASK / 'data/original/train.csv')
    development, holdout = train_test_split(train, test_size=.2, stratify=train.Survived, random_state=20261027)
    development.to_csv(RUN / 'inputs/data/development.csv', index=False)
    holdout.to_csv(EVALUATOR / 'holdout.csv', index=False)
    shutil.copyfile(TASK / 'data/original/test.csv', RUN / 'inputs/data/test.csv')
    for p in (TASK / 'docs').glob('*.md'):
        shutil.copyfile(p, RUN / 'inputs/docs' / p.name)
    (RUN/'inputs/docs/index.md').write_text('# Competition documents\n\n' + '\n'.join(
        f'- [{p.name}]({p.name})' for p in sorted((RUN/'inputs/docs').glob('*.md'))), encoding='utf-8')
    share_run_inputs(RUN, TASK / 'static/inputs', ROOT)
    # Sealed labels stay in a separate evaluator source store, never actor inputs.
    intern_input(EVALUATOR / 'holdout.csv', TASK / 'static/evaluator', ROOT)
    for folder in ('skills', 'references', 'tools', 'rules', '.claude-plugin'):
        shutil.copytree(ROOT / folder, RUN / 'agent/plugin' / folder, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    shutil.copy2(ROOT / 'requirements.txt', RUN / 'agent/plugin/requirements.txt')
    share_frozen_plugin(RUN, ROOT/'evals/static/plugin-files', ROOT)
    shutil.copyfile(TASK/'task.md',RUN/'agent/task.md')
    for name in ('execute.ps1','run_checks.py'):
        shutil.copyfile(ROOT/'evals/harness'/name,RUN/'agent'/name)
    profile = {
        'source': 'inputs/data/development.csv', 'rows': len(development),
        'columns': {col: {'dtype': str(development[col].dtype),
                         'missing': int(development[col].isna().sum()),
                         'unique_nonmissing': int(development[col].nunique())} for col in development},
        'label_counts': {str(k): int(v) for k, v in development.Survived.value_counts().items()},
        'numeric_summary': development.describe().to_dict(),
        'note': 'Descriptive development facts only. Agent owns interpretation and modelling choices.'}
    write(RUN / 'inputs/development-profile.json', profile)
    config = {'run_id': RUN_ID, 'seed': 20261027, 'development_rows': len(development),
              'sealed_holdout_rows': len(holdout), 'evaluation_claim': 'Additional passengers from the competition population; not unseen families or causal effects',
              'metric': 'accuracy', 'submission_authorized': False,
              'prediction_contract': {'input': 'inputs/data/test.csv', 'id': 'PassengerId', 'target': 'Survived', 'values': [0, 1]},
              'benchmark_role': 'Repeated workflow regression on the original split; not a new independent generalization study',
              'authorship': 'Fresh Astra agent owns analysis and self-repairs; parent reviews only after completion',
              'budget': {'max_candidate_pipelines': 6, 'max_cv_folds': 3, 'max_workers': 2,
                         'hyperparameter_search': 'Optional within six candidates; include ablations and tuning trials',
                         'max_execution_calls':12,'cell_timeout_seconds':180,'worker_timeout_seconds':300},
              'notebook_requirements':{'pip_setup':True,'figures':True},
              'model': 'gpt-6-astra', 'reasoning_effort':'medium',
              'input_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (RUN/'inputs/data').glob('*.csv')},
              'plugin_sha256': {p.relative_to(RUN/'agent/plugin').as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in (RUN/'agent/plugin').rglob('*') if p.is_file()},
              'python': sys.version}
    import importlib.metadata
    config['available_package_versions'] = {name: importlib.metadata.version(name) for name in ['numpy', 'pandas', 'scikit-learn', 'joblib', 'matplotlib']}
    write(RUN / 'config.json', config)
    write(EVALUATOR / 'split.json', {'seed': 20261027, 'method': 'stratified random 20 percent holdout before actor invocation',
        'development_passenger_ids': development.PassengerId.tolist(), 'holdout_passenger_ids': holdout.PassengerId.tolist(),
        'source_sha256': hashlib.sha256((TASK/'data/original/train.csv').read_bytes()).hexdigest()})
    venv.EnvBuilder(with_pip=True, system_site_packages=True).create(RUN/'agent/environment')
    print(json.dumps({'run': str(RUN), 'development_rows': len(development), 'holdout_rows': len(holdout)}))


if __name__ == '__main__':
    main()
