import re, ipdb

import numpy as np

from .meta import Explainer

try:
    import shap
except ImportError:
    raise ImportError('Please install Lundberg\'s SHAP package at '
                              'https://github.com/slundberg/shap')

class Shap(Explainer):
    def __str__(self):
        return "ShapExplainer"

    @property
    def model(self):
        return self._model

    @property
    def feature_names(self):
        return self._feature_names

    @property
    def target_names(self):
        return self._target_names

    @property
    def shap_values(self):
        return self._shap_values

    def __init__(self, model, trial_id, transformer=None, feature_names=None, target_names=None, seed=None, _id='shap'):         
        self._model = model
        self._transformer = transformer
        self._feature_names = feature_names
        self._target_names = target_names 
        self._seed = seed
        self._id = _id
        self._trial = trial_id

    def fit(self, X, explainer=None):
        features =  self._transformer.transform(X) if self._transformer else X

        if (explainer == 'linear') or ('linear_model' in str(self._model.__class__).split('.')):
            self._explainer = shap.LinearExplainer(self._model, features, feature_dependence="independent")
        elif (explainer == 'tree') or \
             ('tree' in str(self._model.__class__).split('.')) or \
             ('forest' in str(self._model.__class__).split('.')) or \
             ('gradient_boosting' in str(self._model.__class__).split('.')):
            self._explainer = shap.TreeExplainer(self._model)
        else:
            self._explainer = shap.KernelExplainer(getattr(self._model, 'predict_proba', self._model.predict), features, link="logit")
    
    def explain(self, X, y, cache=True, num_features=None):
        features =  self._transformer.transform(X) if self._transformer else X
        self._shap_values = self._explainer.shap_values(features)

        importances = sorted(zip(self.feature_names, self._shap_values[0]), key=lambda x: abs(x[1]), reverse=True)
     
        prediction = self._model.predict(features)[0]
 
        return importances[:num_features], prediction