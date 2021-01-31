import abc

from cycle_machine.brain.delta import DeltaSolutionConfig
from cycle_machine.repository import Repository
from cycle_machine.schedule.market_feed.finnhub import FinnHubMarketFeed


class MarketFeed:
    __metaclass__ = abc.ABCMeta

    def __init__(self, repository: Repository, symbol: str):
        self.repository = repository
        self.symbol = symbol

    @staticmethod
    def market_feed(symbol):
        solution_config = DeltaSolutionConfig(symbol)

    @abc.abstractmethod
    def get_new_bar_for(self, period: int):
        pass


def get_market_feed(delta_solution_config: DeltaSolutionConfig) -> FinnHubMarketFeed:
    if delta_solution_config.data_feed_broker == 'finnhub':
        return FinnHubMarketFeed(delta_solution_config)