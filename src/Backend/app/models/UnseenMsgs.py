from app import db
from app.models import BaseModel

class UnseenMsgs(BaseModel.BaseModel, db.Model):
    """Model for the UnseenMsgs table"""
    __tablename__ = 'unseenmsgs'

    chatID = db.Column(db.BigInteger, db.ForeignKey('chats.chatID'), primary_key = True)
    userID = db.Column(db.BigInteger, db.ForeignKey('users.userID'), primary_key = True)
    msgID = db.Column(db.BigInteger, db.ForeignKey('messages.msgID'), primary_key = True)
    unseen = db.Column(db.Boolean)

    def __init__(self, chatID, userID, msgID):
        self.chatID = chatID
        self.userID = userID
        self.msgID = msgID
        self.unseen = True

    def _to_dict(self):
        objDict = {}
        objDict["userID"] = str(self.userID)
        objDict["chatID"] = str(self.chatID)
        objDict["msgID"] = str(self.msgID)
        objDict["unseen"] = str(self.unseen)
        return objDict