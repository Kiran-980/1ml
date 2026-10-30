"""Initial store-item overview."""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


def build_figure():
    data = pd.read_csv(Path(__file__).parent / 'inputs/sales.csv')
    active = data.loc[data.active_store.eq(True)]
    supported = active.groupby('item_id').date.nunique()
    active = active[active.item_id.isin(supported[supported >= 3].index)]
    means = active.pivot_table(index='store_id', columns='item_id', values='sales', aggfunc='mean')
    row_order = means.mean(axis=1).sort_values(ascending=False, kind='stable').index
    column_order = means.mean(axis=0).sort_values(ascending=False, kind='stable').index
    means = means.loc[row_order, column_order]
    fig, ax = plt.subplots(figsize=(7, 4), layout='constrained')
    image = ax.imshow(means.to_numpy(), aspect='auto', origin='lower')
    ax.set(xlabel='Item ID', ylabel='Store ID', title='Mean daily sales: active stores')
    fig.colorbar(image, ax=ax, label='Units per day')
    return fig


if __name__ == '__main__':
    build_figure().savefig(Path(__file__).parent / 'heatmap.png', dpi=150)
