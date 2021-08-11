from app.views.helperFunctions.combiner import Combiner
from app.views.helperFunctions.scorer import FeaturesEnum
from app.views.helperFunctions.combiner import JaccardCombiner as DecoratedCombiner


class AverageCombiner(Combiner):

    def __init__(self, tagWeight = 2., timeWeight = 1./3600, hopsWeight=1./2):
        super(AverageCombiner, self).__init__()
        self.combiner = DecoratedCombiner()
        self.tagWeight = tagWeight
        self.timeWeight = timeWeight
        self.hopsWeight = hopsWeight

    def combine(self, feature_vec):
        tagsScore = self.combiner.combine(feature_vec)
        hopsScore = feature_vec.get(FeaturesEnum.HOPS, 0)
        timeScore = feature_vec.get(FeaturesEnum.TIME, 0)
        return tagsScore * self.tagWeight + hopsScore * self.hopsWeight + timeScore * self.timeWeight