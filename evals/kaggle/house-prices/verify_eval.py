"""Score a reviewed, frozen actor bundle once; never train or repair it."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from datetime import datetime, timezone

TASK = Path(__file__).resolve().parent
ROOT = next(p for p in TASK.parents if (p / '.claude-plugin/plugin.json').is_file())
sys.path.insert(0, str(ROOT))
from evals.harness.notebook_server import local_path, input_csv_options
from evals.harness.regression_metrics import log_rmse, constant_log_prediction


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', required=True)
    args = parser.parse_args()
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', args.run):
        parser.error('Invalid run slug')
    run, evaluator = TASK / 'runs' / args.run, TASK / 'evaluator' / args.run
    report = evaluator / 'verification.json'
    marker = evaluator / 'scoring-started.json'
    if report.exists() or marker.exists():
        raise ValueError('Preserve the one-shot final-label evaluation; scoring already started')
    manifest = json.loads((run / 'reports/artifact-manifest.json').read_text())
    review = json.loads((evaluator / 'review.json').read_text())
    assert review['status'] in ('accepted', 'accepted_with_limitations'), 'Qualitative review has not accepted this bundle'
    paths = [manifest[k] for k in ('notebook', 'model', 'predictions', 'metrics', 'requirements')]
    paths += manifest.get('supporting_modules', [])
    hashes = {p: digest(local_path(run, p)) for p in paths}
    assert hashes == review['approved_sha256'], 'Artifacts changed after review'
    bundle = json.loads((run / 'reports/verify_bundle-feedback.json').read_text())
    execution = json.loads((run / 'reports/execute_notebook-feedback.json').read_text())
    assert bundle['status'] == execution['status'] == 'passed'
    assert bundle['artifact_sha256'] == hashes, 'Fresh-process checks are stale'
    assert execution['notebook_sha256'] == hashes[manifest['notebook']], 'Execution evidence is stale'
    config = json.loads((run / 'config.json').read_text())
    for relative, expected in config['input_sha256'].items():
        assert digest(local_path(run, relative)) == expected, f'Input changed: {relative}'
    for relative, expected in config['plugin_sha256'].items():
        assert digest(local_path(run / 'agent/plugin', relative)) == expected, f'Frozen plugin changed: {relative}'
    import joblib
    import nbformat
    import numpy as np
    import pandas as pd
    nb = nbformat.read(local_path(run, manifest['notebook']), as_version=4)
    code = [c for c in nb.cells if c.cell_type == 'code']
    assert code and all(c.execution_count is not None for c in code)
    assert not any(o.output_type == 'error' for c in code for o in c.outputs)
    frozen = {'run_id': run.name, 'sha256': hashes, 'started_at': datetime.now(timezone.utc).isoformat(),
              'review_sha256': digest(evaluator / 'review.json'), 'config_sha256': digest(run / 'config.json')}
    with marker.open('x', encoding='utf-8') as stream:
        json.dump(frozen, stream, indent=2)
    # No labels are opened until all prior gates and the immutable-score marker exist.
    split = json.loads((evaluator / 'split.json').read_text())
    assert digest(TASK / 'data/original/train.csv') == split['source_sha256']
    assert digest(evaluator / 'holdout.csv') == split['holdout_sha256']
    reader = input_csv_options(manifest)
    assert bundle.get('input_csv_options', {}) == reader, 'Verified parser contract changed'
    original = pd.read_csv(TASK / 'data/original/train.csv', **reader).set_index('Id')
    development = pd.read_csv(run / 'inputs/data/development.csv', **reader)
    holdout = pd.read_csv(evaluator / 'holdout.csv', **reader)
    assert development.Id.astype(str).tolist() == list(map(str, split['development_ids']))
    assert holdout.Id.astype(str).tolist() == list(map(str, split['holdout_ids']))
    assert set(development.Id).isdisjoint(holdout.Id)
    for frame in (development, holdout):
        pd.testing.assert_frame_equal(frame, original.loc[frame.Id].reset_index()[frame.columns], check_dtype=False)
    # Import actor modules without creating/updating bytecode in its frozen run.
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(run))
    model = joblib.load(local_path(run, manifest['model']))
    predicted = np.asarray(model.predict(holdout.drop(columns='SalePrice')))
    observed = holdout.SalePrice.to_numpy(dtype=float)
    score = log_rmse(observed, predicted)
    baseline = constant_log_prediction(development.SalePrice)
    baseline_score = log_rmse(holdout.SalePrice, np.full(len(holdout), baseline))
    pd.DataFrame({'Id': holdout.Id, 'SalePrice': predicted}).to_csv(evaluator / 'holdout-predictions.csv', index=False)
    result = {
        'status': 'verified', 'run_id': run.name, 'holdout_rows': len(holdout),
        'metric': 'sqrt(mean((ln(observed)-ln(predicted))**2))', 'holdout_log_rmse': score,
        'constant_baseline_log_rmse': baseline_score, 'constant_baseline_prediction': baseline,
        'holdout_mae': float(np.mean(np.abs(observed - predicted))),
        'executed_code_cells': len(code), 'submission_rows': bundle['rows'],
        'reload_prediction_parity': True, 'sha256': hashes,
        'submitted': False, 'kaggle_score': None, 'leaderboard_percentile': None,
        'authorship': 'Fresh Astra agent using frozen plugin files and execution tools',
        'parent_analysis_repairs': False, 'review_status': review['status'],
        'limitations': [
            'One familiar public dataset and one agent run; no controlled skill-versus-no-skill comparison.',
            'Random-row holdout does not establish future-market, geographic-transfer or causal performance.',
            'Native model subagent with file-based skill loading; not a test of installed plugin discovery.',
            'Workspace boundaries are instructed, not an OS security sandbox.',
        ],
    }
    save(report, result)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
