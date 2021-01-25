import json
from datetime import datetime
from json import JSONEncoder

from flask import Flask
from flask_cors import CORS

from cycle_machine.brain.delta import DeltaSolutionConfig
from cycle_machine.repository import get_repository
from cycle_machine.repository.mapper.delta_solution_run import mongo_friendly_deserialize
from cycle_machine.logger import logger

_service_name = "cycle_machine"
_logger = logger
_app = Flask(_service_name)

CORS(_app)


class RestDefaultJsonEncoder(JSONEncoder):
    def default(self, v):
        if isinstance(v, datetime):
            return v.isoformat()
        else:
            return v.__dict__


@_app.route('/')
def hello():
    return json.dumps({"service": "cycle_machine"})


@_app.route("/periods/<string:symbol>")
def time_frames_for_symbol(symbol):
    solution_config = DeltaSolutionConfig(symbol)
    return json.dumps(solution_config.periods_asc())


"""Instead of a last bar count we will do a last cycle count since it takes a minimum of one cycle to display """
# TODO: TAKE NOTE!


@_app.route('/series/<string:symbol>/<int:period>')
def solution_series_for_symbol(symbol, period: int):
    delta_solution_config = DeltaSolutionConfig(symbol)
    delta_period_calculator_config = delta_solution_config.delta_period_calculation_config(period)

    repository = get_repository(delta_solution_config)
    bars = repository.load_series(period)

    truncate_index = [e for e, b in enumerate(bars) if b.date_time == delta_period_calculator_config.start_date][0]

    payload = {
        'cycle_meta_data': {
            'symbol': delta_period_calculator_config.symbol,
            'period': delta_period_calculator_config.period,
            'start_time': delta_period_calculator_config.start_date.timestamp(),
            'truncate_index': truncate_index,
            'point_count': delta_period_calculator_config.delta_point_count,
            'distributions': delta_period_calculator_config.number_of_distributions,
            'bars_in_cycle': delta_period_calculator_config.bars_per_cycle,
            # 'cycle_numbers': [],  # TODO: GET THIS!
        },
        'bars': bars
    }

    return json.dumps(payload, cls=RestDefaultJsonEncoder)


@_app.route('/solution-run/<string:symbol>/<int:period>')
def default_solution_run(symbol, period: int):
    delta_solution_config = DeltaSolutionConfig(symbol)
    repository = get_repository(delta_solution_config)
    return mongo_friendly_deserialize(repository.load_solution_run(period))


@_app.route('/solution-overlays/<string:symbol>/<int:period>')
def solution_overlays(symbol, period: int):
    delta_solution_config = DeltaSolutionConfig(symbol)
    repository = get_repository(delta_solution_config)
    return json.dumps(repository.load_solution_overlay(period))


def instantiate_service():
    _logger.info("service: %s is starting." % _service_name)
    _app.run()


