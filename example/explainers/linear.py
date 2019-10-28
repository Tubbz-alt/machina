import numpy as np
from scipy import stats
import ipdb

from .meta import Explainer

class Linear(Explainer):
    def __str__(self):
        return "LinearExplainer"

    @property
    def model(self):
        return self._model

    @property
    def feature_names(self):
        return self._feature_names

    @property
    def target_names(self):
        return self._target_names

    def __init__(self, model, trial_id, transformer=None, feature_names=None, target_names=None, seed=None, _id='importances'):
        self._model = model
        self._transformer = transformer
        self._feature_names = feature_names
        self._target_names = target_names
        self._seed = seed
        self._id = _id
        self._trial = trial_id
  
    def explain(self, X, y, num_features=None):
        features =  self._transformer.transform(X) if self._transformer else X
        prediction = self._model.predict(features)[0]
        importances = sorted(zip(self.feature_names, (self._model.coef_ * features)[0]), key=lambda x: abs(x[1]), reverse=True)
        
        return importances[:num_features], prediction