"""Maintainer-only MCP notebook executor. It supplies execution, never ML solutions.

Runs trusted agent-authored code locally with a clean environment and bounded time.
File-path confinement is not an OS sandbox for executed Python. Credentials and
evaluator labels are not included in tool inputs or the kernel environment.
"""
import argparse
import ast
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import traceback


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding='utf-8')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_notebook_requirements(nb, requirements):
    """Mechanical evidence gates, not a judgment of EDA or scientific quality."""
    from IPython.core.inputtransformer2 import TransformerManager
    transformer = TransformerManager()
    installs, imports, figures = [], [], 0
    for index, cell in enumerate(nb['cells']):
        if cell['cell_type'] != 'code' or cell.get('execution_count') is None:
            continue
        source = cell['source']
        if isinstance(source, list):
            source = ''.join(source)
        tree = ast.parse(transformer.transform_cell(source))
        guarded_results = set()
        for branch in ast.walk(tree):
            if not isinstance(branch, ast.If) or not isinstance(branch.test, ast.Compare):
                continue
            test = branch.test
            if (isinstance(test.left, ast.Attribute) and test.left.attr == 'returncode'
                    and isinstance(test.left.value, ast.Name) and len(test.ops) == 1
                    and isinstance(test.ops[0], ast.NotEq) and len(test.comparators) == 1
                    and isinstance(test.comparators[0], ast.Constant) and test.comparators[0].value == 0
                    and any(isinstance(n, ast.Raise) for statement in branch.body for n in ast.walk(statement))):
                guarded_results.add(test.left.value.id)
        guarded_calls = {id(n.value) for n in ast.walk(tree) if isinstance(n, ast.Assign)
                         and any(isinstance(t, ast.Name) and t.id in guarded_results for t in n.targets)}
        for statement in tree.body:
            if isinstance(statement, (ast.Import, ast.ImportFrom)):
                names = [a.name for a in statement.names] if isinstance(statement, ast.Import) else [statement.module or '']
                if any(n.split('.')[0] not in sys.stdlib_module_names for n in names):
                    imports.append((index, statement.lineno))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                continue
            args = node.args
            magic = (node.func.attr == 'run_line_magic' and len(args) >= 2
                     and isinstance(args[0], ast.Constant) and args[0].value == 'pip'
                     and isinstance(args[1], ast.Constant) and str(args[1].value).lstrip().startswith('install '))
            command = []
            if args and isinstance(args[0], (ast.List, ast.Tuple)):
                command = [a.value if isinstance(a, ast.Constant) else ast.unparse(a) for a in args[0].elts]
            checked = node.func.attr == 'check_call' or (node.func.attr == 'run' and (id(node) in guarded_calls or any(
                k.arg == 'check' and isinstance(k.value, ast.Constant) and k.value.value is True for k in node.keywords)))
            subprocess_pip = checked and command[:4] == ['sys.executable', '-m', 'pip', 'install']
            if magic or subprocess_pip:
                installs.append((index, node.lineno))
        for output in cell.get('outputs', []):
            figures += int(any(value and (mime.startswith('image/') or mime in (
                'application/vnd.plotly.v1+json', 'application/vnd.vegalite.v5+json'))
                for mime, value in output.get('data', {}).items()))
    if requirements.get('pip_setup'):
        if not installs:
            raise ValueError('Notebook requires an executed active-kernel pip setup cell before third-party imports; requirements.txt alone is insufficient. Use %pip install or subprocess.check_call([sys.executable, "-m", "pip", "install", ...]).')
        if imports and min(imports) < min(installs):
            raise ValueError('Move active-kernel pip installation before the first third-party import, then rerun cleanly.')
    if requirements.get('figures') and figures == 0:
        raise ValueError('Notebook requires rendered EDA figures with interpretations; no figure outputs were saved. Plot-library imports and printed tables do not meet this requirement.')
    return {'pip_setup_detected': bool(installs), 'figure_outputs': figures,
            'scientific_quality': 'requires separate review'}


def local_path(root, name):
    if not isinstance(name, str) or not name or Path(name).is_absolute():
        raise ValueError('Artifact paths must be nonempty relative paths')
    target = (root / name).resolve()
    if not target.is_relative_to(root.resolve()):
        raise ValueError('Artifact path escapes workspace')
    return target


def input_csv_options(manifest):
    """Actor-declared parsing contract; no row filtering or alternate source paths."""
    options = manifest.get('input_csv_options', {})
    if not isinstance(options, dict) or set(options) - {'keep_default_na', 'na_values', 'dtype'}:
        raise ValueError('Unsupported input_csv_options; only null-token and dtype declarations are allowed')
    return options


def clean_env(runtime):
    keep = {'SYSTEMROOT', 'WINDIR', 'COMSPEC', 'PATH', 'PATHEXT', 'USERPROFILE', 'APPDATA', 'LOCALAPPDATA', 'PROGRAMDATA', 'PROGRAMFILES', 'PROGRAMFILES(X86)', 'HOMEDRIVE', 'HOMEPATH'}
    env = {k: v for k, v in os.environ.items() if k.upper() in keep}
    env.update(TEMP=str(runtime), TMP=str(runtime), TMPDIR=str(runtime),
               JUPYTER_RUNTIME_DIR=str(runtime), IPYTHONDIR=str(runtime/'ipython'),
               PYTHONUTF8='1', OMP_NUM_THREADS='2', OPENBLAS_NUM_THREADS='2', MKL_NUM_THREADS='2',
               PIP_CONFIG_FILE=os.devnull, PIP_NO_INPUT='1', PIP_DISABLE_PIP_VERSION_CHECK='1',
               PIP_CACHE_DIR=str(runtime/'pip-cache'))
    return env


def execute(root, audit, python, operation):
    """Worker process: fresh imports for both notebook execution and model reload."""
    manifest = json.loads((root/'reports/artifact-manifest.json').read_text(encoding='utf-8'))
    notebook = local_path(root, manifest['notebook'])
    if notebook.suffix != '.ipynb':
        raise ValueError('notebook must name an .ipynb file')
    if operation == 'verify_bundle':
        import joblib
        import nbformat
        import numpy as np
        import pandas as pd
        from sklearn.pipeline import Pipeline
        from sklearn.compose import TransformedTargetRegressor
        config = json.loads((root/'config.json').read_text())
        contract = config['prediction_contract']
        task = contract.get('task', 'classification' if 'values' in contract else None)
        notebook_checks = check_notebook_requirements(
            nbformat.read(notebook, as_version=4), config.get('notebook_requirements', {}))
        requirements_path = local_path(root, manifest['requirements'])
        if not requirements_path.read_text(encoding='utf-8').strip():
            raise ValueError('Requirements specification is empty')
        sys.path.insert(0, str(root))
        model = joblib.load(local_path(root, manifest['model']))
        preprocessing_owner = model
        while isinstance(preprocessing_owner, TransformedTargetRegressor):
            preprocessing_owner = getattr(preprocessing_owner, 'regressor_', None)
        if task in ('forecasting', 'clustering'):
            if task == 'forecasting' and not callable(getattr(model, 'predict', None)):
                raise ValueError('Forecast bundle must provide predict(raw_future_dataframe)')
        elif not isinstance(preprocessing_owner, Pipeline):
            raise ValueError('Expected a complete fitted sklearn Pipeline')
        features = pd.read_csv(local_path(root, contract['input']), **input_csv_options(manifest))
        saved = pd.read_csv(local_path(root, manifest['predictions']))
        assert list(saved.columns) == [contract['id'], contract['target']], 'Prediction schema mismatch'
        assert len(saved) == len(features), 'Prediction row count mismatch'
        assert saved[contract['id']].is_unique, 'Duplicate prediction IDs'
        saved_ids = pd.read_csv(local_path(root, manifest['predictions']), dtype={contract['id']: str}, keep_default_na=False)[contract['id']]
        assert saved_ids.tolist() == features[contract['id']].astype(str).tolist(), 'Prediction row order mismatch'
        assignment_mode = manifest.get('assignment_mode') if task == 'clustering' else None
        if task == 'clustering' and assignment_mode == 'transductive':
            if manifest.get('fit_input_sha256') != digest(local_path(root, contract['input'])):
                raise ValueError('Transductive input fingerprint does not match the fitted population')
            label_owner = model.steps[-1][1] if isinstance(model, Pipeline) else model
            if not hasattr(label_owner, 'labels_'):
                raise ValueError('Transductive bundle must expose fitted labels_')
            predicted = np.asarray(label_owner.labels_)
        else:
            if task == 'clustering' and assignment_mode != 'predict':
                raise ValueError('Clustering assignment_mode must be predict or transductive')
            if not callable(getattr(model, 'predict', None)):
                raise ValueError('Predictive bundle must provide predict(raw_dataframe)')
            predicted = np.asarray(model.predict(features))
        values = saved[contract['target']]
        assert predicted.shape == values.to_numpy().shape, 'Prediction shape mismatch'
        if task == 'classification':
            assert values.isin(contract['values']).all(), 'Invalid prediction values'
            assert np.array_equal(predicted, values.to_numpy()), 'Fresh-process prediction mismatch'
        elif task == 'clustering':
            for candidate in (values, pd.Series(predicted)):
                assert pd.api.types.is_numeric_dtype(candidate) and not pd.api.types.is_bool_dtype(candidate), 'Cluster labels must be numeric integers'
                array = candidate.to_numpy()
                assert np.isfinite(array).all() and np.equal(array, np.floor(array)).all() and (array >= -1).all(), 'Cluster labels must be finite integers >= -1'
            assert np.array_equal(predicted, values.to_numpy()), 'Fresh-process prediction mismatch'
        elif task in ('regression', 'forecasting'):
            for candidate in (values, pd.Series(predicted)):
                assert pd.api.types.is_numeric_dtype(candidate) and not pd.api.types.is_bool_dtype(candidate), 'Regression predictions must be numeric'
                assert np.isfinite(candidate.to_numpy()).all(), 'Regression predictions must be finite'
                if 'minimum' in contract:
                    assert (candidate >= contract['minimum']).all(), 'Regression prediction below minimum'
                if 'minimum_exclusive' in contract:
                    assert (candidate > contract['minimum_exclusive']).all(), 'Regression prediction outside strict minimum'
                if 'maximum' in contract:
                    assert (candidate <= contract['maximum']).all(), 'Regression prediction above maximum'
            # CSV serialization and floating-point reduction may alter last bits.
            assert np.allclose(predicted, values.to_numpy(), rtol=1e-10, atol=1e-12), 'Fresh-process prediction mismatch'
        else:
            raise ValueError('Prediction contract must declare a supported task')
        metrics = json.loads(local_path(root, manifest['metrics']).read_text())
        if not isinstance(metrics, dict) or not metrics:
            raise ValueError('Missing machine-readable metrics')
        paths = [manifest[k] for k in ('notebook', 'model', 'predictions', 'metrics', 'requirements')]
        paths += manifest.get('supporting_modules', [])
        return {'status': 'passed', 'operation': operation, 'rows': len(saved),
                'artifact_sha256': {p: digest(local_path(root, p)) for p in paths},
                'fresh_process': True, 'holdout_accessed': False, 'notebook_checks': notebook_checks,
                'prediction_task': task, 'input_csv_options': input_csv_options(manifest),
                'assignment_mode': assignment_mode,
                'predict_api_checked': task == 'clustering' and assignment_mode == 'predict',
                'new_row_prediction_checked': False,
                'parity_tolerance': {'rtol': 1e-10, 'atol': 1e-12} if task in ('regression', 'forecasting') else 'exact'}

    import nbformat
    from nbclient import NotebookClient
    from jupyter_client import KernelManager
    sys.path.insert(0, str(root/'agent/plugin/tools'))
    import render
    import state
    if not (root/'1ml/state.json').exists():
        state.init_project(root, name=root.name, notebook=manifest['notebook'], goal='Agent-controlled offline evaluation')
    if notebook.exists():
        shutil.copy2(notebook, audit/'previous.ipynb')
    rendered = audit/'rendered.ipynb'
    for index, path in enumerate(manifest['plans']):
        plan_path = local_path(root, path)
        plan = json.loads(plan_path.read_text(encoding='utf-8'))
        shutil.copy2(plan_path, audit/f'plan-{index:02d}.json')
        render.render_plan(plan, rendered, root, plan['stage'])
    nb = nbformat.read(rendered, as_version=4)
    km = KernelManager(kernel_name='python3')
    km.kernel_spec.argv = [str(python), '-m', 'ipykernel_launcher', '-f', '{connection_file}']
    started = time.monotonic()
    status, error = 'passed', None
    try:
        NotebookClient(nb, km=km, timeout=180, startup_timeout=30, allow_errors=False,
                       resources={'metadata': {'path': str(root)}}).execute(
                           env=clean_env(audit/'runtime'), cleanup_kc=True)
    except Exception as exc:
        status, error = 'failed', f'{type(exc).__name__}: {exc}'
    notebook.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(nb, notebook)
    shutil.copy2(notebook, audit/'executed.ipynb')
    cells = []
    for cell in nb.cells:
        if cell.cell_type != 'code':
            continue
        output = []
        for value in cell.outputs:
            if value.output_type == 'stream':
                output.append(value.text)
            elif value.output_type in ('display_data', 'execute_result'):
                output.append(value.get('data', {}).get('text/plain', ''))
            elif value.output_type == 'error':
                output.append('\n'.join(value.traceback))
        cells.append({'id': cell.get('id'), 'execution_count': cell.execution_count,
                      'output': '\n'.join(output)[-3500:]})
    return {'status': status, 'operation': operation, 'error': error[-9000:] if error else None,
            'seconds': time.monotonic()-started, 'notebook': manifest['notebook'],
            'notebook_sha256': digest(notebook), 'cells': cells, 'holdout_accessed': False}


def call_worker(root, audit_root, python, operation):
    if operation not in ('execute_notebook', 'verify_bundle'):
        raise ValueError('Unknown operation')
    audit_root.mkdir(parents=True, exist_ok=True)
    number = len(list(audit_root.glob('call-*'))) + 1
    if number > 12:
        return {'status': 'blocked', 'error': 'Execution-call budget exhausted'}
    audit = audit_root/f'call-{number:02d}'
    (audit/'runtime').mkdir(parents=True)
    command = [str(python), '-X', 'utf8', str(Path(__file__).resolve()), '--worker', operation,
               '--root', str(root), '--audit', str(audit), '--python', str(python)]
    # The venv inherits installed harness libraries, while pip targets this venv.
    try:
        result = subprocess.run(command, cwd=root, env=clean_env(audit/'runtime'),
                                capture_output=True, text=True, encoding='utf-8', timeout=300)
        (audit/'worker.stdout.log').write_text(result.stdout, encoding='utf-8')
        (audit/'worker.stderr.log').write_text(result.stderr, encoding='utf-8')
        response = json.loads((audit/'result.json').read_text()) if (audit/'result.json').exists() else {
            'status': 'failed', 'error': result.stderr[-6000:], 'exit_code': result.returncode}
    except subprocess.TimeoutExpired as exc:
        response = {'status': 'failed', 'error': 'Worker exceeded 300 seconds', 'operation': operation}
        save(audit/'timeout.json', response)
    save(root/f'reports/{operation}-feedback.json', response)
    return response


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--audit', type=Path, required=True)
    parser.add_argument('--python', type=Path, default=Path(sys.executable))
    parser.add_argument('--worker', choices=['execute_notebook', 'verify_bundle'])
    args = parser.parse_args()
    root, audit, python = args.root.resolve(), args.audit.resolve(), args.python.resolve()
    if args.worker:
        try:
            result = execute(root, audit, python, args.worker)
        except Exception:
            result = {'status': 'failed', 'operation': args.worker, 'error': traceback.format_exc()[-10000:]}
        save(audit/'result.json', result)
        return
    from mcp.server.mcpserver import MCPServer
    server = MCPServer('ML evaluation execution', instructions='Execute your saved cell plans and inspect actual results. No model choices or repairs are supplied.', log_level='WARNING')

    @server.tool()
    def execute_notebook() -> dict:
        """Render reports/artifact-manifest.json plans and run the full notebook in a clean project kernel. Returns outputs/errors; preserves every version. Repair your files and call again on failure. Package installation cells run in the project venv. Does not read evaluator holdout."""
        return call_worker(root, audit, python, 'execute_notebook')

    @server.tool()
    def verify_bundle() -> dict:
        """Reload the manifest model in a fresh process and verify raw-input prediction parity, CSV schema/order and metrics. Call after successful notebook execution. Returns failures for you to repair; never reveals final holdout scores."""
        return call_worker(root, audit, python, 'verify_bundle')

    server.run(transport='stdio')


if __name__ == '__main__':
    main()
