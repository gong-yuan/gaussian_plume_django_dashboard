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

def construct_input(fixed_inputs, default_values, default_key):
    default_values = default_values.copy()
    sim_inputs = {'parameter_name': [], 'parameter_value': [], 'sim_input': []}
    if default_key in ['Q0', 'H0', 'Q1', 'H1', 'Q2', 'H2']:
        multipliers = [1.1, 0.9]
        orig_val = default_values[default_key]
        for multiplier in multipliers:
            default_values[default_key] = float(orig_val) * multiplier
            sim_inputs['parameter_name'].append(default_key)
            sim_inputs['parameter_value'].append(float(orig_val) * multiplier)
            sim_inputs['sim_input'].append({**fixed_inputs, **(default_values.copy())})

    elif default_key == 'dry_size':
        for dry_size in [0.6, 6]:
            default_values[default_key] = dry_size / 10**9
            sim_inputs['parameter_name'].append(default_key)
            sim_inputs['parameter_value'].append(dry_size / 10**9)
            sim_inputs['sim_input'].append({**fixed_inputs, **(default_values.copy())})


    elif default_key == ['stack_x0', 'stack_y0'] or default_key == ['stack_x1', 'stack_y1'] or default_key == ['stack_x2', 'stack_y2']:
        coor_file = "~/ubuntu2404/" + default_key[0].replace('_x', '_') + '_sensitivity.csv'
        coords = pd.read_csv(coor_file)
        for i in range(coords.shape[0]):
            for coor_key in default_key:
                default_values[coor_key] = coords.iloc[i].loc[coor_key[:-1]]
            sim_inputs['parameter_name'].append(', '.join(default_key))
            sim_inputs['parameter_value'].append(', '.join(coords.iloc[i].astype(str).values.reshape(-1)))
            sim_inputs['sim_input'].append({**fixed_inputs, **(default_values.copy())})

    return sim_inputs


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
    }

    default_values = {
        "dry_size": str(60 / (10**9)),
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
        'parameter_name': ['default'], 
        'parameter_value': [np.nan], 
        'aggregate_corr': [base_agg_corr],
        'active_corr': base_simulation.corrs['active'],
        'passive_cycle_1': [base_simulation.corrs['passive']['cycle 1']],
        'passive_cycle_2': [base_simulation.corrs['passive']['cycle 2']],
        'passive_cycle_3': [base_simulation.corrs['passive']['cycle 3']],
        'passive_cycle_4': [base_simulation.corrs['passive']['cycle 4']],
        'passive_cycle_5': [base_simulation.corrs['passive']['cycle 5']],
        'active_obs': [base_simulation.num_points['active']],
        'passive_obs': [base_simulation.num_points['passive']]
    }
    counter = 0
    for default_key in ['Q0', 'H0', 'Q1', 'H1', 'Q2', 'H2', 'dry_size'] +  [['stack_x0', 'stack_y0'], ['stack_x1', 'stack_y1'], ['stack_x2', 'stack_y2']]:
        # default_key = ['stack_x0', 'stack_y0']
        sim_inputs = construct_input(fixed_inputs, default_values, default_key)
        # print(f'\n Current variable: {default_key} \n')
        for idx, sim_input in enumerate(sim_inputs['sim_input']):
            counter+=1
            # for k, v in sim_input.items():
            #     if v != orig_inputs[k]:
            #         print(k, v, orig_inputs[k])
            comp = comparison.run_comparison(simulation.run_simulation(**sim_input))
            # print(comp.corrs)
            agg_corrs['active_corr'].extend(comp.corrs['active'])
            [agg_corrs['passive_cycle_'+str(cycle_id)].append(comp.corrs['passive']['cycle '+str(cycle_id)]) for cycle_id in range(1,6)]
            agg_corrs['aggregate_corr'].append(comparison.aggregate_corr(comp.corrs))
            agg_corrs['parameter_name'].append(sim_inputs['parameter_name'][idx])
            agg_corrs['parameter_value'].append(sim_inputs['parameter_value'][idx])
            agg_corrs['active_obs'].append(comp.num_points['active'])
            agg_corrs['passive_obs'].append(comp.num_points['passive'])
            # set_trace()

        # print(f"aggregated correlation for key = {default_key}", agg_corrs['aggregate_corr'], '\n')
    df = pd.DataFrame(agg_corrs)
    df['sensitivity'] = df['aggregate_corr'] - base_agg_corr
    end_time = time.time()
    print(end_time - start_time, counter)   
    df.sort_values('sensitivity').to_csv('Sensitivity.csv', index = False)
df['sensitivity'] = df['aggregate_corr'] - base_agg_corr 
df.sort_values('sensitivity')
set_trace()
