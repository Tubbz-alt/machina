import sys, os

import flask
from machina import Machina

from machina import Machina, trial
from machina.decorators import sessionize_identifiers, authentication_required

def test_request_arguments_persist(experiment):
    @experiment.route('/instructions', methods=['GET'])
    @sessionize_identifiers
    def instructions():
        pass

def test_request_arguments_update():
    pass

def test_assignmentId_auth():
    pass

def test_workerId_auth():
    pass

def test_hitId_auth():
    pass

def test_token_auth():
    # no token

    # incorrect token

    # correct token
    pass

def test_preview_auth():
    pass

def test_correct_auth():
    pass