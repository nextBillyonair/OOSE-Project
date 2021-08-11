import sys
import os
sys.path.append(os.path.abspath("../src/Backend"))
import db_commands
from app.models import UserRelations
import json
from app import app, db, socketio
from sqlalchemy import and_

# check db relation between user1 with userID1 and user2 with userID2, PLEASE DELETE IN REFACTOR, USE checkIfConnected AND getFiltered (carefully)
def checkRelation(userID1, userID2, relation, target = 1):
    query = db.session.query(UserRelations.UserRelations).filter(and_(UserRelations.UserRelations.fromUserID==userID1, UserRelations.UserRelations.toUserID==userID2))
    count = 0
    for entry in query:
        e = entry._to_dict()
        assert e['fromUserID'] == str(userID1)
        assert e['toUserID'] == str(userID2)
        assert e['relation'] == relation
        count += 1
    assert count == target

# checks if two users are connected
def checkIfConnected(test_client, userID1, userID2, success=True, connected=True, position=None, sid=None):
    if position is None or sid is None:
        response = test_client.get('/v1/isConnected/' + str(userID1) + '/' + str(userID2), data=json.dumps(dict(userID=userID1, userID2=userID2)))
    else:
        response = test_client.get('/v1/isConnected/' + str(userID1) + '/' + str(userID2) + '/' + str(sid) + '/' + str(position), data=json.dumps(dict(userID=userID1, userID2=userID2)))

    if success:
        assert response.status == '200 OK'
        data = json.loads(response.get_data(as_text=True))
        assert data['connected'] == connected
    else:
        assert response.status != '200 OK'

# returns list of users that are either blocked by userID or have a hanging request with or sent by userID, ADD TO MORE TESTS IN REFACTOR
def getFiltered(test_client, userID, success=True):
    response = test_client.get('/v1/filtered/' + str(userID), data=json.dumps(dict(userID=userID)))

    if success:
        assert response.status == '200 OK'
        data = json.loads(response.get_data(as_text=True))
        return data
    else:
        assert response.status != '200 OK'

# using user1's client, block user2 with userID2 from user1 with userID1
def blockUser(test_client, userID1, userID2, success=True):
    response = test_client.post('v1/block/' + str(userID2), data=json.dumps(dict(userID=userID1)))

    if success:
        assert response.status == '200 OK'
        data = json.loads(response.get_data(as_text=True))
        assert data['response'] == 'success'
    else:
        assert response.status != '200 OK'

def unblockUser(test_client, userID1, userID2, success=True):
    response = test_client.post('/v1/unblock/' + str(userID2), data=json.dumps(dict(userID=userID1)))

    if success:
        assert response.status == '200 OK'
        data = json.loads(response.get_data(as_text=True))
        assert data['response'] == 'success'
    else:
        assert response.status != '200 OK'

def getBlockedUsers(test_client, userID, target, success=True):
    response = test_client.get('/v1/block/' + str(userID), data=json.dumps(dict(userID=userID)))

    if success:
        assert response.status == '200 OK'
        data = json.loads(response.get_data(as_text=True))
        assert len(data) == target
        return data
    else:
        assert response.status != '200 OK'

def deactivateUser(test_client, userID, success=True):
    response = test_client.post('/v1/deactivate/' + str(userID), data=json.dumps(dict(userID=userID)))

    if success:
        assert response.status == '200 OK'
        data = json.loads(response.get_data(as_text=True))
        assert data['response'] == 'success'
    else:
        assert response.status != '200 OK'

# check socket_client for target amount of messages, CLEARS MESSAGES!
def checkNumSocketMessages(socket_client, target):
    recvd = socket_client.get_received()
    assert len(recvd) == target

def startTwoUserTest():
    assert db_commands.close_session() == "DB Session Ended"
    assert db_commands.clear_db() == "DB Tables dropped"

    assert db_commands.create_db() == "DB Created Successfully"

    test_client = app.test_client()
    test_client2 = app.test_client()

    socket_client = socketio.test_client(app)
    socket_client.get_received()

    socket_client2 = socketio.test_client(app)
    socket_client2.get_received()

    userID1 = createUser1(test_client, socket_client)
    userID2 = createUser2(test_client2, socket_client2)

    test_client.post('/v1/isNearby', data=json.dumps(dict(userID=userID1, userID2=userID2)))
    test_client2.post('/v1/isNearby', data=json.dumps(dict(userID=userID2, userID2=userID1)))

    return test_client, test_client2, socket_client, socket_client2, userID1, userID2

def endTwoUserSession(test_client, test_client2, socket_client, socket_client2, userID1, userID2):
    socket_client.emit('remove user', {'userID':userID1})
    test_client.post('v1/logout')
    socket_client2.emit('remove user', {'userID':userID2})
    test_client2.post('v1/logout')
    assert db_commands.close_session() == "DB Session Ended"
    assert db_commands.clear_db() == "DB Tables dropped"

def createUser(userID, accessToken, test_client, socket_client):
    test_client.post('/v1/login',data=json.dumps(dict(userID=userID,accessToken=accessToken)))

    socket_client.emit('new user', {'userID':userID, 'accessToken':accessToken})
    recvd = socket_client.get_received()

    assert len(recvd) == 1

    assert recvd[0]['name'] == 'New'

    assert recvd[0]['args'] == [None]

    return userID

def createUser1(test_client, socket_client):

    userID = 10210109395352346
    accessToken = 'EAAIFungVNekBAEBPZB6aItiwSMCk9ftAwq4II95zFJEZCsVWkb0TcmlyIAZA9iVCadOZARcLFxRKqwurq3cxKQkh8QnEEC1mVPjpV0UkNnaGNNuUELauoXtUSNiVgIi7cpLvaMGWZA4ALQVpZC1mTkTRUju8VZBPxSUvX4sa8cA6X5tU4018fMzZCvZBD6p4xt7svFy6ZCD9jlQ9PZCV0V4j0lH1Ogd20shsorOZAIkvZABVq7QZDZD'
    return createUser(userID, accessToken, test_client, socket_client)

def createUser2(test_client, socket_client):

    userID = 10214179832709333
    accessToken = 'EAAIFungVNekBAIR4wHn6ksppRGUqLbTLLOyfUWFfR71SMvG4uMrlpQPS9Ndcj10hA7UupyDiV6J1TtCe5nLhCMcWZAi4ZBGLsaqvp7YZBcpR0yKYtCyYRCM45KHQcoSjINgf8HaCu7Jd5xnWCYPsKoMqVLfEQufWWEIkHeyEqtaYZBLMVio3CBiZBaVcl7qi9wuRnd5JRPZC4SZCG0EZBZCG8shkc8WIt3tHzrpamhL5hzRZCpDjGQtoGTaLBTcZB62vtMZD'
    return createUser(userID, accessToken, test_client, socket_client)

def checkIfLongDistance(test_client, userID1, userID2):
    isLongDistance = test_client.get("/v1/longdistance/" + str(userID1) + "/" + str(userID2), 
        data=json.dumps(dict(userID1=userID1, userID2=userID2)))
    data = json.loads(isLongDistance.get_data(as_text=True))
    assert data['longdistance']
    return data['longdistance']

def checkLongDistTwoWay(clientID1, clientID2, userID1, userID2):
    checkIfLongDistance(clientID1, userID1, userID2)
    checkIfLongDistance(clientID2, userID2, userID1)

def checkIfNotLongDistance(test_client, userID1, userID2):
    isLongDistance = test_client.get("/v1/longdistance/" + str(userID1) + "/" + str(userID2), 
        data=json.dumps(dict(userID=userID1, userID2=userID2)))
    try:
        userID1 = long(userID1)
        userID2 = long(userID2)
    except ValueError:
        return isLongDistance.status
    if userID1 == userID2:
        assert isLongDistance.status != "200 OK"
        return isLongDistance.status
    
    data = json.loads(isLongDistance.get_data(as_text=True))
    
    if 'error' in data:
        return data
    else:
        data = json.loads(isLongDistance.get_data(as_text=True))
        assert not data['longdistance']

def checkNotLongDistTwoWay(clientID1, clientID2, userID1, userID2):
    checkIfNotLongDistance(clientID1, userID1, userID2)
    checkIfNotLongDistance(clientID2, userID2, userID1)

def postLongDistance(test_client, userID1, userID2):
    return test_client.post('/v1/longdistance/' + str(userID2), {'userID1':userID1}, 
        data=json.dumps(dict(userID=userID1)))

def postNotLongDistance(test_client, userID1, userID2):
    return test_client.post('/v1/notlongdistance/' + str(userID2), {'userID1':userID1}, 
        data=json.dumps(dict(userID=userID1)))

def getUserSettings(clientID, userID):
    timeRadius = clientID.get('/v1/userSettings/' + str(userID), 
        data=json.dumps(dict(userID=userID)))
    data = json.loads(timeRadius.get_data(as_text=True))
    return data

def getUserSettingsAsserts(data, userID, hours, radius, tags):
    assert data['userID'] == str(userID)
    assert data['radius'] == radius
    assert data['hours'] == hours
    assert data['tags'] == tags

def getTags(test_client, userID1, userID2, success=True):
    response = test_client.get('/v1/tags/' + str(userID1) + '/' + str(userID2), data=json.dumps(dict(userID=userID1, userID2=userID2)))

    if success:
        assert response.status == '200 OK'
        data = json.loads(response.get_data(as_text=True))
    else:
        assert response.status != '200 OK'

def postTags(test_client, userID, tags, success=True):
    response = test_client.post('v1/tags', data=json.dumps({
        'userID':userID, 
        'tags':tags 
    }))

    if success:
        response.status == '200 OK'
    else:
        response.status != '200 OK'
        