from SALib.sample import saltelli
from SALib.analyze import sobol
from SALib.test_functions import Ishigami
from simulation import Simulation
import numpy as np
import pandas as pd
from tqdm import tqdm
import sys
import argparse
import warnings
warnings.filterwarnings("ignore")

variables = [
    ('mean_age', 30, 50),
    ('risk_age', 40, 55),
    # ('critical_mortality_chance', 0.05, 0.2)
]

result_variables = [
    # 'timesteps',
    'dead',
    'recovered',
    # 'infected',
    # 'infectious',
    'unaffected',
]

labels = [x[0] for x in variables]

problem = {
  'num_vars': len(variables),
  'names': labels,
  'bounds': [[x[1], x[2]] for x in variables]
}

def get_prefixed_filename(prefix, filename):
    return filename if prefix is None else f'{prefix}_{filename}'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Computes parameter sensitivity')
    parser.add_argument('step', type=str, nargs='?', default='all', choices=['sim', 'sen', 'all'], help='Step name (sim - run simulations, sen - compute sensitivity)')
    parser.add_argument('-n', '--name', type=str, nargs=1, help='Analysis name')

    params = parser.parse_args()

    if params.step in ['all', 'sim']:
        print('Generating parameter sets')
        param_values = saltelli.sample(problem, 10, calc_second_order=False)

        inputs = [dict(zip(labels, v)) for v in param_values]

        results = []
        for i in tqdm(iterable=inputs, unit='simulation', desc='Running simulations'):
            sim = Simulation(kwargs=i)

            sim.Config.quiet = True
            sim.Config.visualise = False
            sim.Config.verbose = False
            sim.Config.simulation_steps = 500
            sim.Config.print_summary = False

            result = sim.run()
            result_dict = {f'r_{k}': v for k, v in result.items()}
            param_dict = {f'p_{k}': v for k, v in i.items()}

            results.append({**param_dict, **result_dict})

        df = pd.DataFrame(data = results)
        print('Saving simulations results')
        df.to_csv(get_prefixed_filename(params.name, 'results.csv'), index=False)

    if params.step in ['all', 'sen']:
        df = pd.read_csv(get_prefixed_filename(params.name, 'results.csv'))
        for rv in tqdm(iterable=result_variables, unit='variable', desc='Computing sensitivity'):
            Y = df[f'r_{rv}'].values
            Si = sobol.analyze(problem, Y, calc_second_order=False)
            sdf = pd.concat(Si.to_df(), axis=1)
            sdf.index.name = 'parameter'
            sdf.to_csv(get_prefixed_filename(params.name, f'{rv}_results.csv'))

    print('Done')