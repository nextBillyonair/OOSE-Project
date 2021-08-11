from app.views.helperFunctions.scorer import Scorer 
from app.views.helperFunctions.scorer import FeaturesEnum

class HopsScorer(Scorer):
    """docstring for TagsScorer"""
    def __init__(self, userSettings):
        super(HopsScorer, self).__init__()

    def score(self, result, feature_vec):
        hops = result['hops']
        feature_vec[int(FeaturesEnum.HOPS)] = hops
