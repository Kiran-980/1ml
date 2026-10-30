"""Inspect actual Matplotlib data/tick objects, not source wording."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys

sys.dont_write_bytecode=True


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--actor',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    os.environ['MPLCONFIGDIR']=str(args.output.parent/'matplotlib-cache')
    os.environ['MPLBACKEND']='Agg'
    import numpy as np
    import pandas as pd
    spec=importlib.util.spec_from_file_location('reviewed_chart',args.actor/'chart.py')
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    data=pd.read_csv(args.actor/'inputs/sales.csv')
    data=data[data.active_store]
    counts=data.groupby('item_id').date.nunique()
    data=data[data.item_id.isin(counts[counts>=3].index)]
    expected=data.groupby(['store_id','item_id']).sales.mean().unstack()
    expected=expected.loc[expected.mean(axis=1).sort_values(ascending=False,kind='stable').index,
                          expected.mean(axis=0).sort_values(ascending=False,kind='stable').index]
    figure=module.build_figure()
    # Match the delivery contract: save once. An extra pre-save canvas draw can
    # run constrained_layout twice and change PNG pixels without changing labels.
    figure.savefig(args.output.parent/(args.output.stem+'.png'),dpi=150)
    figure.canvas.draw()
    axes=[ax for ax in figure.axes if ax.get_xlabel().startswith('Item ID') and ax.get_ylabel().startswith('Store ID')]
    if len(axes)!=1:
        raise ValueError('Expected one explicitly identified store-item heatmap axis')
    ax=axes[0]
    if ax.images:
        values=np.asarray(ax.images[0].get_array()); centers_x=np.arange(expected.shape[1]); centers_y=np.arange(expected.shape[0])
    else:
        meshes=[c for c in ax.collections if type(c).__name__=='QuadMesh']
        if len(meshes)!=1: raise ValueError('No inspectable heatmap matrix')
        values=np.asarray(meshes[0].get_array()).reshape(expected.shape)
        centers_x=np.arange(expected.shape[1])+.5; centers_y=np.arange(expected.shape[0])+.5
    def at_centers(positions,labels,centers):
        return [next((label.get_text() for p,label in zip(positions,labels) if np.isclose(p,c)),None) for c in centers]
    observed_x=at_centers(ax.get_xticks(),ax.get_xticklabels(),centers_x)
    observed_y=at_centers(ax.get_yticks(),ax.get_yticklabels(),centers_y)
    checks={'matrix_matches_source':values.shape==expected.shape and bool(np.allclose(values,expected.to_numpy())),
            'item_ticks_match_matrix_columns':observed_x==list(map(str,expected.columns)),
            'store_ticks_match_matrix_rows':observed_y==list(map(str,expected.index))}
    result={'status':'passed' if all(checks.values()) else 'failed','checks':checks,
            'observed_item_ticks':observed_x,'observed_store_ticks':observed_y,
            'expected_item_ids':expected.columns.tolist(),'expected_store_ids':expected.index.tolist(),
            'expected_values':expected.to_numpy().tolist(),'retained_observations':len(data)}
    args.output.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result))
    raise SystemExit(0 if all(checks.values()) else 1)


if __name__=='__main__': main()
