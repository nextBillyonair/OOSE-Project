import sys
import os
sys.path.append(os.path.abspath("../src/Backend"))
import db_commands
from app.models import ChatNames, Chats
import json
from app import db

# check db for all chats with chatID, ensures chatID is correct, users in chat correct, as well as proper number of chat names
def checkNumChats(chatID, userID1, userID2, target):
    count = 0
    for chat in db.session.query(Chats.Chats).filter(Chats.Chats.chatID == chatID):
        c = chat._to_dict()
        assert c["chatID"] == str(chatID)
        assert set(c["users"]) == set([str(userID1), str(userID2)])
        count += 1
    assert count == target
    count = 0
    for chatname in db.session.query(ChatNames.ChatNames).filter(ChatNames.ChatNames.chatID == chatID):
        count += 1
    assert count == target * 2

def checkTotalChats(target):
    count = 0
    for entry in db.session.query(Chats.Chats):
        count += 1
    assert count == target

# gets all of the chats for a given user
def getChats(test_client, userID, success=True):
    chats = test_client.get("v1/chats/" + str(userID))
    if success:
        data = json.loads(chats.get_data(as_text=True))
        return data
    else:
        assert chats.response != '200 OK'
        