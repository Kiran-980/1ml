"""Score an unchanged, qualitatively accepted completed tabular evaluation once."""
import argparse
import hashlib
import json
from pathlib import Path
import sys


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--project',type=Path,required=True)
    args=parser.parse_args(); project=args.project.resolve()
    if project.parent.name!='work': raise ValueError('Expected a completed temporary work project')
    task=project.parent.parent; out=task/'evaluator'/project.name
    acceptance=json.loads((out/'qualitative-review.json').read_text())
    if acceptance['status']!='accepted': raise ValueError('Qualitative acceptance required before sealed scoring')
    target_path=out/'verification.json'
    if target_path.exists(): raise ValueError('Preserve existing one-shot score')
    hashes=json.loads((out/'completed-sha256.json').read_text())
    def unchanged():
        assert all(hashlib.sha256((project/p).read_bytes()).hexdigest()==digest for p,digest in hashes.items())
    unchanged()
    sys.dont_write_bytecode=True; sys.path.insert(0,str(project))
    import joblib
    import numpy as np
    import pandas as pd
    from sklearn.metrics import accuracy_score, confusion_matrix, mean_absolute_error
    from evals.harness.regression_metrics import log_rmse, constant_log_prediction
    manifest=json.loads((project/'reports/artifact-manifest.json').read_text())
    config=json.loads((project/'config.json').read_text())
    contract=config['prediction_contract']; target=contract['target']
    options=manifest.get('input_csv_options',{})
    development=pd.read_csv(project/'inputs/data/development.csv',**options)
    holdout=pd.read_csv(out/'holdout.csv',**options)
    assert set(development[contract['id']]).isdisjoint(holdout[contract['id']])
    model=joblib.load(project/manifest['model'])
    predictions=np.asarray(model.predict(holdout.drop(columns=target)))
    assert predictions.shape==(len(holdout),)
    observed=holdout[target].to_numpy()
    if contract.get('task')=='regression':
        baseline=np.full(len(holdout),constant_log_prediction(development[target].to_numpy()))
        metrics={'log_rmse':log_rmse(observed,predictions),'baseline_log_rmse':log_rmse(observed,baseline),
                 'mae':float(mean_absolute_error(observed,predictions))}
    else:
        assert set(np.unique(predictions))<=set(contract['values'])
        majority=development[target].mode().iloc[0]
        metrics={'accuracy':float(accuracy_score(observed,predictions)),
                 'baseline_accuracy':float(accuracy_score(observed,np.full(len(observed),majority))),
                 'correct':int(np.sum(observed==predictions)),
                 'confusion_matrix':confusion_matrix(observed,predictions,labels=contract['values']).tolist()}
    unchanged()
    result={'status':'passed','rows':len(holdout),'metrics':metrics,'actor_files_unchanged':len(hashes),
            'holdout_sha256':hashlib.sha256((out/'holdout.csv').read_bytes()).hexdigest(),
            'model_sha256':hashlib.sha256((project/manifest['model']).read_bytes()).hexdigest(),
            'fits_performed_by_reviewer':0,'submission_made':False,
            'claim':'Fixed reused local holdout scored after qualitative acceptance; workflow regression evidence, not a Kaggle score or fresh independent generalization study.'}
    target_path.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__': main()
