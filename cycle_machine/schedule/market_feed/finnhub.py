import json
from datetime import datetime
import pytz
from tzlocal import get_localzone

import httpx
from cycle_machine.brain.delta import DeltaSolutionConfig
from cycle_machine.config import FINNHUB_AUTH_TOKEN
from cycle_machine.brain.series import Bar
from pytz import reference


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


    def _finnmhub_response_reduce_to_higher_period(self, finnhub_response: dict, period: int):

        pre_values = self._finnhub_response_to_bar_list(finnhub_response)

        return finnhub_response
        pass

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

    def get_bars_for(self, period: int, start_time: datetime, end_time: datetime):
        resolution = self.__get_resolution(period)

        bar_url = self._finnHubUrl + "/forex/candle?symbol=%s&resolution=%s&from=%d&to=%d" \
                  % (self._delta_solution_config.data_feed_symbol, resolution, start_time.timestamp(), end_time.timestamp())

        r = httpx.get(bar_url, headers=self._headers)
        json_data = json.loads(r.content)
        json_data = self._finnmhub_response_reduce_to_higher_period(json_data, period)
        bar_list = self._finnhub_response_to_bar_list(json_data)

        return bar_list


if __name__ == '__main__':
    solution_config = DeltaSolutionConfig("GOLD")
    feed = FinnHubMarketFeed(solution_config)
    feed.get_bars_for(1440)
