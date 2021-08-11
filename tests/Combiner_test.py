import sys                                                                                                                                         
sys.path.insert(0, './helperFunctions')  
import os
sys.path.append(os.path.abspath("../../src/Backend"))

import UserHelperFuns, RequestHelperFuns, ChatHelperFuns, ChatsHelperFuns, GraphHelperFuns
import json
from app import app, db, socketio
from app.models import NearbyUsers
import db_commands
import pickle
from app.views.helperFunctions import GraphHelper
from app.views.helperFunctions.combiner import JaccardCombiner, DiceCombiner, AverageCombiner, MLCombiner
from app.views.helperFunctions.scorer import FeaturesEnum

def testJaccardCombiner():
	feature_vec = {}
	feature_vec[FeaturesEnum.NUM_USER_TOKENS] = 0
	feature_vec[FeaturesEnum.NUM_OTHER_USER_TOKENS] = 0
	feature_vec[FeaturesEnum.INTERSECTION_TOKENS] = 0
	combiner = JaccardCombiner()
	score = combiner.combine(feature_vec)
	assert score == 1

	feature_vec = {}
	score = combiner.combine(feature_vec)
	assert score == 1

	feature_vec[FeaturesEnum.NUM_USER_TOKENS] = 1
	feature_vec[FeaturesEnum.NUM_OTHER_USER_TOKENS] = 1
	feature_vec[FeaturesEnum.FUZZY_SCORE] = 1
	combiner = JaccardCombiner(True)
	score = combiner.combine(feature_vec)
	assert score == 0

def testDiceCombiner():
	feature_vec = {}
	feature_vec[FeaturesEnum.NUM_USER_TOKENS] = 0
	feature_vec[FeaturesEnum.NUM_OTHER_USER_TOKENS] = 0
	feature_vec[FeaturesEnum.INTERSECTION_TOKENS] = 0
	combiner = DiceCombiner()
	score = combiner.combine(feature_vec)
	assert score == 1

	feature_vec = {}
	score = combiner.combine(feature_vec)
	assert score == 1

	feature_vec[FeaturesEnum.NUM_USER_TOKENS] = 1
	feature_vec[FeaturesEnum.NUM_OTHER_USER_TOKENS] = 1
	feature_vec[FeaturesEnum.FUZZY_SCORE] = 1
	combiner = DiceCombiner(True)
	score = combiner.combine(feature_vec)
	assert score == 0

def testAverageCombiner():
	feature_vec = {}
	feature_vec[FeaturesEnum.NUM_USER_TOKENS] = 0
	feature_vec[FeaturesEnum.NUM_OTHER_USER_TOKENS] = 0
	feature_vec[FeaturesEnum.INTERSECTION_TOKENS] = 0
	feature_vec[FeaturesEnum.HOPS] = 0
	feature_vec[FeaturesEnum.TIME] = 0
	combiner = AverageCombiner()
	score = combiner.combine(feature_vec)
	assert score == 2

	feature_vec = {}
	score = combiner.combine(feature_vec)
	assert score == 2

def testMLCombiner():
	weights = [1,1,1,1,1]

	file = 'weight.pickle'

	pickle.dump(weights, open(file, 'wb'))


	mlModelFile = os.path.dirname(os.path.abspath(__file__)) + '/' + file
	combiner = MLCombiner(mlModelFile)

	feature_vec = {}
	feature_vec[FeaturesEnum.NUM_USER_TOKENS] = 1
	feature_vec[FeaturesEnum.NUM_OTHER_USER_TOKENS] = 1
	feature_vec[FeaturesEnum.INTERSECTION_TOKENS] = 1
	feature_vec[FeaturesEnum.HOPS] = 1
	feature_vec[FeaturesEnum.TIME] = 1

	assert combiner.combine(feature_vec) == 5
