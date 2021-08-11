from sqlalchemy import UniqueConstraint
from app import db
from app.models import BaseModel

class Requests(BaseModel.BaseModel, db.Model):
    """Model for the stations table"""
    __tablename__ = 'requests'

    requestID = db.Column(db.BigInteger, primary_key = True)
    fromUserID = db.Column(db.BigInteger, db.ForeignKey('users.userID'))
    toUserID = db.Column(db.BigInteger, db.ForeignKey('users.userID'))
    msg = db.Column(db.String)
    timeStamp = db.Column(db.DateTime)
    completed = db.Column(db.Boolean)

    UniqueConstraint(fromUserID, toUserID)

    def __init__(self, fromUserID, toUserID, msg, timeStamp, completed=False):

        self.fromUserID = fromUserID
        self.toUserID = toUserID
        self.msg = msg
        self.timeStamp = timeStamp
        self.completed = completed

    def _to_dict(self):
        objDict = {}
        objDict["requestID"] = str(self.requestID)
        objDict["fromUserID"] = str(self.fromUserID)
        objDict["toUserID"] = str(self.toUserID)
        objDict["msg"] = self.msg
        objDict["timeStamp"] = self.timeStamp.isoformat()
        objDict["completed"] = self.completed
        return objDict

    def serialize(self):
        return {}