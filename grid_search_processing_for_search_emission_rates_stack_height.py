import numpy as np
from shapely.geometry import Polygon, box, mapping
import gaussian_plume_model as gp
import pandas as pd
from pdb import set_trace
import math
import emission_stack_height_parameters_prefinal as eh
import itertools

df = pd.read_csv('prefinal_grid_search_parallel.csv')
params = pd.read_csv('prefinal_grid_parameters.csv').reset_index().rename(columns={'index': 'param_id'})
df = df.sort_values(['active_modelled_max_ratio', 'aggregate_corr'], ascending = [True, False]).reset_index(drop = True)

df = pd.merge(df, params,on = 'param_id')
keep_cols=['aggregate_corr', 'active_modelled_max_ratio', 'active_modelled_min_ratio', 'sensitivity', 'Q0', 'Q1', 'Q2', 'H0', 'H1', 'H2', 'stack_x0', 'stack_y0', 'stack_x1', 'stack_y1', 'stack_x2', 'stack_y2']
df.sort_values('aggregate_corr', ascending = False, inplace = True)
best_params = df[keep_cols].sort_values('aggregate_corr', ascending = False)[['Q0', 'Q1', 'Q2', 'H0', 'H1', 'H2']].iloc[0].to_dict()
df[['active_modelled_max_ratio', 'Q0', 'Q1', 'Q2']].head(100).corr()
print(params.shape[0])