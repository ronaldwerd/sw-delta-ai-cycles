from datetime import datetime

import jsonpickle
import json

from cycle_machine.brain.repository import Repository
from cycle_machine.brain.series import Bar


def _cycle_time_coordinates(overlay_series: [Bar], overlay_solution_run):
    start_time = jsonpickle.loads(json.dumps(overlay_solution_run['delta_points_cycles']['start_time']))
    overlay_solution_run_cycle_numbers = overlay_solution_run['delta_points_cycles']['cycles'].keys()
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


def _cycle_inversion_identifiers(solution_run):
    cycles = solution_run['delta_points_cycles']['cycles']

    cycle_inversions = []

    for c in cycles:
        cycle_inversions.append(cycles[c][0]['inversion'])
        pass

    return cycle_inversions


def _find_nearest_bar_index_for_time(series: [Bar], t: datetime):
    date_times = [b.date_time for b in series]
    closest_date = min(date_times, key=lambda x: abs(x - t))
    bar_index = date_times.index(closest_date)
    return bar_index


def _time_frame_coordinates_bar_indexes(overlay_series: [Bar], time_frame_coordinates_for_cycles, inversions_for_cycles):
    for i in range(0, len(inversions_for_cycles)):
        c = time_frame_coordinates_for_cycles[str(i)]

        for k in c.keys():
            x1 = _find_nearest_bar_index_for_time(overlay_series, c[k][0])
            x2 = _find_nearest_bar_index_for_time(overlay_series, c[k][1])
            print("z")

        # _find_nearest_bar_index_for_time(overlay_series, c['1'][0])
        # x1 = _find_nearest_bar_index_for_time(overlay_series, c[k][0])
        # x2 = _find_nearest_bar_index_for_time(overlay_series, c[k][1])

        print("z")
        pass

    high_overlays = []
    low_overlays = []
    return [high_overlays, low_overlays]


def compute_overlays(base_series: [Bar], overlay_series: [Bar], base_solution_run, overlay_solution_run):
    overlay_time_frame_coordinates = _cycle_time_coordinates(overlay_series, overlay_solution_run)

    # base_solution_run
    # TODO the first cycle time and the base_solution_run start time should be the same!

    base_solution_run_start_time = jsonpickle.loads(json.dumps(base_solution_run['delta_points_cycles']['start_time']))
    cycles = overlay_solution_run['delta_points_cycles']['cycles']

    inversions_for_overlay_cycle = _cycle_inversion_identifiers(overlay_solution_run)

    _time_frame_coordinates_bar_indexes(base_series, overlay_time_frame_coordinates, inversions_for_overlay_cycle)

    # repository.load_series(overlay_solution_run['delta_points_cycles']['period'])

    print("z")
    # TODO: Overlay onto base_solution run....
    # TODO: Return best possible bars?

