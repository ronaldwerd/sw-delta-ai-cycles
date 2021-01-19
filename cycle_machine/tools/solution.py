import argparse
import timeit
import json
import jsonpickle

from cycle_machine.brain.delta import DeltaSolution
from cycle_machine.brain.delta.config import DeltaSolutionConfig
from cycle_machine.brain.repository import get_repository, MongoDbRepository
from cycle_machine.brain.repository.mapper.delta_solution_run import mongo_friendly_serialize, mongo_friendly_deserialize

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
    def cycle_time_coordinates(overlay_solution_run):
        start_time = jsonpickle.loads(json.dumps(overlay_solution_run['delta_points_cycles']['start_time']))
        overlay_solution_run_cycle_numbers = overlay_solution_run['delta_points_cycles']['cycles'].keys()
        overlay_series = repository.load_series(overlay_solution_run['delta_points_cycles']['period'])
        overlay_truncate_index = overlay_series.index([b for b in overlay_series if b.date_time == start_time][0])
        cycle_time_coordinates = {}

        for c in overlay_solution_run_cycle_numbers:
            cycle_start_bar = (int(c) * overlay_solution_run['delta_points_cycles']['bars_in_cycle']) + overlay_truncate_index

            cycle_time_coordinates[c] = {}

            for range_line_key in overlay_solution_run['range_lines']:
                x1 = overlay_solution_run['range_lines'][range_line_key][0] + cycle_start_bar
                x2 = overlay_solution_run['range_lines'][range_line_key][1] + cycle_start_bar

                x1_time = overlay_series[x1].date_time
                x2_time = overlay_series[x2].date_time

                cycle_time_coordinates[c][range_line_key] = [x1_time, x2_time]

        return cycle_time_coordinates

    def cycle_inversion_identifiers(solution_run):
        cycles = solution_run['delta_points_cycles']['cycles']

        cycle_inversions = []

        for c in cycles:
            cycle_inversions.append(cycles[c][0]['inversion'])
            pass

        return cycle_inversions

    def compute_overlays(base_solution_run, overlay_solution_run):
        overlay_time_frame_coordinates = cycle_time_coordinates(overlay_solution_run)
        base_solution_run
        # TODO the first cycle time and the base_solution_run start time should be the same!

        base_solution_run_start_time = jsonpickle.loads(json.dumps(base_solution_run['delta_points_cycles']['start_time']))
        cycles = overlay_solution_run['delta_points_cycles']['cycles']

        inversions_for_overlay_cycle = cycle_inversion_identifiers(overlay_solution_run)

        print("z")
        # TODO: Overlay onto base_solution run....
        # TODO: Return best possible bars?


    base_period = 1440
    overlay_period = 2880

    delta_solution_config = DeltaSolutionConfig(args.compute_symbol)
    repository = get_repository(delta_solution_config)

    base_solution_run = mongo_friendly_deserialize(repository.load_solution_run(base_period))
    overlay_solution_run = mongo_friendly_deserialize(repository.load_solution_run(overlay_period))

    some_damn_result = range_lines_above = compute_overlays(base_solution_run, overlay_solution_run)

    print("z")

    pass
