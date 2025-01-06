import gaussian_plume_model as gp
import numpy as np
import time
from pdb import set_trace
import simulation
import comparison
import pandas as pd
import random # may break test

onemap_api_key = gp.get_onemap_token()

def construct_input(fixed_inputs, default_values, row):
    default_values = default_values.copy()
    for key in sorted(set(default_values.keys()).difference(['location_type'])):
        if key in ['Q0', 'H0', 'Q1', 'H1', 'Q2', 'H2']:
            default_values[key] = str(row[key])
        else:
            default_values[key] = row[key]
    return {**fixed_inputs, **default_values}

def process_row(args):
    fixed_inputs, default_values, row = args
    sim_input = construct_input(fixed_inputs, default_values, row)
    comp = comparison.run_comparison(simulation.run_simulation(**sim_input))
    agg_corr = comparison.aggregate_corr(comp.corrs)
    return {
        'aggregate_corr': agg_corr,
        'active_corr': comp.corrs['active'][0],
        'passive_cycle_1': comp.corrs['passive']['cycle 1'],
        'passive_cycle_2': comp.corrs['passive']['cycle 2'],
        'passive_cycle_3': comp.corrs['passive']['cycle 3'],
        'passive_cycle_4': comp.corrs['passive']['cycle 4'],
        'passive_cycle_5': comp.corrs['passive']['cycle 5'],
        'active_obs': comp.num_points['active'],
        'passive_obs': comp.num_points['passive'],
        'active_modelled_max_ratio': comp.active_modelled_range_ratio['max'],
        'active_modelled_min_ratio': comp.active_modelled_range_ratio['min'],
        'param_id': row.name
    }


if __name__=="__main__":

    for i in range(3):
        default_values['stack_x' + str(i)] = locs[2*i]
        default_values['stack_y' + str(i)] = locs[2*i+1]

    orig_inputs = {**fixed_inputs, **default_values}
    base_simulation = comparison.run_comparison(simulation.run_simulation(**orig_inputs))
    base_agg_corr = comparison.aggregate_corr(base_simulation.corrs)

    agg_corrs = {
        'aggregate_corr': [base_agg_corr],
        'active_corr': base_simulation.corrs['active'],
        'passive_cycle_1': [base_simulation.corrs['passive']['cycle 1']],
        'passive_cycle_2': [base_simulation.corrs['passive']['cycle 2']],
        'passive_cycle_3': [base_simulation.corrs['passive']['cycle 3']],
        'passive_cycle_4': [base_simulation.corrs['passive']['cycle 4']],
        'passive_cycle_5': [base_simulation.corrs['passive']['cycle 5']],
        'active_obs': [base_simulation.num_points['active']],
        'passive_obs': [base_simulation.num_points['passive']],
        'active_modelled_max_ratio': [base_simulation.active_modelled_range_ratio['max']],
        'active_modelled_min_ratio': [base_simulation.active_modelled_range_ratio['min']],
        'param_id': [-1]
    }

    coarse_paras = pd.read_csv('all_combinations_prescaling.csv')
    # for _, row in coarse_paras.sample(10).iterrows():
    #     args = (fixed_inputs, default_values, row)
    #     print(process_row(args))
    #     set_trace()
    
    with Pool() as pool:
        results = pool.map(
            process_row,
            [(fixed_inputs, default_values, row) for _, row in coarse_paras.iterrows()]
        )

    df = pd.DataFrame(results)
    df['sensitivity'] = df['aggregate_corr'] - base_agg_corr
    end_time = time.time()
    print(end_time - start_time) 
    # set_trace()  
    df.sort_values('sensitivity', ascending = False).to_csv('prescaling_grid_search_parallel.csv', index = False)

