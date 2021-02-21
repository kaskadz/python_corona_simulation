import os
import sys
import pandas as pd
from tqdm import tqdm
from simulation import Simulation
import warnings
warnings.filterwarnings("ignore")

paramsets_file = 'paramsets.csv'
def load_paramsets_if_present():
    return pd.read_csv(paramsets_file, index_col=0) if os.path.isfile(paramsets_file) else None

def result_file_exists(result_id):
    return os.path.isfile(f'results/r_{result_id}.csv')

if __name__ == '__main__':
    paramsets = load_paramsets_if_present()
    assert paramsets is not None

    for setid in tqdm(sys.argv[1:]):
        if not result_file_exists(setid):
            param_dict = paramsets.loc[setid].dropna().to_dict()
            param_dict['quiet'] = True
            param_dict['visualize'] = False
            param_dict['verbose'] = False
            param_dict['print_sum'] = False
            param_dict['run_id'] = setid
            param_dict['simulation_steps'] = 2000
            sim = Simulation(**param_dict)
            sim.run()