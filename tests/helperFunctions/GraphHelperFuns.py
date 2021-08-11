import sys
import os
sys.path.append(os.path.abspath("../src/Backend"))
import db_commands
from app.models import User, UserSettings
from flask import request
from flask_socketio import emit, join_room
from app import app, db, socketio, hashing, session
import json

FB_APP_ID = '569248390133225'
FB_APP_NAME = 'Footsie'
FB_APP_SECRET = '5a63dd2867cb4e221d393374ef469b0e'

@socketio.on('set session')
def handle_new_user(data):
    h = data.get('h')
    userID = data.get('userID')
    if not h:
        return

    session['user'] = h
    join_room(str(userID))
    emit("New", room=str(userID))

@app.route('/v1/setSession', methods=['POST'])
def setSession():
    try:
        data = json.loads(request.data)
    except ValueError:
        return ""

    h = data.get('h')
    if h:
        session['user'] = h
    return ""

def hacky_login(userID, accessToken):

    users = User.User.query.filter_by(userID=userID).all()
    users = list(users)
    if len(users) == 0:
        user = User.User(userID, accessToken)
        db.session.add(user)
    else:
        user = users[0]
        user.accessToken = accessToken

    db.session.commit()

    if len(users) == 0:
        userSettings = UserSettings.UserSettings(userID, 1, 1, ["","",""])
        db.session.add(userSettings)
        db.session.commit()

    h = hashing.hash_value(accessToken, salt=FB_APP_SECRET)
    return h

def bulkLogout(clientList):
    for client in clientList:
        client.post('/v1/logout')

def bulkLogin(userList, clientList):
    i = 0
    for user in userList:
        h = hacky_login(int(user), str(user))
        clientList[i].post('/v1/setSession', data=json.dumps({'h':h}))
        i += 1

def createUser(clientList, socketList, userList):
    test_client = app.test_client()

    socket_client = socketio.test_client(app)
    socket_client.get_received()

    userID = len(userList) + 1
    numUsers = len(userList)

    if numUsers == 0:
        userID = 1
    else:
        userID = numUsers + 1

    accessToken = str(userID)

    h = hacky_login(userID, accessToken)
    test_client.post('/v1/setSession', data=json.dumps({'h':h}))

    socket_client.emit('set session', {'h':h, 'userID':userID})
    recvd = socket_client.get_received()

    assert len(recvd) == 1

    assert recvd[0]['name'] == 'New'

    assert recvd[0]['args'] == [None]

    clientList.append(test_client)
    socketList.append(socket_client)
    userList.append(userID)

    assert len(userList) == userID

    return clientList, socketList, userList

def startMultiUserTest():
    assert db_commands.close_session() == "DB Session Ended"
    assert db_commands.clear_db() == "DB Tables dropped"
    assert db_commands.create_db() == "DB Created Successfully"

    return [], [], []

def endMultiUserTest(clientList, socketList, userList):
    numUsers = len(userList)
    i = 0
    while i < numUsers:
        socketList[i].emit('remove user', {'userID':i+1})
        clientList[i].post('v1/logout')
        i += 1
    assert db_commands.close_session() == "DB Session Ended"
    assert db_commands.clear_db() == "DB Tables dropped"

def setRadius(userID, clientID, radius):
    return clientID.post('/v1/radius', data=json.dumps({'userID':userID, 'radius':radius}))

def setTime(userID, clientID, hours):
    return clientID.post('/v1/time', data=json.dumps({'userID':userID, 'hours':hours}))

def setRadiusMax(userID, clientID):
    return clientID.post('/v1/radius', data=json.dumps({'userID':userID, 'radius':4}))

def setTimeMax(userID, clientID):
    return clientID.post('/v1/time', data=json.dumps({'userID':userID, 'hours':24}))

def checkNotNearBy(clientID, userID1, userID2):
    notNear = clientID.get('/v1/isNearby/' + str(userID1) + '/' + str(userID2), 
        data=json.dumps(dict(userID=userID1, userID2=userID2)))
    try:
        userID1 = long(userID1)
        userID2 = long(userID2)
    except ValueError:
        return notNear.status
    if userID1 == userID2:
        assert notNear.status != "200 OK"
        return notNear.status
    
    data = json.loads(notNear.get_data(as_text=True))
    
    if 'error' in data:
        return data
    else:
        data = json.loads(notNear.get_data(as_text=True))
        assert not data['nearby']

def checkNotNearBulk(clientList, userList):
    for i in range(0, len(userList)):
        for j in range(0, len(userList)):
            if i != j:
                checkNotNearBy(clientList[i], userList[i], userList[j])

def checkNearBy(clientID, userID1, userID2):
    nearby = clientID.get('/v1/isNearby/' + str(userID1) + '/' + str(userID2), 
        data=json.dumps(dict(userID=userID1, userID2=userID2)))
    data = json.loads(nearby.get_data(as_text=True))
    assert data['nearby']
    return data['time']

def getNearbyUsers(clientID, userID):
    nearbyUsers = clientID.get('/v1/getNearbyUsers/' + str(userID), 
        data=json.dumps(dict(userID=userID)))
    data = json.loads(nearbyUsers.get_data(as_text=True))
    return data

def getNearbyUsersMax(clientID, userID, maxPeople):
    nearbyUsers = clientID.get('/v1/getNearbyUsers/' + str(userID) + '/' + str(maxPeople), 
        data=json.dumps(dict(userID=userID, maxPeople=maxPeople)))
    data = json.loads(nearbyUsers.get_data(as_text=True))
    return data

def postNearby(clientID, userID1, userID2):
    return clientID.post('/v1/isNearby', {'userID':userID1, 'userID2':userID2}, 
        data=json.dumps(dict(userID=userID1, userID2=userID2)))

def postNearbyTwoWay(clientID1, clientID2, userID1, userID2):
    postNearby(clientID1, userID1, userID2)
    postNearby(clientID2, userID2, userID1)
