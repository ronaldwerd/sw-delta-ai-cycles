import math
import numpy as np

from cycle_machine.brain.delta.objects import DeltaCycles


def calculate_range_lines(delta_cycles: DeltaCycles):
    cycle_manifest = {}
    ranges = {}

    if len(delta_cycles) == 0:
        return None

    cycle_numbers = delta_cycles.get_cycle_numbers()
    c0 = cycle_numbers[0]

    for dp in delta_cycles.get(c0):
        if dp.inversion is False:
            cycle_manifest[dp.point_number] = []

    for c in cycle_numbers:
        for dp in delta_cycles.get(c):
            if dp.inversion is False:
                if dp.point_number in cycle_manifest:
                    cycle_manifest[dp.point_number].append(dp.bar_index)

    for c in cycle_manifest:
        points = cycle_manifest[c]
        std = np.std(points)
        mean = np.mean(points)
        range_start = math.floor(mean - std)
        range_end = math.floor(mean + std)
        ranges[c] = (range_start, range_end)

    return ranges
