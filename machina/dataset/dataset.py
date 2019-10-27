# http://scikit-learn.org/stable/datasets/index.html
# http://parl.ai/static/docs/tutorial_task.html
# https://pytorch.org/tutorials/beginner/data_loading_tutorial.html
# https://pytorch.org/docs/stable/data.html
# https://stanford.edu/~shervine/blog/pytorch-how-to-generate-data-parallel.html
from abc import ABCMeta, abstractmethod

import bisect
import warnings

import requests, os

class Dataset(metaclass=ABCMeta):
    """An abstract class representing a Dataset.
    All other datasets should subclass it. All subclasses should override
    ``__len__``, that provides the size of the dataset, and ``__getitem__``,
    supporting integer indexing in range from 0 to len(self) exclusive.
    """
    @abstractmethod
    def __init__(self):
        raise NotImplementedError 

    @property
    @abstractmethod
    def source(self):
        raise NotImplementedError   
    
    @property
    @abstractmethod
    def data(self):
        raise NotImplementedError   

    @property
    @abstractmethod
    def target(self):
        raise NotImplementedError   

    @property
    @abstractmethod
    def target_names(self):
        raise NotImplementedError   

    @property
    @abstractmethod
    def feature_names(self):
        raise NotImplementedError 

    @abstractmethod
    def build(self):
        raise NotImplementedError

class RegressionMixin():
    pass

class ClassificationMixin():
    pass
    
class Tabular(Dataset):
    pass

class Image(Dataset):
    pass

class Text(Dataset):
    pass

class Sequential(Dataset):
    pass

def download(urls, base_folder):
    if not os.path.exists(base_folder):
        os.mkdir(base_folder)

    for url in urls:
        filename = url.split('/')[-1]
        res = requests.get(url, stream=True)
        with open(base_folder + '/' + filename, "wb") as fh:
            for chunk in res.iter_content(chunk_size=512):
                if chunk:
                    fh.write(chunk)