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


def convert_to_bool(value):
    if value is bool:
        return value
    else:
        return value >= 0.5


variables = [
    ('mean_age', 30, 50),
    ('max_age', 50, 110),
    ('proportion_wearing_masks', 0.0, 1.0),
    # ('proportion_distancing', 0.0, 0.1),
    ('healthcare_capacity', 0, 250),
    ('self_isolate_proportion', 0.0, 1.0),
    # ('test_chances'),
    ('lockdown', 0, 1, convert_to_bool),
    ('lockdown_percentage', 0.005, 0.5),
    ('lockdown_compliance', 0.50, 100)
]

variable_converters = {x[0]: x[3] for x in variables if len(x) == 4}

result_variables = [
    'timesteps',
    'dead',
    'recovered',
    'infected',
    'infectious',
    'unaffected',
]

labels = [x[0] for x in variables]

problem = {
  'num_vars': len(variables),
  'names': labels,
  'bounds': [[x[1], x[2]] for x in variables]
}


def param_values_to_inputs(param_values):
    def convert(label, value):
        converter = variable_converters.get(label)
        if converter:
            return (label, converter(value))
        else:
            return (label, value)

    return [dict([convert(l, v) for l, v in zip(labels, values)]) for values in param_values]


def get_prefixed_filename(prefix, filename):
    return filename if prefix is None else f'{prefix}_{filename}'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Computes parameter sensitivity')
    parser.add_argument('step', type=str, nargs='?', default='all', choices=['sim', 'sen', 'all'], help='Step name (sim - run simulations, sen - compute sensitivity)')
    parser.add_argument('-n', '--name', type=str, nargs=1, help='Analysis name')

    params = parser.parse_args()
    experiment_name = None if params.name is None else params.name[0]

    if params.step in ['all', 'sim']:
        print('Generating parameter sets')
        param_values = saltelli.sample(problem, 1000, calc_second_order=True)

        inputs = param_values_to_inputs(param_values)

        results = []
        for i in tqdm(iterable=inputs, unit='simulation', desc='Running simulations'):
            sim = Simulation(kwargs=i)

            sim.Config.quiet = True
            sim.Config.visualise = False
            sim.Config.verbose = False
            sim.Config.simulation_steps = 1000
            sim.Config.print_summary = False

            result = sim.run()
            result_dict = {f'r_{k}': v for k, v in result.items()}
            param_dict = {f'p_{k}': v for k, v in i.items()}

            results.append({**param_dict, **result_dict})

        df = pd.DataFrame(data = results)
        print('Saving simulations results')
        df.to_csv(get_prefixed_filename(experiment_name, 'results.csv'), index=False)

    if params.step in ['all', 'sen']:
        df = pd.read_csv(get_prefixed_filename(experiment_name, 'results.csv'))
        for rv in tqdm(iterable=result_variables, unit='variable', desc='Computing sensitivity'):
            Y = df[f'r_{rv}'].values
            Si = sobol.analyze(problem, Y, calc_second_order=True)
            sdf = pd.concat(Si.to_df(), axis=1)
            sdf.index.name = 'parameter'
            sdf.to_csv(get_prefixed_filename(experiment_name, f'{rv}_results.csv'))

    print('Done')