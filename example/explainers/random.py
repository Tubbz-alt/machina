import numpy as np
from scipy import stats
import datetime

from .meta import Explainer

class Random(Explainer):
    def __str__(self):
        return "RandomExplainer"

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
        '''Generate random weights (which sum to 1) according to a Dirichlet distribution
        
        alpha parameter controls the distribution of the weights.

        a large alpha forces the weights to be uniform in the limit.

        a small alpha forces the weights to be sparse (with a single weight close to one)
        '''
        self._model = model
        self._transformer = transformer
        self._feature_names = feature_names
        self._target_names = target_names
        self._seed = seed
        self._id = _id
        self._trial = trial_id

    def explain(self, X, y, num_features=None, alpha=1.0):
        np.random.seed(datetime.datetime.now().microsecond + (self._trial * 1000000))

        features = self._transformer.transform(X) if self._transformer else X
        
        num_features = num_features if num_features else features.shape[1]
        #prior = np.random.exponential(scale=self._scale, size=len(X.index))
        weights = np.random.dirichlet(np.ones(num_features) * alpha, size=1)[0]

        # randomly assign each randomly picked feature to contribtue to one of the classes
        p = 0.5
        classes = (stats.bernoulli.rvs(p, size=num_features) * 2) - 1
        selected_features = np.random.choice(self._feature_names, size=num_features, replace=False)

        importances = sorted(zip(selected_features, (weights * classes)), key=lambda x: abs(x[1]), reverse=True)
        prediction = self._model.predict(features)[0]

        return importances, prediction