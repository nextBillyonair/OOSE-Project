from app import db
from app.models import BaseModel

class Sessions(BaseModel.BaseModel, db.Model):
    """Model for the Sessions table"""
    __tablename__ = 'sessions'

    sid = db.Column(db.BigInteger, primary_key=True)
    userID = db.Column(db.BigInteger, db.ForeignKey('users.userID'))
    usersInSession = db.Column(db.BigInteger)

    def __init__(self,userID):
        self.userID = userID
        self.usersInSession = 0

    def _to_dict(self):
        objDict = {}
        objDict["sid"] = str(self.sid)
        objDict["userID"] = str(self.userID)
        objDict["usersInSession"] = str(self.usersInSession)
        return objDict
