from app.views.helperFunctions.scorer import Scorer 
from app.views.helperFunctions.preprocessing import preprocessor 
from app.views.helperFunctions.scorer import FeaturesEnum
from fuzzywuzzy import fuzz

class FuzzyScorer(Scorer):
    """docstring for FuzzyScorer"""

    def __init__(self, userSettings):
        super(FuzzyScorer, self).__init__()
        self.tags = set(preprocessor(userSettings.tags))

    def fuzzyCompare(self, tags1, tags2):
        total = 0
        for tag in tags1:
            maxRatio = 0
            for t in tags2:
                maxRatio = max(maxRatio, fuzz.token_sort_ratio(tag, t))
            total += maxRatio / 100.
        return total

    def score(self, result, feature_vec):
        tags = set(preprocessor(result['tags']))
        feature_vec[int(FeaturesEnum.FUZZY_SCORE)] = self.fuzzyCompare(tags, self.tags)
