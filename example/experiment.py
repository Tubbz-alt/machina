import json, pickle, datetime, os, random
import numpy as np
import pandas as pd

from flask import request, render_template, redirect, url_for, session, make_response, jsonify

from machina import Machina, trial
from machina import mturk, database

from explainers.random import Random
from explainers.linear import Linear
from explainers.shap import Shap
from explainers.charts import Bar

from measures import Measures, Survey
import secret

ENDPOINTS = {
    'mturk': 'https://www.mturk.com/mturk/externalSubmit',
    'sandbox': 'https://workersandbox.mturk.com/mturk/externalSubmit',
    'local': '/submit'
}

SUBMIT_URL = ENDPOINTS[os.getenv('TARGET')]

# load pickled models and data
pickles = {}

with open('models/sparse.pkl', 'rb') as f:
    pickles['sparse'] = pickle.load(f)

with open('models/dense.pkl', 'rb') as f:
    pickles['dense'] = pickle.load(f)

with open("config.json", "r") as f:
    config = json.load(f)

explainers = {
    'lasso': Linear,
    'ridge': Linear,
    'rf': Shap,
    'random': Random
}

db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASS')
db_name = os.getenv('DB_NAME')

experiment = Machina('channel-cap', __name__, config={
    'seed': config['seed'],
    'db': f"postgres://{db_user}:{db_pass}@localhost:5432/{db_name}"
})

@experiment.app.after_request
def tracking(response):
    database.Metric.create(trial=trial._model, session=session.get('uuid'), path=request.path, referrer=request.referrer, action='visit', value=response.status)
    if trial.get('index') is not None:
        session[f"start"] = session.get(f"start", datetime.datetime.utcnow())
    return response

@experiment.route('/demo', methods=['GET'])
def demo():
    trial['hitId'] = 'demo'
    trial['workerId'] = session['uuid']
    trial['assignmentId'] = session['uuid']
    trial['token'] = os.getenv('TOKEN')

    return redirect(url_for('instructions', _scheme="https", _external=True))

@experiment.route('/instructions', methods=['GET'])
@mturk.sessionize
@mturk.validate(preview=True)
def instructions():
    template = 'begin.html.j2'
        
    if trial.get('index') is not None:
        # Participant is in middle of HIT 
        trial['instructions'] += 1
        template = 'instructions.html.j2'
    elif ('assignmentId' in request.args) and (request.args['assignmentId'] == 'ASSIGNMENT_ID_NOT_AVAILABLE'):
        # HIT preview
        template = 'preview.html.j2'
    else:
        # first read of instructions
        trial['instructions_start'] = datetime.datetime.utcnow()
    return render_template(template, trial=trial)

@experiment.route('/data_dictionary', methods=['GET'])
@mturk.validate(preview=False)
def data_dictionary():
    if trial.get('complete'):
        return redirect(url_for('complete', _scheme="https", _external=True))
    
    if trial.get('index') is not None:
        trial['dictionary'] += 1

    return render_template('dictionary.html.j2', trial=trial)

@experiment.route('/assign', methods=['POST'])
@mturk.validate(preview=False)
def assignment():
    if trial.get('index') is not None:
        return redirect(url_for('example', index=trial['index'] + 1, _scheme="https", _external=True))

    if trial.get('complete'):
        return redirect(url_for('complete', _scheme="https", _external=True))

    print(f"Begin assignment for {session['uuid']}")

    seed = datetime.datetime.now().microsecond + (session['trial_id'] * 1000000)
    random.seed(seed)
    np.random.seed(seed)

    trial['assign_begin'] = datetime.datetime.utcnow()

    trial['sparsity'] = random.choice(['sparse', 'dense'])
    trial['city0'], trial['city1'] = random.sample(['la', 'nyc'], k=2) 
    trial['model'] = random.choice(['lasso', 'ridge', 'rf', 'random'])
    
    data = pickles[trial['sparsity']]
    X0, X1, X_test, y = data[trial['city0']]['X_test'], data[trial['city1']]['X_test'], data['X_test'], data['y_test']

    model_cls = trial['model'] if (trial['model'] != 'random') else 'rf'
    model0 = data[trial['city0']][model_cls]['clf']
    model1 = data[trial['city1']][model_cls]['clf']
    expl_cls = explainers[trial['model']]

    expl0 = expl_cls(
        model=model0, 
        trial_id=session['trial_id'],
        transformer=data[trial['city0']]['transformer'],
        feature_names=X0.columns.values, 
        target_names='Price ($)',
        seed=config['seed'],
        _id='left'
    )

    expl1 = expl_cls(
        model=model1, 
        trial_id=session['trial_id'],
        transformer=data[trial['city1']]['transformer'],
        feature_names=X1.columns.values, 
        target_names='Price ($)',
        seed=config['seed']+1,
        _id='right'
    )
    
    if expl_cls is Shap:
        print('fitting SHAP')
        expl0.fit(X0, explainer='tree')
        expl1.fit(X1, explainer='tree')

    trial['shuffle'] = np.random.permutation(len(X_test))
    trial['features'] = np.random.permutation(10) * 2 + 1
    
    trial['shuffle_str'] = np.array2string(trial['shuffle'])
    trial['features_str'] = np.array2string(trial['features'])
    
    trial['explainers'] = (expl0, expl1)
    trial['explainer_cls'] = str(expl0)
    
    trial['index'] = 0
    trial['X0'], trial['X1'], trial['X_test'], trial['y'] = X0, X1, X_test, y
    trial['instructions'] = 0
    trial['dictionary'] = 0

    return redirect(url_for('example', index=trial['index'] + 1, _scheme="https", _external=True))

@experiment.route('/example/<int:index>/', methods=['GET', 'POST'])
@mturk.validate(preview=False)
def example(index):
    if trial.get('index') is None:
        return redirect(url_for('instructions', _scheme="https", _external=True))

    if (index - 1) != trial['index']:
        return redirect(url_for('example', index=trial['index'] + 1, _scheme="https", _external=True))

    if trial.get('complete'):
        return redirect(url_for('complete', _scheme="https", _external=True))

    seed = datetime.datetime.now().microsecond + (session['trial_id'] * 1000000)
    random.seed(seed)
    np.random.seed(seed)

    edx, k = trial['shuffle'][index-1], trial['features'][index-1]
    example0, example1, y = trial['X0'].iloc[edx:edx+1], trial['X1'].iloc[edx:edx+1], trial['y'].iloc[edx]
    expl0, expl1 = trial['explainers']

    measures = Measures(request.form)

    if request.method == 'POST':
        if measures.validate():
            database.Measure.create(example=edx,
                                    task=index-1, 
                                    num_features=k, 
                                    trial=trial._model,
                                    choice=measures.choice.data,
                                    model=trial[f"city{session['city_idx'][measures.choice.data-1]}"],
                                    confidence=int(measures.confidence.data),
                                    validation_errors=session["error"],
                                    start=session["start"],
                                    end=session['before_request'])
            
            session.pop("city_idx")
            session.pop("example_0")
            session.pop("example_1")
            session.pop("error")
            session.pop("start")

            trial['index'] += 1
            if (index + 1) > len(trial['shuffle']):
                # all tasks complete
                return redirect(url_for('survey', _scheme="https", _external=True))
            else:
                # continue with tasks
                return redirect(url_for('example', index=index + 1, _scheme="https", _external=True))
        else:
            session["error"] += 1

    if "city_idx" not in session:
        left, right = random.sample([('0', expl0, example0), ('1', expl1, example1)], k=2) 
        session['city_idx'] = [left[0], right[0]]
        session["example_0"] = left[1].explain(X=left[2], y=y, num_features=k)
        session["example_1"] = right[1].explain(X=right[2], y=y, num_features=k)
    
    if "error" not in session:
        session["error"] = 0
    
    importances0, prediction0 = session["example_0"]
    importances1, prediction1 = session["example_1"]

    return render_template('task.html.j2',
                           example_num=index,
                           example_tot=len(trial['shuffle']),
                           features=trial['X_test'].iloc[edx],
                           label=y,
                           ex0=Bar().plot(importances0), 
                           pred0=prediction0,
                           ex1=Bar().plot(importances1), 
                           pred1=prediction1,
                           measures=measures)

@experiment.route('/survey', methods=['GET', 'POST'])
@mturk.validate(preview=False)
def survey():
    if trial.get('index') is None:
        return redirect(url_for('instructions', _scheme="https", _external=True))

    if trial['index'] < len(trial['shuffle']):
        return redirect(url_for('example', index=trial['index'] + 1, _scheme="https", _external=True))

    if trial.get('complete'):
        return redirect(url_for('complete', _scheme="https", _external=True))

    survey = Survey(request.form)
    if request.method == 'POST':
        if survey.validate():
            database.Survey.create(trial=trial._model,
                                   education=int(survey.education.data),
                                   computer_knowledge=int(survey.computer_knowledge.data),
                                   computer_experience=int(survey.computer_experience.data),
                                   data_knowledge=int(survey.data_knowledge.data),
                                   data_experience=int(survey.data_experience.data),
                                   feedback=survey.feedback.data,
                                   validation_errors=session["error"],
                                   start=session["start"],
                                   end=session['before_request'])

            session.pop("error")
            session.pop("start")
            trial['complete'] = session['before_request']
            return make_response(jsonify(message='Survey successfully submitted!'), 200) 
        else:
            session["error"] += 1
            return make_response(jsonify(message='Validation Failure.'), 400) 

    if "error" not in session:
        session["error"] = 0

    return render_template('survey.html.j2', survey=survey, trial=trial, submit_url=SUBMIT_URL)

@experiment.route('/submit', methods=['POST'])
@mturk.validate(preview=False)
def submit():
    if trial.get('index') is None:
        return redirect(url_for('instructions', _scheme="https", _external=True))

    return redirect(url_for('complete', _scheme="https", _external=True))

@experiment.route('/complete', methods=['GET'])
@mturk.validate(preview=False)
def complete():
    if trial.get('index') is None:
        return redirect(url_for('instructions', _scheme="https", _external=True))

    return render_template('complete.html.j2')