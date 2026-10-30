"""Copy into a competition run's agent folder; execution feedback only."""
import argparse
import json
from pathlib import Path
import sys

run = Path(__file__).resolve().parents[1]
repository = run.parents[4]
sys.path.insert(0, str(repository))
from evals.harness.notebook_server import call_worker

parser = argparse.ArgumentParser()
parser.add_argument('operation', choices=['execute_notebook', 'verify_bundle'])
args = parser.parse_args()
result = call_worker(run, run.parents[1] / 'evaluator' / run.name,
                     run / 'agent/environment/Scripts/python.exe', args.operation)
summary = dict(result)
if 'cells' in summary:
    summary['cells'] = [{**cell, 'output': cell['output'][-1400:]} for cell in summary['cells']]
print(json.dumps(summary, indent=2))
raise SystemExit(0 if result.get('status') == 'passed' else 1)
