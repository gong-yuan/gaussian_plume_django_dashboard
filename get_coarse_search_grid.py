import numpy as np
from shapely.geometry import Polygon, box, mapping
import gaussian_plume_model as gp
import pandas as pd
from pdb import set_trace
import math
import emission_stack_height_parameters_coarse_search as eh
import itertools

def get_stack_xy(stack_locs):
    stack_locs_xy = {}
    for k, v in stack_locs.items():
        stack_x = []
        stack_y = []
        if k in ['stack_0_range', 'stack_1_range']:
            for x_coor in v['stack_x']:
                for y_coor in v['stack_y']:
                    stack_x.append(x_coor)
                    stack_y.append(y_coor)
        elif k in ['stack_2_range', 'original_stacks']:
            for coor in v.values():
                stack_x.append(coor[0])
                stack_y.append(coor[1])
        stack_xm, stack_ym = gp.coors_convert(stack_x, stack_y, onemap_api_key, '4326to3414')
        stack_locs_xy[k] = {
            "stack_x": stack_xm,
            "stack_y": stack_ym
        }
    return stack_locs_xy

def set_anti_clockwise_order(stack_loc_xy):
    for k, v in stack_loc_xy.items():
        rectangle = [(x, y) for x, y in zip(v['stack_x'], v['stack_y'])]
        if k in ['stack_0_range', 'stack_1_range']:
            rectangle = rectangle[:2] + rectangle[2:][::-1]
        elif k in ['stack_2_range']:
            rectangle = [rectangle[x] for x in [0,2,3,1]]
        stack_loc_xy[k] = rectangle  

def generate_grid(rectangle, x_grid_size, y_grid_size):
    x_coords, y_coords = zip(*rectangle)
    x_min, x_max = min(x_coords), max(x_coords)
    y_min, y_max = min(y_coords), max(y_coords)
    # print(x_min, x_max, x_grid_size, y_min, y_max, y_grid_size)
    grid_cells = []
    # for x in np.arange(np.floor(x_min / x_grid_size) * x_grid_size, np.ceil(x_max / x_grid_size) * x_grid_size, x_grid_size):
    #     for y in np.arange(np.floor(y_min / y_grid_size) * y_grid_size, np.ceil(y_max / y_grid_size) * y_grid_size, y_grid_size):
    for x in np.arange(x_min, x_max - x_grid_size, x_grid_size):
        for y in np.arange(y_min, y_max - y_grid_size, y_grid_size):
            grid_cells.append(box(x, y, x + x_grid_size, y + y_grid_size))
    # set_trace()
    return grid_cells

def generate_grid_rotated_rectangle(rectangle):
    rec_center = [np.mean([corner[i] for corner in rectangle]) for i in range(2)]
    center_points = {'box_id': [], 'stack_x': [], 'stack_y': []}
    for i, corner in enumerate(rectangle):
        curr_center = [(rec_center[i] + corner[i]) / 2 for i in range(2)]
        center_points['box_id'].append(i)
        center_points['stack_x'].append(curr_center[0])
        center_points['stack_y'].append(curr_center[1])
    return pd.DataFrame(center_points)


# Function to calculate the area of a polygon using the shoelace formula
def polygon_area(coords):
    n = len(coords)
    area = 0.5 * abs(
        sum(coords[i][0] * coords[(i + 1) % n][1] - coords[i][1] * coords[(i + 1) % n][0] for i in range(n))
    )
    return area

# Function to calculate Euclidean distance between two points
def euclidean_distance(p1, p2):
    return ((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)**0.5

def filter_rotated(rectangle, grid_cells):
    poly = Polygon(rectangle)
    return [cell for cell in grid_cells if cell.intersects(poly)]

import pandas as pd
import numpy as np
import itertools


if __name__=="__main__":
    sf_dir = '~/ubuntu2404/'
    # stack_0: top right
    # stack_1: bottom left
    # stack_2: bottom right
    onemap_api_key = gp.get_onemap_token()
    stack_locs = {
        "stack_0_range": { 
            "stack_x": [1.2793929, 1.2871254],
            "stack_y": [103.7098452, 103.7157675]
        },
        "stack_1_range": {
            "stack_x": [1.2658105, 1.2691195],
            "stack_y": [103.6964365, 103.6984305]
        },
        "stack_2_range": {
            "corner1": [1.270155, 103.712018],
            "corner2": [1.267838, 103.716395],
            "corner3": [1.267280, 103.710688],
            "corner4": [1.264920, 103.714893]
        }
    }
    stack_loc_xy = get_stack_xy(stack_locs)
    set_anti_clockwise_order(stack_loc_xy)
    width_length = {}
    min_grid_size = float('inf')
    grid_cells = {}
    prod = 1
    
    stack_locations = []
    for k, v in stack_loc_xy.items(): 
        # if k != 'stack_2_range': continue
        width = euclidean_distance(v[0], v[1])
        height = euclidean_distance(v[1], v[2])
        area = polygon_area(v)
        if k in ['stack_0_range', 'stack_1_range']:
            curr_grid_cells = generate_grid(v, width / 2, height / 2)
            grid_cells[k] = filter_rotated(v, curr_grid_cells) 
            curr_grid_df = pd.DataFrame([ {"stack_x": coors[0], "stack_y": coors[1], 'box_id': i} for i, x in enumerate(grid_cells[k]) for coors in mapping(x)['coordinates'][0]]).drop_duplicates().sort_values(['box_id', 'stack_x', 'stack_y']).reset_index(drop = True)
            # print(curr_grid_df)
            center_points = curr_grid_df.groupby('box_id')[['stack_x', 'stack_y']].mean().reset_index()
        elif k == 'stack_2_range':
            center_points = generate_grid_rotated_rectangle(v)
        # set_trace() 
        center_points.to_csv(sf_dir + k + '_grid.csv', index = False)
        center_points['stack_id'] = k
        stack_locations.append(center_points)
        prod *= center_points.shape[0]
        print(center_points.shape[0])
    print(prod * 2.4 / 60 / 60 * 4 * 4 * 6 * 3 * 3 * 3)
    set_trace()
#     if min_grid_size > grid_size:
#         min_grid_size = grid_size
#     print(k, 'width = ', width, ', height = ', height, ', area = ', area, ', area w * h = ', width * height, ', grid size = ', grid_size, ', num grids = ', area / grid_size / grid_size)
# grid_cells = {}
# for k, v in stack_loc_xy.items():
    stack_loc_df = pd.concat(stack_locations)
    eh_params = {}
    for k, v in eh.params.items():
        eh_params[k] = []
        for value in np.arange(float(v['min']), float(v['max']) + 0.01, float(v['step'])):
            eh_params[k].append(str(value))
    # set_trace()
    unique_levels = [x for x in eh_params.values()] + [
           [str(x) + ',' + str(y) for y in stack_loc_df['box_id'].unique().tolist()] for x in stack_loc_df['stack_id'].unique().tolist()
        ]
    # set_trace()
    all_combinations = itertools.product(*unique_levels)
    # print(len([x for x in all_combinations]) * 2.4/60/60)
    all_df = pd.DataFrame([x for x in all_combinations])
    all_df.columns = [x for x in eh_params.keys()] + [x for x in stack_loc_xy.keys()]
    stack_loc_df['stack_coor_id'] = stack_loc_df['stack_id'] + ',' + stack_loc_df['box_id'].astype(str)
    stack_loc_df.drop(['box_id', 'stack_id'], inplace = True, axis = 1)

    for i, col in enumerate(stack_loc_xy.keys()):
        all_df = pd.merge(all_df, stack_loc_df.rename(columns = {'stack_coor_id': col}), on = col, suffixes = ['',  str(i)])
    all_df.rename(columns = {'stack_x': 'stack_x0', 'stack_y': 'stack_y0'}, inplace = True)
    # set_trace()
    print(all_df.shape)
    for emission_col, height_col in zip(['Q0', 'Q1', 'Q2'], ['H0', 'H1', 'H2']):
        is_zero_emission = all_df[emission_col].astype(float) == 0
        curr_df = all_df.loc[is_zero_emission].sort_values(all_df.columns.tolist()).drop_duplicates(subset = all_df.columns.difference([emission_col, height_col]), keep = 'first')
        all_df = pd.concat([all_df.loc[~is_zero_emission], curr_df]).reset_index(drop = True)
        print(is_zero_emission.sum(), curr_df.shape[0], is_zero_emission.sum()/3)
        print(curr_df.groupby(emission_col)[height_col].unique())
        # set_trace()
    all_df = all_df.sort_values(all_df.columns.tolist()).reset_index(drop = True)
    set_trace()
    for col in ['Q0', 'Q1', 'Q2'] + ['H0', 'H1', 'H2']:
        all_df[col] = all_df[col].astype(float)
    
    all_df.to_csv('coarse_grid_parameters.csv', index = False)
    print(all_df.shape[0] * 2.4/60/60)
    set_trace()