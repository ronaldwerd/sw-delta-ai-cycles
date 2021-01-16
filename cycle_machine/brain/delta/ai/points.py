import copy
import math
import operator
import itertools
import numpy as np
from operator import itemgetter
from sortedcontainers import SortedDict
from pprint import pprint

from cycle_machine.brain.delta.ai import helpers
from cycle_machine.brain.delta.objects import DeltaPoint


def _cross_find(highs, lows, pos, x1, x2):
    cx1 = copy.deepcopy(x1 + 1)
    cx2 = copy.deepcopy(x2 - 1)

    cx1_arr = [cx1]
    cx2_arr = [cx2]

    l_slope_index = 1
    r_slope_index = 1

    while cx1 < cx2:
        if pos == 'high':
            while bool(cx1 + l_slope_index + 1 < len(lows) - 1) and lows[cx1 + l_slope_index + 1] < lows[cx1 + l_slope_index]:
                l_slope_index = l_slope_index + 1

            next_l = cx1 + l_slope_index

            if cx2_arr[-1] - 1 - next_l < 2:
                cx1 = next_l
            else:
                # cx1 = int(highs[next_l:x2].argmax()) + next_l
                cx1 = int(highs[next_l:cx2_arr[-1]].argmax()) + next_l
                l_slope_index = 1

            cx1_arr.append(cx1)

            while bool(cx2 - r_slope_index - 1) > 0 and highs[cx2 - r_slope_index - 1] > highs[cx2 - r_slope_index]:
                r_slope_index = r_slope_index + 1

            next_r = cx2 - r_slope_index - 1

            if next_r - cx1_arr[-1] < 2:
                cx2 = next_r
            else:
                # cx2 = int(lows[x1:next_r].argmin()) + x1
                cx2 = int(lows[cx1_arr[-1]:next_r].argmin()) + x1
                r_slope_index = 1

            cx2_arr.append(cx2)

        if pos == 'low':
            while bool(cx1 + l_slope_index + 1 < len(highs) - 1) and highs[cx1 + l_slope_index + 1] > highs[cx1 + l_slope_index]:
                l_slope_index = l_slope_index + 1

            next_l = cx1 + l_slope_index

            if cx2_arr[-1] - 1 - next_l < 2:
                cx1 = next_l
            else:
                # cx1 = int(lows[next_l:x2].argmin()) + next_l
                cx1 = int(lows[next_l:cx2_arr[-1]].argmin()) + next_l
                l_slope_index = 1

            cx1_arr.append(cx1)

            while bool(cx2 - r_slope_index - 1) > 0 and lows[cx2 - r_slope_index - 1] < lows[cx2 - r_slope_index]:
                r_slope_index = r_slope_index + 1

            next_r = cx2 - r_slope_index - 1

            if next_r - cx1_arr[-1] < 2:
                cx2 = next_r
            else:
                # cx2 = int(highs[x1:next_r].argmax()) + x1
                cx2 = int(highs[cx1_arr[-1]:next_r].argmax()) + x1
                r_slope_index = 1
            pass

            cx2_arr.append(cx2)

        if cx2_arr[-1] < x1:
            del cx1_arr[-1]
            del cx2_arr[-1]

        if cx1_arr[-1] > x2:
            del cx1_arr[-1]
            del cx2_arr[-1]

        cx1_arr[-1] = max(0, cx1_arr[-1])
        cx2_arr[-1] = max(0, cx2_arr[-1])

    return cx1_arr, cx2_arr


def _get_ranges_from_deltas(deltas, bars_in_cycle):
    chomped_keys = list(deltas.keys())[:-1]

    ic = 1
    ranges = []
    for i in list(chomped_keys):
        next_i = list(deltas.keys())[ic]

        r = i - next_i
        if r < 0:
            x1 = i
            x2 = next_i
        else:
            x1 = next_i
            x2 = i

        if ic == 1:
            ranges.append([0, x1])
            pass

        r = [x1, x2]
        ranges.append(r)

        if ic == len(list(chomped_keys)):
            ranges.append([x2, bars_in_cycle])
            pass

        ic = ic + 1

    return ranges


def _high_and_low(path_l, path_r, highs, lows, pos, scan_x1, scan_x2):
    x1, x2 = sorted([path_l[-1], path_r[-1]])

    if x1 == x2:
        return x1, x2

    if pos == 'high':
        if x1 + 1 >= scan_x2 - 1:
            hi = int(highs[scan_x1 + 1: scan_x2 - 1].argmax()) + scan_x1 + 1
        else:
            hi = int(highs[x1 + 1:scan_x2 - 1].argmax()) + x1 + 1
        if scan_x1 + 1 >= hi - 1:
            li = int(lows[scan_x1 + 1:scan_x2 - 1].argmin()) + scan_x1 + 1
        else:
            li = int(lows[scan_x1 + 1:hi].argmin()) + scan_x1 + 1

        if scan_x2 - 1 - li + 1 > 2:
            hi = int(highs[li + 1:scan_x2 - 1].argmax()) + li + 1

        if hi < li:
            li = hi
    else:
        if x1 + 1 >= scan_x2 - 1:
            li = int(lows[scan_x1 + 1:scan_x2 - 1].argmin()) + scan_x1 + 1
        else:
            li = int(lows[x1 + 1:scan_x2 - 1].argmin()) + x1 + 1
        if scan_x1 + 1 >= li - 1:
            hi = int(highs[scan_x1 + 1:scan_x2 - 1].argmax()) + scan_x1 + 1
        else:
            hi = int(highs[scan_x1 + 1:li].argmax()) + scan_x1 + 1

        if scan_x2 - 1 - hi + 1 > 2:
            li = int(lows[hi + 1:scan_x2 - 1].argmin()) + hi + 1

        if hi > li:
            hi = li

    return hi, li


# We are going to use a list of classes to store ranks. Some ranks will be the same but have different price deltas.
class DeltaComboRank:
    def __init__(self, bar_rank, high_point, low_point, price_delta):
        self.price_delta = price_delta
        self.bar_rank = bar_rank
        self.high_point = high_point
        self.low_point = low_point


class PointsHighLowSequence:
    def __init__(self, cycle_bars: []):
        self.cycle_bars = cycle_bars
        self.bars_in_cycle = len(cycle_bars)
        self.highs = np.array([b.high for b in cycle_bars])
        self.lows = np.array([b.low for b in cycle_bars])

        self.highs_and_lows = []
        pass

    def __len__(self):
        return len(self.highs_and_lows)

    def count_points_in_range(self, x1, x2):
        count = 0

        for p in self.highs_and_lows:
            if x1 <= p[0] <= x2:
                count = count + 1

        return count

    @staticmethod
    def _invert_high_low_str(str_value):
        if str_value == 'high':
            return 'low'

        if str_value == 'low':
            return 'high'

        return None

    def keys(self):
        return [bi[0] for bi in self.highs_and_lows]

    def add_points(self, high_point, low_point):
        t_high = [high_point, 'high']
        t_low = [low_point, 'low']

        self.highs_and_lows.append(t_high)
        self.highs_and_lows.append(t_low)

        # Until I figure this out using lambda sort function, this is the raw way.
        self.highs_and_lows.sort(key=lambda tup: tup[0])

        previous_delta = self.highs_and_lows[0]
        for i in range(1, len(self.highs_and_lows)):
            next_delta = self.highs_and_lows[i]
            if previous_delta[1] == 'high' and next_delta[1] == 'high':
                next_delta[1] = 'low'

            if previous_delta[1] == 'low' and next_delta[1] == 'low':
                next_delta[1] = 'high'

            previous_delta = next_delta

    def get_bar_distances(self):
        bar_index_ranges_flat = [0] + self.keys() + [self.bars_in_cycle - 1]
        bar_index_ranges_tup = []

        for bi in range(1, len(bar_index_ranges_flat)):
            tup = (bar_index_ranges_flat[bi - 1], bar_index_ranges_flat[bi])
            bar_index_ranges_tup.append(tup)

        return bar_index_ranges_tup

    def get_position_for_coordinates(self, x1, x2):
        if x1 == 0:
            if 0 in [p[0] for p in self.highs_and_lows]:
                return self.highs_and_lows[0][1]
            else:
                return self._invert_high_low_str(self.highs_and_lows[0][1])

        if x2 == self.bars_in_cycle - 1:
            if self.bars_in_cycle - 1 in [p[0] for p in self.highs_and_lows]:
                return self._invert_high_low_str(self.highs_and_lows[-1][1])
            else:
                return self.highs_and_lows[-1][1]

        last_t = self.highs_and_lows[0]
        for t in self.highs_and_lows[1:]:
            if last_t[0] == x1:
                if t[0] == x2:
                    return last_t[1]
            last_t = t

        raise ValueError("Coordinates %d, %d are not found." % (x1, x2))

    def trim(self):
        def __trim():
            for i in range(0, len(self.highs_and_lows)):
                tup = self.highs_and_lows[i]

                if tup[0] <= 2 or tup[0] >= self.bars_in_cycle - 3:
                    self.highs_and_lows.pop(i)
                    return True

            return False
        while __trim() is True:
            pass

    @staticmethod
    def attempt_high_low_rule_enforcement(highs, lows, highs_and_lows, bars_in_cycle):
        for i in range(len(highs_and_lows) - 2):
            k1 = highs_and_lows[i]
            km = highs_and_lows[i + 1]
            k3 = highs_and_lows[i + 2]

            if k1[1] == k3[1] and k1[1] == 'low' and km[1] == 'high':
                real_high = int(highs[k1[0]:k3[0] + 1].argmax() + k1[0])

                if real_high != km[0] and [i[0] for i in highs_and_lows].count(real_high) < 2:
                    km[0] = real_high
                    return True

            if k1[1] == k3[1] and k1[1] == 'high' and km[1] == 'low':
                real_low = int(lows[k1[0]:k3[0] + 1].argmin() + k1[0])

                if real_low != km[0] and [i[0] for i in highs_and_lows].count(real_low) < 2:
                    km[0] = real_low
                    return True

        # Ensure the edges are correct
        if highs_and_lows[0][1] == 'high' and highs_and_lows[0][0] > 2:
            real_high = int(highs[0:highs_and_lows[1][0]].argmax())

            if real_high != highs_and_lows[0][0]:
                highs_and_lows[0][0] = real_high
                return True

        if highs_and_lows[0][1] == 'low' and highs_and_lows[0][0] > 2:
            real_low = int(lows[0:highs_and_lows[1][0]].argmin())

            if real_low != highs_and_lows[0][0]:
                highs_and_lows[0][0] = real_low
                return True

        # last delta to the end of the cycle
        if highs_and_lows[-1][1] == 'high':
            real_high = int(highs[highs_and_lows[-2][0]:bars_in_cycle].argmax() + highs_and_lows[-2][0])

            if real_high != highs_and_lows[-1][0]:
                highs_and_lows[-1][0] = real_high
                return True

        if highs_and_lows[-1][1] == 'low':
            _lows = lows
            real_low = int(_lows[highs_and_lows[-2][0]:bars_in_cycle].argmin() + highs_and_lows[-2][0])

            if real_low != highs_and_lows[-1][0]:
                highs_and_lows[-1][0] = real_low
                return True
        return False

    def enforce_high_low_rules(self):
        passes = 0
        while self.attempt_high_low_rule_enforcement(self.highs, self.lows, self.highs_and_lows, self.bars_in_cycle):
            passes = passes + 1

    @staticmethod
    def attempt_high_low_rule_enforcement_special(highs, lows, highs_and_lows, bars_in_cycle):

        def find_qualified_high(x1, x2):
            nonlocal highs, highs_and_lows
            same_bar_qualifier_left = 0
            same_bar_qualifier_right = 0

            if x1 != 0:
                if highs[x1] < highs[x1 - 1]:
                    same_bar_qualifier_left = 1

            if x2 != len(highs) - 1:
                if highs[x2] < highs[x2 + 1]:
                    same_bar_qualifier_right = 1

            scan_x1 = x1 + same_bar_qualifier_left
            scan_x2 = x2 + 1 - same_bar_qualifier_right

            if scan_x2 - scan_x1 < 1:
                scan_x1 = x1
                scan_x2 = x2

            return int(highs[scan_x1:scan_x2].argmax() + scan_x1)

        def find_qualified_low(x1, x2):
            nonlocal lows, highs_and_lows
            same_bar_qualifier_left = 0
            same_bar_qualifier_right = 0

            if x1 != 0:
                if lows[x1] > lows[x1 - 1]:
                    same_bar_qualifier_left = 1

            if x2 != len(lows) - 1:
                if lows[x2] > lows[x2 + 1]:
                    same_bar_qualifier_right = 1

            scan_x1 = x1 + same_bar_qualifier_left
            scan_x2 = x2 + 1 - same_bar_qualifier_right

            if scan_x2 - scan_x1 < 1:
                scan_x1 = x1
                scan_x2 = x2

            return int(lows[scan_x1:scan_x2].argmin() + scan_x1)

        for i in range(len(highs_and_lows) - 2):
            k1 = highs_and_lows[i]      # LEFT
            km = highs_and_lows[i + 1]  # MIDDLE
            k3 = highs_and_lows[i + 2]  # RIGHT

            if k1[1] == k3[1] and k1[1] == 'low' and km[1] == 'high':
                real_high = find_qualified_high(k1[0], k3[0])

                if real_high != km[0] and [i[0] for i in highs_and_lows].count(real_high) < 2:
                    km[0] = real_high
                    return True

            if k1[1] == k3[1] and k1[1] == 'high' and km[1] == 'low':
                real_low = find_qualified_low(k1[0], k3[0])

                if real_low != km[0] and [i[0] for i in highs_and_lows].count(real_low) < 2:
                    km[0] = real_low
                    return True

        # Ensure the edges are correct
        if highs_and_lows[0][1] == 'high' and highs_and_lows[0][0] > 2:
            real_high = int(highs[0:highs_and_lows[1][0]].argmax())

            if real_high != highs_and_lows[0][0]:
                highs_and_lows[0][0] = real_high
                return True

        if highs_and_lows[0][1] == 'low' and highs_and_lows[0][0] > 2:
            real_low = int(lows[0:highs_and_lows[1][0]].argmin())

            if real_low != highs_and_lows[0][0]:
                highs_and_lows[0][0] = real_low
                return True

        # last delta to the end of the cycle
        if highs_and_lows[-1][1] == 'high':
            real_high = int(highs[highs_and_lows[-2][0]:bars_in_cycle].argmax() + highs_and_lows[-2][0])

            if real_high != highs_and_lows[-1][0]:
                highs_and_lows[-1][0] = real_high
                return True

        if highs_and_lows[-1][1] == 'low':
            _lows = lows
            real_low = int(_lows[highs_and_lows[-2][0]:bars_in_cycle].argmin() + highs_and_lows[-2][0])

            if real_low != highs_and_lows[-1][0]:
                highs_and_lows[-1][0] = real_low
                return True
        return False

    def enforce_high_low_rules_special(self):
        # self.attempt_high_low_rule_enforcement_special(self.highs, self.lows, self.highs_and_lows, self.bars_in_cycle)
        passes = 0
        while self.attempt_high_low_rule_enforcement_special(self.highs, self.lows, self.highs_and_lows, self.bars_in_cycle):
            passes = passes + 1

        # print("Made passes: " + str(passes))

    def enforce_high_low_rules_special_2(self):
        def attempt_high_low_rule_enforcement_special_2(highs, lows, highs_and_lows, bars_in_cycle):

            def find_qualified_high_2(x1, x2):
                nonlocal highs, highs_and_lows
                same_bar_qualifier_left = 0
                same_bar_qualifier_right = 0

                if x1 != 0:
                    if highs[x1] < highs[x1 - 1]:
                        same_bar_qualifier_left = 1

                if x2 != len(highs) - 1:
                    if highs[x2] < highs[x2 + 1]:
                        same_bar_qualifier_right = 1

                scan_x1 = x1 + same_bar_qualifier_left
                scan_x2 = x2 + 1 - same_bar_qualifier_right

                if scan_x2 - scan_x1 < 1:
                    scan_x1 = x1
                    scan_x2 = x2

                if x1 == x2:
                    print("Something is too tight...")
                    return highs[x1]

                return int(highs[scan_x1:scan_x2].argmax() + scan_x1)

            def find_qualified_low_2(x1, x2):
                nonlocal lows, highs_and_lows
                same_bar_qualifier_left = 0
                same_bar_qualifier_right = 0

                if x1 != 0:
                    if lows[x1] > lows[x1 - 1]:
                        same_bar_qualifier_left = 1

                if x2 != len(lows) - 1:
                    if lows[x2] > lows[x2 + 1]:
                        same_bar_qualifier_right = 1

                scan_x1 = x1 + same_bar_qualifier_left
                scan_x2 = x2 + 1 - same_bar_qualifier_right

                if scan_x2 - scan_x1 < 1:
                    scan_x1 = x1
                    scan_x2 = x2

                if x1 == x2:
                    print("Something is too tight...")
                    return highs[x1]

                return int(lows[scan_x1:scan_x2].argmin() + scan_x1)

            #
            # WTF IS GOING ON WITH THIS DAMN FUNCTION????
            #

            for i in range(len(highs_and_lows) - 2):
                k1 = highs_and_lows[i]      # LEFT
                km = highs_and_lows[i + 1]  # MIDDLE
                k3 = highs_and_lows[i + 2]  # RIGHT

                if k1[1] == k3[1] and k1[1] == 'low' and km[1] == 'high':
                    real_high = find_qualified_high_2(k1[0], k3[0])

                    if real_high != km[0] and [i[0] for i in highs_and_lows].count(real_high) < 2:
                        km[0] = real_high
                        return True

                if k1[1] == k3[1] and k1[1] == 'high' and km[1] == 'low':
                    real_low = find_qualified_low_2(k1[0], k3[0])

                    if real_low != km[0] and [i[0] for i in highs_and_lows].count(real_low) < 2:
                        km[0] = real_low
                        return True

            # Ensure the edges are correct
            if highs_and_lows[0][1] == 'high' and highs_and_lows[0][0] > 2:
                real_high = int(highs[0:highs_and_lows[1][0]].argmax())

                if real_high != highs_and_lows[0][0]:
                    highs_and_lows[0][0] = real_high
                    return True

            if highs_and_lows[0][1] == 'low' and highs_and_lows[0][0] > 2:
                real_low = int(lows[0:highs_and_lows[1][0]].argmin())

                if real_low != highs_and_lows[0][0]:
                    highs_and_lows[0][0] = real_low
                    return True

            # last delta to the end of the cycle
            if highs_and_lows[-1][1] == 'high':
                real_high = int(highs[highs_and_lows[-2][0]:bars_in_cycle].argmax() + highs_and_lows[-2][0])

                if real_high != highs_and_lows[-1][0]:
                    highs_and_lows[-1][0] = real_high
                    return True

            if highs_and_lows[-1][1] == 'low':
                _lows = lows
                real_low = int(_lows[highs_and_lows[-2][0]:bars_in_cycle].argmin() + highs_and_lows[-2][0])

                if real_low != highs_and_lows[-1][0]:
                    highs_and_lows[-1][0] = real_low
                    return True
            return False

        passes = 0
        while attempt_high_low_rule_enforcement_special_2(self.highs, self.lows, self.highs_and_lows, self.bars_in_cycle):
            passes = passes + 1

        # print("Made passes: " + str(passes))


class PointsCalculator:
    def __init__(self, bars, assumed_point_count: int, distribution_count: int, distribution_bar_count: int):
        self.bars = bars
        self.assumed_point_count = assumed_point_count
        self.distribution_count = distribution_count
        self.distribution_bar_count = distribution_bar_count

        self.bars_in_cycle = self.distribution_count * self.distribution_bar_count
        self.bars_for_cycles = list(helpers.chunks(self.bars, self.distribution_count * self.distribution_bar_count))
        self.delta_check_length = math.ceil(self.bars_in_cycle / assumed_point_count)
        self.suggested_deltas_per_distribution = math.ceil(self.assumed_point_count / self.distribution_count)

    def _rank_delta_position(self, rhi, rli, r_scan_x1, r_scan_x2):
        # Right and left distance, only score which one is closest.
        a, b = sorted([rhi, rli])

        ld = (a - r_scan_x1)
        rd = (r_scan_x2 - b)
        bars_apart = abs(rhi - rli)

        # We never calculate edge distances because it disperses the deltas poorly.
        if r_scan_x1 == 0 or r_scan_x2 == self.bars_in_cycle:
            if r_scan_x1 == 0:
                range_rank = (bars_apart + rd) * -1
            else:
                range_rank = (bars_apart + ld)
        else:
            if ld < rd:
                range_rank = (bars_apart + ld)
            else:
                range_rank = (bars_apart + rd) * -1

        # print("({}) | {}, {} | ({}) -> {}".format(r_scan_x1, rhi, rli, r_scan_x2, range_rank))
        return abs(int(math.ceil(range_rank)))

    def get_inversions(self, highs_and_lows: PointsHighLowSequence):
        inversion_keys = []

        max_points = int(math.ceil(self.assumed_point_count / self.distribution_count))
        points_within_first_distribution_length = highs_and_lows.count_points_in_range(0, self.distribution_bar_count)

        if points_within_first_distribution_length > max_points:
            inversion_keys.append(0)

        current_delta_point_count = (len(highs_and_lows.highs_and_lows) - len(inversion_keys))

        if current_delta_point_count - self.assumed_point_count == 1:
            inversion_keys.append(len(highs_and_lows.highs_and_lows) - 1)

        return inversion_keys

    def delta_array_to_points(self, cycle_num: int, points_high_lows_sequence: PointsHighLowSequence, inversion_keys: []):
        sequence = 0
        point_number = 1
        delta_points = []
        cycle = self.bars_for_cycles[cycle_num]

        for i, d in enumerate(points_high_lows_sequence.highs_and_lows):
            sequence = sequence + 1
            is_inversion = i in inversion_keys

            # Compensate for the final delta point being an inversion.
            if len(inversion_keys) > 0 and inversion_keys[-1] == len(points_high_lows_sequence.highs_and_lows) - 1 and inversion_keys[-1] == i:
                point_number = point_number - 1

            dp = DeltaPoint(int(sequence), point_number, cycle[int(d[0])], int(d[0]), d[1], is_inversion)
            sequence = sequence + 1

            if is_inversion is False:
                point_number = point_number + 1

            delta_points.append(dp)

        return delta_points

    def get_all_delta_points_and_ranks(self, r_scan_x1, r_scan_x2, pos, highs, lows):
        # ohi, oli are the original hi and low indexes found, if something better is not available,
        # we will return the original indexes, other wise we will return nhi and nli which are
        # new hi and new low indexes
        delta_ranks_list = []

        # We are returning one rank in the array for tight positions.
        if r_scan_x2 - r_scan_x1 < 3:
            high_point = np.argmax(highs[r_scan_x1: r_scan_x2]) + r_scan_x1
            low_point = np.argmin(lows[r_scan_x1: r_scan_x2]) + r_scan_x1
            price_delta = highs[high_point] - lows[low_point]
            rank = self._rank_delta_position(high_point, low_point, r_scan_x1, r_scan_x2)
            dcr = DeltaComboRank(rank, high_point, low_point, price_delta)
            delta_ranks_list.append(dcr)
            return delta_ranks_list

        path_l, path_r = _cross_find(highs, lows, pos, r_scan_x1, r_scan_x2)
        ohi, oli = _high_and_low(path_l, path_r, highs, lows, pos, r_scan_x1, r_scan_x2)

        nhi = copy.deepcopy(ohi)
        nli = copy.deepcopy(oli)

        next_rank = self._rank_delta_position(nhi, nli, r_scan_x1, r_scan_x2)

        ranks = SortedDict()
        ranks[abs(next_rank)] = (nhi, nli)
        delta_ranks_list.append(DeltaComboRank(bar_rank=next_rank, high_point=nhi, low_point=nli, price_delta=abs(highs[nhi] - lows[nli])))

        while True:
            li, ri = sorted([nhi, nli])

            if next_rank >= 0:
                if r_scan_x2 - ri < 3:
                    break

                path_l, path_r = _cross_find(highs, lows, pos, ri, r_scan_x2)
                nhi, nli = _high_and_low(path_l, path_r, highs, lows, pos, ri, r_scan_x2)
                pass

            # If the rank is is a negative number, we scan from right to left
            if next_rank < 0:
                if li - r_scan_x1 < 3:
                    break

                path_l, path_r = _cross_find(highs, lows, pos, r_scan_x1, li)
                nhi, nli = _high_and_low(path_l, path_r, highs, lows, pos, r_scan_x1, li)
                pass

            next_rank = self._rank_delta_position(nhi, nli, r_scan_x1, r_scan_x2)
            delta_ranks_list.append(DeltaComboRank(bar_rank=next_rank, high_point=nhi, low_point=nli, price_delta=abs(highs[nhi] - lows[nli])))

            if abs(next_rank) not in ranks:
                ranks[abs(next_rank)] = (nhi, nli)
            else:
                break

        return delta_ranks_list

    def get_all_delta_points_and_ranks_special(self, r_scan_x1, r_scan_x2, pos, highs, lows):
        # ohi, oli are the original hi and low indexes found, if something better is not available,
        # we will return the original indexes, other wise we will return nhi and nli which are
        # new hi and new low indexes
        delta_ranks_list = []

        # We are returning one rank in the array for tight positions.
        if r_scan_x2 - r_scan_x1 < 3:
            high_point = np.argmax(highs[r_scan_x1: r_scan_x2]) + r_scan_x1
            low_point = np.argmin(lows[r_scan_x1: r_scan_x2]) + r_scan_x1
            price_delta = highs[high_point] - lows[low_point]
            rank = self._rank_delta_position(high_point, low_point, r_scan_x1, r_scan_x2)
            dcr = DeltaComboRank(rank, high_point, low_point, price_delta)
            delta_ranks_list.append(dcr)
            return delta_ranks_list

        path_l, path_r = _cross_find(highs, lows, pos, r_scan_x1, r_scan_x2)
        ohi, oli = _high_and_low(path_l, path_r, highs, lows, pos, r_scan_x1, r_scan_x2)

        nhi = copy.deepcopy(ohi)
        nli = copy.deepcopy(oli)

        next_rank = self._rank_delta_position(nhi, nli, r_scan_x1, r_scan_x2)

        ranks = SortedDict()
        ranks[abs(next_rank)] = (nhi, nli)
        delta_ranks_list.append(DeltaComboRank(bar_rank=next_rank, high_point=nhi, low_point=nli, price_delta=abs(highs[nhi] - lows[nli])))

        while True:
            li, ri = sorted([nhi, nli])

            if next_rank >= 0:
                if r_scan_x2 - ri < 3:
                    break

                path_l, path_r = _cross_find(highs, lows, pos, ri, r_scan_x2)
                nhi, nli = _high_and_low(path_l, path_r, highs, lows, pos, ri, r_scan_x2)
                pass

            # If the rank is is a negative number, we scan from right to left
            if next_rank < 0:
                if li - r_scan_x1 < 3:
                    break

                path_l, path_r = _cross_find(highs, lows, pos, r_scan_x1, li)
                nhi, nli = _high_and_low(path_l, path_r, highs, lows, pos, r_scan_x1, li)
                pass

            next_rank = self._rank_delta_position(nhi, nli, r_scan_x1, r_scan_x2)
            delta_ranks_list.append(DeltaComboRank(bar_rank=next_rank, high_point=nhi, low_point=nli, price_delta=abs(highs[nhi] - lows[nli])))

            if abs(next_rank) not in ranks:
                ranks[abs(next_rank)] = (nhi, nli)
            else:
                break

        return delta_ranks_list

    def find_best_rank(self, ranks):
        double_delta_on_bar_ranks = []
        every_other_delta_rank = []

        for r in ranks:
            if r.high_point == r.low_point:
                double_delta_on_bar_ranks.append(r)
            else:
                every_other_delta_rank.append(r)

        every_other_delta_rank.sort(key=lambda r: (r.bar_rank, r.price_delta), reverse=True)
        double_delta_on_bar_ranks.sort(key=lambda r: (r.bar_rank, r.price_delta), reverse=True)

        if len(double_delta_on_bar_ranks) == 0:
            return every_other_delta_rank[0]

        if len(double_delta_on_bar_ranks) > 0 and len(every_other_delta_rank) == 0:
            return double_delta_on_bar_ranks[0]

        if double_delta_on_bar_ranks[0].bar_rank > every_other_delta_rank[0].bar_rank:
            if abs(double_delta_on_bar_ranks[0].bar_rank - every_other_delta_rank[0].bar_rank) < math.ceil(self.delta_check_length / 2):
                return every_other_delta_rank[0]
            else:
                return double_delta_on_bar_ranks[0]
        else:
            return every_other_delta_rank[0]

    def compute_cycle(self, cycle_num: int):
        highs = np.array([b.high for b in self.bars_for_cycles[cycle_num]])
        lows = np.array([b.low for b in self.bars_for_cycles[cycle_num]])

        high_low_sequence = PointsHighLowSequence(self.bars_for_cycles[cycle_num])

        li = lows.argmin()
        hi = highs.argmax()

        high_low_sequence.add_points(hi, li)

        def find_best_deltas():
            ranks_from_ranges = {}

            distances = high_low_sequence.get_bar_distances()

            for d in distances:
                if d[1] - d[0] > self.delta_check_length:
                    rx1 = d[0]
                    rx2 = d[1]

                    sub_ranks = self.get_all_delta_points_and_ranks(rx1, rx2, high_low_sequence.get_position_for_coordinates(rx1, rx2), highs, lows)
                    rank = self.find_best_rank(sub_ranks)

                    if rank not in ranks_from_ranges:
                        ranks_from_ranges[rank.bar_rank] = (rank.high_point, rank.low_point)

            rank_keys_list = list(ranks_from_ranges.keys())
            rank_keys_list.sort()
            rank_keys_list.reverse()
            final_rank = rank_keys_list[0]

            # Get the deltas from the final rank
            deltas_high_and_low = ranks_from_ranges[final_rank]
            ahi = deltas_high_and_low[0]
            ali = deltas_high_and_low[1]
            high_low_sequence.add_points(ahi, ali)

        while len(high_low_sequence) < self.assumed_point_count:
            find_best_deltas()

        high_low_sequence.trim()

        while len(high_low_sequence) - len(self.get_inversions(high_low_sequence)) < self.assumed_point_count:
            find_best_deltas()

        # high_low_sequence.enforce_high_low_rules()

        return high_low_sequence

    def compute_highs_and_lows(self, cycle_num: int = None):
        if cycle_num is None:
            cycles_computed = {}

            for c in range(0, len(self.bars_for_cycles) - 1):
                highs_and_lows = self.compute_cycle(c)
                cycles_computed[c] = highs_and_lows
                print("Cycle: %d" % c)

            return cycles_computed
        else:
            return {cycle_num: self.compute_cycle(cycle_num)}

    def finalize_inversions_between_cycles(self, cycle_a: PointsHighLowSequence, cycle_b: PointsHighLowSequence):
        merged_highs = np.array(list(cycle_a.highs[-self.distribution_bar_count:]) + list(cycle_b.highs[:self.distribution_bar_count]))
        merged_lows = np.array(list(cycle_a.lows[-self.distribution_bar_count:]) + list(cycle_b.lows[:self.distribution_bar_count]))

        # Take the last and first quadrant of a and b and glue them together
        cycle_a_deltas_right_slice = []
        cycle_b_deltas_left_slice = []

        for p in cycle_a.highs_and_lows:
            if p[0] >= self.bars_in_cycle - self.distribution_bar_count:
                new_p = copy.deepcopy(p)
                new_p[0] = new_p[0] - (self.bars_in_cycle - self.distribution_bar_count)
                cycle_a_deltas_right_slice.append(new_p)

        for p in cycle_b.highs_and_lows:
            if p[0] <= self.distribution_bar_count:
                new_p = copy.deepcopy(p)
                new_p[0] = new_p[0] + self.distribution_bar_count
                cycle_b_deltas_left_slice.append(new_p)

        merged_spliced_cycles = cycle_a_deltas_right_slice + cycle_b_deltas_left_slice

        def iron_duplicate_highs_and_lows():
            nonlocal cycle_a, cycle_b
            last_position = merged_spliced_cycles[0]

            for c in merged_spliced_cycles[1:]:
                position = c

                if last_position[1] == position[1]:
                    duplicate_index_first = merged_spliced_cycles.index(c)

                    new_delta = None

                    if last_position[1] == 'low' and position[0] - last_position[0] > 1:
                        new_delta = [np.argmax(merged_highs[last_position[0]:position[0]]) + last_position[0], 'high']

                    if last_position[1] == 'high' and position[0] - last_position[0] > 1:
                        new_delta = [np.argmin(merged_lows[last_position[0]:position[0]]) + last_position[0], 'low']

                    # TODO: Do we insert or remove? It's a tough SOB question!
                    # TODO: This code is complicated!!!!!! How in the hell can I make it easier to read?
                    # NOTE: 2 is the constant for the MAXIMUM number of inversions with this algorithm.
                    if new_delta is not None:
                        if new_delta[0] < self.distribution_bar_count:
                            if len(cycle_a) < self.assumed_point_count + (2 - len(self.get_inversions(cycle_a))):
                                merged_spliced_cycles.insert(duplicate_index_first, new_delta)
                            else:
                                if last_position[1] == 'low':
                                    if merged_lows[duplicate_index_first - 1] > merged_lows[duplicate_index_first]:
                                        merged_spliced_cycles.pop(duplicate_index_first - 1)
                                    else:
                                        merged_spliced_cycles.pop(duplicate_index_first)

                                if last_position[1] == 'high':
                                    if merged_lows[duplicate_index_first - 1] < merged_highs[duplicate_index_first]:
                                        merged_spliced_cycles.pop(duplicate_index_first - 1)
                                    else:
                                        merged_spliced_cycles.pop(duplicate_index_first)

                        if new_delta[0] > self.distribution_bar_count:
                            if len(cycle_b) < self.assumed_point_count + (2 - len(self.get_inversions(cycle_b))):
                                merged_spliced_cycles.insert(duplicate_index_first, new_delta)
                            else:
                                if last_position[1] == 'low':
                                    if merged_lows[duplicate_index_first - 1] > merged_lows[duplicate_index_first]:
                                        merged_spliced_cycles.pop(duplicate_index_first - 1)
                                    else:
                                        merged_spliced_cycles.pop(duplicate_index_first)

                                if last_position[1] == 'high':
                                    if merged_lows[duplicate_index_first - 1] < merged_highs[duplicate_index_first]:
                                        merged_spliced_cycles.pop(duplicate_index_first - 1)
                                    else:
                                        merged_spliced_cycles.pop(duplicate_index_first)

                    return True

                last_position = copy.copy(position)

            return False

        if len(merged_spliced_cycles) > 1:
            max_run = 20
            p = 0
            while PointsHighLowSequence.attempt_high_low_rule_enforcement(merged_highs, merged_lows, merged_spliced_cycles, len(merged_highs)) and p < max_run:
                p = p + 1

            p = 0
            while iron_duplicate_highs_and_lows() and p < max_run:
                p = p + 1

            p = 0
            while PointsHighLowSequence.attempt_high_low_rule_enforcement(merged_highs, merged_lows, merged_spliced_cycles, len(merged_highs)) and p < max_run:
                p = p + 1

        updated_deltas_a = [p for p in merged_spliced_cycles if p[0] < self.distribution_bar_count]
        updated_deltas_b = [p for p in merged_spliced_cycles if p[0] > self.distribution_bar_count]

        for p_a in updated_deltas_a:
            p_a[0] = p_a[0] + (self.bars_in_cycle - self.distribution_bar_count)
            pass

        for p_b in updated_deltas_b:
            p_b[0] = p_b[0] - self.distribution_bar_count
            pass

        # Finally we will modify cycle_a and cycle_b with the updates
        cycle_a.highs_and_lows = cycle_a.highs_and_lows[0:len(cycle_a.highs_and_lows) - len(cycle_a_deltas_right_slice)] + updated_deltas_a
        cycle_b.highs_and_lows = updated_deltas_b + cycle_b.highs_and_lows[len(cycle_b_deltas_left_slice):]

        # Cycles may not have the correct number of deltas, we need to count the left and right delta.
        # If the cycle count is not correct we need to add deltas at the start or the end of the cycle.
        if len(cycle_a.highs_and_lows) - len(self.get_inversions(cycle_a)) < self.assumed_point_count:
            rx1 = cycle_a.highs_and_lows[-1][0]
            rx2 = self.bars_in_cycle - 1

            if rx2 - rx1 > 1:
                sub_ranks = self.get_all_delta_points_and_ranks(rx1, rx2, cycle_a.get_position_for_coordinates(rx1, rx2), cycle_a.highs, cycle_a.lows)
                rank = self.find_best_rank(sub_ranks)
                cycle_a.add_points(rank.high_point, rank.low_point)
                print("add")
            else:
                print("o no")

        if len(cycle_b.highs_and_lows) - len(self.get_inversions(cycle_b)) < self.assumed_point_count:
            rx1 = 0
            rx2 = cycle_b.highs_and_lows[1][0]

            if rx2 - rx1 > 1:
                sub_ranks = self.get_all_delta_points_and_ranks(rx1, rx2, cycle_b.get_position_for_coordinates(rx1, rx2), cycle_b.highs, cycle_b.lows)
                rank = self.find_best_rank(sub_ranks)
                cycle_b.add_points(rank.high_point, rank.low_point)
                print("add")
            else:
                print("o no")

        return cycle_a, cycle_b

    @staticmethod
    def find_best_rank_with_range_lines(ranks: [], range_a, range_b, position) -> DeltaComboRank:
        range_list_a = list(range(range_a[0], range_a[1]))
        range_list_b = list(range(range_b[0], range_b[1]))
        middle_a = range_list_a[math.ceil(len(range_list_a) / 2)]
        middle_b = range_list_b[math.ceil(len(range_list_b) / 2)]

        ranks_with_range_lines = {}

        for ri in range(0, len(ranks)):
            if position == "high":
                a_rank = abs(middle_a - ranks[ri].high_point)
                b_rank = abs(middle_b - ranks[ri].low_point)
                ranks_with_range_lines[ri] = a_rank + b_rank
                pass

            if position == "low":
                a_rank = abs(middle_a - ranks[ri].low_point)
                b_rank = abs(middle_b - ranks[ri].high_point)
                ranks_with_range_lines[ri] = a_rank + b_rank
                pass

        sorted(ranks_with_range_lines)
        return list(ranks_with_range_lines.keys())[0]

    def recompute_with_range_lines(self, cycle: PointsHighLowSequence, inversions: [], range_lines: []):
        new_cycle = PointsHighLowSequence(cycle.cycle_bars)
        pos = cycle.highs_and_lows[0][1]

        o = 0
        inversion_start_x1 = 0

        if 0 in inversions:
            inversion_start_x1 = cycle.highs_and_lows[1][0]
            pos = cycle.highs_and_lows[1][1]
            new_cycle.highs_and_lows.append(cycle.highs_and_lows[0])

        range_line_range = range(1, int(len(range_lines) / 2) + 1)
        for i in range_line_range:
            a = i + o
            b = i + 1 + o
            o = o + 1
            # print(str(a) + " - " + str(b))
            r_scan_x1 = max([range_lines[a][0], inversion_start_x1])
            r_scan_x2 = range_lines[b][1]

            # Keep right
            min_r_scan_x = max([range_lines[a][0]] + new_cycle.keys())
            sub_ranks = self.get_all_delta_points_and_ranks(min_r_scan_x, r_scan_x2,
                                                            PointsHighLowSequence._invert_high_low_str(pos),
                                                            cycle.highs, cycle.lows)
            if pos == 'high':
                if len(sub_ranks) > 0:
                    rank_index = self.find_best_rank_with_range_lines(sub_ranks, range_lines[a], range_lines[b], pos)
                    rank = sub_ranks[rank_index]
                    new_cycle.add_points(rank.high_point, rank.low_point)
                else:
                    high_point = r_scan_x1
                    low_point = r_scan_x1
                    new_cycle.add_points(high_point, low_point)

            if pos == 'low':
                if len(sub_ranks) > 0:
                    rank_index = self.find_best_rank_with_range_lines(sub_ranks, range_lines[a], range_lines[b], pos)
                    rank = sub_ranks[rank_index]
                    new_cycle.add_points(rank.high_point, rank.low_point)
                else:
                    high_point = r_scan_x1
                    low_point = r_scan_x1
                    new_cycle.add_points(high_point, low_point)

        return new_cycle

    def recompute_with_range_lines_special(self, cycle: PointsHighLowSequence, inversions: [], range_lines: []):
        new_cycle = PointsHighLowSequence(cycle.cycle_bars)

        if 0 in inversions:
            pos = cycle.highs_and_lows[0][1]
        else:
            pos = PointsHighLowSequence._invert_high_low_str(cycle.highs_and_lows[0][1])

        o = 0
        inversion_start_x1 = 0

        range_line_range = range(1, int(len(range_lines) / 2) + 1)

        for i in range_line_range:
            a = i + o
            b = i + 1 + o
            o = o + 1
            # print(str(a) + " - " + str(b))
            r_scan_x1 = max([range_lines[a][0], inversion_start_x1])
            r_scan_x2 = range_lines[b][1]

            # Keep right
            min_r_scan_x = max([range_lines[a][0]] + new_cycle.keys())
            sub_ranks = self.get_all_delta_points_and_ranks(min_r_scan_x, r_scan_x2,
                                                            PointsHighLowSequence._invert_high_low_str(pos),
                                                            cycle.highs, cycle.lows)
            if pos == 'high':
                if len(sub_ranks) > 0:
                    rank_index = self.find_best_rank_with_range_lines(sub_ranks, range_lines[a], range_lines[b], pos)
                    rank = sub_ranks[rank_index]
                    new_cycle.add_points(rank.high_point, rank.low_point)
                else:
                    high_point = r_scan_x1
                    low_point = r_scan_x1
                    new_cycle.add_points(high_point, low_point)

            if pos == 'low':
                if len(sub_ranks) > 0:
                    rank_index = self.find_best_rank_with_range_lines(sub_ranks, range_lines[a], range_lines[b], pos)
                    rank = sub_ranks[rank_index]
                    new_cycle.add_points(rank.high_point, rank.low_point)
                else:
                    high_point = r_scan_x1
                    low_point = r_scan_x1
                    new_cycle.add_points(high_point, low_point)

        return new_cycle

