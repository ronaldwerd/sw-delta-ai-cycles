import json
from datetime import datetime
import pytz
from tzlocal import get_localzone
import math
import httpx
from cycle_machine.brain.delta import DeltaSolutionConfig
from cycle_machine.config import FINNHUB_AUTH_TOKEN
from cycle_machine.brain.series import Bar
from pytz import reference
import numpy

class FinnHubMarketFeed():
    def set_timezones(self):
        self.local_timezone = get_localzone()
        self.broker_timezone = pytz.timezone("EET")
        # TODO: Do we switch in the summer? DST/EET ? we will find out

    def change_datetime_for_bar(self, bar_datetime: datetime):
        localized_timestamp = self.local_timezone.localize(bar_datetime)
        return localized_timestamp.astimezone(self.broker_timezone)

    def __init__(self, delta_solution_config: DeltaSolutionConfig):
        self._delta_solution_config = delta_solution_config

        self._finnHubUrl = "https://finnhub.io/api/v1"
        self._token = FINNHUB_AUTH_TOKEN
        self._headers = {'X-Finnhub-Token': self._token}

        self.local_timezone = None
        self.broker_timezone = None

        self.set_timezones()

    @staticmethod
    def __get_resolution(period: int):
        resolutions = [60, 30, 15, 5, 1]

        if period % 1440 == 0:
            return 'D'

        for r in resolutions:
            if period % r == 0:
                return r

        return 1

    @staticmethod
    def __get_period_from_resolution(resolution):
        if resolution == 'D':
            return 1440

        return resolution

    def _finnhub_response_to_bar_list(self, finnhub_response: dict) -> [Bar]:
        open_list = finnhub_response['o']
        bar_list = []

        # We do not add the last bar because it is not complete.
        for i in range(0, len(open_list) - 1):
            b = Bar(
                self.change_datetime_for_bar(datetime.fromtimestamp(finnhub_response['t'][i])),
                finnhub_response['h'][i],
                finnhub_response['l'][i],
                finnhub_response['o'][i],
                finnhub_response['c'][i],
            )
            bar_list.append(b)

        return bar_list


    def _parse_finnhub_response(self, finnhub_response: dict, period: int, resolution_period: int) -> [Bar]:
        if period % resolution_period < 0:
            raise ArithmeticError("Invalid combination of period %s and resolution_period %s" % period, resolution_period)

        value_aggregate_length = period / resolution_period

        if value_aggregate_length == 1:
            return self._finnhub_response_to_bar_list(finnhub_response)

        value_aggregate_length = int(value_aggregate_length)

        pre_values = self._finnhub_response_to_bar_list(finnhub_response)
        last_bar_index = (len(finnhub_response['c']) - 1) - (len(finnhub_response['c']) % 2)

        aggregate_bar_list = []

        for i in range(0, last_bar_index, math.floor(value_aggregate_length)):
            aggregate_value_range = i + value_aggregate_length

            high = aggregate_value_range - 1

            b = Bar(
                self.change_datetime_for_bar(datetime.fromtimestamp(finnhub_response['t'][i])),
                max(finnhub_response['h'][i:aggregate_value_range]),
                min(finnhub_response['l'][i:aggregate_value_range]),
                numpy.average(finnhub_response['o'][i:aggregate_value_range]),
                numpy.average(finnhub_response['c'][i:aggregate_value_range]),
            )

            aggregate_bar_list.append(b)

        return aggregate_bar_list


    def get_bars_for(self, period: int, start_time: datetime, end_time: datetime):
        resolution = self.__get_resolution(period)
        resolution_period = self.__get_period_from_resolution(resolution)

        bar_url = self._finnHubUrl + "/forex/candle?symbol=%s&resolution=%s&from=%d&to=%d" \
                  % (self._delta_solution_config.data_feed_symbol, resolution, start_time.timestamp(), end_time.timestamp())

        r = httpx.get(bar_url, headers=self._headers)
        json_data = json.loads(r.content)
        bar_list = self._parse_finnhub_response(json_data, period, resolution_period)

        return bar_list


if __name__ == '__main__':
    solution_config = DeltaSolutionConfig("GOLD")
    feed = FinnHubMarketFeed(solution_config)
    feed.get_bars_for(1440)
