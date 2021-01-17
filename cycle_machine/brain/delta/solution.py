import copy

import numpy as np

from cycle_machine.brain.delta.ai.points import PointsCalculator
from cycle_machine.brain.delta.ai.ranges import calculate_range_lines
from cycle_machine.brain.delta.config import DeltaPeriodCalculationConfig
from cycle_machine.brain.delta.objects import DeltaCycles


class DeltaSolutionRun:
    def __init__(self, run_from: str, dpc: DeltaPeriodCalculationConfig, pc: PointsCalculator, cycles_highs_and_lows: {}, cycle_inversions: {}):
        self.pc = pc
        self.run_from = run_from
        self.cycles_highs_and_lows = cycles_highs_and_lows
        self.cycles_inversions = cycle_inversions
        self.delta_points_cycles = {}
        self.range_lines = {}
        self.cycle_ranks = {}
        self.rank_average = 0

        for c in self.cycles_highs_and_lows:
            self.delta_points_cycles[c] = self.pc.delta_array_to_points(c, self.cycles_highs_and_lows[c], self.cycles_inversions[c])

        self.delta_points_cycles = DeltaCycles(pc.bars[0].date_time,
                                               dpc.period,
                                               dpc.delta_point_count,
                                               dpc.number_of_distributions,
                                               dpc.bars_in_distribution,
                                               self.delta_points_cycles)

        self.range_lines = calculate_range_lines(self.delta_points_cycles)

        for i in range(0, len(self.delta_points_cycles)):
            granular_rank = DeltaCycles.rank_cycle(self.delta_points_cycles.get(i), self.range_lines)
            self.cycle_ranks[i] = granular_rank

    # We could put our additional hacks below here that could be finalized code later on.
    # Experiment stubs could stay here for singular cycle run purposes

    def rank_cycles_average(self):
        self.rank_average = np.average([self.cycle_ranks[r]['total'] for r in self.cycle_ranks])
        return self.rank_average


class DeltaSolutionPeriod:
    def __init__(self, bar_sequence: [], dpc: DeltaPeriodCalculationConfig, quadrant: int):
        self.dpc = dpc
        self.truncate_index = 0
        self.truncate_index_with_quadrant = 0

        possible_bars_for_cycle = [e for e, b in enumerate(bar_sequence) if b.date_time == dpc.start_date]

        if len(possible_bars_for_cycle) > 0:
            self.truncate_index = [e for e, b in enumerate(bar_sequence) if b.date_time == dpc.start_date][0]
            self.truncate_index_with_quadrant = self.truncate_index + (dpc.bars_in_distribution * quadrant)
            self.bars_for_cycles = bar_sequence[self.truncate_index_with_quadrant::]
        else:
            truncate_index_with_quadrant = (dpc.bars_in_distribution * quadrant)
            self.bars_for_cycles = bar_sequence[truncate_index_with_quadrant::]
            print("Warning... start date not defined for period: " + str(dpc.period))

        self.points_calculator = PointsCalculator(self.bars_for_cycles, dpc.delta_point_count, dpc.number_of_distributions, dpc.bars_in_distribution)
        self.walk_through = []

    def _cycle_compute_first_run(self) -> DeltaSolutionRun:
        cycles_highs_and_lows = self.points_calculator.compute_highs_and_lows(cycle_num=None)
        cycles_inversions = {}

        for c in cycles_highs_and_lows:
            cycles_inversions[c] = self.points_calculator.get_inversions(cycles_highs_and_lows[c])

        return DeltaSolutionRun('_cycle_compute_first_run', self.dpc, self.points_calculator, cycles_highs_and_lows, cycles_inversions)

    def _cycle_compute_with_prev_range_lines(self, dsr: DeltaSolutionRun):
        new_cycles_highs_and_lows = {}
        for c in dsr.cycles_highs_and_lows:
            try:
                new_cycles_highs_and_lows[c] = self.points_calculator.recompute_with_range_lines(
                    dsr.cycles_highs_and_lows[c],
                    dsr.cycles_inversions[c],
                    dsr.range_lines
                )

                new_cycles_highs_and_lows[c].enforce_high_low_rules_special()
                delta_points = dsr.pc.delta_array_to_points(c, new_cycles_highs_and_lows[c], dsr.cycles_inversions[c])
                new_rank = DeltaCycles.rank_cycle(delta_points, dsr.range_lines)
                old_rank = DeltaCycles.rank_cycle(dsr.delta_points_cycles.get(c), dsr.range_lines)
                # print("New Rank: " + str(new_rank['total']) + ", " + str(old_rank['total']))

                if new_rank['total'] > old_rank['total']:
                    new_cycles_highs_and_lows[c] = dsr.cycles_highs_and_lows[c]
                    # print("worse rank for: " + str(c))
            except Exception as e:
                print("Unable to compute: " + str(c))
                pass
        new_dsr = DeltaSolutionRun('_cycle_compute_with_prev_range_lines', self.dpc, self.points_calculator, new_cycles_highs_and_lows, dsr.cycles_inversions)
        return new_dsr

    def _alternate_poorly_ranked_inversions_for_better_calculations(self, dsr: DeltaSolutionRun, percentile_influence) -> DeltaSolutionRun:
        cycle_ranks_list = [dsr.cycle_ranks[r]['total'] for r in dsr.cycle_ranks]
        percentile = np.percentile(cycle_ranks_list, percentile_influence)

        poorly_ranked_cycles = []
        better_ranked_cycles = []

        for r in dsr.cycle_ranks:
            if dsr.cycle_ranks[r]['total'] >= percentile:
                poorly_ranked_cycles.append(r)

        new_dsr = copy.deepcopy(dsr)
        new_dsr.run_from = "_alternate_poorly_ranked_inversions_for_better_calculations"

        for prc in poorly_ranked_cycles:
            cmp_rank = new_dsr.cycle_ranks[prc]['total']

            inversions_for_recompute = []

            if len(new_dsr.cycles_inversions[prc]) == 0:
                inversions_for_recompute.append(0)

            try:
                print("Attempting to re-work: " + str(prc))
                new_highs_and_lows = self.points_calculator.recompute_with_range_lines_special(new_dsr.cycles_highs_and_lows[prc],
                                                                                               inversions_for_recompute,
                                                                                               new_dsr.range_lines)

                new_highs_and_lows.enforce_high_low_rules_special()
                alternative_delta_points = new_dsr.pc.delta_array_to_points(prc, new_highs_and_lows, inversions_for_recompute)
                new_rank = DeltaCycles.rank_cycle(alternative_delta_points, new_dsr.range_lines)['total']

                if new_rank < cmp_rank:
                    better_ranked_cycles.append(new_rank)
                    new_dsr.cycles_highs_and_lows[prc] = new_highs_and_lows
                    new_dsr.cycles_inversions[prc] = inversions_for_recompute
                    print("Cycle " + str(prc) + " is better flipped: " + str(cmp_rank) + " vs " + str(new_rank))
            except Exception as e:
                print("Can't re-work: " + str(prc))
                pass

        print(str(len(better_ranked_cycles)) + " / " + str(len(poorly_ranked_cycles)) + " flipped.")
        return new_dsr

    # Master control logic for optimal algorithm pipeline for final results.
    def _compute_cycles(self):
        dsr = self._cycle_compute_first_run()
        self.walk_through.append(dsr)

        can_reduce = True
        while can_reduce:
            dsr = self._cycle_compute_with_prev_range_lines(dsr)

            if dsr.rank_cycles_average() < self.walk_through[-1].rank_cycles_average():
                self.walk_through.append(dsr)
            else:
                can_reduce = False

        dsr = self._alternate_poorly_ranked_inversions_for_better_calculations(self.walk_through[-1], 70)
        self.walk_through.append(dsr)

        can_reduce = True
        while can_reduce:
            dsr = self._cycle_compute_with_prev_range_lines(dsr)

            if dsr.rank_cycles_average() < self.walk_through[-1].rank_cycles_average():
                self.walk_through.append(dsr)
            else:
                can_reduce = False

    #
    # Methods below to get the most current objects within the walk_through stack.
    #
    def compute_cycles(self):
        return self._compute_cycles()

    def get_delta_cycles(self) -> DeltaCycles:
        return self.walk_through[-1].delta_points_cycles

    def get_range_lines(self) -> DeltaCycles:
        return self.walk_through[-1].range_lines


