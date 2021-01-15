import argparse

from cycle_machine.brain.delta.config import DeltaSolutionConfig

parser = argparse.ArgumentParser(description='Solution interaction tools.')
parser.add_argument('--compute-symbol', dest='compute_symbol', required=True)

args = parser.parse_args()

delta_solution_config = DeltaSolutionConfig(args.compute_symbol)
periods = delta_solution_config.periods_asc()

for p in periods:
    calculator_config = delta_solution_config.delta_period_calculation_config(p)
    print(p)
    pass
