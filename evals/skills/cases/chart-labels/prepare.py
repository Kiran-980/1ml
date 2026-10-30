"""Prepare one isolated synthetic chart behavioral trial; no Kaggle writes."""
import csv
import hashlib
import json
from pathlib import Path
import shutil

CASE = Path(__file__).resolve().parent
ROOT = CASE.parents[3]
TRIAL = ROOT / 'evals/skills/trials/chart-labels/2026-10-27-001-astra'


def hashes(root, exclude=()):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file() and not set(p.relative_to(root).parts).intersection(exclude)}


def main():
    if TRIAL.exists():
        raise ValueError('Preserve prior trial: destination already exists')
    actor, evaluator = TRIAL / 'actor', TRIAL / 'evaluator'
    (actor / 'inputs').mkdir(parents=True)
    evaluator.mkdir()
    rows = []
    # Deliberately nonconsecutive IDs; activity filtering and sales ordering matter.
    for store, level, enabled in [(12,30,True),(3,200,False),(27,70,True),(8,50,True)]:
        for item, increment, days in [(101,9,3),(20,3,3),(307,15,3),(42,300,2)]:
            for day in range(1,days+1):
                rows.append([f'2025-01-0{day}',store,item,level+increment+day,enabled])
    with (actor / 'inputs/sales.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f); w.writerow(['date','store_id','item_id','sales','active_store']); w.writerows(rows)
    for name in ('chart.py','task.md'):
        shutil.copyfile(CASE / name, actor / name)
    for folder in ('skills','references','rules','tools','.claude-plugin'):
        shutil.copytree(ROOT / folder, actor / 'plugin' / folder,
                        ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    shutil.copyfile(ROOT/'requirements.txt',actor/'plugin/requirements.txt')
    forecasting=ROOT/'evals/kaggle/store-item-demand'
    (evaluator/'forecasting-before.json').write_text(json.dumps(hashes(forecasting,('environment','runtime','cache')),indent=2))
    (evaluator/'source-before.json').write_text(json.dumps(hashes(actor),indent=2))
    (evaluator/'criteria.json').write_text(json.dumps({
        'scenario':'Finish a filtered and sorted synthetic store-item descriptive overview',
        'expected_rows':[27,8,12], 'expected_columns':[307,101,20],
        'expected_means':[[87,81,75],[67,61,55],[47,41,35]],
        'gates':['data filtering/order/aggregation correct','plot ticks map to actual data IDs at cell centers',
                 'saved figure updated and readable','source inputs and plugin unchanged',
                 'existing forecasting files unchanged','no parent coaching or artifact repairs'],
        'scope':'Single fresh-agent post-change behavior check; no randomized no-skill control'
    },indent=2))
    print(TRIAL)


if __name__=='__main__':
    main()
