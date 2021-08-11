from app import db
from app.models import BaseModel

class Chats(BaseModel.BaseModel, db.Model):
    """Model for the Chats table"""
    __tablename__ = 'chats'

    chatID = db.Column(db.BigInteger, primary_key = True)
    users = db.Column(db.ARRAY(db.BigInteger))

    def __init__(self, users):
        self.users = users

    def _to_dict(self):
        objDict = {}
        objDict["chatID"] = str(self.chatID)
        objDict["users"] = [str(u) for u in self.users]
        return objDict