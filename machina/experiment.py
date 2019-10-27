import os, ipdb, inspect, uuid, datetime

from . import database
from playhouse.reflection import Introspector

from .proxy import trial
from flask import Flask, redirect, url_for, request, make_response, after_this_request, g, abort, session

class Machina:
    def __init__(self, name, module, config=None):
        self._name = name
        self._module = module
        self._config = {}
        print('Experiment init')
      
        if config:
            if isinstance(config, str):
                # read config from file
                self._config = json.load(open(config, 'r'))
            elif isinstance(config, dict):
                # set config from dictionary
                self._config = config

        self._seed = self._config['seed'] if ('seed' in self._config) else 18
        self._db_url = self._config['db'] if ('db' in self._config) else f'sqlite:///machina.db'
        self._db = database.connect(self._db_url)

        exp = database.create_experiment(db=self._db_url, experiment=self, path=os.path.realpath(inspect.stack()[1].filename))        
        self._id = exp[0].id 

        self._app = Flask(self._module)
        self._bootstrap_app()

        if os.getenv('SECRET_KEY'):
            SECRET_KEY = os.getenv('SECRET_KEY')
        else:
            SECRET_KEY = os.urandom(24)
            print(
                f"Generated SECRET_KEY={SECRET_KEY}\n\n"
                "This key is ephemeral and once the server is shutdown will be lost. "
                "To preserve sessions across server restarts please generate a key "
                "and configure a SECRET_KEY environemnt variable.\n\n")

        self._app.secret_key = SECRET_KEY
        trial._experiment = self
        trial._model_cls = self._build_model()

    @property
    def name(self):
        return self._name
    
    @property
    def config(self):
        return self._config

    @property
    def seed(self):
        return self._seed

    @property
    def db_url(self):
        return self._db_url

    @property
    def db(self):
        return self._db

    @property
    def app(self):
        return self._app

    def _build_model(self):
        model = database.Trial

        with self._db:
            _schema = database.Meta.get_by_id(self._id).trial_schema
            
            for name, field in _schema:
                field.bind(model, name)
                model._meta.add_field(name, field)

        return model

    def _bootstrap_app(self):
        @self._app.before_request
        def session_handler():
            session.permanent = True
            session['before_request'] = datetime.datetime.utcnow()
            session['uuid'] = session.get('uuid', uuid.uuid4())

            trial._model_cls = self._build_model()
            session['trial_id'] = trial._load().id

        @self._app.teardown_request
        def trial_teardown(exception):
            trial._save()

        @self._app.after_request
        def set_response_headers(response):
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            #response.headers['Content-Security-Policy'] = "default-src 'self' machina-static.surge.sh"
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            
            return response

        self._app.config.update(
            SESSION_COOKIE_HTTPONLY=True,
            PREFERRED_URL_SCHEME='https'
            #SESSION_COOKIE_SAMESITE='Lax',
            #PERMANENT_SESSION_LIFETIME=600
        )

        if os.getenv('SESSION_COOKIE_SECURE'):
            self._app.config['SESSION_COOKIE_SECURE'] = True

    def route(self, path, **options):
        return self._app.route(path, **options)

    def serve(self, host='127.0.0.1', port=5001,
                    debug=False,
                    workers=1,
                    threads=1,
                    preload=True,
                    config=None,
                    profile=False,
                    token=False,
                    pilot=False):

        self.token = token
        self.pilot = pilot

        if debug:
            os.environ['FLASK_ENV'] = 'development'

            if profile:
                from werkzeug.contrib.profiler import ProfilerMiddleware
                self._app.config['PROFILE'] = True

                self._app.wsgi_app = ProfilerMiddleware(self._app.wsgi_app, restrictions=[30])
            
            return self._app.run(host=host, port=port, debug=True, threaded=False, use_reloader=False)

        run_args = [
            'gunicorn',
            '-w', str(workers),
            '--threads', str(threads),
            '-k', 'sync',
            #'-t', str(worker_timeout),
            '-b', host + ':' + str(port),
            '-n', f'machina-{self.name}-server',
        ]

        if config:
            run_args += ['-c', config]

        if preload:
            run_args += ['--preload']

        run_args += [f'machina.wsgi:initialize("{self.id}", "{self._db_url}")']

        return subprocess.run(run_args)

    def run(self):
        pass