from app.views.helperFunctions.combiner import Combiner
from app.views.helperFunctions.scorer import FeaturesEnum
import pickle
import os

class MLCombiner(Combiner):

    def __init__(self, file):
        super(MLCombiner, self).__init__()
        
        self.weights = pickle.load(open(file, 'rb'))

    def combine(self, feature_vec):
        score = 0
        for i, weight in enumerate(self.weights):
            score += weight * feature_vec.get(i, 0)
        return score