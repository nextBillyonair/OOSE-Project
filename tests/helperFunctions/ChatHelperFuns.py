import sys
import os
sys.path.append(os.path.abspath("../src/Backend"))
import db_commands
from app.models import ChatNames, Chats, Messages, UnseenMsgs
import json
from app import db

# get chatname for the chat with chatID and userID
def getChatName(userID, chatID):
    query = ChatNames.ChatNames.query.filter_by(chatID=chatID).filter_by(userID=userID).all()
    count = 0
    for chatName in query:
        count += 1
    assert count == 1
    data = list(query)
    return data[0].chatName

# set chatname of chat with chatID and userID
def setChatName(test_client, userID, chatID, name, success=True):
    response = test_client.post('/v1/chatname', data=json.dumps(dict(userID=userID, chatID=chatID, name=name)))
    if success:
        assert response.status == '200 OK'
        data = json.loads(response.get_data(as_text=True))
        assert data['response'] == 'success'
    else:
        assert response.status != '200 OK'

# checks for target amount of db messages for chat with chatID
def checkNumMessages(chatID, target):
    count = 0
    for message in db.session.query(Messages.Messages).filter(Messages.Messages.chatID == chatID):
        count += 1
    assert count == target

def checkTotalMessages(target):
    count = 0
    for entry in db.session.query(Messages.Messages):
        count += 1
    assert count == target

# sends a message from user1 to user2
def sendMessage(test_client, userID, chatID, msg, success=True):
    response = test_client.post('v1/sendMessage', data=json.dumps(dict(userID=userID, chatID=chatID, msg=msg)))
    if success:
        assert response.status == '200 OK'
        data = json.loads(response.get_data(as_text=True))
        assert data.get('msgID') is not None
        assert data.get('msg') == msg
        assert data.get('chatID') == chatID
        assert data.get('timeStamp') is not None
        assert data.get('userID') == str(userID)
    else:
        assert response.status != '200 OK'

# gets the most recent chat message given a chatID
def getChat(test_client, userID, chatID, success=True):
    response = test_client.get('v1/chat/' + str(userID) + "/" + str(chatID))
    if success:
        assert response.status == '200 OK'
    else:
        assert response.status != '200 OK'

    data = json.loads(response.get_data(as_text=True))
    return data

# check socket_client for a new chat message from userID
def getChatIDNewChat(data, userID, msg=""):
    return getChatID(data, userID, msg)

def getChatIDAcceptRequest(socket_client, userID, msg = ""):
    recvd = socket_client.get_received()
    assert len(recvd) == 1
    assert recvd[0]['name'] == 'accept request'

    args = recvd[0]['args']
    assert len(args) == 1

    arg = args[0]

    return getChatID(arg, userID, msg)

def getChatID(arg, userID, msg):
    assert arg.get('chat') != None
    assert arg.get('chatName') != None
    assert arg.get('msg') == msg
    chat = arg.get('chat')

    assert chat.get('chatID') != None
    assert chat.get('users') != None
    assert str(userID) in chat.get('users')
    return chat.get('chatID')

def validChatID(chatID):
    msgs = list(Messages.Messages.query.filter_by(chatID=chatID))
    chats = list(Chats.Chats.query.filter_by(chatID=chatID))
    chatNames = list(ChatNames.ChatNames.query.filter_by(chatID=chatID))
    unseenMsgs = list(UnseenMsgs.UnseenMsgs.query.filter_by(chatID=chatID))
    if len(msgs) > 0 or len(chats) > 0 or len(chatNames) > 0 or len(unseenMsgs) > 0:
        return True
    else:
        return False

def checkUnseenMsgs(test_client, userID, unseen, target=1):
    chats = test_client.get('v1/chats/' + str(userID))
    data = json.loads(chats.get_data(as_text=True))
    count = 0
    for chat in data:
        if unseen:
        	assert chat['unseen'] == True
        else:
        	assert chat.get('unseen') is None
        count += 1
    assert count == 1

def isActive(test_client, userID, chatID):
    active = test_client.get('/v1/isactive/' + str(userID) + '/' + str(chatID))
    data = json.loads(active.get_data(as_text=True))
    return data
