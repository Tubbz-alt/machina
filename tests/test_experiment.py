import sys, os

import flask
from machina import Machina

def test_route_attached(experiment, flask_client):
    '''Routes should be properly proxied to Flask app object'''

    @experiment.route('/')
    def index():
        return 'Testing'

    rv = flask_client.get('/')
    assert rv.data == b'Testing'

def test_methods_allowed(experiment, flask_client):
    '''Routes should only allow specified HTTP methods'''

    @experiment.route('/', methods=['GET'])
    def index():
        return 'GET DATA'

    @experiment.route('/submit', methods=['POST'])
    def submit():
        return 'POST DATA'

    rv = flask_client.get('/')
    assert rv.data == b'GET DATA'

    rv = flask_client.post('/')
    assert rv.status_code == 405

    rv = flask_client.get('/submit')
    assert rv.status_code == 405

    rv = flask_client.post('/submit')
    assert rv.data == b'POST DATA'  

def test_variable_rules(experiment, flask_client):
    @experiment.route('/<example_id>')
    def index(example_id):
        return example_id

    assert flask_client.get('/1').data == b'1'
    assert flask_client.get('/2').data == b'2'

def test_query_params(experiment):
    @experiment.route('/')
    def index():
        return 'Testing'

    with experiment.app.test_request_context('/?assignmentId=123'):
        assert flask.request.args['assignmentId'] == '123'

def test_data_submit(experiment, flask_client):
    '''Routes should only allow specified HTTP methods'''

    @experiment.route('/submit', methods=['POST'])
    def submit():
        return flask.request.form['name']
  
    assert flask_client.post('/submit', data={'name': 'jonny'}).data == b'jonny'

def test_config_defaults():
    experiment = Machina('test', __name__)

    assert hasattr(experiment, 'config')
    assert len(experiment.config) == 0
    assert experiment.seed == 18
    assert experiment.db_url == 'sqlite:///machina.db'

# def test_config_file():
#     experiment = Machina('test', __name__, config='')

#     assert hasattr(experiment, 'config')
#     assert len(experiment.config) == 3
#     assert experiment.seed == 2
#     assert experiment.db_url == 'sqlite:///testing.db'
#     assert experiment.config['extra'] == 'additional info'

def test_config_dictionary():
    experiment = Machina('test', __name__, config={
        'seed': 2,
        'db_url': 'sqlite:///testing.db',
        'extra': 'additional info'
    })

    assert hasattr(experiment, 'config')
    assert len(experiment.config) == 3
    assert experiment.seed == 2
    assert experiment.db_url == 'sqlite:///testing.db'
    assert experiment.config['extra'] == 'additional info'

def test_secret_generation(monkeypatch):
    '''24byte SECRET_KEY should be generated if none found in environment'''

    assert os.getenv('SECRET_KEY') is None

    # need to initialize experiment again since SECRET_KEY is generated on __init__
    experiment = Machina('test', __name__)

    assert experiment.app.secret_key is not None
    assert len(experiment.app.secret_key) == 24

def test_environment_secret(monkeypatch):
    '''Flask app should read SECRET_KEY from environment if available'''
    SECRET = 'the key'
    monkeypatch.setenv('SECRET_KEY', SECRET)

    # need to initialize experiment again since SECRET_KEY is generated on __init__
    experiment = Machina('test', __name__)

    assert experiment.app.secret_key == SECRET