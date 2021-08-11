from app import app, db, session
from app.models import ChatNames, Chats, Logs, Requests, Sessions, UserRelations
from flask import request, jsonify
import json
import datetime
from sqlalchemy import select, and_
from sqlalchemy.exc import IntegrityError
from app.views.helperFunctions import AuthenticateHelper, RequestHelper

@app.route('/v1/filtered/<userID>', methods=['GET'])
def getFiltered(userID):
    try:
        userID = long(userID)
    except ValueError:
        return jsonify({'error':'userID must be of type long'}), 400

    if not AuthenticateHelper.authenticate(userID):
        return jsonify({"error":"Not logged in"}), 401

    query = select([UserRelations.UserRelations.toUserID.label("id")])
    query = query.where(and_(UserRelations.UserRelations.fromUserID == userID, UserRelations.UserRelations.relation == UserRelations.RelationEnum.blocked))
    userIDs = db.session.execute(query)
    result = [dict(u) for u in userIDs]

    query = select([Requests.Requests.toUserID.label("id")])
    query = query.where(Requests.Requests.fromUserID == userID)
    userIDs = db.session.execute(query)
    result = result + [dict(u) for u in userIDs]

    query = select([Requests.Requests.fromUserID.label("id")])
    query = query.where(Requests.Requests.toUserID == userID)
    userIDs = db.session.execute(query)
    result = result + [dict(u) for u in userIDs]

    return jsonify(result)

@app.route('/v1/unblock/<userID2>', methods=['POST'])
def unblockUser(userID2):
    try:
        data = json.loads(request.data)
    except ValueError:
        return jsonify({'error':'Body of request must be of json-able string'}), 400

    userID = data.get('userID')

    if userID is None:
        return jsonify({'error':'Body of request must contain userID fields'}), 400

    try:
        userID = long(userID)
        userID2 = long(userID2)
    except ValueError:
        return jsonify({'error':'userID and userID2 must be of type long'}), 400

    if not AuthenticateHelper.authenticate(userID):
        return jsonify({"error":"Not logged in"}), 401

    if not AuthenticateHelper.isUser(userID2):
        return jsonify({"error":"User does not exist"}), 404

    relation = UserRelations.UserRelations.query.filter_by(fromUserID=userID).filter_by(toUserID=userID2).filter_by(relation=UserRelations.RelationEnum.blocked).all()
    relation = list(relation)

    if len(relation) == 0:
        return jsonify({'error':'User is not blocked'}), 404
        
    # if existing chat, connected
    existingRelation = relation[0]

    chat = Chats.Chats.query.filter(Chats.Chats.users.any(userID)).filter(Chats.Chats.users.any(userID2)).all()
    chat = list(chat)

    if len(chat) == 0:
        # delete the row
        db.session.delete(existingRelation)
    else:
        # they've had a chat
        existingRelation = relation[0]
        existingRelation.relation = UserRelations.RelationEnum.connected

    try:
        db.session.commit()
    except IntegrityError:
        # no problem here, deleted before this function deleted it
        pass

    return jsonify({"response":"success"})

@app.route('/v1/block/<userID2>', methods=['POST'])
def blockUser(userID2):
    try:
        data = json.loads(request.data)
    except ValueError:
        return jsonify({'error':'Body of request must be of json-able string'}), 400

    userID = data.get('userID')

    if userID is None:
        return jsonify({'error':'Body of request must contain userID fields'}), 400

    try:
        userID = long(userID)
        userID2 = long(userID2)
    except ValueError:
        return jsonify({'error':'userID and userID2 must be of type long'}), 400

    if not AuthenticateHelper.authenticate(userID):
        return jsonify({"error":"Not logged in"}), 401

    if not AuthenticateHelper.isUser(userID2):
        return jsonify({"error":"User does not exist"}), 404

    modifyRelation(userID, userID2, UserRelations.RelationEnum.blocked)

    requests = Requests.Requests.query.filter_by(fromUserID=userID2).filter_by(toUserID=userID).all()
    if len(requests) == 1:
        return RequestHelper.decline(userID, requests[0].requestID)

    return jsonify({"response":"success"})

def modifyRelation(userID, userID2, userRelation):
    relation = UserRelations.UserRelations.query.filter_by(fromUserID=userID).filter_by(toUserID=userID2).all()
    relation = list(relation)
    if len(relation) == 0:
        newRelation = UserRelations.UserRelations(userID, userID2, userRelation)
        db.session.add(newRelation)
    else:
        existingRelation = relation[0]
        existingRelation.relation = userRelation

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        # new row added with relation, try again
        modifyRelation(userID, userID2, userRelation)

@app.route('/v1/block/<userID>', methods=['GET'])
def getBlockedUsers(userID):

    try:
        userID = long(userID)
    except ValueError:
        return jsonify({'error':'userID must be of type long'}), 400

    if not AuthenticateHelper.authenticate(userID):
        return jsonify({"error":"Not logged in"}), 401

    blockedUsers = UserRelations.UserRelations.query.filter_by(fromUserID=userID).filter_by(relation=UserRelations.RelationEnum.blocked).all()
    blockedUsers = list(blockedUsers)
    return jsonify([b._to_user_dict() for b in blockedUsers])

@app.route('/v1/isConnected/<userID>/<userID2>/<sid>/<position>', methods=['GET'])
def checkIfConnectedAndLog(userID, userID2, sid=None, position=None):

    try:
        userID = long(userID)
        userID2 = long(userID2)
    except ValueError:
        return jsonify({'error':'userID and userID2 must be of type long'}), 400

    if not AuthenticateHelper.authenticate(userID):
        return jsonify({"error":"Not logged in"}), 401

    if not AuthenticateHelper.isUser(userID2):
        return jsonify({"error":"User does not exist anymore"}), 404

    connection = UserRelations.UserRelations.query.filter_by(fromUserID=userID).filter_by(toUserID=userID2).filter(UserRelations.UserRelations.relation != UserRelations.RelationEnum.blocked).all()

    connection = list(connection)
    if len(connection) == 1:
        chats = Chats.Chats.query.filter(Chats.Chats.users.any(userID)).filter(Chats.Chats.users.any(userID2)).all()
        chats = list(chats)
        for chat in chats:
            if len(chat.users) == 2:
                chatnames = ChatNames.ChatNames.query.filter_by(chatID=chat.chatID).filter_by(userID=userID).all()
                if len(chatnames) == 1:
                    chat = chat._to_dict()
                    chat["chatName"] = chatnames[0].chatName
                    return jsonify({"connected":True,"chat":chat})
                
    if sid is not None and position is not None:
        try:
            position = long(position)
            sid = long(sid)
        except ValueError:
            return jsonify({'error':'Position and sid must be longs'}), 400

        sessions = Sessions.Sessions.query.filter_by(sid=sid).filter_by(userID=userID).all()
        sessions = list(sessions)
        if len(sessions) == 1:
            db.session.add(Logs.Logs(sid, userID2, Logs.ActionEnum.clicked, position, datetime.datetime.utcnow()))
            db.session.commit()
        else:
            return jsonify({"error":"Invalid session id and user id pair"}), 400

    return jsonify({"connected":False})

@app.route('/v1/isConnected/<userID>/<userID2>', methods=['GET'])
def checkIfConnected(userID, userID2):
    return checkIfConnectedAndLog(userID, userID2)

# check if connected
@app.route('/v1/longdistance/<userID>/<userID2>', methods=['GET'])
def checkIfLongDistance(userID, userID2):

    try:
        userID = long(userID)
        userID2 = long(userID2)
    except ValueError:
        return jsonify({'error':'userID and userID2 must be of type long'}), 400

    if not AuthenticateHelper.authenticate(userID):
        return jsonify({"error":"Not logged in"}), 401

    if not AuthenticateHelper.isUser(userID2):
        return jsonify({"error":"User does not exist anymore"}), 404

    userRelations = UserRelations.UserRelations.query.filter_by(fromUserID=userID).filter_by(toUserID=userID2).filter_by(relation=UserRelations.RelationEnum.longdistance).all()
    userRelations = list(userRelations)
    if len(userRelations) == 1:
        return jsonify({"longdistance":True})
    else:
        return jsonify({"longdistance":False})

# make connected
@app.route('/v1/longdistance/<userID2>', methods=['POST'])
def postLongDistance(userID2):

    try:
        data = json.loads(request.data)
    except ValueError:
        return jsonify({'error':'Body of request must be of json-able string'}), 400

    userID = data.get('userID')

    if userID is None:
        return jsonify({'error':'Body of request must contain userID field'}), 400

    try:
        userID = long(userID)
        userID2 = long(userID2)
    except ValueError:
        return jsonify({'error':'userID and userID2 must be of type long'}), 400

    if not AuthenticateHelper.authenticate(userID):
        return jsonify({"error":"Not logged in"}), 401

    if not AuthenticateHelper.isUser(userID2):
        return jsonify({"error":"User does not exist anymore"}), 404

    userRelations = UserRelations.UserRelations.query.filter_by(fromUserID=userID).filter_by(toUserID=userID2).all()
    userRelations = list(userRelations)
    if len(userRelations) == 1:
        userRelation = userRelations[0]
        userRelation.relation = UserRelations.RelationEnum.longdistance
    else:
        userRelation = UserRelations.UserRelations(userID, userID2, UserRelations.RelationEnum.longdistance)
        db.session.add(userRelation)

    try:
        db.session.commit()
    except IntegrityError:
        pass

    return jsonify({"response":"success"})

@app.route('/v1/notlongdistance/<userID2>', methods=['POST'])
def postNotLongDistance(userID2):

    try:
        data = json.loads(request.data)
    except ValueError:
        return jsonify({'error':'Body of request must be of json-able string'}), 400

    userID = data.get('userID')

    if userID is None:
        return jsonify({'error':'Body of request must contain userID field'}), 400

    try:
        userID = long(userID)
        userID2 = long(userID2)
    except ValueError:
        return jsonify({'error':'userID and userID2 must be of type long'}), 400

    if not AuthenticateHelper.authenticate(userID):
        return jsonify({"error":"Not logged in"}), 401

    if not AuthenticateHelper.isUser(userID2):
        return jsonify({"error":"User does not exist anymore"}), 404

    userRelations = UserRelations.UserRelations.query.filter_by(fromUserID=userID).filter_by(toUserID=userID2).filter_by(relation=UserRelations.RelationEnum.longdistance).all()
    userRelations = list(userRelations)
    if len(userRelations) == 1:
        userRelation = userRelations[0]
        if userRelation.relation == UserRelations.RelationEnum.longdistance:
            userRelation.relation = UserRelations.RelationEnum.connected
        else:
            return jsonify({"error":"Cannot change from long distance to connected"}), 404
    else:
        return jsonify({"error":"Cannot change from long distance to connected"}), 404

    try:
        db.session.commit()
    except IntegrityError:
        pass

    return jsonify({"response":"success"})
