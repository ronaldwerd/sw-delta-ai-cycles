import json
import math
from datetime import datetime

import httpx
import mpmath
import pytz
from cycle_machine.brain.delta import DeltaSolutionConfig
from cycle_machine.brain.series import Bar
from cycle_machine.config import FINNHUB_AUTH_TOKEN
from tzlocal import get_localzone
from cycle_machine import logger

_logger = logger.get_logger_for("finnhub_market_feed")

class FinnHubMarketFeed():
    def set_timezones(self):
        self.local_timezone = get_localzone()
        self.broker_timezone = pytz.timezone("EET")
        # TODO: Do we switch in the summer? DST/EET ? we will find out

    def change_datetime_for_bar(self, bar_datetime: datetime, broker_timezone: str):
        localized_timestamp = self.local_timezone.localize(bar_datetime)
        return localized_timestamp.astimezone(broker_timezone).replace(tzinfo=None)

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

    def _parse_finnhub_response(self, finnhub_response: dict, period: int, resolution_period: int, resolution) -> [Bar]:
        if period % resolution_period < 0:
            raise ArithmeticError("Invalid combination of period %s and resolution_period %s" % period, resolution_period)

        value_aggregate_length = math.floor(period / resolution_period)
        last_bar_index = (len(finnhub_response['c']) - 1) - (len(finnhub_response['c']) % value_aggregate_length)

        aggregate_bar_list = []

        for i in range(0, last_bar_index, value_aggregate_length):
            aggregate_value_range = i + (value_aggregate_length - 1)

            if value_aggregate_length > 1:
                high = max(finnhub_response['h'][i:aggregate_value_range])
                low = min(finnhub_response['l'][i:aggregate_value_range])
            else:
                high = finnhub_response['h'][i]
                low = finnhub_response['l'][i]

            b = Bar(
                self.change_datetime_for_bar(datetime.fromtimestamp(finnhub_response['t'][i]), self.broker_timezone),
                high,
                low,
                finnhub_response['o'][i],
                finnhub_response['c'][aggregate_value_range],
            )

            aggregate_bar_list.append(b)

        return aggregate_bar_list


    def get_bars_for(self, period: int, start_time: datetime, end_time: datetime):
        resolution = self.__get_resolution(period)
        resolution_period = self.__get_period_from_resolution(resolution)

        bar_url = self._finnHubUrl + "/forex/candle?symbol=%s&resolution=%s&from=%d&to=%d" \
                  % (self._delta_solution_config.data_feed_symbol, resolution, start_time.timestamp(), end_time.timestamp())

        bar_list = []

        try:
            timeout = httpx.Timeout(200.0, connect=200.0)
            r = httpx.get(bar_url, headers=self._headers, timeout=timeout)
            json_data = json.loads(r.content)

            if json_data['s'] == 'no_data':
                return []

            bar_list = self._parse_finnhub_response(json_data, period, resolution_period,  resolution)
        except httpx.HTTPError as e:
            _logger.error("Unable to get data for %s - %s" % (self._delta_solution_config.symbol, period))
            _logger.debug(str(e) + " " + bar_url)
            pass

        return bar_list

