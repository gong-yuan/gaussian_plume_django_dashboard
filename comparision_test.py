#!/usr/bin/env python3

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
    set_trace()

if __name__ == "__main__":
    run_test_comparison()
