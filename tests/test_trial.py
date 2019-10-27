import pytest

import flask
from machina import trial

def test_set_and_get_item(experiment, flask_client):
    @experiment.route('/init')
    def init_session():
        return 'empty'

    @experiment.route('/set')
    def set_key():
        trial['key'] = 'golden'
        return 'golden'

    with flask_client as c:
        c.get('/init')

        assert '_trial' not in flask.session

        with pytest.raises(KeyError):
            trial['key']

        assert '_trial' in flask.session
        assert trial.get('key') is None
        assert trial.get('key', 'missing') == 'missing'

        c.get('/set')
        assert 'key' in trial
        assert 'key' in flask.session['_trial']

        assert trial['key'] == 'golden'
        assert flask.session['_trial']['key'] == 'golden'

def test_in(experiment, flask_client):
    @experiment.route('/init')
    def init_session():
        return 'empty'

    @experiment.route('/set')
    def set_key():
        trial['key'] = 'golden'
        return 'golden'

    with flask_client as c:
        c.get('/init')
        assert '_trial' not in flask.session
        assert ('key' in trial) is False
        assert '_trial' in flask.session

        assert 'key' not in trial
        assert 'key' not in flask.session['_trial']

        c.get('/set')
        
        assert 'key' in trial
        assert 'key' in flask.session['_trial']

def test_del_item(experiment, flask_client):
    @experiment.route('/init')
    def init_session():
        return 'empty'

    @experiment.route('/set')
    def set_key():
        trial['key'] = 'golden'
        return 'golden'

    with flask_client as c:
        c.get('/init')
        assert '_trial' not in flask.session

        with pytest.raises(KeyError):
            del trial['key']

        assert '_trial' in flask.session

        c.get('/set')
        assert 'key' in trial
        assert 'key' in flask.session['_trial']

        del trial['key']

        assert 'key' not in trial
        assert 'key' not in flask.session['_trial']

        with pytest.raises(KeyError):
            trial['key']

def test_update(experiment, flask_client):
    pass

def test_len(experiment, flask_client):
    pass

def test_pop(experiment, flask_client):
    pass

def test_popitem(experiment, flask_client):
    pass

def test_iter(experiment, flask_client):
    pass

def test_keys(experiment, flask_client):
    pass

def test_values(experiment, flask_client):
    pass

def test_items(experiment, flask_client):
    pass

def test_clear(experiment, flask_client):
    pass

def test_copy(experiment, flask_client):
    pass

def test_setdefault(experiment, flask_client):
    pass

def test_request_persistence(experiment, flask_client):
    @experiment.route('/set')
    def set_key():
        trial['key'] = 'stay'
        return 'key set'

    @experiment.route('/get')
    def get_key():
        return trial['key']

    @experiment.route('/update')
    def update_key():
        trial['key'] = 'gold'
        return 'key update'

    with flask_client as c:
        c.get('/set')

        assert '_trial' in flask.session
        assert trial['key'] == 'stay'
        assert 'key' in flask.session['_trial']
        assert flask.session['_trial']['key'] == 'stay'

        rv = c.get('/get')
        assert rv.data == b'stay'

        c.get('/update')

        assert trial['key'] == 'gold'
        assert 'key' in flask.session['_trial']
        assert flask.session['_trial']['key'] == 'gold'

        rv = c.get('/get')
        assert rv.data == b'gold'

def test_db():
    experiment = Machina('test', __name__, seed=18, db='sqlite:///testing.db')
    experiment.app.config['TESTING'] = True

    @experiment.route('/db')
    def get_database():
        return trial.db

    experiment.app.test_client().get('/db').data == b'sqlite:///testing.db'