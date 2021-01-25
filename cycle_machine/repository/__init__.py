import abc
from abc import ABC

from pymongo import MongoClient

from cycle_machine.brain.delta.config import DeltaSolutionConfig
from cycle_machine.brain.delta.solution import DeltaSolutionRun
from cycle_machine.repository.mapper.delta_solution_run import mongo_friendly_deserialize
from cycle_machine.brain.series import Bar
from cycle_machine.config import MONGO_DB_HOSTNAME, MONGO_DB_PORT, MONGO_DB_DBNAME
from cycle_machine.tools.mt4reader import History


def _collection_name_for_data(symbol: str, period: int):
    return "market.data.fx.%s.%d" % (symbol, period)


def _collection_name_for_solution_result(symbol: str, period: int):
    return "solution.result.%s.%d" % (symbol, period)


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

    @abc.abstractmethod
    def load_solution_run(self, period):
        pass

    @abc.abstractmethod
    def save_solution_overlay(self, period: int, overlays: dict):
        pass

    @abc.abstractmethod
    def load_solution_overlay(self, period: int) -> dict:
        pass

    @abc.abstractmethod
    def save_mt4_history(self, history: History, period: int):
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
        cursor = self.mongo_db[_collection_name_for_data(self.delta_solution_config.symbol, period)].find().sort("date_time")

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

    def load_solution_run(self, period: int):
        collection_name = 'solution.result.' + self.delta_solution_config.symbol + "." + str(period)
        return self.mongo_db[collection_name].find_one()

    def _overlay_collection(self, period: int):
        pass

    def save_solution_overlay(self, period: int, overlay: dict):
        collection_name = 'solution.result.' + self.delta_solution_config.symbol + "." + str(period) + ".overlays"
        self.mongo_db[collection_name].insert_one(overlay)

    def load_solution_overlay(self, period: int) -> []:
        collection_name = 'solution.result.' + self.delta_solution_config.symbol + "." + str(period) + ".overlays"
        cursor = self.mongo_db[collection_name].find()
        overlays = []

        for overlay in cursor:
            overlays.append(mongo_friendly_deserialize(overlay))

        return overlays

    def save_mt4_history(self, history: History, period):
        collection_name = _collection_name_for_data(self.delta_solution_config.symbol, period)
        self.mongo_db[collection_name].delete_many({})

        bar_count = 0
        for b in history.bars:
            self.mongo_db[collection_name].insert_one(b.__dict__)
            bar_count = bar_count + 1

        return bar_count


def get_repository(delta_solution_config: DeltaSolutionConfig) -> Repository:
    if delta_solution_config.data_source == 'mongo':
        return MongoDbRepository(delta_solution_config)

    if delta_solution_config.data_source == 'cache':
        return CacheFileRepository(delta_solution_config)

