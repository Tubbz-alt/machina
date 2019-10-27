import os, ipdb
from functools import wraps
from flask import request, abort, session

from .util import colors as c
from .proxy import trial

def sessionize(f):
    @wraps(f)
    def inner(*args, **kwargs):
        #print(f"{c.BLUE}Sessionize Identifiers Checks{c.END}")
        #print(f"args:\t{request.args}")
        if ('token' in request.args) and (request.args['token'] == os.environ.get('TOKEN')) and ('workerId' in request.args) and ('hitId' in request.args) and ('assignmentId' in request.args) and (request.args['assignmentId'] != 'ASSIGNMENT_ID_NOT_AVAILABLE'):
            if (trial.get('workerId') is None) and (trial.get('hitId') is None) and (trial.get('token') is None) and (trial.get('assignmentId') is None):
                trial['workerId'] = request.args['workerId']
                trial['hitId'] = request.args['hitId']
                trial['token'] = request.args['token']
                trial['assignmentId'] = request.args['assignmentId']
                
                print(f"{c.GREEN}Sessionization checks passed. Setting Values:{c.END}")
                print(f"\tassignmentId: {trial.get('assignmentId', None)}")
                print(f"\tworkerId: {trial.get('workerId', None)}")
                print(f"\thitId: {trial.get('hitId', None)}")
                print(f"\ttoken: {trial.get('token', None)}\n")
            # elif (trial.get('workerId') is not None) and (trial.get('hitId') is not None) and (trial.get('token') == os.environ.get('TOKEN')) and (trial.get('assignmentId') == 'ASSIGNMENT_ID_NOT_AVAILABLE'):
            #     trial['assignmentId'] = request.args['assignmentId']
            #     print(f"{c.WARNING}Updating assignmentId:{c.END}")
            #     print(f"\tassignmentId: {trial.get('assignmentId', None)}")

        return f(*args, **kwargs)
    return inner

def validate(preview=False):
    def decorator(f):
        @wraps(f)
        def inner(*args, **kwargs):
            #print(f"{c.WARNING}Verifying Identifiers.{c.END}")
            if not (trial.get('assignmentId', None) and
                    (preview or trial.get('workerId', None)) and 
                    trial.get('hitId', None) and 
                    (os.environ.get('TOKEN') == trial.get('token', None)) and
                    (preview or (trial.get('assignmentId', None) != 'ASSIGNMENT_ID_NOT_AVAILABLE'))):
                if preview:
                    if not (('token' in request.args) and 
                       (request.args['token'] == os.environ.get('TOKEN')) and 
                       ('hitId' in request.args) and 
                       ('assignmentId' in request.args) and (request.args['assignmentId'] == 'ASSIGNMENT_ID_NOT_AVAILABLE')):
                        print(f"\t{c.RED}Authentication failed for {trial.get('workerId', None)}.{c.END}\n")
                        abort(403)
                else:
                    print(f"\t{c.RED}Authentication failed for {trial.get('workerId', None)}.{c.END}\n")
                    abort(403)
            
            #print(f"\t{c.GREEN}Authentication succeeded for{c.END} {c.BLUE}{trial.get('workerId', None)}{c.END}.\n")    
            return f(*args, **kwargs)
        return inner
    return decorator