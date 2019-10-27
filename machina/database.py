from playhouse import db_url
from playhouse.sqliteq import SqliteQueueDatabase
from playhouse.sqlite_ext import SqliteExtDatabase, JSONField
from playhouse.pool import PooledSqliteExtDatabase
from playhouse.fields import PickleField
from playhouse.migrate import SqliteMigrator, PostgresqlMigrator, MySQLMigrator, migrate

import json, pickle, datetime, ipdb, os
from decimal import Decimal
from pathlib import Path

from peewee import Model, DecimalField, IntegerField, CharField, BlobField, \
                   TextField, BooleanField, ForeignKeyField, UUIDField, Field, DateTimeField

def is_json_serializable(value):
    try:
        json.dumps(value)
    except TypeError:
        return False

    return True 

def _infer_field_type(value):
    if isinstance(value, str):
        return TextField
    elif isinstance(value, (datetime.date, datetime.datetime)):
        return DateTimeField
    elif value is True or value is False:
        return BooleanField
    elif isinstance(value, int):
        return IntegerField
    elif isinstance(value, float):
        return FloatField
    elif isinstance(value, Decimal):
        return DecimalField
    elif is_json_serializable(value):
        return JSONField
    else:
        return PickleField

'''
Models

    -> experiment has many trials
    -> trial has many tasks

    -> experiment has many factors
    -> factor has many variants

    -> participant has many trials

    -> trial belongs to user (one-to-one)

    -> treatment connects variants to trial
'''

class Meta(Model):
    experiment = CharField(max_length=50, unique=True)
    seed = IntegerField(default=18)
    path = CharField(max_length=512)
    db = CharField(max_length=512)
    trial_schema = PickleField()
    status = CharField(max_length=50, default='initialized')
    hitId = CharField(max_length=256, unique=True, null=True)
    created_at = DateTimeField(default=datetime.datetime.utcnow)

class Trial(Model):
    experiment_id = IntegerField()
    session = UUIDField(index=True)
    created_at = DateTimeField()
    updated_at = DateTimeField()

class Measure(Model):
    trial = ForeignKeyField(Trial, backref='measures', on_delete='CASCADE', null=True)
    example = IntegerField()
    task = IntegerField()
    num_features = IntegerField()
    confidence = IntegerField()
    choice = CharField(max_length=50)
    model = CharField(max_length=50)
    #top_features = JSONField()
    validation_errors = IntegerField()
    start = DateTimeField()
    end = DateTimeField()

    created_at = DateTimeField(default=datetime.datetime.utcnow)

class Survey(Model):
    trial = ForeignKeyField(Trial, backref='measures', on_delete='CASCADE', null=True)
    education = IntegerField()
    computer_knowledge = IntegerField()
    computer_experience = IntegerField()
    data_knowledge = IntegerField()
    data_experience = IntegerField()
    feedback = TextField()
    validation_errors = IntegerField()
    start = DateTimeField()
    end = DateTimeField()

    created_at = DateTimeField(default=datetime.datetime.utcnow)


class Metric(Model):
    trial = ForeignKeyField(Trial, backref='metrics', on_delete='CASCADE', null=True)

    created_at = DateTimeField(default=datetime.datetime.utcnow)
    session = UUIDField()

    path = TextField()
    referrer = TextField(null=True)

    action = CharField()
    value = TextField()


MODEL_CLASSES = [Meta, Trial, Metric, Survey, Measure]


'''
Connection
'''

def create_experiment(db, experiment, path):
    # directory = os.path.join(Path.home(), '.machina')

    # if not os.path.exists(directory):
    #     print(f'Creating metadata database at {directory}/meta.db')
    #     os.makedirs(directory, exist_ok=True)

    # experiment._meta = SqliteExtDatabase(os.path.join(directory, 'meta.db'), timeout=10)
    # experiment._meta.pragma('journal_mode', 'wal', permanent=True)
    # experiment._meta.pragma('foreign_keys', 1, permanent=True)

    #experiment._meta.bind([Meta])

    with experiment._db:
        #experiment._meta.create_tables([Meta])
        exp = Meta.get_or_create(experiment=experiment.name, defaults={
            'seed': experiment.seed,
            'path': path,
            'db': db,
            'trial_schema': []
        })

    return exp

def connect(url="sqlite:///:memory:", pool=False, max_connections=32, stale_timeout=300):
    url_fragments = url.split(':')
    scheme = url_fragments[0]
    db = None

    if scheme == 'sqlite':
        fname = url.split('/')[-1]

        # if pool:
        #     db = PooledSqliteExtDatabase(fname, timeout=10, max_connections=max_connections, stale_timeout=stale_timeout)
        # else:
        db = SqliteExtDatabase(fname, timeout=10)
            
        db.pragma('journal_mode', 'wal', permanent=True)
        db.pragma('foreign_keys', 1, permanent=True)
    else:
        # if pool:
        #     scheme += '+pool:'
        #     url += f"?max_connections={max_connections}"
        #     url += f"&stale_timeout={stale_timeout}"

        #url = ':'.join(url_fragments[:])
        db = db_url.connect(url)

    db._machina_db_class = scheme

    if scheme == 'sqlite':
        db._machina_migrator = SqliteMigrator(db)
    elif scheme in ['postgres', 'postgresext', 'postgresqlext', 'postgres+pool', 'postgresext+pool', 'postgresqlext+pool']:
        db._machina_migrator = PostgresqlMigrator(db)
    elif scheme == 'mysql':
        db._machina_migrator = MySQLMigrator(db)
    else:
        raise RuntimeError(f'{scheme} is not a supported database class for schema migrations.')

    db.bind(MODEL_CLASSES)

    with db:
        db.create_tables(MODEL_CLASSES)
    
    return db

def _add_column(name, value, experiment, model_cls):
    field = _infer_field_type(value)(null=True)
 
    with experiment._db:
        with experiment._db.atomic() as txn:
            migrate(experiment._db._machina_migrator.add_column(model_cls._meta.table_name, name, field))
            meta = Meta.get_by_id(experiment._id)
            meta.trial_schema += [(name, field)]
            meta.save()

    field.bind(model_cls, name)
    model_cls._meta.add_field(name, field)