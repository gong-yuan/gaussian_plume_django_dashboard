import gaussian_plume_model as gp
import numpy as np
import time
from pdb import set_trace
import geopy.distance
import simulation
import comparison
import pandas as pd
import random # may break test

onemap_api_key = gp.get_onemap_token()
# grids will be created using qgis

def do_comparison(**kwargs):
    return comparison.run_comparison(simulation.run_simulation(**kwargs))

def construct_input(fixed_inputs, default_values, row):
    default_values = default_values.copy()
    for key in sorted(set(default_values.keys()).difference(['location_type'])):
        if key in ['Q0', 'H0', 'Q1', 'H1', 'Q2', 'H2']:
            default_values[key] = str(row[key])
        else:
            default_values[key] = row[key]
    return {**fixed_inputs, **default_values}


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

    # P = Pool()
    # sol = [P.apply_async(do_comparison, kwds=sim_inputs) for x in range(10)]
    # P.close()
    # P.join()
    # for s in sol: s.get()
    # counter = 0

    coarse_paras = pd.read_csv('coarse_grid_parameters.csv')
    counter = 0
    for rid, row in coarse_paras.head(100).iterrows():
        sim_input = construct_input(fixed_inputs, default_values, row)
        # print(sim_input['location_type'])
        comp = comparison.run_comparison(simulation.run_simulation(**sim_input))
        agg_corrs['active_corr'].extend(comp.corrs['active'])
        [agg_corrs['passive_cycle_'+str(cycle_id)].append(comp.corrs['passive']['cycle '+str(cycle_id)]) for cycle_id in range(1,6)]
        agg_corrs['aggregate_corr'].append(comparison.aggregate_corr(comp.corrs))
        agg_corrs['active_obs'].append(comp.num_points['active'])
        agg_corrs['passive_obs'].append(comp.num_points['passive'])
        agg_corrs['active_modelled_max_ratio'].append(comp.active_modelled_range_ratio['max'])
        agg_corrs['active_modelled_min_ratio'].append(comp.active_modelled_range_ratio['min'])
        agg_corrs['param_id'].append(rid)
        # set_trace()
    df = pd.DataFrame(agg_corrs)
    df['sensitivity'] = df['aggregate_corr'] - base_agg_corr
    end_time = time.time()
    print(end_time - start_time, counter)   
    df.sort_values('sensitivity').to_csv('Coarse_grid_search.csv', index = False)

set_trace()
