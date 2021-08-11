import sys
sys.path.insert(0, './helperFunctions')  
import UserHelperFuns, RequestHelperFuns, ChatHelperFuns, ChatsHelperFuns
import json
import datetime
import os
sys.path.append(os.path.abspath("../../src/Backend"))
from app import app, db
import db_commands
from app.models import Requests, UserRelations
from app.views import RequestsView

def testBlockAfterAcceptedRequest():
    test_client, test_client2, socket_client, socket_client2, userID1, userID2 = UserHelperFuns.startTwoUserTest()
    
    # userID1 sends request
    RequestHelperFuns.sendRequest(test_client, userID1, userID2)

    filtered = UserHelperFuns.getFiltered(test_client, userID1)
    assert len(filtered) == 1
    assert filtered[0].get("id") == userID2

    filtered = UserHelperFuns.getFiltered(test_client2, userID2)
    assert len(filtered) == 1
    assert filtered[0].get("id") == userID1

    requestlist = RequestHelperFuns.getRequests(test_client2, userID2)
    assert len(requestlist) == 1

    # user2 get socketio msg
    requestID = RequestHelperFuns.getReceivedRequest(socket_client2, userID1, userID2)

    # user1 blocks
    UserHelperFuns.blockUser(test_client, userID1, userID2)
    filtered = UserHelperFuns.getFiltered(test_client, userID1)
    assert filtered[0].get("id") == userID2

    # test: database to check relation
    UserHelperFuns.checkRelation(userID1, userID2, 'RelationEnum.blocked')

    # user2 accepts
    data = RequestHelperFuns.acceptRequest(test_client2, userID2, requestID)
    UserHelperFuns.checkIfConnected(test_client2, userID2, userID1)
    filtered = UserHelperFuns.getFiltered(test_client2, userID2)
    assert len(filtered) == 0

    requestlist = RequestHelperFuns.getRequests(test_client2, userID2)
    assert len(requestlist) == 0

    # check user is still blocked
    UserHelperFuns.checkRelation(userID1, userID2, 'RelationEnum.blocked')

    # user1 gets no further messages
    UserHelperFuns.checkNumSocketMessages(socket_client, 0)
    
    # user2 gets accept message
    chatID = ChatHelperFuns.getChatIDNewChat(data, userID2)

    # request deleted (accepted)
    RequestHelperFuns.checkNumRequests(requestID, 0)

    blocked = UserHelperFuns.getBlockedUsers(test_client, userID1, 1)

    assert blocked[0].get('userID') == str(userID2)

    ChatsHelperFuns.checkNumChats(chatID, userID1, userID2, 1)

    ChatHelperFuns.checkNumMessages(chatID, 1)
    UserHelperFuns.endTwoUserSession(test_client, test_client2, socket_client, socket_client2, userID1, userID2)

def testAcceptRequest():
    test_client, test_client2, socket_client, socket_client2, userID1, userID2 = UserHelperFuns.startTwoUserTest()
    
    # userID1 sends request
    RequestHelperFuns.sendRequest(test_client, userID1, userID2)

    # user2 get socketio msg
    requestID = RequestHelperFuns.getReceivedRequest(socket_client2, userID1, userID2)

    # check no current relations
    UserHelperFuns.checkRelation(userID1, userID2, "", 0)

    # accept request
    data = RequestHelperFuns.acceptRequest(test_client2, userID2, requestID)

    # check to see they're connected
    UserHelperFuns.checkRelation(userID1, userID2, "RelationEnum.connected")
    UserHelperFuns.checkIfConnected(test_client, userID1, userID2)
    UserHelperFuns.checkIfConnected(test_client2, userID2, userID1)

    # check that chatIDs from both ends are equal
    chatID = ChatHelperFuns.getChatIDAcceptRequest(socket_client, userID2)

    chatID2 = ChatHelperFuns.getChatIDNewChat(data, userID1)

    assert chatID == chatID2

    # request deleted, accepted
    RequestHelperFuns.checkNumRequests(requestID, 0)

    # still should be one chat with one message
    ChatsHelperFuns.checkNumChats(chatID, userID1, userID2, 1)

    ChatHelperFuns.checkNumMessages(chatID, 1)
    UserHelperFuns.endTwoUserSession(test_client, test_client2, socket_client, socket_client2, userID1, userID2)

def testDeclineRequest():
    test_client, test_client2, socket_client, socket_client2, userID1, userID2 = UserHelperFuns.startTwoUserTest()

    # userID1 sends request
    RequestHelperFuns.sendRequest(test_client, userID1, userID2)

    # user2 get socketio msg
    requestID = RequestHelperFuns.getReceivedRequest(socket_client2, userID1, userID2)

    # check no current relations
    UserHelperFuns.checkRelation(userID1, userID2, "", 0)
    UserHelperFuns.checkRelation(userID2, userID1, "", 0)

    # decline request
    RequestHelperFuns.declineRequest(test_client2, userID2, requestID)

    # still no relation
    UserHelperFuns.checkRelation(userID1, userID2, "", 0)
    UserHelperFuns.checkRelation(userID2, userID1, "", 0)

    # both users should have no incoming messages
    UserHelperFuns.checkNumSocketMessages(socket_client, 0)

    UserHelperFuns.checkNumSocketMessages(socket_client2, 0)

    # request still in db
    RequestHelperFuns.checkNumRequests(requestID, 1)
    UserHelperFuns.endTwoUserSession(test_client, test_client2, socket_client, socket_client2, userID1, userID2)

def testBlockAfterRequest():
    test_client, test_client2, socket_client, socket_client2, userID1, userID2 = UserHelperFuns.startTwoUserTest()

    RequestHelperFuns.sendRequest(test_client, userID1, userID2)

    requestID = RequestHelperFuns.getReceivedRequest(socket_client2, userID1, userID2)

    UserHelperFuns.blockUser(test_client2, userID2, userID1)

    UserHelperFuns.checkRelation(userID2, userID1, 'RelationEnum.blocked')

    UserHelperFuns.checkRelation(userID1, userID2, '', 0)

    RequestHelperFuns.checkNumRequests(requestID, 1)

    blocked = UserHelperFuns.getBlockedUsers(test_client2, userID2, 1)

    assert blocked[0].get('userID') == str(userID1)
    UserHelperFuns.endTwoUserSession(test_client, test_client2, socket_client, socket_client2, userID1, userID2)

def testBlockAfterDeclinedRequest():
    test_client, test_client2, socket_client, socket_client2, userID1, userID2 = UserHelperFuns.startTwoUserTest()
    
    RequestHelperFuns.sendRequest(test_client, userID1, userID2)

    requestID = RequestHelperFuns.getReceivedRequest(socket_client2, userID1, userID2)

    UserHelperFuns.blockUser(test_client, userID1, userID2)

    UserHelperFuns.checkRelation(userID1, userID2, 'RelationEnum.blocked')

    RequestHelperFuns.declineRequest(test_client2, userID2, requestID)

    UserHelperFuns.checkRelation(userID1, userID2, 'RelationEnum.blocked')

    UserHelperFuns.checkNumSocketMessages(socket_client, 0)

    RequestHelperFuns.checkNumRequests(requestID, 1)

    ChatsHelperFuns.checkTotalChats(0)

    blocked = UserHelperFuns.getBlockedUsers(test_client, userID1, 1)

    assert blocked[0].get('userID') == str(userID2)
    UserHelperFuns.endTwoUserSession(test_client, test_client2, socket_client, socket_client2, userID1, userID2)

def testSendRequestAfterBlocked():
    test_client, test_client2, socket_client, socket_client2, userID1, userID2 = UserHelperFuns.startTwoUserTest()
    
    UserHelperFuns.blockUser(test_client, userID1, userID2)

    UserHelperFuns.checkRelation(userID1, userID2, 'RelationEnum.blocked')

    RequestHelperFuns.sendRequest(test_client, userID1, userID2, success=False)

    UserHelperFuns.endTwoUserSession(test_client, test_client2, socket_client, socket_client2, userID1, userID2)

def testTwoWayAcceptRequest():
    test_client, test_client2, socket_client, socket_client2, userID1, userID2 = UserHelperFuns.startTwoUserTest()

    RequestHelperFuns.sendRequest(test_client, userID1, userID2)

    requestID1 = RequestHelperFuns.getReceivedRequest(socket_client2, userID1, userID2)

    UserHelperFuns.checkRelation(userID1, userID2, "", 0)

    RequestHelperFuns.sendRequest(test_client2, userID2, userID1)

    requestID2 = RequestHelperFuns.getReceivedRequest(socket_client, userID2, userID1)

    UserHelperFuns.checkRelation(userID1, userID2, "", 0)

    RequestHelperFuns.acceptRequest(test_client2, userID2, requestID1)
    recvd = socket_client.get_received()
    assert len(recvd) == 1

    UserHelperFuns.checkRelation(userID1, userID2, "RelationEnum.connected")
    UserHelperFuns.checkRelation(userID2, userID1, "RelationEnum.connected")
    UserHelperFuns.checkIfConnected(test_client, userID1, userID2)
    UserHelperFuns.checkIfConnected(test_client2, userID2, userID1)

    RequestHelperFuns.acceptRequest(test_client, userID1, requestID2, success=False)

    recvd = socket_client.get_received()
    assert len(recvd) == 0

    UserHelperFuns.endTwoUserSession(test_client, test_client2, socket_client, socket_client2, userID1, userID2)

def testTwoWayDeclineRequest():
    test_client, test_client2, socket_client, socket_client2, userID1, userID2 = UserHelperFuns.startTwoUserTest()
    
    RequestHelperFuns.sendRequest(test_client, userID1, userID2)

    requestID1 = RequestHelperFuns.getReceivedRequest(socket_client2, userID1, userID2)

    UserHelperFuns.checkRelation(userID1, userID2, "", 0)

    RequestHelperFuns.sendRequest(test_client2, userID2, userID1)

    requestID2 = RequestHelperFuns.getReceivedRequest(socket_client, userID2, userID1)

    UserHelperFuns.checkRelation(userID1, userID2, "", 0)

    RequestHelperFuns.declineRequest(test_client2, userID2, requestID1)
    recvd = socket_client.get_received()
    assert len(recvd) == 0

    RequestHelperFuns.declineRequest(test_client, userID1, requestID2, success=False)

    recvd = socket_client.get_received()
    assert len(recvd) == 0

    UserHelperFuns.endTwoUserSession(test_client, test_client2, socket_client, socket_client2, userID1, userID2)

def testErrorCheckingSendRequest():
    test_client, test_client2, socket_client, socket_client2, userID1, userID2 = UserHelperFuns.startTwoUserTest()
    
    # test when data is not a jsonable string
    response = test_client.post('v1/sendRequest', data=dict(test=42))
    assert response != "200 OK"

    # test when data does not contain either userID or msg
    response = test_client.post('v1/sendRequest', data=json.dumps(dict(userID=userID1, receiverID=userID2)))
    assert response != "200 OK"

    response = test_client.post('v1/sendRequest', data=json.dumps(dict(userID=userID1, msg="")))
    assert response != "200 OK"

    response = test_client.post('v1/sendRequest', data=json.dumps(dict(receiverID=userID2, msg="")))
    assert response != "200 OK"

    response = test_client.post('v1/sendRequest', data=json.dumps(dict(userID=userID1, receiverID="Hello", msg="")))
    assert response != "200 OK"

    # test when userID is not type long
    RequestHelperFuns.sendRequest(test_client, "NotaLong", userID2, success=False)

    # test when receiverID invalid (where 42 is not an actual userID)
    RequestHelperFuns.sendRequest(test_client, userID1, "42", success=False)

    # test userID != receiverID
    RequestHelperFuns.sendRequest(test_client, userID1, userID1, success=False)

    # test can't send two requests to someone
    RequestHelperFuns.sendRequest(test_client, userID1, userID2)
    RequestHelperFuns.sendRequest(test_client, userID1, userID2, success=False)

    # test sending request to connected user
    requestID = RequestHelperFuns.getReceivedRequest(socket_client2, userID1, userID2)
    RequestHelperFuns.acceptRequest(test_client2, userID2, requestID)
    RequestHelperFuns.sendRequest(test_client, userID1, userID2, success=False)

    # test request not send if logged out
    socket_client.emit('remove user', {'userID':userID1})
    test_client.post('v1/logout')
    socket_client2.emit('remove user', {'userID':userID2})
    test_client2.post('v1/logout')
    RequestHelperFuns.sendRequest(test_client, userID1, userID2, success=False)
    assert db_commands.close_session() == "DB Session Ended"
    assert db_commands.clear_db() == "DB Tables dropped"

    test_client, test_client2, socket_client, socket_client2, userID1, userID2 = UserHelperFuns.startTwoUserTest()
    UserHelperFuns.blockUser(test_client2, userID2, userID1)
    RequestHelperFuns.sendRequest(test_client, userID1, userID2)
    UserHelperFuns.unblockUser(test_client2, userID2, userID1)
    assert db_commands.close_session() == "DB Session Ended"
    assert db_commands.clear_db() == "DB Tables dropped"

    test_client, test_client2, socket_client, socket_client2, userID1, userID2 = UserHelperFuns.startTwoUserTest()

    db.session.add(UserRelations.UserRelations(userID2, userID1, UserRelations.RelationEnum.longdistance))
    db.session.commit()

    RequestHelperFuns.sendRequest(test_client, userID1, userID2, success=False)
    assert db_commands.close_session() == "DB Session Ended"
    assert db_commands.clear_db() == "DB Tables dropped"

def testErrorCheckingAcceptRequest():
    test_client, test_client2, socket_client, socket_client2, userID1, userID2 = UserHelperFuns.startTwoUserTest()

    RequestHelperFuns.sendRequest(test_client, userID1, userID2)
    requestID = RequestHelperFuns.getReceivedRequest(socket_client2, userID1, userID2)

    # test body is not jsonable string
    response = test_client.post('v1/acceptRequest', data=dict(test=42))
    assert response != "200 OK"

    # test body does not have userID or requestID
    response = test_client.post('v1/acceptRequest', data=json.dumps(dict(userID=userID2)))
    assert response != "200 OK"

    response = test_client.post('v1/acceptRequest', data=json.dumps(dict(requestID=requestID)))
    assert response != "200 OK"

    # test body must have userid and requestid of type long
    RequestHelperFuns.acceptRequest(test_client2, "NotaLong", requestID, success=False)
    RequestHelperFuns.acceptRequest(test_client2, userID2, "NotaLong", success=False)

    # test shoudl not accept request if from wrong user
    RequestHelperFuns.acceptRequest(test_client, userID1, requestID, success=False)

    # test cannot accept request of blocked user
    UserHelperFuns.blockUser(test_client2, userID2, userID1)
    RequestHelperFuns.acceptRequest(test_client2, userID2, requestID, success=False)
    UserHelperFuns.unblockUser(test_client2, userID2, userID1)

    # test cannot accept request when logged out
    socket_client.emit('remove user', {'userID':userID1})
    test_client.post('v1/logout')
    socket_client2.emit('remove user', {'userID':userID2})
    test_client2.post('v1/logout')
    RequestHelperFuns.acceptRequest(test_client2, userID2, requestID, success=False)
    assert db_commands.close_session() == "DB Session Ended"
    assert db_commands.clear_db() == "DB Tables dropped"

def testErrorCheckingGetRequests():
    test_client, test_client2, socket_client, socket_client2, userID1, userID2 = UserHelperFuns.startTwoUserTest()

    # test userid is type long
    RequestHelperFuns.getRequests(test_client, "NotaLong", success=False)

    # test cannot get requests if not logged in
    socket_client.emit('remove user', {'userID':userID1})
    test_client.post('v1/logout')
    socket_client2.emit('remove user', {'userID':userID2})
    test_client2.post('v1/logout')
    RequestHelperFuns.getRequests(test_client, userID1, success=False)
    assert db_commands.close_session() == "DB Session Ended"
    assert db_commands.clear_db() == "DB Tables dropped"

def testErrorCheckingDeclineRequest():
    test_client, test_client2, socket_client, socket_client2, userID1, userID2 = UserHelperFuns.startTwoUserTest()

    response = test_client.post('v1/declineRequest', data=dict(test=42))
    assert response.status != '200 OK'

    RequestHelperFuns.sendRequest(test_client, userID1, userID2)
    requestID = RequestHelperFuns.getReceivedRequest(socket_client2, userID1, userID2)

    response = test_client.post('v1/declineRequest', data=json.dumps(dict(userID=userID1)))
    assert response.status != '200 OK'
    response = test_client.post('v1/declineRequest', data=json.dumps(dict(requestID=requestID)))
    assert response.status != '200 OK'

    RequestHelperFuns.declineRequest(test_client2, "NotaLong", requestID, success=False)

    RequestHelperFuns.declineRequest(test_client2, userID2, "NotaLong", success=False)

    RequestHelperFuns.declineRequest(test_client2, userID2, "42", success=False)

    RequestHelperFuns.declineRequest(test_client, userID1, requestID, success=False)

    socket_client.emit('remove user', {'userID':userID1})
    test_client.post('v1/logout')
    socket_client2.emit('remove user', {'userID':userID2})
    test_client2.post('v1/logout')
    RequestHelperFuns.declineRequest(test_client2, userID2, requestID, success=False)
    assert db_commands.close_session() == "DB Session Ended"
    assert db_commands.clear_db() == "DB Tables dropped"

def testDeleteOldRequests():
    test_client, test_client2, socket_client, socket_client2, userID1, userID2 = UserHelperFuns.startTwoUserTest()

    request = Requests.Requests(userID1, userID2, "", datetime.datetime.utcnow()-datetime.timedelta(hours=25))
    db.session.add(request)
    db.session.commit()

    assert len(RequestHelperFuns.getRequests(test_client2, userID2)) == 1

    RequestsView.delete_old_requests()

    assert len(RequestHelperFuns.getRequests(test_client2, userID2)) == 0

    UserHelperFuns.endTwoUserSession(test_client, test_client2, socket_client, socket_client2, userID1, userID2)
    