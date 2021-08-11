from app import db, session
from app.models import Chats, FeatureVectors, NearbyUsers, UserSettings, UserRelations
from app.views.helperFunctions.scorer import HopsScorer, TagsScorer, TimeScorer, FuzzyScorer
from app.views.helperFunctions.combiner import JaccardCombiner

import datetime
import itertools
from sqlalchemy.orm import aliased
from sqlalchemy import and_, func
from sqlalchemy.exc import IntegrityError
import functools
import json

feature_scorers = [HopsScorer, TagsScorer, TimeScorer, FuzzyScorer]

# file = 'footsie_model'
# mlModelFile = os.path.dirname(os.path.abspath(__file__)) + '/' + file
# combiner = MLCombiner(mlModelFile)

combiner = JaccardCombiner()

def isNearbyInGraph(userID1, userID2):
    nearby, _ = getNearbyUsersDict(userID1, otherUserID=userID2)
    return nearby

def isNearbyAndTimeInGraph(userID1, userID2):
    return getNearbyUsersDict(userID1, otherUserID=userID2)

def getNearbyUsers(userID, maxPeople = 25, sid=None):
    hopPeople, userSettings = getNearbyUsersDict(userID, maxPeople)
    result = list(hopPeople.values())
    if len(result) >= maxPeople:
        result = result[:maxPeople]
    result = sortResults(result, userSettings, sid)

    return result

def sortResults(result, userSettings, sid):

    scorers = []
    for scorer in feature_scorers:
        scorers.append(scorer(userSettings))

    scoreList = [0] * len(result)

    for i, res in enumerate(result):
        feature_vec = {}
        for scorer in scorers:
            scorer.score(res, feature_vec)
        db.session.add(FeatureVectors.FeatureVectors(sid, res['id'], feature_vec))
        scoreList[i] = (i, combiner.combine(feature_vec))

    print(scoreList)
    scoreList.sort(key=lambda x: x[1])

    sortedResults = [0] * len(result)
    for j, (i, _) in enumerate(scoreList):
        sortedResults[j] = result[i]

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        pass

    return sortedResults

def getNearbyUsersDict(userID, maxPeople = None, otherUserID=None):
    if None not in (maxPeople, otherUserID):
        return {}, {}

    userA = UserSettings.UserSettings.query.filter_by(userID=userID).all()
    userA = list(userA)
    if len(userA) == 0:
        return {}, {}

    userA = userA[0]

    hopPeople = {}

    nowTimeBuffer = datetime.timedelta(minutes=5)
    nowTime = datetime.datetime.utcnow() + nowTimeBuffer

    nearby = session.get('nearby', {})

    if otherUserID is not None:
        if unicode(otherUserID) in nearby:
            if nearby[unicode(otherUserID)]['time'] >= nowTime and nearby[unicode(otherUserID)]['hops'] < userA.radius:
                return True, nearby[unicode(otherUserID)]['time']

    for key in nearby.keys():
        if nearby[key]['time'] >= nowTime and nearby[key]['hops'] < userA.radius:
            nearby[long(key)] = nearby[key]
        nearby.pop(key)

    if maxPeople is not None:
        if len(nearby) >= maxPeople:
            return nearby, userA

    hopPeople[userID] = nowTime

    for hop in range(0, userA.radius):
        tmpHopPeople = {}

        keys = hopPeople.keys()
        if len(keys) == 0:
            break

        n1 = aliased(NearbyUsers.NearbyUsers)
        n2 = aliased(NearbyUsers.NearbyUsers)
        u1 = aliased(UserSettings.UserSettings)
        if len(keys) > 25:
            query = db.session.query(n1.userID, n1.otherUserID, func.least(n1.timeStamp, n2.timeStamp).label('timeStamp'))
            query = query.join(n2, and_(n1.userID == n2.otherUserID, n1.otherUserID == n2.userID))
            subquery = query.filter(and_(n1.userID.in_(keys), n1.otherUserID != userID)).subquery('res')

            query = db.session.query(subquery.c.otherUserID, func.max(subquery.c.timeStamp).label('timeStamp'))
            subquery2 = query.group_by(subquery.c.otherUserID).subquery('res2')

            query = db.session.query(subquery.c.userID, subquery.c.otherUserID, subquery.c.timeStamp, u1.radius, u1.hours, u1.tags)
            query = query.join(subquery2, and_(subquery.c.timeStamp == subquery2.c.timeStamp, subquery.c.otherUserID == subquery2.c.otherUserID))
            query = query.join(u1, and_(subquery.c.otherUserID == u1.userID, u1.radius >= hop))

            if maxPeople is not None:
                query = query.limit(maxPeople)
        else:
            query = db.session.query(n1.userID, n1.otherUserID, func.least(n1.timeStamp, n2.timeStamp).label('timeStamp'), u1.radius, u1.hours, u1.tags)
            query = query.join(n2, and_(n1.userID == n2.otherUserID, n1.otherUserID == n2.userID))
            query = query.filter(and_(n1.userID.in_(keys), u1.radius >= hop, n1.otherUserID != userID))
            query = query.join(u1, n1.otherUserID == u1.userID)

        nearbyUsers = query.all()

        for near in nearbyUsers:

            key = near.otherUserID
            timeStamp = hopPeople[near.userID]
            tags = near.tags

            newTimeStamp = min(near.timeStamp, timeStamp)
            if key in tmpHopPeople:
                newTimeStamp = max(newTimeStamp, tmpHopPeople[key])

            tmpHopPeople[key] = newTimeStamp

            timeLeft = newTimeStamp + datetime.timedelta(hours=min(userA.hours, near.hours))

            if timeLeft > nowTime:
                if key not in nearby or nearby[key]['time'] <  timeLeft:
                    nearby[key] = {'time': timeLeft, 'id': key, 'tags':tags, 'hops':hop}

                    if otherUserID is not None and otherUserID == key:
                        session['nearby'] = nearby
                        return True, timeLeft

                    if maxPeople is not None and len(nearby) >= maxPeople:
                        session['nearby'] = nearby
                        return nearby, userA

        hopPeople = tmpHopPeople

    session['nearby'] = nearby

    if otherUserID is not None:
        timeLeft = None
        return otherUserID in nearby, timeLeft

    return nearby, userA

def isNearbyInChat(userID, chatID):
    chats = Chats.Chats.query.filter_by(chatID=chatID).all()
    chats = list(chats)
    if len(chats) == 0:
        return False, None
    else:

        chat = chats[0]
        time = None
        connected = True
        for user1, user2 in itertools.product(chat.users, chat.users):
            if user1 == user2:
                continue

            userrelations = UserRelations.UserRelations.query.filter_by(fromUserID=user1).filter_by(toUserID=user2).all()
            userrelations = list(userrelations)

            if len(userrelations) == 1:
                userrelation = userrelations[0]
                if userrelation.relation != UserRelations.RelationEnum.longdistance:
                    connected = False
                    break
            else:
                return False, None

        if connected:
            return True, None

        # first, for all users, look up relations
        for user in chat.users:
            if str(user) == str(userID):
                continue
            nearby, timeTmp = isNearbyAndTimeInGraph(userID, user)
            if not nearby:
                return False, None
            if time is None:
                time = timeTmp
            elif timeTmp < time:
                time = timeTmp

        return True, time
