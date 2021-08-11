from app import app, db, socketio, session
from app.models import Chats, ChatNames, Messages, UnseenMsgs, UserRelations
from flask_socketio import emit
from flask import request, jsonify
import datetime
import json
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError
from app.views.helperFunctions import AuthenticateHelper, GraphHelper

@app.route('/v1/chat/<userID>/<chatID>', methods=['GET'])
def getChat(userID, chatID):
    try:
        userID = long(userID)
        chatID = long(chatID)
    except ValueError:
        return jsonify({'error':'userID and chatID must be of type long'}), 400

    if not AuthenticateHelper.authenticate(userID):
        return jsonify({"error":"Not logged in"}), 401

    chats = Chats.Chats.query.filter_by(chatID=chatID).filter(Chats.Chats.users.any(userID)).all()
    chats = list(chats)
    if len(chats) == 1:
        messages = Messages.Messages.query.filter_by(chatID=chatID).order_by(desc(Messages.Messages.timeStamp)).all()
        messages = list(messages)
        return jsonify([m._to_dict() for m in messages])

    return jsonify({'error':'User not part of the chat'}), 400

@app.route('/v1/isactive/<userID>/<chatID>', methods=['GET'])
def isActive(userID, chatID):
    try:
        userID = long(userID)
        chatID = long(chatID)
    except ValueError:
        return jsonify({'error':'userID and chatID must be of type long'}), 400

    if not AuthenticateHelper.authenticate(userID):
        return jsonify({"error":"Not logged in"}), 401

    nearby, time = GraphHelper.isNearbyInChat(userID, chatID)

    response = {"active":nearby}
    if nearby and time is not None:
        response["time"] = time

    return jsonify(response)

@app.route('/v1/seenChat/<userID>/<chatID>', methods=['POST'])
def seenChat(userID, chatID):
    try:
        userID = long(userID)
        chatID = long(chatID)
    except ValueError:
        return jsonify({'error':'userID and chatID must be of type long'}), 400

    UnseenMsgs.UnseenMsgs.query.filter_by(chatID=chatID).filter_by(userID=userID).delete()
    
    try:
        db.session.commit()
    except IntegrityError:
        # already deleted
        pass

    return jsonify({"response":"success"})

@app.route('/v1/chatname', methods=['POST'])
def setChatName():

    try:
        data = json.loads(request.data)
    except ValueError:
        return jsonify({'error':'Body of request must be of json-able string'}), 400

    userID = data.get('userID')
    chatID = data.get('chatID')
    name = data.get('name')

    if None in (userID, chatID, name):
        return jsonify({'error':'Data must contain userID, chatID, and name fields'}), 400

    try:
        userID = long(userID)
        chatID = long(chatID)
        name = unicode(name)
    except ValueError:
        return jsonify({'error':'userID and chatID must be of type long and name must be in unicode'}), 400

    if not AuthenticateHelper.authenticate(userID):
        return jsonify({"error":"Not logged in"}), 401

    names = ChatNames.ChatNames.query.filter_by(chatID=chatID).filter_by(userID=userID).all()
    names = list(names)

    try:
        chatName = names[0]
        chatName.chatName = name
        db.session.commit()
    except (IndexError, IntegrityError):
        return jsonify({'error':'There is no chatname to change'}), 404

    return jsonify({"response":"success"})

@app.route('/v1/sendMessage', methods=['POST'])
def handle_send_message():

    try:
        data = json.loads(request.data)
    except ValueError:
        return jsonify({'error':'Body of request must be of json-able string'}), 400

    userID = data.get('userID')
    chatID = data.get('chatID')
    msg = data.get('msg')
    if None in (userID, chatID, msg):
        return jsonify({'error':'Data must contain userID, chatID, and msg fields'}), 400

    try:
        userID = long(userID)
        chatID = long(chatID)
        msg = unicode(msg)
    except ValueError:
        return jsonify({'error':'userID and chatID must be of type long and msg must be unicode'}), 400

    if not AuthenticateHelper.authenticate(userID):
        return jsonify({"error":"Not logged in"}), 401

    chats = Chats.Chats.query.filter_by(chatID=chatID).filter(Chats.Chats.users.any(userID)).all()
    chats = list(chats)

    if len(chats) == 0:
        return jsonify({'error':'Invalid chatID'}), 400

    chat = chats[0]
    nearby, _ = GraphHelper.isNearbyInChat(userID, chatID)

    if not nearby:
        return jsonify({'error':'Chat is not active'}), 405

    message = Messages.Messages(chatID, userID, msg, datetime.datetime.utcnow())
    db.session.add(message)

    try:
        db.session.commit()
    except IntegrityError:
        return jsonify({'error':'Chat may not exist anymore'}), 404

    for user in chat.users:
        if user == long(userID):
            continue

        db.session.add(UnseenMsgs.UnseenMsgs(chatID, user, message.msgID))
        
        relations = UserRelations.UserRelations.query.filter_by(fromUserID=user).filter_by(toUserID=userID).all()

        if len(relations) == 0:
            # not directly connected
            socketio.emit('send message', message._to_dict(), room=str(user))
        else:
            # one relation
            relation = relations[0]
            if relation.relation == UserRelations.RelationEnum.connected:
                socketio.emit('send message', message._to_dict(), room=str(user))

    try:
        db.session.commit()
    except IntegrityError:
        # chat was deleted
        return jsonify({'error':'Chat may not exist anymore'}), 404

    return jsonify(message._to_dict())
