from app import db
from app.models import BaseModel

class FeatureVectors(BaseModel.BaseModel, db.Model):
    """Model for the FeatureVectors table"""
    __tablename__ = 'featurevectors'

    id = db.Column(db.BigInteger, primary_key=True)
    sid = db.Column(db.BigInteger, db.ForeignKey('sessions.sid'))
    otherUserID = db.Column(db.BigInteger, db.ForeignKey('users.userID'))
    featureVector = db.Column(db.JSON)

    def __init__(self,sid,otherUserID,featureVector):
        self.sid = sid
        self.otherUserID = otherUserID
        self.featureVector = featureVector

    def _to_dict(self):
        objDict = {}
        objDict["sid"] = str(self.sid)
        objDict["otherUserID"] = str(self.otherUserID)
        objDict["userID"] = str(self.userID)
        objDict["featurevector"] = self.featureVector

        return objDict