import json
from datetime import datetime

import jsonpickle

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


def _cycle_first_delta_points(solution_run):
    cycles = solution_run['delta_points_cycles']['cycles']

    first_delta_points = []

    for c in cycles:
        first_delta_points.append(cycles[c][0])
        pass

    return first_delta_points


def _find_nearest_bar_index_for_time(series: [Bar], t: datetime):
    date_times = [b.date_time for b in series]
    closest_date = min(date_times, key=lambda x: abs(x - t))
    bar_index = date_times.index(closest_date)
    return bar_index


def _time_frame_coordinates_bar_indexes(overlay_series: [Bar], time_frame_coordinates_for_cycles, first_delta_point_for_cycles):
    high_overlays = {}
    low_overlays = {}

    for i in range(0, len(first_delta_point_for_cycles)):
        c = time_frame_coordinates_for_cycles[str(i)]
        i_str = str(i)
        high_overlays[str(i_str)] = {}
        low_overlays[str(i_str)] = {}

        if first_delta_point_for_cycles[i]['position'] == 'high':
            start_high = True
        else:
            start_high = False

        if first_delta_point_for_cycles[i]['inversion']:
            start_high = not start_high

        for k in c.keys():
            x1 = _find_nearest_bar_index_for_time(overlay_series, c[k][0])
            x2 = _find_nearest_bar_index_for_time(overlay_series, c[k][1])

            if start_high:
                high_overlays[i_str][k] = [x1, x2]
            else:
                low_overlays[i_str][k] = [x1, x2]

            start_high = not start_high

    return [high_overlays, low_overlays]


def compute_overlays(base_series: [Bar], overlay_series: [Bar], base_solution_run, overlay_solution_run):
    overlay_time_frame_coordinates = _cycle_time_coordinates(overlay_series, overlay_solution_run)
    cycle_first_delta_points = _cycle_first_delta_points(overlay_solution_run)

    high_overlays, low_overlays = _time_frame_coordinates_bar_indexes(base_series, overlay_time_frame_coordinates, cycle_first_delta_points)
    overlay_dict = {
        "high_overlays": high_overlays,
        "low_overlays": low_overlays,
        "period": overlay_solution_run['delta_points_cycles']['period']
    }

    return overlay_dict
