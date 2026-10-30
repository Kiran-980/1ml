"""Deterministic SQLite + HTTP-JSON fixtures; no CSV input or solution supplied."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import shutil
import sqlite3
import sys

CASE=Path(__file__).resolve().parent
ROOT=CASE.parents[3]
sys.path.insert(0,str(ROOT))
from evals.harness.storage import intern_input, share_frozen_plugin

def hashes(folder):
    return {p.relative_to(folder).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in folder.rglob('*') if p.is_file()}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--run',required=True); ap.add_argument('--freeze',action='store_true')
    a=ap.parse_args()
    assert a.run.replace('-','').isalnum()
    trial=ROOT/'evals/skills/trials/database-url'/a.run
    m,e=trial/'materials',trial/'evaluator'
    if a.freeze:
        assert (m/'sources.json').is_file() and not (e/'materials-before.json').exists()
        (e/'materials-before.json').write_text(json.dumps(hashes(m),indent=2),encoding='utf-8')
        protected={}
        for d in (ROOT/'evals/kaggle').iterdir():
            if not (d/'delivery-manifest.json').exists(): continue
            paths=json.loads((d/'delivery-manifest.json').read_text())['published_files']
            for rel in paths+['README.md','current-run.json','delivery-manifest.json']:
                p=d/rel
                if p.is_file(): protected[p.relative_to(ROOT).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
        (e/'existing-results-before.json').write_text(json.dumps(protected,indent=2),encoding='utf-8')
        print(json.dumps({'trial':str(trial),'materials_frozen':True,'empty_project':not any((trial/'project').iterdir())})); return
    assert not trial.exists()
    (trial/'project').mkdir(parents=True); (m/'database').mkdir(parents=True); (e/'http').mkdir(parents=True)
    rng=random.Random(20261028)
    regions=[{'region_code':code,'terrain_index':terrain,'planned_hours':hours,'region_name':name}
             for code,terrain,hours,name in [('01',.2,24,'Metro'),('07',.7,36,'Coastal'),('NA',1.3,48,'North Area'),('12',.5,24,'Central'),('20',1.8,48,'Highland')]]
    payload={'snapshot_id':'shipment-context-v1','effective_from':'2025-01-01','regions':regions}
    (e/'http/region-context.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
    db=m/'database/shipments.sqlite'
    with sqlite3.connect(db) as con:
        con.execute('CREATE TABLE shipments (shipment_id TEXT PRIMARY KEY, customer_id TEXT NOT NULL, dispatch_day TEXT NOT NULL, region_code TEXT NOT NULL, distance_km REAL, parcel_kg REAL, queue_minutes REAL, expedited INTEGER NOT NULL, cohort TEXT NOT NULL, late INTEGER)')
        from datetime import date,timedelta
        for i in range(1200):
            customer=rng.randrange(240); region=regions[customer%len(regions)]
            distance=round(rng.uniform(5,220),2); weight=round(rng.lognormvariate(.5,.8),2)
            queue=round(rng.uniform(0,110),2); expedited=int(rng.random()<.3)
            logit=-3.1+.013*distance+.018*queue+.5*region['terrain_index']-.025*(region['planned_hours']-24)-.75*expedited+.06*weight
            late=int(rng.random()<1/(1+math.exp(-logit))) if i<900 else None
            values=(f'S{i+1:05d}',f'C{customer:04d}',str(date(2025,1,1)+timedelta(days=i//5)),region['region_code'],
                    None if rng.random()<.05 else distance,None if rng.random()<.04 else weight,queue,expedited,
                    'development' if i<900 else 'prediction',late)
            con.execute('INSERT INTO shipments VALUES (?,?,?,?,?,?,?,?,?,?)',values)
    con.close()
    intern_input(db,ROOT/'evals/skills/static/inputs',ROOT)
    for name in ('skills','references','tools','rules','.claude-plugin'):
        shutil.copytree(ROOT/name,m/'agent/plugin'/name,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    shutil.copyfile(ROOT/'requirements.txt',m/'agent/plugin/requirements.txt')
    share_frozen_plugin(m,ROOT/'evals/static/plugin-files',ROOT)
    shutil.copyfile(CASE/'task.md',trial/'task.md')
    (m/'data-dictionary.md').write_text('''# Synthetic shipment source dictionary

This deterministic synthetic fixture tests source-loading and ML workflow behavior, not real logistics performance. One shipment is one row. Sources are fixed snapshots; there are no credentials.

The read-only SQLite table `shipments` contains 900 development and 300 later prediction shipments. `shipment_id` and `customer_id` are text identifiers; repeated customers are possible. `dispatch_day` is the date of dispatch. `region_code` is an opaque text key: `01`, `07`, `NA`, `12`, `20`. In particular `NA` means North Area, not missing. `distance_km`, `parcel_kg`, `queue_minutes` and `expedited` are known at dispatch; missing measurements are SQL NULL. `cohort` determines the labeled/unlabeled role and is not a predictor. `late` is the later observed binary outcome (1=late); NULL in prediction rows means unknown, not on-time.

The HTTP JSON document has `snapshot_id`, `effective_from` and a `regions` records array. Each region has `region_code`, `terrain_index`, `planned_hours` and `region_name`. This one-row-per-region context was known before all supplied dispatches; it is static throughout the fixture. The join key is region_code. The database contains no regional context table. Preserve keys and observation counts when combining sources.

Predict late arrivals at dispatch for additional shipments. Prior-customer overlap and temporal availability should be reflected in the evaluation claim. False positives and negatives both matter; accuracy is the requested primary metric for this fixture, with class-error context. No costs or intervention benefit are specified. No labels exist for the prediction cohort in the supplied database.

`sources.json` identifies the source connections and fixed versions. The URL requires its loopback fixture service to be running; it is an external source dependency, not a notebook helper. Use normal HTTP access to the documented route. Report source availability failures explicitly. The evaluator retains the original database and HTTP fixture for repeatable runs.
''',encoding='utf-8')
    criteria={'scope':'SQLite read-only and loopback HTTP JSON; not production authentication or every DB vendor',
      'expected':{'development_rows':900,'prediction_rows':300,'region_codes':['01','07','NA','12','20'],'context_rows':5},
      'gates':['Actual SQL and HTTP loading, no CSV input bridge','Source hashes unchanged and keys/cardinality preserved',
      'Lifecycle analysis and honest evaluation claim','Current root delivery and notebook-only genuine history',
      'Clean replay through original source connections','Exact documented history reconstruction and verification',
      'No parent intervention/result repairs','No external submissions']}
    (e/'criteria.json').write_text(json.dumps(criteria,indent=2),encoding='utf-8')
    print(trial)

if __name__=='__main__': main()
