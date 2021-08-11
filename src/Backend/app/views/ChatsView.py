from app import app, db, session
from app.models import ChatNames, Chats, Messages, UnseenMsgs, UserRelations
from flask import jsonify
from sqlalchemy import desc, and_, outerjoin
from sqlalchemy.orm import aliased
from app.views.helperFunctions import AuthenticateHelper

@app.route('/v1/chats/<userID>', methods=['GET'])
def getChats(userID):

    try:
        userID = long(userID)
    except ValueError:
        return jsonify({'error':'userID must be of type long'}), 400

    if not AuthenticateHelper.authenticate(userID):
        return jsonify({"error":"Not logged in"}), 401

    m1 = aliased(Messages.Messages)
    m2 = aliased(Messages.Messages)

    query = db.session.query(m1.msgID)
    query = query.outerjoin(m2, and_(m2.chatID == m1.chatID, m1.timeStamp < m2.timeStamp))
    query = query.filter(m2.msgID.is_(None))

    query2 = db.session.query(Messages.Messages.msg, UnseenMsgs.UnseenMsgs.unseen, Chats.Chats.chatID, ChatNames.ChatNames.chatName, Chats.Chats.users)
    query2 = query2.outerjoin(UnseenMsgs.UnseenMsgs, and_(
        UnseenMsgs.UnseenMsgs.chatID == Messages.Messages.chatID, \
        UnseenMsgs.UnseenMsgs.userID == userID, \
        UnseenMsgs.UnseenMsgs.msgID == Messages.Messages.msgID))
    query2 = query2.filter(and_(Messages.Messages.msgID.in_(query), \
                                Chats.Chats.chatID==ChatNames.ChatNames.chatID, \
                                Chats.Chats.users.any(userID), \
                                ChatNames.ChatNames.userID == userID, \
                                Messages.Messages.chatID == Chats.Chats.chatID, \
                                UserRelations.UserRelations.fromUserID == userID, \
                                Chats.Chats.users.any(UserRelations.UserRelations.toUserID), \
                                UserRelations.UserRelations.relation != UserRelations.RelationEnum.blocked))

    query2 = query2.order_by(desc(Messages.Messages.timeStamp))
    chats = query2.all()

    return jsonify([c._asdict() for c in chats])
