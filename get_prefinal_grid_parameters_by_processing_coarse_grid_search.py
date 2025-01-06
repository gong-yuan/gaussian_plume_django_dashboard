import numpy as np
from shapely.geometry import Polygon, box, mapping
import gaussian_plume_model as gp
import pandas as pd
from pdb import set_trace
import math
import emission_stack_height_parameters_prefinal as eh
import itertools

curr_file = 'Coarse_grid_search_parallel.csv'
params_file = 'coarse_grid_parameters.csv'
params = pd.read_csv(params_file).reset_index().rename(columns = {'index': 'param_id'})
# set_trace()
df = pd.read_csv(curr_file)
df = df.sort_values(['active_modelled_max_ratio', 'aggregate_corr'], ascending = [True, False]).reset_index(drop = True)

is_matching_range = (df['active_modelled_max_ratio'] <= 10) & (~df['aggregate_corr'].isna())
df.loc[is_matching_range].sort_values('aggregate_corr', ascending = False)
df.loc[is_matching_range].head()

df = pd.merge(df, params,on = 'param_id')
keep_cols=['aggregate_corr', 'active_modelled_max_ratio', 'active_modelled_min_ratio', 'sensitivity', 'Q0', 'Q1', 'Q2', 'H0', 'H1', 'H2', 'stack_x0', 'stack_y0', 'stack_x1', 'stack_y1', 'stack_x2', 'stack_y2']
df[keep_cols].sort_values('aggregate_corr', ascending = False).to_csv('tmp.csv')
df.sort_values('aggregate_corr', ascending = False)[['active_modelled_max_ratio', 'Q0', 'Q1', 'Q2', 'H0', 'H1', 'H2']].head(25).corr().round(2)
candidate_df = df.loc[df['aggregate_corr'] >= 0.795].reset_index(drop = True)

stack_locs = {}
for col in [['stack_x0', 'stack_y0'], ['stack_x1', 'stack_y1'], ['stack_x2', 'stack_y2']]:
    stack_x, stack_y = candidate_df.groupby(col).size().sort_values(ascending = False).reset_index()[col].iloc[0]
    stack_locs[col[0]], stack_locs[col[1]] = stack_x, stack_y

n_params = params.shape[0] * 1.6
n_h2 = int(np.floor((n_params / (2**5)) ** (1/6)))
n_eh = int(2 * n_h2)

eh_params = {}
for k, v in eh.params.items():
    eh_params[k] = []
    n_points = n_eh
    if k == 'H2':
        n_points = n_h2

    for value in np.linspace(float(v['min']), float(v['max']), n_points):
        eh_params[k].append(str(value))

unique_levels = [x for x in eh_params.values()] 
all_combinations = itertools.product(*unique_levels)
all_df = pd.DataFrame([x for x in all_combinations])
all_df.columns = [x for x in eh_params.keys()] 
for k, v in stack_locs.items():
    all_df[k] = v
all_df = all_df.sort_values(all_df.columns.tolist()).reset_index(drop = True)
for col in ['Q0', 'Q1', 'Q2'] + ['H0', 'H1', 'H2']:
    all_df[col] = all_df[col].astype(float)
all_df.to_csv('prefinal_grid_parameters.csv', index = False)
# print(n_h2 * n_eh** 5)

set_trace()

if False:
    print(candidate_df.shape[0])
    for col in ['Q0', 'Q1', 'Q2'] + ['H0', 'H1', 'H2'] + [['stack_x0', 'stack_y0'], ['stack_x1', 'stack_y1'], ['stack_x2', 'stack_y2']]:  curr_summ = candidate_df.groupby(col)['aggregate_corr'].agg(['min', 'max', 'mean', 'median', 'size']).reset_index().sort_values('size', ascending = False); curr_summ.to_csv(''.join(col) + '.csv', index = False); print(curr_summ)

    for col in ['Q0', 'Q1', 'Q2'] + ['H0', 'H1', 'H2'] + [['stack_x0', 'stack_y0'], ['stack_x1', 'stack_y1'], ['stack_x2', 'stack_y2']]:  curr_summ = candidate_df.groupby(col)['active_modelled_max_ratio'].agg(['min', 'max', 'mean', 'median', 'size']).reset_index().sort_values('size', ascending = False); curr_summ.to_csv(''.join(col) + '.csv', index = False); print(curr_summ)

    candidate_df.sort_values('aggregate_corr', ascending = False)[['active_modelled_max_ratio', 'Q0', 'Q1', 'Q2', 'H0', 'H1', 'H2']].corr().round(2)
    set_trace()