import argparse

from cycle_machine.brain.delta.config import DeltaSolutionConfig
from cycle_machine.brain.repository import get_repository

parser = argparse.ArgumentParser(description='Solution interaction tools.')
parser.add_argument('--compute-symbol', dest='compute_symbol', required=True)

args = parser.parse_args()

delta_solution_config = DeltaSolutionConfig(args.compute_symbol)

repository = get_repository(delta_solution_config)
periods = delta_solution_config.periods_asc()

print("Computing cycles for: " + args.compute_symbol)

for p in periods:
    calculator_config = delta_solution_config.delta_period_calculation_config(p)
    bar_sequence = repository.load_series(p)
    pass