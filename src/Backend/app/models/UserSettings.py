from app import db
from app.models import BaseModel

class UserSettings(BaseModel.BaseModel, db.Model):
    """Model for the stations table"""
    __tablename__ = 'usersettings'

    userID = db.Column(db.BigInteger, db.ForeignKey('users.userID'), primary_key = True)
    radius = db.Column(db.Integer)
    hours = db.Column(db.Integer)
    tags = db.Column(db.ARRAY(db.String))

    def __init__(self, userID, radius, hours, tags):

        self.userID = userID
        self.radius = radius
        self.hours = hours
        self.tags = tags

    def _to_dict(self):
        objDict = {}
        objDict["userID"] = str(self.userID)
        objDict["radius"] = self.radius
        objDict["hours"] = self.hours
        objDict["tags"] = self.tags

        return objDict
