#!/usr/bin/env python3
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from pdb import set_trace
import pandas as pd
import numpy as np

class Comparison:
    def __init__(self,
                 simulation_data):
        simulation_data['ppb'] = 24.45 * simulation_data['Concentration_µg'] / 78.11
        self.simulation_data = simulation_data

        data_dir = '/home/yuan/Arch/'

        active_file = data_dir + 'actual conc.csv'
        active = pd.read_csv(active_file, header = 0)
        active.columns = ['Sampling Location', 'X', 'Y', 'ppb']
        active = active.loc[active['Sampling Location'] !='Company C'].reset_index(drop = True)
        active = active.dropna().drop([0]).reset_index(drop = True)
        for col in ['X', 'Y', 'ppb']: active[col] = active[col].astype(float)
        self.active_data = active


        passive_file = data_dir + 'Benzene concentration in ppb.xlsx'
        passive = []
        for cycle in range(1, 6):
            curr_c = 'cycle ' + str(cycle)
            curr = pd.read_excel(passive_file, sheet_name = curr_c)
            curr['Cycle'] = curr_c
            key_col = [x for x in curr.columns if 'Benzene' in x]
            assert len(key_col) == 1
            curr.rename(columns = {key_col[0]: 'Benzene'}, inplace = True)
            passive.append(curr[['Cycle', 'X', 'Y', 'Benzene']])
        passive = pd.concat(passive)

        self.passive_data = passive
        self.detail_diffs = {}
        self.corrs = {}
        self.num_points = {}

    def find_simulation_data_corners(self):
        points_x = self.simulation_data['X'].tolist()
        points_y = self.simulation_data['Y'].tolist()
        points = np.column_stack((points_x, points_y))
        centroid = np.mean(points, axis=0)
        self.simulation_data['Dist'] = np.sqrt((self.simulation_data['X'] - centroid[0])**2 + (self.simulation_data['Y'] - centroid[1])**2)
        self.simulation_data.sort_values('Dist', ascending = False, inplace = True)
        self.corner1 = self.simulation_data[['X', 'Y']].iloc[0].values
        self.corner2 = self.simulation_data[['X', 'Y']].iloc[1].values
        self.corner3 = self.simulation_data[['X', 'Y']].iloc[2].values
        self.corner4 = self.simulation_data[['X', 'Y']].iloc[3].values
        self.polygon = Polygon([tuple(self.corner1), tuple(self.corner3), tuple(self.corner4), tuple(self.corner2)])


    def find_nearest(self, sampling_type):
        if sampling_type == 'active':
            sampling_data = self.active_data
        elif sampling_type == 'passive':
            sampling_data = self.passive_data

        results = []
        for _, row in sampling_data.iterrows():
            x2, y2 = float(row['X']), float(row['Y'])
            distances = np.sqrt((self.simulation_data['X'] - x2)**2 + (self.simulation_data['Y'] - y2)**2)
            min_index = distances.idxmin()
            nearest_row = self.simulation_data.loc[min_index]

            is_within_rectangle = self.polygon.contains(Point(x2, y2))
            result = {
                'Nearest X': nearest_row['X'],
                'Nearest Y': nearest_row['Y'],
                'Distance': distances[min_index],
                'Nearest ppb': nearest_row['ppb'],
                'Within Rectangle':  is_within_rectangle
            }
            if is_within_rectangle:
                results.append({**result, **row.to_dict()})

        self.num_points[sampling_type] = len(results)
        self.detail_diffs[sampling_type] = pd.DataFrame(results)
         

    def calculate_correlation(self, sampling_type):
        sample_detail = self.detail_diffs[sampling_type]
        # print("Number of observations selected: ", sampling_type, self.num_points[sampling_type])
        
        if sampling_type == 'active':
            try:
                self.corrs[sampling_type] = [sample_detail[['ppb', 'Nearest ppb']].corr().iloc[0, 1]]
                self.active_modelled_range_ratio = {'max' : sample_detail[ 'Nearest ppb'].max() / sample_detail['ppb'].max(), 'min': sample_detail[ 'Nearest ppb'].min() / sample_detail['ppb'].min()}
            except:
                if self.num_points[sampling_type] == 0:
                    self.corrs[sampling_type] = -1
        elif sampling_type == 'passive':
            self.corrs[sampling_type] = {}
            for curr_cycle in sample_detail['Cycle'].unique():
                curr = sample_detail.loc[sample_detail['Cycle'] == curr_cycle]
                try:
                    self.corrs[sampling_type][curr_cycle] = curr[['Benzene', 'Nearest ppb']].corr().iloc[0, 1]
                except:
                    if self.num_points[sampling_type] == 0:
                        self.corrs[sampling_type][curr_cycle] = -1

    def compare_passive_data(self):
        for cycle in self.passive_data['Cycle'].unique():
            curr_data = self.passive_data[self.passive_data['Cycle'] == cycle]
            fig, ax = plt.subplots()
            ax.scatter(
                x=curr_data['Nearest ppb'].rank(),
                y=curr_data['Benzene'].rank(),
                color='blue',
                marker='o',
                s=50,
                alpha=0.6,
                edgecolors='w'
            )
            curr_corr = curr_data[['Benzene', 'Nearest ppb']].corr().iloc[0, 1]
            ax.plot(ax.get_xlim(), ax.get_ylim(), 'k-', alpha=0.75, zorder=0)
            plt.title(f"Passive Sampling {cycle} vs Modelled Benzene Rank, Corr = {curr_corr:.4f}")
            plt.xlabel("Passive Sampling Rank")
            plt.ylabel("Modelled Rank")
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(f"passive_{cycle}.png", dpi=600)
            plt.close()

def run_comparison(simulation_data):
    comp = Comparison(simulation_data)
    comp.find_simulation_data_corners()
    for sampling_type in ['active', 'passive']:
        comp.find_nearest(sampling_type)
        comp.calculate_correlation(sampling_type)
    return comp

def run_test_comparison():
    data_dir = '/home/yuan/Arch/'
    model_file = data_dir + 'Output_2024-6-24_17-43-28.csv'
    simulation_data = pd.read_csv(model_file)
    comp = Comparison(simulation_data)
    comp.find_simulation_data_corners()

    # data1 = pd.read_csv('~/tmp.csv')
    # data2 = pd.merge(data1, comp.detail_diffs['active'], on = ['Sampling Location', 'X', 'Y', 'Within Rectangle'])
    # test_cols = [x for x in data2.columns if '_x' in x]
    # for col in test_cols: assert np.isclose((data2[col] - data2[col.replace('_x', '_y')]).abs().max(), 0, atol = 1e-10)
    # active.to_csv('~/tmp.csv', index = False)
    for sampling_type in ['active', 'passive']:
        comp.find_nearest(sampling_type)
        comp.calculate_correlation(sampling_type)

    assert np.isclose(comp.corrs['active'], 0.6838926447305695, atol = 1e-10)
    passive_corrs = [0.7111048730173786, 0.5663054239924209, 0.5760478346787296, 0.3896606272245846, 0.6587413725166882]
    for i, pcorr in enumerate(passive_corrs):
        assert np.isclose(comp.corrs['passive cycle ' + str(i+1)], pcorr, atol = 1e-10)

def aggregate_corr(corrs):
    assert -1 not in set(corrs['active']).union(set(corrs['passive'].values()))
    return 0.5 * corrs['active'][0] + sum(corrs['passive'].values()) * 0.1

if __name__ == "__main__":
    run_test_comparison()

