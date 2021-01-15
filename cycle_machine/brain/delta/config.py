import hashlib
import json
import os
from datetime import datetime

from cycle_machine import config
from dateutil import parser


class DeltaPeriodCalculationConfig:
    def __init__(self, symbol: str, period: int, bars_in_distribution: int, number_of_distributions: int, delta_point_count: int, start_date: datetime, data_source: str):
        self.symbol = symbol
        self.period = period
        self.number_of_distributions = number_of_distributions
        self.bars_in_distribution = bars_in_distribution
        self.bars_per_cycle = number_of_distributions * bars_in_distribution
        self.delta_point_count = delta_point_count
        self.start_date = start_date
        self.data_source = data_source


class DeltaSolutionConfig:
    @staticmethod
    def available_solutions():
        available = []

        for d in os.listdir(config.SOLUTION_DIR):
            available.append(d)

        return available

    def __init__(self, symbol: str):
        self.data_source = None
        self.symbol = symbol
        self._periods = {}

        self.__md5_check_sum = None

        self.refresh()

    def refresh(self):
        json_config = os.path.join(config.SOLUTION_DIR, self.symbol + '.json')

        with open(json_config) as file:
            file_contents = file.read()

            md5 = hashlib.md5()
            md5.update(file_contents.encode())
            md5_digest = md5.hexdigest()

            if self.__md5_check_sum == md5_digest:
                return False

            self.__md5_check_sum = md5_digest

            json_dict = json.loads(file_contents)

            self.data_source = json_dict['data_source']

            periods_ascending = sorted(json_dict['periods'], key=lambda k: k['period'], reverse=True)
            data_source = json_dict['data_source']

            for p in periods_ascending:
                if 'start_date' in p:
                    if 'enabled' in p and p['enabled'] is False:
                        continue

                    dpc = DeltaPeriodCalculationConfig(self.symbol,
                                                       p['period'],
                                                       p['bars_in_distribution'],
                                                       p['distributions'],
                                                       p['delta_points'],
                                                       parser.parse(p['start_date']),
                                                       data_source)
                    self._periods[p['period']] = dpc

            return True

    def periods_asc(self):
        periods_asc = [k for k in self._periods]
        periods_asc.sort()
        return periods_asc

    def delta_period_calculation_config(self, period: int) -> DeltaPeriodCalculationConfig:
        return self._periods[period]
