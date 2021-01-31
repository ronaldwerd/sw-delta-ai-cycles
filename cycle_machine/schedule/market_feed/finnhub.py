import json
from datetime import datetime
import pytz


import httpx
from cycle_machine.brain.delta import DeltaSolutionConfig
from cycle_machine.config import FINNHUB_AUTH_TOKEN
from cycle_machine.brain.series import Bar
from pytz import reference


class FinnHubMarketFeed():
    def __init__(self, delta_solution_config: DeltaSolutionConfig):
        self._finnHubUrl = "https://finnhub.io/api/v1"
        self.token = FINNHUB_AUTH_TOKEN
        self.headers = {'X-Finnhub-Token': self.token}

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
    def _finnmhub_response_reduce_to_higher_period(finnhub_response: dict, period: int):
        return finnhub_response
        pass

    @staticmethod
    def _finnhub_response_to_bar_list(finnhub_response: dict) -> [Bar]:
        open_list = finnhub_response['o']
        bar_list = []

        """
        timezone = pytz.timezone("America/Los_Angeles")
        d_aware = timezone.localize(d)
        """

        for i in range(0, len(open_list)):
            two_hours = datetime.timedelta(hours=2)
            bar_date_time = datetime.fromtimestamp(finnhub_response['t'][i]),


            b = Bar(

                finnhub_response['h'][i],
                finnhub_response['l'][i],
                finnhub_response['o'][i],
                finnhub_response['c'][i],
            )
            bar_list.append(b)

        return bar_list

    def get_bars_for(self, period: int, start_time: datetime, today_time: datetime):
        """"""

        # yesterday = datetime.now() - timedelta(1)

        """
            # TODO: SO DAMN USEFUL!!!
            # datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
            # TODO: YEAH YEAH!!!
            
        """
        my_timestamp = datetime.fromtimestamp(1611180000)

        # create both timezone objects
        local_timezone_str = reference.LocalTimezone().tzname(datetime.now())
        old_timezone = pytz.timezone("America/New_York")
        new_timezone = pytz.timezone("Israel")

        # tzlocal()).tzname()

        # two-step process

        localized_timestamp = old_timezone.localize(my_timestamp)
        new_timezone_timestamp = localized_timestamp.astimezone(new_timezone)

        print("z")

        resolution = self.__get_resolution(period)

        start_time.timestamp()

        from_date = 1611187200
        to_date = 1611705600

        bar_url = self._finnHubUrl + "/forex/candle?symbol=FXPRO:41&resolution=%s&from=%d&to=%d" \
                  % (resolution, start_time.timestamp(), to_date)

        r = httpx.get(bar_url, headers=self.headers)
        json_data = json.loads(r.content)
        json_data = self._finnmhub_response_reduce_to_higher_period(json_data, period)
        bar_list = self._finnhub_response_to_bar_list(json_data)

        print("z")
        pass


if __name__ == '__main__':
    solution_config = DeltaSolutionConfig("GOLD")
    feed = FinnHubMarketFeed(solution_config)
    feed.get_bars_for(1440)


"""

2019-10-12T07:20:50.52Z

2021-01-25T00:00:00.00Z

"""


"""
FXCM...

U10D2449090
Qqbt2

"""