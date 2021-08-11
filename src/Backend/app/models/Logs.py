from app import db
import enum
from app.models import BaseModel

class ActionEnum(enum.Enum):
    clicked = 1
    sendrequest = 2

class Logs(BaseModel.BaseModel, db.Model):
    """Model for the Logs table"""
    __tablename__ = 'logs'

    id = db.Column(db.BigInteger, primary_key=True)
    sid = db.Column(db.BigInteger, db.ForeignKey('sessions.sid'))
    otherUserID = db.Column(db.BigInteger, db.ForeignKey('users.userID'))
    action = db.Column(db.Enum(ActionEnum))
    position = db.Column(db.BigInteger)
    timeStamp = db.Column(db.DateTime)

    def __init__(self, sid,otherUserID,action,position,timeStamp):
        self.sid = sid
        self.otherUserID = otherUserID
        self.action = action
        self.position = position
        self.timeStamp = timeStamp

    def _to_dict(self):
        objDict = {}
        objDict["sid"] = str(self.sid)
        objDict["otherUserID"] = str(self.otherUserID)
        objDict["userID"] = str(self.userID)
        objDict["msg"] = self.msg
        objDict["timeStamp"] = self.timeStamp.isoformat()
        return objDict
