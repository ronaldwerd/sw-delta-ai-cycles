import json
from datetime import datetime

import httpx
from cycle_machine.brain.delta import DeltaSolutionConfig
from cycle_machine.config import FINNHUB_AUTH_TOKEN
from cycle_machine.brain.series import Bar


# from cycle_machine.schedule.market_feed import MarketFeed

"""
class OandaMarketFeed(MarketFeed, ABC):
    def __init__(self, delta_solution_config: DeltaSolutionConfig):
        # super().__init__(delta_solution_config.symbol)
        self.account_id = OANDA_ACCOUNT
        self.auth_token = OANDA_AUTH_TOKEN
        self.headers = {'Authorization': 'Bearer 5e7e97815705362bc760b2c392cc1b2b-b505d4306b2f9a6c8c3b354ee8b423e9'}

    def get_bars_for(self, period: int):
        oanda_url_and_rest_prefix = "https://api-fxpractice.oanda.com/v3/accounts/101-002-2782537-002" \
                                    "/pricing?instruments=XAU_USD"
        r = httpx.get(oanda_url_and_rest_prefix, headers=self.headers)
        json_data = json.loads(r.content)

        print("z")
        pass
"""

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
    def _finnhub_response_to_bar_list(finnhub_response: dict) -> [Bar]:
        open_list = finnhub_response['o']
        bar_list = []

        for i in range(0, len(open_list)):
            b = Bar(
                datetime.fromtimestamp(finnhub_response['t'][i]),
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
        resolution = self.__get_resolution(period)

        start_time.timestamp()

        from_date = 1611187200
        to_date = 1611705600

        bar_url = self._finnHubUrl + "/forex/candle?symbol=FXPRO:41&resolution=%s&from=%d&to=%d" \
                  % (resolution, from_date, to_date)

        r = httpx.get(bar_url, headers=self.headers)
        json_data = json.loads(r.content)

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