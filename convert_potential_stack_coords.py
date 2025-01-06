#!/usr/bin/env python3
import gaussian_plume_model as gp
import pandas as pd
from pdb import set_trace
# stack_0: top right
# stack_1: bottom left
# stack_2: bottom right
stack_locs = {

}

onemap_api_key = gp.get_onemap_token()
sf_dir = '~/ubuntu2404/'
stack_locs_xy = {}
for k, v in stack_locs.items():
    stack_x = []
    stack_y = []
    if k in ['stack_0_range', 'stack_1_range']:
        for x_coor in v['stack_x']:
            for y_coor in v['stack_y']:
                stack_x.append(x_coor)
                stack_y.append(y_coor)
        # set_trace()
    elif k in ['stack_2_range', 'original_stacks']:
        for coor in v.values():
            stack_x.append(coor[0])
            stack_y.append(coor[1])
    stack_xm, stack_ym = gp.coors_convert(stack_x, stack_y, onemap_api_key, '4326to3414')
    curr_df = pd.DataFrame({"X": stack_xm, "Y": stack_ym})
    curr_df.to_csv(sf_dir + k + '.csv', index = False)
    stack_locs_xy[k] = {
        "stack_x": stack_xm,
        "stack_y": stack_ym
    }
# stack_xm, stack_ym = gp.coors_convert(stack_x_orig, stack_y_orig, onemap_api_key, '4326to3414')

sensitivity_coors = {}
for i in range(len(stack_locs_xy['original_stacks']['stack_x'])):
    stack_coor = {
        'stack_x': stack_locs_xy['original_stacks']['stack_x'][i], 
        'stack_y': stack_locs_xy['original_stacks']['stack_y'][i]
        }
    sensitivity_coor = {}
    if i in [0, 1]:
        # for normal rectangle, rotate 
        for k, v in stack_locs_xy['stack_' + str(i) + '_range'].items():
            delta = max(v) - min(v) 
            sensitivity_coor[k] = [stack_coor[k] - delta * 0.1, stack_coor[k] + delta * 0.1]
    else:
        # stack 2 is a rotated rectangle
        coor_loc = ['top_left', 'top_right', 'bottom_left', 'bottom_right']
        four_corners = {}
        for k in range(4):
            four_corners[coor_loc[k]] = [
                stack_locs_xy['stack_' + str(i) + '_range']['stack_x'][k],
                stack_locs_xy['stack_' + str(i) + '_range']['stack_y'][k]
            ]
        delta_width = [
            four_corners['top_left'][0] - four_corners['bottom_left'][0],
            four_corners['top_left'][1] - four_corners['bottom_left'][1]
        ]
        delta_length = [
            four_corners['top_left'][0] - four_corners['top_right'][0],
            four_corners['top_left'][1] - four_corners['top_right'][1]
        ]
        
        sensitivity_coor['stack_x'] = [
            stack_coor['stack_x'] - 0.1 * delta_width[0] - 0.1 * delta_length[0],
            stack_coor['stack_x'] + 0.1 * delta_width[0] + 0.1 * delta_length[0]
        ]

        sensitivity_coor['stack_y'] = [
            stack_coor['stack_y'] - 0.1 * delta_width[1] - 0.1 * delta_length[1],
            stack_coor['stack_y'] + 0.1 * delta_width[1] + 0.1 * delta_length[1]
        ]
    sensitivity_coors['stack_' + str(i)] = sensitivity_coor
    pd.DataFrame(sensitivity_coor).to_csv(sf_dir + 'stack_' + str(i) + '_sensitivity.csv', index = False)
set_trace()