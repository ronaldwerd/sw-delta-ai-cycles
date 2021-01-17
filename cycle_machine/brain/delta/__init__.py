from cycle_machine.brain.delta.config import DeltaSolutionConfig
from cycle_machine.brain.delta.solution import DeltaSolutionPeriod


class DeltaSolution:
    def __init__(self, symbol):
        self.config = DeltaSolutionConfig(symbol)
        self.symbol = symbol
        self.period_configurations = {}
        self.periods = {}

        for p in self.config.periods_asc():
            self.period_configurations[p] = self.config.delta_period_calculation_config(p)

    def refresh_configuration(self):
        if self.config.refresh():
            for p in self.config.periods_asc():
                self.period_configurations[p] = self.config.delta_period_calculation_config(p)
            return True
        return False

    def get_periods_above(self, period):
        return [k for k in self.periods.keys() if k > period]

    def calculate_and_return_period(self, bar_sequence: [], period: int, quadrant: int = 0) -> DeltaSolutionPeriod:
        self.periods[period] = DeltaSolutionPeriod(bar_sequence, self.period_configurations[period], quadrant)
        return self.periods[period]
