import math


class DeltaPoint:
    def __init__(self, sequence, point_number, bar, bar_index, position, inversion):
        self.label = str(point_number)
        self.sequence = sequence
        self.point_number = point_number
        self.bar = bar
        self.bar_index = bar_index
        self.position = position
        self.inversion = inversion

        if inversion is True:
            self.label = "(" + self.label + ")"
            pass


class DeltaRange:
    def __init__(self, time_start, time_end, period, sequence):
        self.time_start = time_start
        self.time_end = time_end
        self.period = period
        self.sequence = sequence
        pass


class DeltaCycles:
    def __init__(self, start_time, period, assumed_point_count, distribution_count, distribution_bar_count, cycles):
        self.start_time = start_time
        self.period = period
        self.assumed_point_count = assumed_point_count
        self.distribution_count = distribution_count
        self.distribution_bar_count = distribution_bar_count
        self.bars_in_cycle = distribution_count * distribution_bar_count
        self.cycles = cycles

    def __len__(self):
        return len(self.cycles)

    def get_cycle_numbers(self):
        return list(self.cycles.keys())

    def get(self, cycle_number: int):
        if cycle_number in self.cycles:
            return self.cycles[cycle_number]

    def set(self, cycle_number: int, delta_points: []):
        self.cycles[cycle_number] = delta_points

    @staticmethod
    def rank_cycle(delta_points: [], range_lines):
        center_coordinates = {}
        ranks = {}

        # Get center coordinate for each range line. We will attempt to re-position the points as close as possible.
        for r in range_lines:
            coordinates = range_lines[r]
            center = ((coordinates[1] - coordinates[0]) / 2) + coordinates[0]
            center_coordinates[r] = math.ceil(center)

        # cycle = self.cycles[cycle_number]
        for dp in delta_points:
            if dp.inversion is False and dp.point_number in center_coordinates:
                ranks[dp.point_number] = abs(dp.bar_index - center_coordinates[dp.point_number])

        ranks['total'] = sum(ranks.values())
        return ranks
