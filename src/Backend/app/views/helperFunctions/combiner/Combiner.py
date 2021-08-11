import abc

class Combiner():
    """Base data model for all objects"""
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def combine(self, feature_vec):
        return
