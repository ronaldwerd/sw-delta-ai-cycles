import abc
from abc import ABC

from pymongo import MongoClient

from cycle_machine.brain.delta.config import DeltaSolutionConfig
from cycle_machine.brain.delta.solution import DeltaSolutionRun
from cycle_machine.brain.series import Bar
from cycle_machine.config import MONGO_DB_HOSTNAME, MONGO_DB_PORT, MONGO_DB_DBNAME


class Repository:
    __metaclass__ = abc.ABCMeta

    def __init__(self, delta_solution_config: DeltaSolutionConfig):
        self.delta_solution_config = delta_solution_config

    @abc.abstractmethod
    def load_series(self, period: int) -> []:
        """Load a series from a data source. such as a file, bytestream or database"""
        pass

    @abc.abstractmethod
    def save_solution_run(self, period: int, delta_solution_run: DeltaSolutionRun) -> int:
        pass


class CacheFileRepository(Repository, ABC):
    def __init__(self, delta_solution_config: DeltaSolutionConfig):
        super().__init__(delta_solution_config)

    def load_series(self, period: int) -> []:
        print("Loading cache file...")

    def save_solution_run(self, period: int, delta_solution_run: DeltaSolutionRun):
        print("Saving solution runs...")
        pass


class MongoDbRepository(Repository, ABC):
    def __load_time_frame_from_mongo_db(self, period) -> []:
        bars = []
        collection_name = 'market.data.fx.' + self.delta_solution_config.symbol + "." + str(period)
        cursor = self.mongo_db[collection_name].find().sort("date_time")

        for market_bar in cursor:
            b = Bar(market_bar['date_time'], market_bar['high'], market_bar['low'], market_bar['open'], market_bar['close'])
            bars.append(b)

        return bars

    def __init__(self, delta_solution_config: DeltaSolutionConfig):
        super().__init__(delta_solution_config)

        self.mongo_client = MongoClient(MONGO_DB_HOSTNAME, MONGO_DB_PORT)
        self.mongo_db = self.mongo_client[MONGO_DB_DBNAME]

    def load_series(self, period: int) -> []:
        return self.__load_time_frame_from_mongo_db(period)

    def save_solution_run(self, period: int, delta_solution_run_json_friendly: dict):
        collection_name = 'solution.result.' + self.delta_solution_config.symbol + "." + str(period)
        self.mongo_db[collection_name].insert_one(delta_solution_run_json_friendly)


def get_repository(delta_solution_config: DeltaSolutionConfig) -> Repository:
    if delta_solution_config.data_source == 'mongo':
        return MongoDbRepository(delta_solution_config)

    if delta_solution_config.data_source == 'cache':
        return CacheFileRepository(delta_solution_config)

