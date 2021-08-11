import sys                                                                                                                                         
sys.path.insert(0, './helperFunctions')                                                                                                            
import UserHelperFuns, RequestHelperFuns, ChatHelperFuns, ChatsHelperFuns
import json
import os
sys.path.append(os.path.abspath("../../src/Backend"))
from app import app, db, socketio
from app.views import UserView
import db_commands

def testUnblock():
    test_client, test_client2, socket_client, socket_client2, userID1, userID2 = UserHelperFuns.startTwoUserTest()
    
    RequestHelperFuns.sendRequest(test_client, userID1, userID2)

    requestID = RequestHelperFuns.getReceivedRequest(socket_client2, userID1, userID2)

    UserHelperFuns.checkRelation(userID1, userID2, "", 0)

    data = RequestHelperFuns.acceptRequest(test_client2, userID2, requestID)

    UserHelperFuns.checkRelation(userID1, userID2, "RelationEnum.connected")
    UserHelperFuns.checkRelation(userID2, userID1, "RelationEnum.connected")
    UserHelperFuns.checkIfConnected(test_client, userID1, userID2)
    UserHelperFuns.checkIfConnected(test_client2, userID2, userID1)

    chatID = ChatHelperFuns.getChatIDAcceptRequest(socket_client, userID2)

    chatID2 = ChatHelperFuns.getChatIDNewChat(data, userID1)

    assert chatID == chatID2
    RequestHelperFuns.checkNumRequests(requestID, 0)

    ChatsHelperFuns.checkNumChats(chatID, userID1, userID2, 1)

    ChatHelperFuns.checkNumMessages(chatID, 1)

    initial = ChatHelperFuns.getChatName(userID2, chatID2)
    initial2 = ChatHelperFuns.getChatName(userID1, chatID)

    UserHelperFuns.blockUser(test_client, userID1, userID2)
    filtered = UserHelperFuns.getFiltered(test_client, userID1)
    assert len(filtered) == 1
    assert filtered[0].get("id") == userID2
    UserHelperFuns.checkRelation(userID1, userID2, "RelationEnum.blocked")
    UserHelperFuns.checkIfConnected(test_client2, userID2, userID1)

    assert initial == ChatHelperFuns.getChatName(userID2, chatID2)

    UserHelperFuns.unblockUser(test_client, userID1, userID2)
    filtered = UserHelperFuns.getFiltered(test_client, userID1)
    assert len(filtered) == 0
    UserHelperFuns.checkIfConnected(test_client, userID1, userID2)
    UserHelperFuns.checkIfConnected(test_client2, userID2, userID1)

    assert initial2 == ChatHelperFuns.getChatName(userID1, chatID)
    UserHelperFuns.endTwoUserSession(test_client, test_client2, socket_client, socket_client2, userID1, userID2)

def testDeactivateAccount():
    test_client, test_client2, socket_client, socket_client2, userID1, userID2 = UserHelperFuns.startTwoUserTest()
    
    RequestHelperFuns.sendRequest(test_client, userID1, userID2)

    requestID = RequestHelperFuns.getReceivedRequest(socket_client2, userID1, userID2)

    UserHelperFuns.checkRelation(userID1, userID2, "", 0)

    data = RequestHelperFuns.acceptRequest(test_client2, userID2, requestID)

    UserHelperFuns.checkRelation(userID1, userID2, "RelationEnum.connected")
    UserHelperFuns.checkRelation(userID2, userID1, "RelationEnum.connected")
    UserHelperFuns.checkIfConnected(test_client, userID1, userID2)
    UserHelperFuns.checkIfConnected(test_client2, userID2, userID1)

    chatID = ChatHelperFuns.getChatIDAcceptRequest(socket_client, userID2)

    chatID2 = ChatHelperFuns.getChatIDNewChat(data, userID1)

    assert chatID == chatID2
    RequestHelperFuns.checkNumRequests(requestID, 0)

    ChatsHelperFuns.checkNumChats(chatID, userID1, userID2, 1)

    ChatHelperFuns.checkNumMessages(chatID, 1)

    UserHelperFuns.deactivateUser(test_client, userID1)

    UserHelperFuns.checkRelation(userID1, userID2, "", 0)
    UserHelperFuns.checkRelation(userID2, userID1, "", 0)
    UserHelperFuns.endTwoUserSession(test_client, test_client2, socket_client, socket_client2, userID1, userID2)

def testErrorCheckingLogin():
    assert db_commands.close_session() == "DB Session Ended"
    assert db_commands.clear_db() == "DB Tables dropped"

    assert db_commands.create_db() == "DB Created Successfully"
    test_client = app.test_client()

    response = test_client.post('/v1/login',data=dict(test=42))
    assert response.status != '200 OK'

    test_client.post('/v1/login',data=json.dumps(dict(userID="42",accessToken="42")))
    assert response.status != '200 OK'

    test_client.post('/v1/login',data=json.dumps(dict(userID="42")))
    assert response.status != '200 OK'

    test_client.post('/v1/login',data=json.dumps(dict(accessToken="42")))
    assert response.status != '200 OK'

    test_client.post('/v1/login',data=json.dumps(dict(userID="Hello", accessToken="EAAIFungVNekBAEBPZB6aItiwSMCk9ftAwq4II95zFJEZCsVWkb0TcmlyIAZA9iVCadOZARcLFxRKqwurq3cxKQkh8QnEEC1mVPjpV0UkNnaGNNuUELauoXtUSNiVgIi7cpLvaMGWZA4ALQVpZC1mTkTRUju8VZBPxSUvX4sa8cA6X5tU4018fMzZCvZBD6p4xt7svFy6ZCD9jlQ9PZCV0V4j0lH1Ogd20shsorOZAIkvZABVq7QZDZD")))
    assert response.status != '200 OK'

    test_client.post('/v1/login',data=json.dumps(dict(userID="42", accessToken="EAAIFungVNekBAEBPZB6aItiwSMCk9ftAwq4II95zFJEZCsVWkb0TcmlyIAZA9iVCadOZARcLFxRKqwurq3cxKQkh8QnEEC1mVPjpV0UkNnaGNNuUELauoXtUSNiVgIi7cpLvaMGWZA4ALQVpZC1mTkTRUju8VZBPxSUvX4sa8cA6X5tU4018fMzZCvZBD6p4xt7svFy6ZCD9jlQ9PZCV0V4j0lH1Ogd20shsorOZAIkvZABVq7QZDZD")))
    assert response.status != '200 OK'

    test_client.post('v1/logout')
    assert db_commands.close_session() == "DB Session Ended"
    assert db_commands.clear_db() == "DB Tables dropped"

def testErrorCheckingNewUser():
    assert db_commands.close_session() == "DB Session Ended"
    assert db_commands.clear_db() == "DB Tables dropped"

    assert db_commands.create_db() == "DB Created Successfully"
    socket_client = socketio.test_client(app)

    socket_client.emit('new user', {'test':42})

    assert db_commands.close_session() == "DB Session Ended"
    assert db_commands.clear_db() == "DB Tables dropped"

def testIndex():
    assert UserView.index() == 'Hello World'

def testErrorCheckingRemoveUser():
    assert db_commands.close_session() == "DB Session Ended"
    assert db_commands.clear_db() == "DB Tables dropped"

    assert db_commands.create_db() == "DB Created Successfully"
    socket_client = socketio.test_client(app)

    socket_client.emit('remove user', {'test':42})
    socket_client.emit('remove user', {'userID':"Hello"})
    socket_client.emit('remove user', {'userID':"42"})

    assert db_commands.close_session() == "DB Session Ended"
    assert db_commands.clear_db() == "DB Tables dropped"

def testErrorCheckingDeactivateAccount():
    assert db_commands.close_session() == "DB Session Ended"
    assert db_commands.clear_db() == "DB Tables dropped"

    assert db_commands.create_db() == "DB Created Successfully"

    test_client = app.test_client()

    socket_client = socketio.test_client(app)
    socket_client.get_received()

    userID = UserHelperFuns.createUser1(test_client, socket_client)

    response = test_client.post('/v1/deactivate/' + "NotaLong", data=dict(test=42))
    assert response.status != '200 OK'

    socket_client.emit('remove user', {'userID':userID})
    test_client.post('v1/logout')
    UserHelperFuns.deactivateUser(test_client, userID, success=False)
    assert db_commands.close_session() == "DB Session Ended"
    assert db_commands.clear_db() == "DB Tables dropped"

def testErrorCheckingGetFiltered():
    assert db_commands.close_session() == "DB Session Ended"
    assert db_commands.clear_db() == "DB Tables dropped"

    assert db_commands.create_db() == "DB Created Successfully"

    test_client = app.test_client()

    socket_client = socketio.test_client(app)
    socket_client.get_received()

    userID = UserHelperFuns.createUser1(test_client, socket_client)

    response = test_client.get('/v1/filtered/' + "NotaLong", data=dict(test=42))
    assert response.status != '200 OK'

    socket_client.emit('remove user', {'userID':userID})
    test_client.post('v1/logout')
    UserHelperFuns.getFiltered(test_client, userID, success=False)
    assert db_commands.close_session() == "DB Session Ended"
    assert db_commands.clear_db() == "DB Tables dropped"

def testErrorCheckingUnblock():
    test_client, test_client2, socket_client, socket_client2, userID1, userID2 = UserHelperFuns.startTwoUserTest()

    response = test_client.post('/v1/unblock/' + str(userID2), data=dict(test=42))
    assert response.status != '200 OK'

    response = test_client.post('/v1/unblock/' + str(userID2), data=json.dumps(dict(test=42)))
    assert response.status != '200 OK'

    response = test_client.post('/v1/unblock/' + "NotaLong", data=json.dumps(dict(userID=userID1)))
    assert response.status != '200 OK'

    response = test_client.post('/v1/unblock/' + str(userID2), data=json.dumps(dict(userID="NotaLong")))
    assert response.status != '200 OK'

    response = test_client.post('/v1/unblock/' + "42", data=json.dumps(dict(userID=userID1)))
    assert response.status != '200 OK'

    UserHelperFuns.unblockUser(test_client, userID1, userID2, success=False)

    socket_client.emit('remove user', {'userID':userID1})
    test_client.post('v1/logout')
    socket_client2.emit('remove user', {'userID':userID2})
    test_client2.post('v1/logout')
    UserHelperFuns.unblockUser(test_client, userID1, userID2, success=False)
    assert db_commands.close_session() == "DB Session Ended"
    assert db_commands.clear_db() == "DB Tables dropped"

def testErrorCheckingBlock():
    test_client, test_client2, socket_client, socket_client2, userID1, userID2 = UserHelperFuns.startTwoUserTest()

    response = test_client.post('/v1/block/' + str(userID2), data=dict(test=42))
    assert response.status != '200 OK'

    response = test_client.post('/v1/block/' + str(userID2), data=json.dumps(dict(test=42)))
    assert response.status != '200 OK'

    response = test_client.post('/v1/block/' + "NotaLong", data=json.dumps(dict(userID=userID1)))
    assert response.status != '200 OK'

    response = test_client.post('/v1/block/' + str(userID2), data=json.dumps(dict(userID="NotaLong")))
    assert response.status != '200 OK'

    response = test_client.post('/v1/block/' + "42", data=json.dumps(dict(userID=userID1)))
    assert response.status != '200 OK'

    socket_client.emit('remove user', {'userID':userID1})
    test_client.post('v1/logout')
    socket_client2.emit('remove user', {'userID':userID2})
    test_client2.post('v1/logout')
    UserHelperFuns.blockUser(test_client, userID1, userID2, success=False)
    assert db_commands.close_session() == "DB Session Ended"
    assert db_commands.clear_db() == "DB Tables dropped"

def testErrorCheckingGetBlockedUsers():
    assert db_commands.close_session() == "DB Session Ended"
    assert db_commands.clear_db() == "DB Tables dropped"

    assert db_commands.create_db() == "DB Created Successfully"

    test_client = app.test_client()

    socket_client = socketio.test_client(app)
    socket_client.get_received()

    userID = UserHelperFuns.createUser1(test_client, socket_client)

    response = test_client.get('/v1/block/' + "NotaLong", data=json.dumps(dict(userID="NotaLong")))
    assert response.status != '200 OK'

    socket_client.emit('remove user', {'userID':userID})
    test_client.post('v1/logout')
    UserHelperFuns.getBlockedUsers(test_client, userID, 0, success=False)
    assert db_commands.close_session() == "DB Session Ended"
    assert db_commands.clear_db() == "DB Tables dropped"

def testErrorCheckingCheckIfConnected():
    test_client, test_client2, socket_client, socket_client2, userID1, userID2 = UserHelperFuns.startTwoUserTest()

    response = test_client.get('/v1/isConnected/' + "NotaLong" + '/' + str(userID2), data=json.dumps(dict(userID=userID1, userID2=userID2)))
    assert response.status != '200 OK'

    response = test_client.get('/v1/isConnected/' + str(userID1) + '/' + "NotaLong", data=json.dumps(dict(userID=userID1, userID2=userID2)))
    assert response.status != '200 OK'

    response = test_client.get('/v1/isConnected/' + str(userID1) + '/' + "42", data=json.dumps(dict(userID=userID1, userID2=userID2)))
    assert response.status != '200 OK'

    response = test_client.get('/v1/isConnected/' + str(userID1) + '/' + str(userID2), data=json.dumps(dict(userID=userID1, userID2=userID2)))
    assert response.status == '200 OK'
    data = json.loads(response.get_data(as_text=True))
    assert data['connected'] == False

    socket_client.emit('remove user', {'userID':userID1})
    test_client.post('v1/logout')
    socket_client2.emit('remove user', {'userID':userID2})
    test_client2.post('v1/logout')
    UserHelperFuns.checkIfConnected(test_client, userID1, userID2, success=False)
    assert db_commands.close_session() == "DB Session Ended"
    assert db_commands.clear_db() == "DB Tables dropped"

def testErrorCheckingCheckIfLongDistance():
    test_client, test_client2, socket_client, socket_client2, userID1, userID2 = UserHelperFuns.startTwoUserTest()

    response = test_client.get('/v1/longdistance/' + str(userID1) + "/", data=json.dumps(dict(userID=userID1)))
    assert response.status != '200 OK'

    response = test_client.get('/v1/longdistance/' + "/" + str(userID2), data=json.dumps(dict(userID2=userID2)))
    assert response.status != '200 OK'

    response = test_client.get('/v1/longdistance/' + "NotaLong" + "/" + str(userID2), data=json.dumps(dict(userID="NotaLong", userID2=userID2)))
    assert response.status != '200 OK'

    response = test_client.get('/v1/longdistance/' + str(userID1) + "/" + "NotaLong", data=json.dumps(dict(userID=userID1, userID2="NotaLong")))
    assert response.status != '200 OK'

    response = test_client.get('/v1/longdistance/' + str(userID1) + "/" + "42", data=json.dumps(dict(userID=userID1, userID2="42")))
    assert response.status != '200 OK'

    socket_client.emit('remove user', {'userID':userID1})
    test_client.post('v1/logout')
    socket_client2.emit('remove user', {'userID':userID2})
    test_client2.post('v1/logout')
    response = test_client.get('/v1/longdistance/' + str(userID1) + "/" + str(userID2), data=json.dumps(dict(userID=userID1, userID2=userID2)))
    assert response != '200 OK'
    assert db_commands.close_session() == "DB Session Ended"
    assert db_commands.clear_db() == "DB Tables dropped"

def testErrorCheckingPostLongDistance():
    test_client, test_client2, socket_client, socket_client2, userID1, userID2 = UserHelperFuns.startTwoUserTest()

    response = test_client.post('/v1/longdistance/' + str(userID2), data=dict(test=42))
    assert response.status != '200 OK'

    response = test_client.post('/v1/longdistance/' + str(userID2), data=json.dumps(dict(test=42)))
    assert response.status != '200 OK'

    response = test_client.post('/v1/longdistance/' + "NotaLong", data=json.dumps(dict(userID=userID1)))
    assert response.status != '200 OK'

    response = test_client.post('/v1/longdistance/' + str(userID2), data=json.dumps(dict(userID="NotaLong")))
    assert response.status != '200 OK'

    response = test_client.post('/v1/longdistance/' + "42", data=json.dumps(dict(userID=userID1)))
    assert response.status != '200 OK'

    socket_client.emit('remove user', {'userID':userID1})
    test_client.post('v1/logout')
    socket_client2.emit('remove user', {'userID':userID2})
    test_client2.post('v1/logout')
    response = test_client.post('/v1/longdistance/' + str(userID2), data=json.dumps(dict(userID=userID1)))
    assert response.status != '200 OK'
    assert db_commands.close_session() == "DB Session Ended"
    assert db_commands.clear_db() == "DB Tables dropped"

def testErrorCheckingPostNotLongDistance():
    test_client, test_client2, socket_client, socket_client2, userID1, userID2 = UserHelperFuns.startTwoUserTest()

    response = test_client.post('/v1/notlongdistance/' + str(userID2), data=dict(test=42))
    assert response.status != '200 OK'

    response = test_client.post('/v1/notlongdistance/' + str(userID2), data=json.dumps(dict(test=42)))
    assert response.status != '200 OK'

    response = test_client.post('/v1/notlongdistance/' + "NotaLong", data=json.dumps(dict(userID=userID1)))
    assert response.status != '200 OK'

    response = test_client.post('/v1/notlongdistance/' + str(userID2), data=json.dumps(dict(userID="NotaLong")))
    assert response.status != '200 OK'

    response = test_client.post('/v1/notlongdistance/' + "42", data=json.dumps(dict(userID=userID1)))
    assert response.status != '200 OK'

    socket_client.emit('remove user', {'userID':userID1})
    test_client.post('v1/logout')
    socket_client2.emit('remove user', {'userID':userID2})
    test_client2.post('v1/logout')
    response = test_client.post('/v1/notlongdistance/' + str(userID2), data=json.dumps(dict(userID=userID1)))
    assert response.status != '200 OK'
    assert db_commands.close_session() == "DB Session Ended"
    assert db_commands.clear_db() == "DB Tables dropped"
    