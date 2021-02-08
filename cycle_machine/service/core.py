import json
import uvicorn
from datetime import datetime
from json import JSONEncoder

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from cycle_machine.brain.delta import DeltaSolutionConfig
from cycle_machine.repository import get_repository
from cycle_machine.repository.mapper.delta_solution_run import mongo_friendly_deserialize
from cycle_machine.logger import get_logger_for


app = FastAPI()
_logger = get_logger_for("service-api")
_service_name = "cycle_machine"

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RestDefaultJsonEncoder(JSONEncoder):
    def default(self, v):
        if isinstance(v, datetime):
            return v.isoformat()
        else:
            return v.__dict__


@app.get("/")
def hello():
    return {"service": "cycle_machine"}


@app.get("/periods/{symbol}")
def time_frames_for_symbol(symbol: str):
    solution_config = DeltaSolutionConfig(symbol)
    return solution_config.periods_asc()


"""Instead of a last bar count we will do a last cycle count since it takes a minimum of one cycle to display """
# TODO: TAKE NOTE!


@app.get('/series/{symbol}/{period}')
def solution_series_for_symbol(symbol: str, period: int):
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

    return payload


@app.get('/solution-run/{symbol}/{period}')
def default_solution_run(symbol: str, period: int):
    delta_solution_config = DeltaSolutionConfig(symbol)
    repository = get_repository(delta_solution_config)
    return mongo_friendly_deserialize(repository.load_solution_run(period))


@app.get('/solution-overlays/{symbol}/{period}')
def solution_overlays(symbol: str, period: int):
    delta_solution_config = DeltaSolutionConfig(symbol)
    repository = get_repository(delta_solution_config)
    return repository.load_solution_overlay(period)


if __name__ == "__main__":
    _logger.info("service: %s is starting." % _service_name)
    uvicorn.run(app, host="0.0.0.0", port=5000)

