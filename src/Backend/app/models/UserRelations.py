from app import db
import enum
from app.models import BaseModel
from sqlalchemy import UniqueConstraint

class RelationEnum(enum.Enum):
    blocked = 1
    connected = 2
    longdistance = 3    

class UserRelations(BaseModel.BaseModel, db.Model):
    """Model for the User Relations table"""
    __tablename__ = 'userrelations'

    fromUserID = db.Column(db.BigInteger, db.ForeignKey('users.userID'), primary_key = True)
    toUserID = db.Column(db.BigInteger, db.ForeignKey('users.userID'), primary_key=True)
    relation = db.Column(db.Enum(RelationEnum))

    UniqueConstraint(fromUserID, toUserID)

    def __init__(self, fromUserID, toUserID, relation):
        self.fromUserID = fromUserID
        self.toUserID = toUserID
        self.relation= relation

    def _to_dict(self):
        objDict = {}
        objDict["fromUserID"] = str(self.fromUserID)
        objDict["toUserID"] = str(self.toUserID)
        objDict["relation"] = str(self.relation)
        return objDict

    def _to_user_dict(self):
        objDict = {}
        objDict["userID"] = str(self.toUserID)
        return objDict