from abc import ABCMeta, abstractmethod

class Explainer(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, model, data, feature_names=None, target_names=None):
        raise NotImplementedError

    @abstractmethod
    def explain(self, X, y):
        raise NotImplementedError