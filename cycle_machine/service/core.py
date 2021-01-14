import json
from datetime import datetime
from json import JSONEncoder

from flask import Flask
from flask_cors import CORS

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


def instantiate_service():
    _logger.info("service: %s is starting." % _service_name)
    _app.run()


