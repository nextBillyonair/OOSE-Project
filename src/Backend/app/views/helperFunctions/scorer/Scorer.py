import abc

class Scorer():
    """Base data model for all objects"""
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def score(self, result, feature_vec):
        return
