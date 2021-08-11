from app import db
from app.models import BaseModel

class ChatNames(BaseModel.BaseModel, db.Model):
    """Model for the Chat Names table"""
    __tablename__ = 'chatnames'

    chatID = db.Column(db.BigInteger, db.ForeignKey('chats.chatID'), primary_key = True)
    userID = db.Column(db.BigInteger, db.ForeignKey('users.userID'), primary_key = True)
    chatName = db.Column(db.String)

    def __init__(self, chatID, userID, chatName):
        self.chatID = chatID
        self.userID = userID
        self.chatName= chatName

    def _to_dict(self):
        objDict = {}
        objDict["chatID"] = str(self.chatID)
        objDict["userID"] = str(self.userID)
        objDict["chatName"] = self.chatName
        return objDict