from app import db
from app.models import BaseModel

class Messages(BaseModel.BaseModel, db.Model):
    """Model for the Messages table"""
    __tablename__ = 'messages'

    msgID = db.Column(db.BigInteger, primary_key = True)
    chatID = db.Column(db.BigInteger, db.ForeignKey('chats.chatID'))
    userID = db.Column(db.BigInteger, db.ForeignKey('users.userID'))
    msg = db.Column(db.String)
    timeStamp = db.Column(db.DateTime)

    def __init__(self,chatID,userID,msg,timeStamp):
        self.chatID = chatID
        self.userID = userID
        self.msg = msg
        self.timeStamp = timeStamp

    def _to_dict(self):
        objDict = {}
        objDict["msgID"] = str(self.msgID)
        objDict["chatID"] = str(self.chatID)
        objDict["userID"] = str(self.userID)
        objDict["msg"] = self.msg
        objDict["timeStamp"] = self.timeStamp.isoformat()
        return objDict