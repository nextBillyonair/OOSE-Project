from sqlalchemy import UniqueConstraint
from app import db
from app.models import BaseModel

class NearbyUsers(BaseModel.BaseModel, db.Model):
    """Model for the stations table"""
    __tablename__ = 'nearbyusers'

    userID = db.Column(db.BigInteger, db.ForeignKey('users.userID'), primary_key = True)
    otherUserID = db.Column(db.BigInteger, db.ForeignKey('users.userID'), primary_key = True)
    timeStamp = db.Column(db.DateTime)

    UniqueConstraint(userID, otherUserID)

    def __init__(self, userID, otherUserID, timeStamp):

        self.userID = userID
        self.otherUserID = otherUserID
        self.timeStamp = timeStamp

    def _to_dict(self):
        objDict = {}
        objDict["userID"] = str(self.userID)
        objDict["otherUserID"] = str(self.otherUserID)
        objDict["timeStamp"] = self.timeStamp.isoformat()
        return objDict
