from SALib.sample import saltelli
from SALib.analyze import sobol
from SALib.test_functions import Ishigami
from simulation import Simulation
import numpy as np
import pandas as pd


variables = [
    ('mean_age', 30, 50),
    ('risk_age', 40, 55),
    ('critical_mortality_chance', 0.05, 0.2)
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


if __name__ == '__main__':
    sim = Simulation(pop_size = 500)

    sim.Config.quiet = True
    sim.Config.visualise = False
    sim.Config.verbose = False
    sim.Config.simulation_steps = 500
    sim.Config.print_summary = False
    res = sim.run()
    print(res)

    # param_values = saltelli.sample(problem, 10, calc_second_order=True)

    # inputs = [dict(zip(labels, v)) for v in param_values]
    # results = []

    # for i in inputs:
    #     sim = Simulation(kwargs=i)

    #     sim.Config.visualise = False
    #     sim.Config.verbose = False
    #     sim.Config.simulation_steps = 500
    #     sim.Config.print_summary = False

    #     result = sim.run()

    # df = pd.DataFrame(data = results)
    # df.to_csv('results.csv')

    # for rv in result_variables:
    #     Y = df[rv].values
    #     Si = sobol.analyze(problem, Y, print_to_console=True)
    #     sdf = Si.to_df()
    #     sdf.to_csv(f'{rv}_results.csv')