from app.views.helperFunctions.scorer import Scorer 
from app.views.helperFunctions.preprocessing import preprocessor 
from app.views.helperFunctions.scorer import FeaturesEnum

class TagsScorer(Scorer):
    """docstring for TagsScorer"""
    def __init__(self, userSettings):
        super(TagsScorer, self).__init__()
        self.userSettings = userSettings
        self.userKeywords = set(preprocessor(self.userSettings.tags))

    def score(self, result, feature_vec):
        tags = set(preprocessor(result['tags']))

        feature_vec[int(FeaturesEnum.NUM_USER_TOKENS)] = len(self.userKeywords)
        feature_vec[int(FeaturesEnum.NUM_OTHER_USER_TOKENS)] = len(tags)
        feature_vec[int(FeaturesEnum.INTERSECTION_TOKENS)] = len(self.userKeywords.intersection(tags))
