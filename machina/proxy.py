from collections import OrderedDict
import uuid, datetime, re
import ipdb

from machina import database as db
from werkzeug.local import LocalProxy
from flask import session, g
from playhouse.shortcuts import model_to_dict

class Proxy(type):
    '''metaclass that implements a modified dict() interface.
    
    Backed by session storage for persistence between requests scoped to each 
    user. Serialized to a database with the option for automatically persisting 
    anytime the object is modified.
    
    Any class that uses the Proxy metaclasses will equivalently inherit these functions
    and all classes will share the same session LocalProxy.'''
    _store = LocalProxy(lambda: g)

    def __getattr__(self, name):
        return getattr(self._store._data, name)

    def __setitem__(self, key, value):
        self._store._data[key] = value

    def __getitem__(self, key):
        return self._store._data.get(key)
    
    def __delitem__(self, key):
        del self._store._data[key]
    
    def __iter__(self):
        return iter(self._store._data)

    def __len__(self):
        return len(self._store._data)

    def _load(self):
        _model = None
        if 'uuid' in session:
            now = datetime.datetime.utcnow()
            
            _model = self._model_cls.get_or_create(session=session['uuid'], defaults={
                'created_at': now,
                'updated_at': now,
                'experiment_id': self._experiment._id,
            })[0]

            self._store._data = model_to_dict(_model)
        else:
            self._store._data = {}

        return _model

    def _save(self):
        for key, value in self._store._data.items():
            if key not in self._model_cls._meta.fields.keys():
                db._add_column(name=key, value=value, experiment=self._experiment, model_cls=self._model_cls)
        
        with self._experiment._db:
            instance = self._model
            for key, value in self._store._data.items():
                setattr(instance, key, value)
            
            for key in self._model_cls._meta.fields.keys():
                if key not in self._store._data.keys():
                    setattr(instance, key, None)

            instance.updated_at = datetime.datetime.utcnow()
            instance.save()

    @property
    def data(self):
        return model_to_dict(self._model) if self._model else {}

    @property
    def _model(self):
        return self._model_cls.get_by_id(session['trial_id']) if 'trial_id' in session else None

class trial(metaclass=Proxy):
    '''Static singleton class. should not be instantiated.
    
    Exposes a dict() interface through Proxy metaclass without
    needing instantiation. Overrides methods to proxy calls to
    underlying '_trial' OrderedDict stored in the session.
    '''
    pass