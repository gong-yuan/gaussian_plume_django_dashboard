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
    from multiprocessing import Pool
    start_time = time.time()
    fixed_inputs = {
        "RH": "0.9",
        "windspeed": "1.4",
        "days": "50",
        "wind_dir": "225",
        "stacks": "3",
        "aerosol_type": "1",  # SODIUM_CHLORIDE
        "humidify": "1",  # DRY_AEROSOL
        "stab1": "2", # Moderately Unstable
        "stability_used": "1",  # CONSTANT_STABILITY
        "output": "1",  # PLAN_VIEW
        "wind": "3",  # PREVAILING_WIND
        "num_contour": "100",
        "dry_size": str(60 / (10**9))
    }

    default_values = {
        "stack_x0": "1.2818367",
        "stack_y0": "103.7141216",
        "Q0": "100",
        "H0": "50",
        "stack_x1": "1.2665375",
        "stack_y1": "103.6978671",
        "Q1": "100",
        "H1": "50",
        "stack_x2": "1.2678407",
        "stack_y2": "103.7140133",
        "Q2": "200",
        "H2": "50"
    }
    # print(default_values.keys())

    default_values['location_type'] = "EPSG:3414"
    locs = [14734.341647276688, 29364.818305600333, 12925.255322795563, 27673.19712903669, 14722.217011973618, 27817.210234902086]
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

    coarse_paras = pd.read_csv('prefinal_grid_parameters.csv')
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
    df.sort_values('sensitivity', ascending = False).to_csv('prefinal_grid_search_parallel.csv', index = False)

