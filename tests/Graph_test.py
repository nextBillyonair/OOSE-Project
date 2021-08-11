import sys
sys.path.insert(0, './helperFunctions')                                                                                                            
import GraphHelperFuns, UserHelperFuns, RequestHelperFuns, ChatHelperFuns
import db_commands
import datetime
import json
import os
sys.path.append(os.path.abspath("../../src/Backend"))
from app.models import NearbyUsers, UserSettings
from app.views import GraphView
from app.views.helperFunctions import GraphHelper
from app import app, db, session

def testNearNotInvertible():
    clientList, socketList, userList = GraphHelperFuns.startMultiUserTest()

    numUsers = 2

    for i in range(0, numUsers):
        clientList, socketList, userList = GraphHelperFuns.createUser(clientList, socketList, userList)

    assert len(userList) == numUsers

    GraphHelperFuns.checkNotNearBulk(clientList, userList)
    
    GraphHelperFuns.postNearby(clientList[0], userList[0], userList[1])
    
    GraphHelperFuns.checkNotNearBy(clientList[0], userList[0], userList[1])
    GraphHelperFuns.checkNotNearBy(clientList[1], userList[1], userList[0])

    GraphHelperFuns.postNearby(clientList[1], userList[1], userList[0])

    GraphHelperFuns.checkNearBy(clientList[0], userList[0], userList[1])
    GraphHelperFuns.checkNearBy(clientList[1], userList[1], userList[0])

    GraphHelperFuns.endMultiUserTest(clientList, socketList, userList)

def testTwoHopConnect():
    clientList, socketList, userList = GraphHelperFuns.startMultiUserTest()

    #create 3 users
    numUsers = 3
    for i in range(0, numUsers):
        clientList, socketList, userList = GraphHelperFuns.createUser(clientList, socketList, userList)
        assert GraphHelperFuns.setRadiusMax(userList[i], clientList[i]).status == "200 OK"
        assert GraphHelperFuns.setTimeMax(userList[i], clientList[i]).status == "200 OK"

    assert len(userList) == numUsers
    
    GraphHelperFuns.checkNotNearBulk(clientList, userList)
    
    GraphHelperFuns.postNearbyTwoWay(clientList[0], clientList[1], userList[0], userList[1])

    GraphHelperFuns.checkNearBy(clientList[0], userList[0], userList[1])
    GraphHelperFuns.checkNearBy(clientList[1], userList[1], userList[0])

    GraphHelperFuns.postNearbyTwoWay(clientList[1], clientList[2], userList[1], userList[2])

    GraphHelperFuns.checkNearBy(clientList[1], userList[1], userList[2])
    GraphHelperFuns.checkNearBy(clientList[2], userList[2], userList[1])

    GraphHelperFuns.checkNearBy(clientList[0], userList[0], userList[2])
    GraphHelperFuns.checkNearBy(clientList[2], userList[2], userList[0])

    GraphHelperFuns.endMultiUserTest(clientList, socketList, userList)

def testThreeHopConnect():
    clientList, socketList, userList = GraphHelperFuns.startMultiUserTest()

    #create 4 users
    numUsers = 4
    for i in range(0, numUsers):
        clientList, socketList, userList = GraphHelperFuns.createUser(clientList, socketList, userList)
        assert GraphHelperFuns.setRadiusMax(userList[i], clientList[i]).status == "200 OK"
        assert GraphHelperFuns.setTimeMax(userList[i], clientList[i]).status == "200 OK"

    assert len(userList) == numUsers

    GraphHelperFuns.checkNotNearBulk(clientList, userList)

    GraphHelperFuns.postNearbyTwoWay(clientList[0], clientList[1], userList[0], userList[1])

    GraphHelperFuns.checkNearBy(clientList[0], userList[0], userList[1])
    GraphHelperFuns.checkNearBy(clientList[1], userList[1], userList[0])

    GraphHelperFuns.checkNotNearBy(clientList[0], userList[0], userList[3])
    GraphHelperFuns.checkNotNearBy(clientList[3], userList[3], userList[0])

    GraphHelperFuns.postNearbyTwoWay(clientList[1], clientList[2], userList[1], userList[2])

    GraphHelperFuns.checkNearBy(clientList[1], userList[1], userList[2])
    GraphHelperFuns.checkNearBy(clientList[2], userList[2], userList[1])

    GraphHelperFuns.checkNotNearBy(clientList[0], userList[0], userList[3])
    GraphHelperFuns.checkNotNearBy(clientList[3], userList[3], userList[0])

    GraphHelperFuns.postNearbyTwoWay(clientList[2], clientList[3], userList[2], userList[3])

    GraphHelperFuns.checkNearBy(clientList[2], userList[2], userList[3])
    GraphHelperFuns.checkNearBy(clientList[3], userList[3], userList[2])            

    GraphHelperFuns.checkNearBy(clientList[0], userList[0], userList[3])
    GraphHelperFuns.checkNearBy(clientList[3], userList[3], userList[0])

    GraphHelperFuns.endMultiUserTest(clientList, socketList, userList)

def testTwoHopTimeFailure():
    clientList, socketList, userList = GraphHelperFuns.startMultiUserTest()

    #create 3 users
    numUsers = 3
    for i in range(0, numUsers):
        clientList, socketList, userList = GraphHelperFuns.createUser(clientList, socketList, userList)
        GraphHelperFuns.setRadiusMax(userList[i], clientList[i])
        GraphHelperFuns.setTimeMax(userList[i], clientList[i])

    assert len(userList) == numUsers

    GraphHelperFuns.setTime(userList[2], clientList[2], 8)

    GraphHelperFuns.checkNotNearBy(clientList[0], userList[0], userList[1])
    GraphHelperFuns.checkNotNearBy(clientList[0], userList[0], userList[2])

    GraphHelperFuns.checkNotNearBy(clientList[1], userList[1], userList[0])
    GraphHelperFuns.checkNotNearBy(clientList[1], userList[1], userList[2])

    GraphHelperFuns.checkNotNearBy(clientList[2], userList[2], userList[0])
    GraphHelperFuns.checkNotNearBy(clientList[2], userList[2], userList[1])
    
    nearbyUsers = NearbyUsers.NearbyUsers(userList[0], userList[1], 
        datetime.datetime.now() - datetime.timedelta(hours=10))
    db.session.add(nearbyUsers)
    db.session.commit()
    
    nearbyUsers = NearbyUsers.NearbyUsers(userList[1], userList[0], 
        datetime.datetime.now() - datetime.timedelta(hours=10))
    db.session.add(nearbyUsers)
    db.session.commit()

    GraphHelperFuns.checkNearBy(clientList[0], userList[0], userList[1])
    GraphHelperFuns.checkNearBy(clientList[1], userList[1], userList[0])

    nearbyUsers = NearbyUsers.NearbyUsers(userList[1], userList[2], datetime.datetime.now())
    db.session.add(nearbyUsers)
    db.session.commit()
    
    nearbyUsers = NearbyUsers.NearbyUsers(userList[2], userList[1], datetime.datetime.now())
    db.session.add(nearbyUsers)
    db.session.commit()

    GraphHelperFuns.checkNearBy(clientList[1], userList[1], userList[2])
    GraphHelperFuns.checkNearBy(clientList[2], userList[2], userList[1])

    GraphHelperFuns.checkNotNearBy(clientList[0], userList[0], userList[2])
    GraphHelperFuns.checkNotNearBy(clientList[2], userList[2], userList[0])

    GraphHelperFuns.endMultiUserTest(clientList, socketList, userList)

def testTooManyHops():
    clientList, socketList, userList = GraphHelperFuns.startMultiUserTest()

    #create 3 users
    numUsers = 3

    for i in range(0, numUsers):
        clientList, socketList, userList = GraphHelperFuns.createUser(clientList, socketList, userList)
        assert GraphHelperFuns.setRadius(userList[i], clientList[i], 1).status == "200 OK"
        assert GraphHelperFuns.setTimeMax(userList[i], clientList[i]).status == "200 OK"
    
    assert len(userList) == numUsers
    
    GraphHelperFuns.checkNotNearBulk(clientList, userList)
    
    GraphHelperFuns.postNearbyTwoWay(clientList[0], clientList[1], userList[0], userList[1])
    
    GraphHelperFuns.checkNearBy(clientList[0], userList[0], userList[1])
    GraphHelperFuns.checkNearBy(clientList[1], userList[1], userList[0])

    GraphHelperFuns.postNearbyTwoWay(clientList[1], clientList[2], userList[1], userList[2])

    GraphHelperFuns.checkNearBy(clientList[1], userList[1], userList[2])
    GraphHelperFuns.checkNearBy(clientList[2], userList[2], userList[1])

    GraphHelperFuns.checkNotNearBy(clientList[0], userList[0], userList[2])
    GraphHelperFuns.checkNotNearBy(clientList[2], userList[2], userList[0])

    GraphHelperFuns.endMultiUserTest(clientList, socketList, userList)

def testFourHopConnect():
    clientList, socketList, userList = GraphHelperFuns.startMultiUserTest()

    #create 5 users
    numUsers = 5

    for i in range(0, numUsers):
        clientList, socketList, userList = GraphHelperFuns.createUser(clientList, socketList, userList)
        assert GraphHelperFuns.setRadiusMax(userList[i], clientList[i]).status == "200 OK"
        assert GraphHelperFuns.setTimeMax(userList[i], clientList[i]).status == "200 OK"
    
    assert len(userList) == numUsers

    GraphHelperFuns.checkNotNearBulk(clientList, userList)
    
    GraphHelperFuns.postNearbyTwoWay(clientList[0], clientList[1], userList[0], userList[1])
    
    GraphHelperFuns.checkNearBy(clientList[0], userList[0], userList[1])
    GraphHelperFuns.checkNearBy(clientList[1], userList[1], userList[0])

    GraphHelperFuns.postNearbyTwoWay(clientList[1], clientList[2], userList[1], userList[2])

    GraphHelperFuns.checkNearBy(clientList[1], userList[1], userList[2])
    GraphHelperFuns.checkNearBy(clientList[2], userList[2], userList[1])

    GraphHelperFuns.postNearbyTwoWay(clientList[2], clientList[3], userList[2], userList[3])

    GraphHelperFuns.checkNearBy(clientList[2], userList[2], userList[3])
    GraphHelperFuns.checkNearBy(clientList[3], userList[3], userList[2])
    
    GraphHelperFuns.postNearbyTwoWay(clientList[3], clientList[4], userList[3], userList[4])

    GraphHelperFuns.checkNearBy(clientList[3], userList[3], userList[4])
    GraphHelperFuns.checkNearBy(clientList[4], userList[4], userList[3])

    GraphHelperFuns.checkNearBy(clientList[0], userList[0], userList[4])
    GraphHelperFuns.checkNearBy(clientList[4], userList[4], userList[0])

    GraphHelperFuns.endMultiUserTest(clientList, socketList, userList)

def testTooManyHopsMax():
    clientList, socketList, userList = GraphHelperFuns.startMultiUserTest()

    #create 6 users
    numUsers = 6

    for i in range(0, numUsers):
        clientList, socketList, userList = GraphHelperFuns.createUser(clientList, socketList, userList)
        assert GraphHelperFuns.setRadiusMax(userList[i], clientList[i]).status == "200 OK"
        assert GraphHelperFuns.setTimeMax(userList[i], clientList[i]).status == "200 OK"
    
    assert len(userList) == numUsers

    GraphHelperFuns.checkNotNearBulk(clientList, userList)
    
    GraphHelperFuns.postNearbyTwoWay(clientList[0], clientList[1], userList[0], userList[1])
    
    GraphHelperFuns.checkNearBy(clientList[0], userList[0], userList[1])
    GraphHelperFuns.checkNearBy(clientList[1], userList[1], userList[0])

    GraphHelperFuns.postNearbyTwoWay(clientList[1], clientList[2], userList[1], userList[2])

    GraphHelperFuns.checkNearBy(clientList[1], userList[1], userList[2])
    GraphHelperFuns.checkNearBy(clientList[2], userList[2], userList[1])
    
    GraphHelperFuns.postNearbyTwoWay(clientList[2], clientList[3], userList[2], userList[3])

    GraphHelperFuns.checkNearBy(clientList[2], userList[2], userList[3])
    GraphHelperFuns.checkNearBy(clientList[3], userList[3], userList[2])
    
    GraphHelperFuns.postNearbyTwoWay(clientList[3], clientList[4], userList[3], userList[4])

    GraphHelperFuns.checkNearBy(clientList[3], userList[3], userList[4])
    GraphHelperFuns.checkNearBy(clientList[4], userList[4], userList[3])

    GraphHelperFuns.postNearbyTwoWay(clientList[4], clientList[5], userList[4], userList[5])

    GraphHelperFuns.checkNearBy(clientList[4], userList[4], userList[5])
    GraphHelperFuns.checkNearBy(clientList[5], userList[5], userList[4])

    GraphHelperFuns.checkNotNearBy(clientList[0], userList[0], userList[5])
    GraphHelperFuns.checkNotNearBy(clientList[5], userList[5], userList[0])

    GraphHelperFuns.endMultiUserTest(clientList, socketList, userList)

def testRadius():
    clientList, socketList, userList = GraphHelperFuns.startMultiUserTest()

    clientList, socketList, userList = GraphHelperFuns.createUser(clientList, socketList, userList)
    
    usersettings = list(UserSettings.UserSettings.query.filter_by(userID=userList[0]).all())
    
    assert usersettings[0].radius == 1

    assert GraphHelperFuns.setRadius(userList[0], clientList[0], 5).status != "200 OK"

    usersettings = list(UserSettings.UserSettings.query.filter_by(userID=userList[0]).all())

    assert usersettings[0].radius == 1

    assert GraphHelperFuns.setRadius(userList[0], clientList[0], 0).status != "200 OK"
    
    usersettings = list(UserSettings.UserSettings.query.filter_by(userID=userList[0]).all())

    assert usersettings[0].radius == 1
    
    assert GraphHelperFuns.setRadius(userList[0], clientList[0], "bob").status != "200 OK"

    GraphHelperFuns.endMultiUserTest(clientList, socketList, userList)

def testHours():
    clientList, socketList, userList = GraphHelperFuns.startMultiUserTest()

    clientList, socketList, userList = GraphHelperFuns.createUser(clientList, socketList, userList)
    
    usersettings = list(UserSettings.UserSettings.query.filter_by(userID=userList[0]).all())

    assert usersettings[0].hours == 1
    
    assert GraphHelperFuns.setTime(userList[0], clientList[0], 25).status != "200 OK"
    
    usersettings = list(UserSettings.UserSettings.query.filter_by(userID=userList[0]).all())
    
    assert usersettings[0].hours == 1
    
    assert GraphHelperFuns.setTime(userList[0], clientList[0], 0).status != "200 OK"

    usersettings = list(UserSettings.UserSettings.query.filter_by(userID=userList[0]).all())
    
    assert usersettings[0].hours == 1

    assert GraphHelperFuns.setTime(userList[0], clientList[0], "bob") != "200 OK"

    GraphHelperFuns.endMultiUserTest(clientList, socketList, userList)

def testNearSelf():
    clientList, socketList, userList = GraphHelperFuns.startMultiUserTest()

    clientList, socketList, userList = GraphHelperFuns.createUser(clientList, socketList, userList)

    GraphHelperFuns.checkNotNearBy(clientList[0], userList[0], userList[0])
    
    assert GraphHelperFuns.postNearby(clientList[0], userList[0], userList[0]).status != "200 OK"

    GraphHelperFuns.checkNotNearBy(clientList[0], userList[0], userList[0])

    GraphHelperFuns.endMultiUserTest(clientList, socketList, userList)

def testBadUser():
    clientList, socketList, userList = GraphHelperFuns.startMultiUserTest()
    
    #create 2 users
    numUsers = 2

    for i in range(0, numUsers):
        clientList, socketList, userList = GraphHelperFuns.createUser(clientList, socketList, userList)

    assert GraphHelperFuns.setTime('bob', clientList[0], 10) != "200 OK"

    assert GraphHelperFuns.setRadius('bob', clientList[0], 1) != "200 OK"

    assert GraphHelperFuns.checkNotNearBy(clientList[0], 'bob', 'bobby')

    assert GraphHelperFuns.getNearbyUsers(clientList[0], 'bob')['error'] == 'userID must be of type long'

    assert UserHelperFuns.getUserSettings(clientList[0], 'bob')['error'] == 'userID must be of type long'

    assert GraphHelperFuns.getNearbyUsersMax(clientList[0], 'bob', 24)['error'] == 'userID must be of type long'

    GraphHelperFuns.endMultiUserTest(clientList, socketList, userList)

def testNotLoggedIn():
    clientList, socketList, userList = GraphHelperFuns.startMultiUserTest()

    #create 1 users
    numUsers = 1

    for i in range(0, numUsers):
        clientList, socketList, userList = GraphHelperFuns.createUser(clientList, socketList, userList)
    
    data = GraphHelperFuns.setTime(2, clientList[0], 10)
    data = json.loads(data.get_data(as_text=True))
    
    assert data['error'] == 'Not logged in'

    data = GraphHelperFuns.setRadius(2, clientList[0], 2)
    data = json.loads(data.get_data(as_text=True))

    assert data['error'] == 'Not logged in'

    data = GraphHelperFuns.postNearby(clientList[0], 2, 1)
    data = json.loads(data.get_data(as_text=True))

    assert data['error'] == 'Not logged in'

    data = GraphHelperFuns.postNearby(clientList[0], 1, 2)
    data = json.loads(data.get_data(as_text=True))

    assert data['error'] == 'Invalid userID2'

    assert UserHelperFuns.getUserSettings(clientList[0], 2)['error'] == 'Not logged in'

    assert GraphHelperFuns.getNearbyUsers(clientList[0], 2)['error'] == 'Not logged in'

    assert GraphHelperFuns.getNearbyUsersMax(clientList[0], 2, 50)['error'] == 'Not logged in'

    assert GraphHelperFuns.checkNotNearBy(clientList[0], 2, userList[0])['error'] == 'Not logged in'

    assert GraphHelperFuns.checkNotNearBy(clientList[0], userList[0], 2)['error'] == 'Invalid userID2'

def testErrorCheckingSetRadius():
    test_client, test_client2, socket_client, socket_client2, userID1, userID2 = UserHelperFuns.startTwoUserTest()

    response = test_client.post('/v1/radius', data=dict())
    assert response.status != '200 OK'

    response = test_client.post('/v1/radius', data=json.dumps(dict(userID="42")))
    assert response.status != '200 OK'

    response = test_client.post('/v1/radius', data=json.dumps(dict(radius="42")))
    assert response.status != '200 OK'

    UserSettings.UserSettings.query.filter_by(userID=userID1).delete()
    db.session.commit()

    assert GraphHelperFuns.setRadius(userID1, test_client, 4).status == "500 INTERNAL SERVER ERROR"

    assert db_commands.close_session() == "DB Session Ended"
    assert db_commands.clear_db() == "DB Tables dropped"

def testErrorCheckingSetTime():
    test_client, test_client2, socket_client, socket_client2, userID1, userID2 = UserHelperFuns.startTwoUserTest()

    response = test_client.post('/v1/time', data=dict())
    assert response.status != '200 OK'

    response = test_client.post('/v1/time', data=json.dumps(dict(userID="42")))
    assert response.status != '200 OK'

    response = test_client.post('/v1/time', data=json.dumps(dict(time="42")))
    assert response.status != '200 OK'

    UserSettings.UserSettings.query.filter_by(userID=userID1).delete()
    db.session.commit()

    assert GraphHelperFuns.setTime(userID1, test_client, 4).status == "500 INTERNAL SERVER ERROR"

    assert db_commands.close_session() == "DB Session Ended"
    assert db_commands.clear_db() == "DB Tables dropped"

def testErrorCheckingGetNearbyUsers():
    UserHelperFuns.startTwoUserTest()
    nearby, _ = GraphHelper.getNearbyUsersDict(0)
    assert len(nearby) == 0
    assert GraphHelper.getNearbyUsersDict(1, 1, 1) == ({}, {})
    assert db_commands.close_session() == "DB Session Ended"
    assert db_commands.clear_db() == "DB Tables dropped"

def testErrorCheckingPostNearby():
    test_client, test_client2, socket_client, socket_client2, userID1, userID2 = UserHelperFuns.startTwoUserTest()

    response = test_client.post('/v1/isNearby', data=dict())
    assert response.status != '200 OK'

    response = test_client.post('/v1/isNearby', data=json.dumps(dict(userID="42")))
    assert response.status != '200 OK'

    response = test_client.post('/v1/isNearby', data=json.dumps(dict(userID2="42")))
    assert response.status != '200 OK'

    response = test_client.post('/v1/isNearby', data=json.dumps(dict(userID="Hello", userID2="42")))
    assert response.status != '200 OK'

    UserSettings.UserSettings.query.filter_by(userID=userID1).delete()
    db.session.commit()
    
    assert GraphHelperFuns.postNearby(test_client, userID1, userID2).status == "500 INTERNAL SERVER ERROR"

    assert db_commands.close_session() == "DB Session Ended"
    assert db_commands.clear_db() == "DB Tables dropped"

def testGetUserSettings():
    clientList, socketList, userList = GraphHelperFuns.startMultiUserTest()

    clientList, socketList, userList = GraphHelperFuns.createUser(clientList, socketList, userList)

    data = UserHelperFuns.getUserSettings(clientList[0], userList[0])
    UserHelperFuns.getUserSettingsAsserts(data, userList[0], 1, 1, ['','',''])

    GraphHelperFuns.setRadiusMax(userList[0], clientList[0])
    data = UserHelperFuns.getUserSettings(clientList[0], userList[0])
    UserHelperFuns.getUserSettingsAsserts(data, userList[0], 1, 4, ['','',''])
    
    GraphHelperFuns.setRadius(userList[0], clientList[0], 3)
    data = UserHelperFuns.getUserSettings(clientList[0], userList[0])
    UserHelperFuns.getUserSettingsAsserts(data, userList[0], 1, 3, ['','',''])

    GraphHelperFuns.setTimeMax(userList[0], clientList[0])
    data = UserHelperFuns.getUserSettings(clientList[0], userList[0])
    UserHelperFuns.getUserSettingsAsserts(data, userList[0], 24, 3, ['','',''])

    GraphHelperFuns.setTime(userList[0], clientList[0], 10)
    data = UserHelperFuns.getUserSettings(clientList[0], userList[0])
    UserHelperFuns.getUserSettingsAsserts(data, userList[0], 10, 3, ['','',''])

    # checking it works with more than one user
    
    clientList, socketList, userList = GraphHelperFuns.createUser(clientList, socketList, userList)

    data = UserHelperFuns.getUserSettings(clientList[1], userList[1])
    UserHelperFuns.getUserSettingsAsserts(data, userList[1], 1, 1, ['','',''])
    
    UserSettings.UserSettings.query.filter_by(userID=userList[0]).delete()
    db.session.commit()

    d = UserHelperFuns.getUserSettings(clientList[0], userList[0])
    assert d['error'] == 'Internal error'

    GraphHelperFuns.endMultiUserTest(clientList, socketList, userList)  

def testPickTimeEfficientEdge():
    clientList, socketList, userList = GraphHelperFuns.startMultiUserTest()

    #create 3 users
    numUsers = 3

    for i in range(0, numUsers):
        clientList, socketList, userList = GraphHelperFuns.createUser(clientList, socketList, userList)
        assert GraphHelperFuns.setRadiusMax(userList[i], clientList[i]).status == "200 OK"
        assert GraphHelperFuns.setTimeMax(userList[i], clientList[i]).status == "200 OK"
    
    assert len(userList) == numUsers
    
    GraphHelperFuns.checkNotNearBulk(clientList, userList)
    
    GraphHelperFuns.postNearbyTwoWay(clientList[0], clientList[1], userList[0], userList[1])

    GraphHelperFuns.checkNearBy(clientList[0], userList[0], userList[1])
    GraphHelperFuns.checkNearBy(clientList[1], userList[1], userList[0])

    GraphHelperFuns.postNearbyTwoWay(clientList[1], clientList[2], userList[1], userList[2])

    GraphHelperFuns.checkNearBy(clientList[1], userList[1], userList[2])
    GraphHelperFuns.checkNearBy(clientList[2], userList[2], userList[1])

    GraphHelperFuns.bulkLogout(clientList)
    GraphHelperFuns.bulkLogin(userList, clientList)

    time1 = GraphHelperFuns.checkNearBy(clientList[0], userList[0], userList[2])
    time2 = GraphHelperFuns.checkNearBy(clientList[2], userList[2], userList[0])

    GraphHelperFuns.postNearbyTwoWay(clientList[0], clientList[2], userList[0], userList[2])
    
    GraphHelperFuns.bulkLogout(clientList)
    GraphHelperFuns.bulkLogin(userList, clientList)

    time3 = GraphHelperFuns.checkNearBy(clientList[0], userList[0], userList[2])
    time4 = GraphHelperFuns.checkNearBy(clientList[2], userList[2], userList[0])

    assert time1 < time3
    assert time2 < time4
    
    GraphHelperFuns.postNearbyTwoWay(clientList[0], clientList[1], userList[0], userList[1])
    
    GraphHelperFuns.bulkLogout(clientList)
    GraphHelperFuns.bulkLogin(userList, clientList)

    time5 = GraphHelperFuns.checkNearBy(clientList[0], userList[0], userList[2])
    time6 = GraphHelperFuns.checkNearBy(clientList[2], userList[2], userList[0])

    assert time3 == time5
    assert time4 == time6

    GraphHelperFuns.postNearbyTwoWay(clientList[1], clientList[2], userList[1], userList[2])

    GraphHelperFuns.bulkLogout(clientList)
    GraphHelperFuns.bulkLogin(userList, clientList)

    time7 = GraphHelperFuns.checkNearBy(clientList[0], userList[0], userList[2])
    time8 = GraphHelperFuns.checkNearBy(clientList[2], userList[2], userList[0])

    assert time3 == time7
    assert time4 == time8

    GraphHelperFuns.endMultiUserTest(clientList, socketList, userList)

def testGetNearbyUsers():
    clientList, socketList, userList = GraphHelperFuns.startMultiUserTest()

    #create 27 users
    numUsers = 27

    for i in range(0, numUsers):
        clientList, socketList, userList = GraphHelperFuns.createUser(clientList, socketList, userList)
    
    assert len(userList) == numUsers
    
    assert GraphHelperFuns.getNearbyUsersMax(clientList[0], userList[0], 'bob')['error'] == 'maxPeople type int'
    
    for i in range(1, numUsers):
        GraphHelperFuns.postNearbyTwoWay(clientList[0], clientList[i], userList[0], userList[i])
        if i == 1 or i == 25:
            GraphHelperFuns.checkNearBy(clientList[0], userList[0], userList[i])
            GraphHelperFuns.checkNearBy(clientList[i], userList[i], userList[0])
            assert len(list(GraphHelperFuns.getNearbyUsers(clientList[0], userList[0])['users'])) == i  
        elif i > 25:
            GraphHelperFuns.checkNearBy(clientList[0], userList[0], userList[i])
            GraphHelperFuns.checkNearBy(clientList[i], userList[i], userList[0])
            assert len(list(GraphHelperFuns.getNearbyUsers(clientList[0], userList[0])['users'])) == 25  

    GraphHelperFuns.endMultiUserTest(clientList, socketList, userList)

def testGetNearbyUsersMax():
    clientList, socketList, userList = GraphHelperFuns.startMultiUserTest()

    #create 102 users
    numUsers = 102

    for i in range(0, numUsers):
        clientList, socketList, userList = GraphHelperFuns.createUser(clientList, socketList, userList)
    
    GraphHelperFuns.setRadius(userList[0], clientList[0], 2)
    
    assert len(userList) == numUsers
    
    assert GraphHelperFuns.getNearbyUsersMax(clientList[0], userList[0], 'bob')['error'] == 'maxPeople type int'
        
    for i in range(1, numUsers):
        GraphHelperFuns.postNearbyTwoWay(clientList[0], clientList[i], userList[0], userList[i])
        if i == 1 or i == 99:
            GraphHelperFuns.checkNearBy(clientList[0], userList[0], userList[i])
            GraphHelperFuns.checkNearBy(clientList[i], userList[i], userList[0])
            assert len(list(GraphHelperFuns.getNearbyUsersMax(clientList[0], userList[0], i + 1)['users'])) == i  
        elif i == 101:
            GraphHelperFuns.checkNearBy(clientList[0], userList[0], userList[i])
            GraphHelperFuns.checkNearBy(clientList[i], userList[i], userList[0])
            assert GraphHelperFuns.getNearbyUsersMax(clientList[0], userList[0], i + 1)['error'] == 'maxPeople must be an integer from 1 to 100'
            assert len(list(GraphHelperFuns.getNearbyUsersMax(clientList[0], userList[0], 100)['users'])) == 100
    
    GraphHelperFuns.setRadius(userList[0], clientList[0], 1)

    clientList[0].post('/v1/logout')
    h = GraphHelperFuns.hacky_login(1, '1')
    clientList[0].post('/v1/setSession', data=json.dumps({'h':h}))

    assert len(list(GraphHelperFuns.getNearbyUsersMax(clientList[0], userList[0], 20)['users'])) == 20
         
    assert GraphHelperFuns.getNearbyUsersMax(clientList[0], userList[0], 0)['error'] == 'maxPeople must be an integer from 1 to 100'

    GraphHelperFuns.endMultiUserTest(clientList, socketList, userList)

def testCacheEdgesOptimization():
    clientList, socketList, userList = GraphHelperFuns.startMultiUserTest()

    #create 2 users
    numUsers = 2

    for i in range(0, numUsers):
        clientList, socketList, userList = GraphHelperFuns.createUser(clientList, socketList, userList)

    GraphHelperFuns.checkNotNearBulk(clientList, userList)
    
    GraphHelperFuns.postNearbyTwoWay(clientList[0], clientList[1], userList[0], userList[1])

    GraphHelperFuns.checkNearBy(clientList[0], userList[0], userList[1])
    GraphHelperFuns.checkNearBy(clientList[1], userList[1], userList[0])

    NearbyUsers.NearbyUsers.query.filter_by(userID=userList[0]).delete()
    NearbyUsers.NearbyUsers.query.filter_by(userID=userList[1]).delete()
    db.session.commit()

    GraphHelperFuns.checkNearBy(clientList[0], userList[0], userList[1])
    GraphHelperFuns.checkNearBy(clientList[1], userList[1], userList[0])
    
    GraphHelperFuns.endMultiUserTest(clientList, socketList, userList)

def testDeleteOldEdge():
    clientList, socketList, userList = GraphHelperFuns.startMultiUserTest()

    #create 2 users
    numUsers = 2

    for i in range(0, numUsers):
        clientList, socketList, userList = GraphHelperFuns.createUser(clientList, socketList, userList)

    request = NearbyUsers.NearbyUsers(userList[0], userList[1], datetime.datetime.utcnow()-datetime.timedelta(hours=25))
    db.session.add(request)
    db.session.commit()
    
    request = NearbyUsers.NearbyUsers(userList[1], userList[0], datetime.datetime.utcnow()-datetime.timedelta(hours=25))
    db.session.add(request)
    db.session.commit()

    GraphView.delete_old_graph_edges()

    GraphHelperFuns.checkNotNearBulk(clientList, userList)

    GraphHelperFuns.endMultiUserTest(clientList, socketList, userList)
