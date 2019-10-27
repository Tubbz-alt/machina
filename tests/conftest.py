import threading, time, json

import pytest
import requests
from flask import request

from machina import Machina, trial

@pytest.fixture
def experiment():
    experiment = Machina('test', __name__, seed=18)
    experiment.app.config['TESTING'] = True

    return experiment

@pytest.fixture
def flask_client(experiment):
    return experiment.app.test_client()

@pytest.fixture(scope="module")
def threaded_server():
    experiment = Machina('integration', __name__, seed=18)

    @experiment.route('/status')
    def status():
        return 'Good to Go!'

    @experiment.route('/set')
    def set_key():
        trial[request.args['key']] = request.args['value']
        return 'key set'

    @experiment.route('/get')
    def get_items():
        return json.dumps(trial.data)

    threading.Thread(target=experiment.app.run).start()

    # wait for server to start
    while True:
        try:
            requests.get('http://localhost:5000/status')
        except ConnectionError:
            time.sleep(0.5)
            continue

        break

    yield experiment

    