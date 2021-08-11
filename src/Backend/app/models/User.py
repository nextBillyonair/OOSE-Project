from app import db
from app.models import BaseModel

class User(BaseModel.BaseModel, db.Model):
    """Model for the User table"""
    __tablename__ = 'users'

    userID = db.Column(db.BigInteger, primary_key = True)
    accessToken = db.Column(db.String)

    def __init__(self, userID, accessToken):
        self.userID = userID
        self.accessToken = accessToken

    def _to_dict(self):
        objDict = {}
        objDict["userID"] = str(self.userID)
        objDict["accessToken"] = self.accessToken
        return objDict