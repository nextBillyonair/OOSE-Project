from app.views.helperFunctions.combiner import Combiner
from app.views.helperFunctions.scorer import FeaturesEnum

class JaccardCombiner(Combiner):

    def __init__(self, use_fuzzy=False):
        super(JaccardCombiner, self).__init__()
        self.use_fuzzy = use_fuzzy

    def combine(self, feature_vec):
        otherKeywords = feature_vec.get(FeaturesEnum.NUM_OTHER_USER_TOKENS, 0)
        userKeywords = feature_vec.get(FeaturesEnum.NUM_USER_TOKENS, 0)
        if self.use_fuzzy:
            inter = feature_vec.get(FeaturesEnum.FUZZY_SCORE, 0)
        else:
            inter = feature_vec.get(FeaturesEnum.INTERSECTION_TOKENS, 0)

        if otherKeywords == 0 or userKeywords == 0:
            return 1.

        return 1. - float(inter) / (otherKeywords + userKeywords - inter)
