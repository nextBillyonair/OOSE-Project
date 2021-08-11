import sys                                                                                                                                         
sys.path.insert(0, './helperFunctions')  
import UserHelperFuns, RequestHelperFuns, ChatHelperFuns, ChatsHelperFuns, GraphHelperFuns
import json
import os
sys.path.append(os.path.abspath("../../src/Backend"))
from app import app, db, socketio
import db_commands
from app.models import Chats, NearbyUsers, Messages, UnseenMsgs, ChatNames, UserRelations
from app.views.randomnames import version
import datetime

# Tests sending a message to a connected user
def testSendMessageToConnectedUser():
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
    UserHelperFuns.checkRelation(userID2, userID1, "RelationEnum.connected")
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

    chat1 = ChatHelperFuns.getChat(test_client, userID1, chatID)
    chat2 = ChatHelperFuns.getChat(test_client2, userID2, chatID2)

    assert chat1 == chat2

    #Sends the message
    ChatHelperFuns.sendMessage(test_client, userID1, chatID, "test message")

    ChatHelperFuns.checkNumMessages(chatID, 2)
    ChatHelperFuns.checkNumMessages(chatID2, 2)

    chat1 = ChatHelperFuns.getChat(test_client, userID1, chatID)
    chat2 = ChatHelperFuns.getChat(test_client2, userID2, chatID2)

    UserHelperFuns.checkNumSocketMessages(socket_client, 0)
    UserHelperFuns.checkNumSocketMessages(socket_client2, 1)

    assert len(chat1) == len(chat2)

    assert chat1 == chat2

    mList1 = []
    mList2 = []

    for message in chat1:
        mList1.append(message.get("msg"))
    for message in chat2:
        mList2.append(message.get("msg"))

    assert len(mList1) == 2 and len(mList2) == 2
    assert mList1 == mList2
    assert "test message" == mList1[0]
    assert "test message" == mList2[0]

    UnseenMsgs.UnseenMsgs.query.filter_by(chatID=chatID).delete()
    Messages.Messages.query.filter_by(chatID=chatID).delete()
    ChatNames.ChatNames.query.filter_by(chatID=chatID).delete()
    Chats.Chats.query.filter_by(chatID=chatID).delete()
    db.session.commit()

    ChatHelperFuns.sendMessage(test_client, userID1, chatID, "test message", False)

    UserHelperFuns.endTwoUserSession(test_client, test_client2, socket_client, socket_client2, userID1, userID2)

# Tests sending a message to a blocked connected user
def testSendMessageToConnectedBlockedUser():
    test_client, test_client2, socket_client, socket_client2, userID1, userID2 = UserHelperFuns.startTwoUserTest()

    # userID1 sends request
    RequestHelperFuns.sendRequest(test_client, userID1, userID2)

    # user2 get socketio msg
    requestID = RequestHelperFuns.getReceivedRequest(socket_client2, userID1, userID2)

    # check no current relations
    UserHelperFuns.checkRelation(userID1, userID2, "", 0)

    data = RequestHelperFuns.acceptRequest(test_client2, userID2, requestID)
    UserHelperFuns.checkRelation(userID1, userID2, "RelationEnum.connected")
    UserHelperFuns.checkRelation(userID2, userID1, "RelationEnum.connected")
    UserHelperFuns.checkIfConnected(test_client, userID1, userID2)
    UserHelperFuns.checkIfConnected(test_client2, userID2, userID1)

    user1Chats = ChatsHelperFuns.getChats(test_client, userID1)
    user2Chats = ChatsHelperFuns.getChats(test_client2, userID2)

    assert len(user1Chats) == len(user2Chats)

    # user2 blocks
    UserHelperFuns.blockUser(test_client2, userID2, userID1)

    # test: database to check relation
    UserHelperFuns.checkRelation(userID2, userID1, 'RelationEnum.blocked')
    UserHelperFuns.checkRelation(userID1, userID2, "RelationEnum.connected")

    chatID = ChatHelperFuns.getChatIDAcceptRequest(socket_client, userID2)

    chatID2 = ChatHelperFuns.getChatIDNewChat(data, userID1)

    assert chatID == chatID2

    RequestHelperFuns.checkNumRequests(requestID, 0)

    ChatsHelperFuns.checkNumChats(chatID, userID1, userID2, 1)

    ChatHelperFuns.checkNumMessages(chatID, 1)

    chat1 = ChatHelperFuns.getChat(test_client, userID1, chatID)
    chat2 = ChatHelperFuns.getChat(test_client2, userID2, chatID2)

    assert chat1 == chat2

    #Sends the message

    ChatHelperFuns.sendMessage(test_client, userID1, chatID, "test message")

    user1Chats = ChatsHelperFuns.getChats(test_client, userID1)
    user2Chats = ChatsHelperFuns.getChats(test_client2, userID2)

    assert len(user1Chats) == len(user2Chats) + 1

    ChatHelperFuns.checkNumMessages(chatID, 2)

    UserHelperFuns.checkNumSocketMessages(socket_client, 0)
    UserHelperFuns.checkNumSocketMessages(socket_client2, 0)
    UserHelperFuns.endTwoUserSession(test_client, test_client2, socket_client, socket_client2, userID1, userID2)

# Tests sending a message to a connected user where the sender has receiver blocked
def testSendMessageToConnectedUserWhileBlockingUser():
    test_client, test_client2, socket_client, socket_client2, userID1, userID2 = UserHelperFuns.startTwoUserTest()
    
    # userID1 sends request
    RequestHelperFuns.sendRequest(test_client, userID1, userID2)

    # user2 get socketio msg
    requestID = RequestHelperFuns.getReceivedRequest(socket_client2, userID1, userID2)

    # check no current relations
    UserHelperFuns.checkRelation(userID1, userID2, "", 0)

    data = RequestHelperFuns.acceptRequest(test_client2, userID2, requestID)
    UserHelperFuns.checkRelation(userID1, userID2, "RelationEnum.connected")
    UserHelperFuns.checkRelation(userID2, userID1, "RelationEnum.connected")
    UserHelperFuns.checkIfConnected(test_client, userID1, userID2)
    UserHelperFuns.checkIfConnected(test_client2, userID2, userID1)

    user1Chats = ChatsHelperFuns.getChats(test_client, userID1)
    user2Chats = ChatsHelperFuns.getChats(test_client2, userID2)

    assert len(user1Chats) == len(user2Chats)

    # user1 blocks
    UserHelperFuns.blockUser(test_client, userID1, userID2)

    # test: database to check relation
    UserHelperFuns.checkRelation(userID1, userID2, 'RelationEnum.blocked')
    UserHelperFuns.checkRelation(userID2, userID1, 'RelationEnum.connected')

    chatID = ChatHelperFuns.getChatIDAcceptRequest(socket_client, userID2)

    chatID2 = ChatHelperFuns.getChatIDNewChat(data, userID1)

    assert chatID == chatID2

    RequestHelperFuns.checkNumRequests(requestID, 0)

    ChatsHelperFuns.checkNumChats(chatID, userID1, userID2, 1)

    ChatHelperFuns.checkNumMessages(chatID, 1)

    chat1 = ChatHelperFuns.getChat(test_client, userID1, chatID)
    chat2 = ChatHelperFuns.getChat(test_client2, userID2, chatID2)

    assert chat1 == chat2

    #Sends the message

    ChatHelperFuns.sendMessage(test_client, userID1, chatID, "test message")

    user1Chats = ChatsHelperFuns.getChats(test_client, userID1)
    user2Chats = ChatsHelperFuns.getChats(test_client2, userID2)

    assert len(user1Chats) + 1 == len(user2Chats)

    ChatHelperFuns.checkNumMessages(chatID, 2)

    UserHelperFuns.checkNumSocketMessages(socket_client, 0)
    UserHelperFuns.checkNumSocketMessages(socket_client2, 1)
    UserHelperFuns.endTwoUserSession(test_client, test_client2, socket_client, socket_client2, userID1, userID2)

# Tests sending a message to a connected user where both users have each other banned
def testSendMessageToConnectedUserWhileBothBlocked():
    test_client, test_client2, socket_client, socket_client2, userID1, userID2 = UserHelperFuns.startTwoUserTest()

    # userID1 sends request
    RequestHelperFuns.sendRequest(test_client, userID1, userID2)

    # user2 get socketio msg
    requestID = RequestHelperFuns.getReceivedRequest(socket_client2, userID1, userID2)

    # check no current relations
    UserHelperFuns.checkRelation(userID1, userID2, "", 0)

    data = RequestHelperFuns.acceptRequest(test_client2, userID2, requestID)
    UserHelperFuns.checkRelation(userID1, userID2, "RelationEnum.connected")
    UserHelperFuns.checkRelation(userID2, userID1, "RelationEnum.connected")
    UserHelperFuns.checkIfConnected(test_client, userID1, userID2)
    UserHelperFuns.checkIfConnected(test_client2, userID2, userID1)

    user1Chats = ChatsHelperFuns.getChats(test_client, userID1)
    user2Chats = ChatsHelperFuns.getChats(test_client2, userID2)

    assert len(user1Chats) == len(user2Chats)

    # user1 blocks
    UserHelperFuns.blockUser(test_client, userID1, userID2)

    # user2 blocks
    UserHelperFuns.blockUser(test_client2, userID2, userID1)

    # test: database to check relation
    UserHelperFuns.checkRelation(userID1, userID2, 'RelationEnum.blocked')
    UserHelperFuns.checkRelation(userID2, userID1, 'RelationEnum.blocked')

    chatID = ChatHelperFuns.getChatIDAcceptRequest(socket_client, userID2)

    chatID2 = ChatHelperFuns.getChatIDNewChat(data, userID1)

    assert chatID == chatID2

    RequestHelperFuns.checkNumRequests(requestID, 0)

    ChatsHelperFuns.checkNumChats(chatID, userID1, userID2, 1)

    ChatHelperFuns.checkNumMessages(chatID, 1)

    chat1 = ChatHelperFuns.getChat(test_client, userID1, chatID)
    chat2 = ChatHelperFuns.getChat(test_client2, userID2, chatID2)

    assert chat1 == chat2

    #Sends the message

    ChatHelperFuns.sendMessage(test_client, userID1, chatID, "test message")

    user1Chats = ChatsHelperFuns.getChats(test_client, userID1)
    user2Chats = ChatsHelperFuns.getChats(test_client2, userID2)

    assert len(user1Chats) == len(user2Chats)
    assert len(user1Chats) == 0 and len(user2Chats) == 0

    ChatHelperFuns.checkNumMessages(chatID, 2)

    UserHelperFuns.checkNumSocketMessages(socket_client, 0)
    UserHelperFuns.checkNumSocketMessages(socket_client2, 0)

    ChatHelperFuns.sendMessage(test_client2, userID2, chatID2, "test message2")

    user1Chats = ChatsHelperFuns.getChats(test_client, userID1)
    user2Chats = ChatsHelperFuns.getChats(test_client2, userID2)

    assert len(user1Chats) == len(user2Chats)
    assert len(user1Chats) == 0 and len(user2Chats) == 0

    UserHelperFuns.checkNumSocketMessages(socket_client, 0)
    UserHelperFuns.checkNumSocketMessages(socket_client2, 0)
    UserHelperFuns.endTwoUserSession(test_client, test_client2, socket_client, socket_client2, userID1, userID2)
    
def testSendMessageNotConnected():
    test_client, test_client2, socket_client, socket_client2, userID1, userID2 = UserHelperFuns.startTwoUserTest()
    
    UserHelperFuns.checkRelation(userID1, userID2, "", 0)
    UserHelperFuns.checkRelation(userID2, userID1, "", 0)
    ChatsHelperFuns.checkTotalChats(0)
    ChatHelperFuns.checkTotalMessages(0)

    ChatHelperFuns.sendMessage(test_client, userID1, 1, "test message", success=False)

    ChatsHelperFuns.checkTotalChats(0)
    ChatHelperFuns.checkTotalMessages(0)
    UserHelperFuns.endTwoUserSession(test_client, test_client2, socket_client, socket_client2, userID1, userID2)
    
#send a message to a chatid that doesn't exist
def testSendMessageToNonExistantChatID():
    test_client, test_client2, socket_client, socket_client2, userID1, userID2 = UserHelperFuns.startTwoUserTest()

    # userID1 sends request
    RequestHelperFuns.sendRequest(test_client, userID1, userID2)

    # user2 get socketio msg
    requestID = RequestHelperFuns.getReceivedRequest(socket_client2, userID1, userID2)

    # check no current relations
    UserHelperFuns.checkRelation(userID1, userID2, "", 0)
    UserHelperFuns.checkRelation(userID2, userID1, "", 0)

    assert not ChatHelperFuns.validChatID(10000)

    ChatHelperFuns.sendMessage(test_client2, userID2, 10000, "test message", success=False)

    assert not ChatHelperFuns.validChatID(10000)

    # still no relation
    UserHelperFuns.checkRelation(userID1, userID2, "", 0)
    UserHelperFuns.checkRelation(userID2, userID1, "", 0)

    # both users should have no incoming messages
    UserHelperFuns.checkNumSocketMessages(socket_client, 0)

    UserHelperFuns.checkNumSocketMessages(socket_client2, 0)

    # request still in db
    RequestHelperFuns.checkNumRequests(requestID, 1)

    UserHelperFuns.endTwoUserSession(test_client, test_client2, socket_client, socket_client2, userID1, userID2)

def testSetChatname():
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
    ChatHelperFuns.setChatName(test_client, userID1, chatID, "test")

    assert ChatHelperFuns.getChatName(userID1, chatID) == "test"
    assert initial == ChatHelperFuns.getChatName(userID2, chatID2)
    UserHelperFuns.endTwoUserSession(test_client, test_client2, socket_client, socket_client2, userID1, userID2)

def testVersion():
    assert version.VERSION == (1, 0, 3)

def testErrorCheckingGetChat():
	test_client, test_client2, socket_client, socket_client2, userID1, userID2 = UserHelperFuns.startTwoUserTest()

	response = test_client.get('v1/chat/' + str(userID1) + "/")
	assert response != '200 OK'

	response = test_client.get('v1/chat/' + "NotaLong" + "/" + "NotaLong")
	assert response != '200 OK'

	socket_client.emit('remove user', {'userID':userID1})
	test_client.post('v1/logout')
	socket_client2.emit('remove user', {'userID':userID2})
	test_client2.post('v1/logout')
	ChatHelperFuns.getChat(test_client, userID1, "42", success=False)
	assert db_commands.close_session() == "DB Session Ended"
	assert db_commands.clear_db() == "DB Tables dropped"

def testErrorCheckingSeenChat():
	test_client, test_client2, socket_client, socket_client2, userID1, userID2 = UserHelperFuns.startTwoUserTest()

	response = test_client.post('v1/seenChat/' + str(userID1) + "/")
	assert response.status != '200 OK'

	response = test_client.post('v1/seenChat/' + "NotaLong" + "/" + "NotaLong")
	assert response.status != '200 OK'

	UserHelperFuns.endTwoUserSession(test_client, test_client2, socket_client, socket_client2, userID1, userID2)

def testErrorCheckingSetChatName():
	test_client, test_client2, socket_client, socket_client2, userID1, userID2 = UserHelperFuns.startTwoUserTest()

	response = test_client.post('/v1/chatname', data=dict(test=42))
	assert response != '200 OK'


	response = test_client.post('/v1/chatname', data=json.dumps(dict(userID=userID1, chatID="42")))
	assert response != '200 OK'

	response = test_client.post('/v1/chatname', data=json.dumps(dict(userID=userID1, name="")))
	assert response != '200 OK'

	response = test_client.post('/v1/chatname', data=json.dumps(dict(chatID="42", name="")))
	assert response != '200 OK'


	response = test_client.post('/v1/chatname', data=json.dumps(dict(userID="NotaLong", chatID="NotaLong", name="")))
	assert response != '200 OK'

	ChatHelperFuns.setChatName(test_client, userID1, "42", "", success=False)

	socket_client.emit('remove user', {'userID':userID1})
	test_client.post('v1/logout')
	socket_client2.emit('remove user', {'userID':userID2})
	test_client2.post('v1/logout')
	ChatHelperFuns.setChatName(test_client, userID1, "42", "", success=False)
	assert db_commands.close_session() == "DB Session Ended"
	assert db_commands.clear_db() == "DB Tables dropped"

def testErrorCheckingSendMessage():
	test_client, test_client2, socket_client, socket_client2, userID1, userID2 = UserHelperFuns.startTwoUserTest()

	response = test_client.post('v1/sendMessage', data=dict(test=42))
	assert response.status != '200 OK'


	response = test_client.post('v1/sendMessage', data=json.dumps(dict(userID=userID1, chatID="42")))
	assert response.status != '200 OK'

	response = test_client.post('v1/sendMessage', data=json.dumps(dict(userID=userID1, msg="")))
	assert response.status != '200 OK'

	response = test_client.post('v1/sendMessage', data=json.dumps(dict(chatID="42", msg="")))
	assert response.status != '200 OK'

	ChatHelperFuns.sendMessage(test_client, "NotaLong", "42", "", success=False)

	ChatHelperFuns.sendMessage(test_client, userID1, "NotaLong", "", success=False)

	ChatHelperFuns.sendMessage(test_client, userID1, "42", "", success=False)

	newchat = Chats.Chats([1, 2])
	db.session.add(newchat)
	db.session.commit()

	ChatHelperFuns.sendMessage(test_client, userID1, newchat.chatID, "", success=False)

	socket_client.emit('remove user', {'userID':userID1})
	test_client.post('v1/logout')
	socket_client2.emit('remove user', {'userID':userID2})
	test_client2.post('v1/logout')
	ChatHelperFuns.sendMessage(test_client, userID1, "42", "", success=False)
	assert db_commands.close_session() == "DB Session Ended"
	assert db_commands.clear_db() == "DB Tables dropped"

def testErrorCheckingGetChats():
	test_client, test_client2, socket_client, socket_client2, userID1, userID2 = UserHelperFuns.startTwoUserTest()

	ChatsHelperFuns.getChats(test_client, "", success=False)

	ChatsHelperFuns.getChats(test_client, "NotaLong", success=False)

	socket_client.emit('remove user', {'userID':userID1})
	test_client.post('v1/logout')
	socket_client2.emit('remove user', {'userID':userID2})
	test_client2.post('v1/logout')
	ChatsHelperFuns.getChats(test_client, userID1, success=False)
	assert db_commands.close_session() == "DB Session Ended"
	assert db_commands.clear_db() == "DB Tables dropped"

def testErrorCheckingIsActive():
	assert db_commands.close_session() == "DB Session Ended"
	assert db_commands.clear_db() == "DB Tables dropped"

	assert db_commands.create_db() == "DB Created Successfully"

	test_client = app.test_client()

	socket_client = socketio.test_client(app)
	socket_client.get_received()

	userID = UserHelperFuns.createUser1(test_client, socket_client)

	response = test_client.get('v1/isactive/' + str(userID) + "/" + "NotaLong")
	assert response != '200 OK'

	response = test_client.get('v1/isactive/' + "NotaLong" + "/" + "42")
	assert response != '200 OK'

	socket_client.emit('remove user', {'userID':userID})
	test_client.post('v1/logout')
	response = test_client.get('v1/isactive/' + str(userID) + "/" + "42")
	assert response != '200 OK'
	assert db_commands.close_session() == "DB Session Ended"
	assert db_commands.clear_db() == "DB Tables dropped"

def testIsActive():
    clientList, socketList, userList = GraphHelperFuns.startMultiUserTest()

    #create 2 users
    numUsers = 2
    for i in range(0, numUsers):
        clientList, socketList, userList = GraphHelperFuns.createUser(clientList, socketList, userList)

    GraphHelperFuns.checkNotNearBulk(clientList, userList)
    
    GraphHelperFuns.postNearbyTwoWay(clientList[0], clientList[1], userList[0], userList[1])

    GraphHelperFuns.checkNearBy(clientList[0], userList[0], userList[1])
    GraphHelperFuns.checkNearBy(clientList[1], userList[1], userList[0])    

    UserHelperFuns.checkRelation(userList[0], userList[1], "", 0)

    RequestHelperFuns.sendRequest(clientList[0], userList[0], userList[1])

    requestID = RequestHelperFuns.getReceivedRequest(socketList[1], userList[0], userList[1])

    data = RequestHelperFuns.acceptRequest(clientList[1], userList[1], requestID)

    UserHelperFuns.checkRelation(userList[0], userList[1], "RelationEnum.connected")
    UserHelperFuns.checkIfConnected(clientList[0], userList[0], userList[1])
    UserHelperFuns.checkIfConnected(clientList[1], userList[1], userList[0])

    chatID = ChatHelperFuns.getChatIDNewChat(data, userList[0])

    active = ChatHelperFuns.isActive(clientList[0], userList[0], chatID)

    assert active['active'] == True
    assert 'time' in active

    GraphHelperFuns.bulkLogout(clientList)
    GraphHelperFuns.bulkLogin(userList, clientList)

    NearbyUsers.NearbyUsers.query.filter_by(userID=userList[0]).delete()
    NearbyUsers.NearbyUsers.query.filter_by(userID=userList[1]).delete()
    db.session.commit()

    GraphHelperFuns.checkNotNearBulk(clientList, userList)

    active = ChatHelperFuns.isActive(clientList[0], userList[0], chatID)

    assert active['active'] == False
    assert 'time' not in active

    UnseenMsgs.UnseenMsgs.query.filter_by(chatID=chatID).delete()
    Messages.Messages.query.filter_by(chatID=chatID).delete()
    ChatNames.ChatNames.query.filter_by(chatID=chatID).delete()
    Chats.Chats.query.filter_by(chatID=chatID).delete()
    db.session.commit()
    
    active = ChatHelperFuns.isActive(clientList[0], userList[0], chatID)
    assert active['active'] == False
    assert 'time' not in active

    GraphHelperFuns.endMultiUserTest(clientList, socketList, userList)

def testLongDistanceMessaging():
    clientList, socketList, userList = GraphHelperFuns.startMultiUserTest()

    #create 2 users
    numUsers = 2
    for i in range(0, numUsers):
        clientList, socketList, userList = GraphHelperFuns.createUser(clientList, socketList, userList)

    GraphHelperFuns.checkNotNearBulk(clientList, userList)
    
    GraphHelperFuns.postNearbyTwoWay(clientList[0], clientList[1], userList[0], userList[1])

    GraphHelperFuns.checkNearBy(clientList[0], userList[0], userList[1])
    GraphHelperFuns.checkNearBy(clientList[1], userList[1], userList[0])    

    UserHelperFuns.checkRelation(userList[0], userList[1], "", 0)

    RequestHelperFuns.sendRequest(clientList[0], userList[0], userList[1])

    requestID = RequestHelperFuns.getReceivedRequest(socketList[1], userList[0], userList[1])

    data = RequestHelperFuns.acceptRequest(clientList[1], userList[1], requestID)

    UserHelperFuns.checkRelation(userList[0], userList[1], "RelationEnum.connected")
    UserHelperFuns.checkIfConnected(clientList[0], userList[0], userList[1])
    UserHelperFuns.checkIfConnected(clientList[1], userList[1], userList[0])

    chatID = ChatHelperFuns.getChatIDNewChat(data, userList[0])

    ChatHelperFuns.sendMessage(clientList[0], userList[0], chatID, "test message")

    ChatHelperFuns.checkNumMessages(chatID, 2)
    
    GraphHelperFuns.bulkLogout(clientList)
    GraphHelperFuns.bulkLogin(userList, clientList)

    NearbyUsers.NearbyUsers.query.filter_by(userID=userList[0]).delete()
    NearbyUsers.NearbyUsers.query.filter_by(userID=userList[1]).delete()
    db.session.commit()

    GraphHelperFuns.checkNotNearBulk(clientList, userList)

    ChatHelperFuns.sendMessage(clientList[0], userList[0], chatID, "test message 2", False)

    ChatHelperFuns.checkNumMessages(chatID, 2)

    UserHelperFuns.checkNotLongDistTwoWay(clientList[0], clientList[1], userList[0], userList[1])

    UserHelperFuns.postLongDistance(clientList[0], userList[0], userList[1])

    UserHelperFuns.checkIfLongDistance(clientList[0], userList[0], userList[1])
    UserHelperFuns.checkIfNotLongDistance(clientList[1], userList[1], userList[0])

    ChatHelperFuns.sendMessage(clientList[0], userList[0], chatID, "test message 3", False)

    ChatHelperFuns.checkNumMessages(chatID, 2)
    
    UserHelperFuns.postLongDistance(clientList[1], userList[1], userList[0])

    UserHelperFuns.checkLongDistTwoWay(clientList[0], clientList[1], userList[0], userList[1])

    ChatHelperFuns.sendMessage(clientList[0], userList[0], chatID, "test message 4")

    ChatHelperFuns.checkNumMessages(chatID, 3)

    ChatHelperFuns.sendMessage(clientList[1], userList[1], chatID, "test message 5")

    ChatHelperFuns.checkNumMessages(chatID, 4)

    UserHelperFuns.postNotLongDistance(clientList[0], userList[0], userList[1])
    
    UserHelperFuns.checkIfNotLongDistance(clientList[0], userList[0], userList[1])
    UserHelperFuns.checkIfLongDistance(clientList[1], userList[1], userList[0])

    ChatHelperFuns.sendMessage(clientList[0], userList[0], chatID, "test message 6", False)

    ChatHelperFuns.checkNumMessages(chatID, 4)

    ChatHelperFuns.sendMessage(clientList[1], userList[1], chatID, "test message 7", False)

    ChatHelperFuns.checkNumMessages(chatID, 4)

    UserHelperFuns.postNotLongDistance(clientList[1], userList[1], userList[0])

    UserHelperFuns.checkNotLongDistTwoWay(clientList[0], clientList[1], userList[0], userList[1])

    ChatHelperFuns.sendMessage(clientList[0], userList[0], chatID, "test message 8", False)

    ChatHelperFuns.checkNumMessages(chatID, 4)

    GraphHelperFuns.postNearby(clientList[0], userList[0], userList[1])

    ChatHelperFuns.sendMessage(clientList[0], userList[0], chatID, "test message 9", False)

    ChatHelperFuns.checkNumMessages(chatID, 4)

    GraphHelperFuns.postNearby(clientList[1], userList[1], userList[0])

    ChatHelperFuns.sendMessage(clientList[0], userList[0], chatID, "test message 10")

    ChatHelperFuns.checkNumMessages(chatID, 5)

    ChatHelperFuns.sendMessage(clientList[1], userList[1], chatID, "test message 11")

    ChatHelperFuns.checkNumMessages(chatID, 6)

    GraphHelperFuns.endMultiUserTest(clientList, socketList, userList)
