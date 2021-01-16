import argparse

from cycle_machine.brain.delta import DeltaSolution
from cycle_machine.brain.delta.config import DeltaSolutionConfig
from cycle_machine.brain.repository import get_repository

parser = argparse.ArgumentParser(description='Solution interaction tools.')
parser.add_argument('--compute-symbol', dest='compute_symbol', required=True)

args = parser.parse_args()

delta_solution_config = DeltaSolutionConfig(args.compute_symbol)

repository = get_repository(delta_solution_config)
periods = delta_solution_config.periods_asc()

print("Computing cycles for: " + args.compute_symbol)

ds = DeltaSolution(args.compute_symbol)

for p in periods:
    print("Loading period %d" % p, end=" ")
    calculator_config = delta_solution_config.delta_period_calculation_config(p)
    bar_sequence = repository.load_series(p)
    cycles_computed = 0

    print("and determining delta points for %d with %d cycle(s)" % (p, cycles_computed), end=" ")
    calc_result = ds.calculate_and_return_period(bar_sequence, p, 0)
    calc_result.compute_cycles()
    print("z")
    break
