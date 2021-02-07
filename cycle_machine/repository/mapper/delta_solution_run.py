import json

import jsonpickle

from cycle_machine.brain.delta.solution import DeltaSolutionRun


def mongo_friendly_serialize(dsr: DeltaSolutionRun) -> dict:
    my_dict = {
        'delta_points_cycles': json.loads(jsonpickle.encode(dsr.delta_points_cycles)),
        'cycle_ranks': json.loads(jsonpickle.encode(dsr.cycle_ranks)),
        'range_lines': json.loads(jsonpickle.encode(dsr.range_lines)),
        'average_rank': dsr.rank_average
    }

    return my_dict


def mongo_friendly_deserialize(solution_run_obj):
    if solution_run_obj is not None:
        solution_run_obj.pop('_id', None)

    return solution_run_obj
