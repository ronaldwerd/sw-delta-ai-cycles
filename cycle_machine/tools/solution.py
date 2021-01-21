import argparse
import timeit
import json
import jsonpickle

from cycle_machine.brain.delta import DeltaSolution
from cycle_machine.brain.delta.ai.overlays import compute_overlays
from cycle_machine.brain.delta.config import DeltaSolutionConfig
from cycle_machine.brain.repository import get_repository, MongoDbRepository
from cycle_machine.brain.repository.mapper.delta_solution_run import mongo_friendly_serialize, mongo_friendly_deserialize
from cycle_machine.brain.series import Bar

parser = argparse.ArgumentParser(description='Solution interaction tools.')
parser.add_argument('--symbol', dest='compute_symbol', required=True,
                    help="Example: EURUSD, USDCAD, USCASH500, GOLD")

parser.add_argument('-compute-cycles', action='store_true',
                    help="Compute delta points for cycles through machine learning (ML) and write to database.")

parser.add_argument('-compute-overlays', action='store_true',
                    help="Compute cycle overlays and write to database")

args = parser.parse_args()


delta_solution_config = DeltaSolutionConfig(args.compute_symbol)

data_repository = get_repository(delta_solution_config)
computation_results_repository = MongoDbRepository(delta_solution_config)

periods = delta_solution_config.periods_asc()

ds = DeltaSolution(args.compute_symbol)

if args.compute_cycles is True:
    print("Computing cycles for: " + args.compute_symbol)

    start = timeit.timeit()

    for p in periods:
        print("Loading period %d" % p, end=" ")
        calculator_config = delta_solution_config.delta_period_calculation_config(p)
        bar_sequence = data_repository.load_series(p)
        cycles_computed = 0

        print("and determining delta points for %d with %d cycle(s)" % (p, cycles_computed), end=" ")
        calc_result = ds.calculate_and_return_period(bar_sequence, p, 0)
        calc_result.compute_cycles()

        delta_solution_run_json_friendly_dict = mongo_friendly_serialize(calc_result.walk_through[-1])
        computation_results_repository.save_solution_run(p, delta_solution_run_json_friendly_dict)

    end = timeit.timeit()

    print("Time in something: %f" % (end - start))


if args.compute_overlays is not None:
    base_period = 1440
    overlay_period = 2880

    delta_solution_config = DeltaSolutionConfig(args.compute_symbol)
    repository = get_repository(delta_solution_config)

    base_solution_run = mongo_friendly_deserialize(repository.load_solution_run(base_period))
    overlay_solution_run = mongo_friendly_deserialize(repository.load_solution_run(overlay_period))

    overlay_2880 = compute_overlays(repository.load_series(1440), repository.load_series(2880), base_solution_run, overlay_solution_run)
    repository.save_solution_overlay(1440, overlay_2880)

    print("z")

    pass
