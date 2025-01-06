import numpy as np
from shapely.geometry import Polygon, box, mapping
import gaussian_plume_model as gp
import pandas as pd
from pdb import set_trace
import math
import itertools
import re
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


def generate_grid_original(rectangle, x_grid_size, y_grid_size):
    x_coords, y_coords = zip(*rectangle)
    x_min, x_max = min(x_coords), max(x_coords)
    y_min, y_max = min(y_coords), max(y_coords)
    # print(x_min, x_max, x_grid_size, y_min, y_max, y_grid_size)
    grid_cells = []
    for x in np.arange(x_min, x_max - x_grid_size, x_grid_size):
        for y in np.arange(y_min, y_max - y_grid_size, y_grid_size):
            grid_cells.append(box(x, y, x + x_grid_size, y + y_grid_size))
    # set_trace()
    return grid_cells


def generate_grid(rectangle, x_grid_size, y_grid_size):
    x_coords, y_coords = zip(*rectangle)
    x_min, x_max = min(x_coords), max(x_coords)
    y_min, y_max = min(y_coords), max(y_coords)
    # print(x_min, x_max, x_grid_size, y_min, y_max, y_grid_size)
    grid_cells = []
    for x in np.arange(np.floor(x_min / x_grid_size) * x_grid_size, np.ceil(x_max / x_grid_size) * x_grid_size, x_grid_size):
        for y in np.arange(np.floor(y_min / y_grid_size) * y_grid_size, np.ceil(y_max / y_grid_size) * y_grid_size, y_grid_size):
            grid_cells.append(box(x, y, x + x_grid_size, y + y_grid_size))
    return grid_cells

def generate_grid_rotated_rectangle(rectangle):
    rec_center = [np.mean([corner[i_coor] for corner in rectangle]) for i_coor in range(2)]
    center_points = {'box_id': [], 'stack_x': [], 'stack_y': []}
    four_corners = []
    for i_corner, corner in enumerate(rectangle):
        curr_center = [(rec_center[i_coor] + corner[i_coor]) / 2 for i_coor in range(2)]
        center_points['box_id'].append(i_corner)
        center_points['stack_x'].append(curr_center[0])
        center_points['stack_y'].append(curr_center[1])
        four_corner = {'box_id': [], 'stack_x': [], 'stack_y': []}
        four_corner['box_id'] = [i_corner for _ in range(4)]

        four_corner['stack_x'].append(corner[0])
        four_corner['stack_y'].append(corner[1])

        mid_side1 = [(corner[i_coor] + rectangle[(i_corner + 1) % 4][i_coor])/2 for i_coor in range(2)]
        four_corner['stack_x'].append(mid_side1[0])
        four_corner['stack_y'].append(mid_side1[1])

        four_corner['stack_x'].append(rec_center[0])
        four_corner['stack_y'].append(rec_center[1])

        mid_side2 = [(corner[i_coor] + rectangle[(i_corner + 3) % 4][i_coor])/2 for i_coor in range(2)]
        four_corner['stack_x'].append(mid_side2[0])
        four_corner['stack_y'].append(mid_side2[1])
        four_corner = pd.DataFrame(four_corner)

        four_corners.append(four_corner)
    return pd.DataFrame(center_points), pd.concat(four_corners)


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

def swap_rows(group):
    group = group.copy()
    if len(group) >= 4:  # Ensure the group has at least 4 rows
        group.iloc[2], group.iloc[3] = group.iloc[3].copy(), group.iloc[2].copy()
    return group

import pandas as pd
import numpy as np
import itertools


if __name__=="__main__":
    df = pd.read_csv('prefinal_grid_search_parallel.csv')
    params = pd.read_csv('prefinal_grid_parameters.csv').reset_index().rename(columns={'index': 'param_id'})
    df = df.sort_values(['active_modelled_max_ratio', 'aggregate_corr'], ascending = [True, False]).reset_index(drop = True)

    df = pd.merge(df, params,on = 'param_id')
    keep_cols=['aggregate_corr', 'active_modelled_max_ratio', 'active_modelled_min_ratio', 'sensitivity', 'Q0', 'Q1', 'Q2', 'H0', 'H1', 'H2', 'stack_x0', 'stack_y0', 'stack_x1', 'stack_y1', 'stack_x2', 'stack_y2']
    best_params = df[keep_cols].sort_values('aggregate_corr', ascending = False)[['Q0', 'Q1', 'Q2', 'H0', 'H1', 'H2', 'stack_x0', 'stack_y0', 'stack_x1', 'stack_y1', 'stack_x2', 'stack_y2']].head(1).reset_index(drop = True)

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
    stack_loc_names = {
        'stack_0_range': {'stack_x': 'stack_x0', 'stack_y': 'stack_y0'},
        'stack_1_range': {'stack_x': 'stack_x1', 'stack_y': 'stack_y1'},
        'stack_2_range': {'stack_x': 'stack_x2', 'stack_y': 'stack_y2'}
    }
    stack_loc_xy = get_stack_xy(stack_locs)
    set_anti_clockwise_order(stack_loc_xy)
    width_length = {}
    min_grid_size = float('inf')
    grid_cells = {}
    prod = 1
    
    selected_boxes = []
    for k, v in stack_loc_xy.items(): 
        width = euclidean_distance(v[0], v[1])
        height = euclidean_distance(v[1], v[2])
        if k in ['stack_0_range', 'stack_1_range']:
            curr_grid_cells = generate_grid_original(v, width / 2, height / 2)
            grid_cells[k] = filter_rotated(v, curr_grid_cells) 
            four_corners_raw = pd.DataFrame([ {"stack_x": coors[0], "stack_y": coors[1], 'box_id': i} for i, x in enumerate(grid_cells[k]) for coors in mapping(x)['coordinates'][0]]).drop_duplicates().sort_values(['box_id', 'stack_x', 'stack_y']).reset_index(drop = True).rename(columns = stack_loc_names[k])
            four_corners = four_corners_raw.groupby('box_id', group_keys=False).apply(swap_rows, include_groups=False)
            four_corners['box_id'] = four_corners_raw['box_id']
            # print(four_corners)
            center_points = four_corners.groupby('box_id')[list(stack_loc_names[k].values())].mean().reset_index()
        elif k == 'stack_2_range':
            center_points, four_corners = generate_grid_rotated_rectangle(v)
            center_points.rename(columns = stack_loc_names[k], inplace = True)
            four_corners.rename(columns = stack_loc_names[k], inplace = True)

        for col in stack_loc_names[k].values():
            center_points[col] = np.round(center_points[col], 11)
            best_params[col] = np.round(best_params[col], 11)
        
        selected_box = pd.merge(pd.merge(center_points, best_params.rename(columns = stack_loc_names[k])[list(stack_loc_names[k].values())], on = list(stack_loc_names[k].values()), how = 'inner'), four_corners, on = 'box_id', how = 'inner', suffixes = ['_center', '_grid'])
        selected_box['stack_id'] = k
        selected_boxes.append(selected_box.rename(columns = {x: re.sub(r'\d', '', x) for x in selected_box.columns}))
    # set_trace()
    selected_boxes = pd.concat(selected_boxes)
    # set_trace()
    selected_boxes.loc[selected_boxes['stack_id'] == 'stack_0_range', ['stack_x_grid', 'stack_y_grid']] 
    areas = selected_boxes.groupby('stack_id').apply(lambda x: polygon_area(x[['stack_x_grid', 'stack_y_grid']].values.tolist()), include_groups=False)
    total_points = np.ceil(1.2 * params.shape[0])
    grid_width = (areas.prod()/total_points) ** (1/6)
    # print(areas / grid_width / grid_width)
    new_stack_xys = {}
    for k in areas.index:
        full_grid_cells = generate_grid(stack_loc_xy[k], grid_width * 2, grid_width * 2)
        touching_grid_cells = filter_rotated(stack_loc_xy[k], full_grid_cells)
        # print(len(full_grid_cells), len(touching_grid_cells))
        new_stack_xys[k] = pd.DataFrame([x.centroid.coords[0] for x in touching_grid_cells], columns = ['stack_x', 'stack_y']).rename(columns = stack_loc_names[k])
        # print(new_stack_xys[k].shape)
    
    # Generate all combinations
    all_combinations = pd.DataFrame(list(itertools.product(
        new_stack_xys['stack_0_range'].to_records(index=False),
        new_stack_xys['stack_1_range'].to_records(index=False),
        new_stack_xys['stack_2_range'].to_records(index=False)
    )))
    # Unpack the combinations into separate columns
    all_combinations = pd.DataFrame({
        'stack_x0': all_combinations[0].str[0],
        'stack_y0': all_combinations[0].str[1],
        'stack_x1': all_combinations[1].str[0],
        'stack_y1': all_combinations[1].str[1],
        'stack_x2': all_combinations[2].str[0],
        'stack_y2': all_combinations[2].str[1]
    })
    for col in ['Q0', 'Q1', 'Q2', 'H0', 'H1', 'H2']:  all_combinations[col] = best_params[col].iloc[0]
    all_combinations.to_csv('all_combinations_prescaling.csv', index = False)
    set_trace()