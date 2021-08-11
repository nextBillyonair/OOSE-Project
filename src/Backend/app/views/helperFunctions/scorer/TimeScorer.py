from app.views.helperFunctions.scorer import Scorer 
from app.views.helperFunctions.scorer import FeaturesEnum
import datetime

class TimeScorer(Scorer):
    """docstring for TagsScorer"""
    def __init__(self, userSettings):
        super(TimeScorer, self).__init__()

    def score(self, result, feature_vec):
        time = result['time']
        feature_vec[int(FeaturesEnum.TIME)] = (time - datetime.datetime.utcnow()).total_seconds()
