from app import app, db, socketio, session
from app.models import ChatNames, Chats, Logs, Messages, Requests, Sessions, UnseenMsgs, UserRelations, UserSettings
from flask import request, jsonify
import datetime
import json
from sqlalchemy import desc, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import aliased
from .randomnames import random_namepair
from app.views.helperFunctions import AuthenticateHelper, RequestHelper, GraphHelper

@app.route('/v1/requests/<userID>', methods=['GET'])
def getRequests(userID):

    try:
        userID = long(userID)
    except ValueError:
        return jsonify({'error':'userID must be of type long'}), 400

    if not AuthenticateHelper.authenticate(userID):
        return jsonify({"error":"Not logged in"}), 401

    r = aliased(Requests.Requests)
    u = aliased(UserSettings.UserSettings)
    ur = aliased(UserRelations.UserRelations)

    query = db.session.query(r.requestID, r.fromUserID, r.toUserID, r.msg, r.timeStamp, r.completed, u.tags)
    query = query.filter(and_(r.toUserID==userID, r.completed==False))
    query = query.outerjoin(ur, and_(ur.fromUserID == r.toUserID, ur.toUserID == r.fromUserID, ur.relation != UserRelations.RelationEnum.blocked))
    query = query.join(u, r.fromUserID == u.userID)
    query = query.order_by(desc(r.timeStamp)).all()

    return jsonify([r._asdict() for r in query])

@app.route('/v1/acceptRequest', methods=['POST'])
def handle_accept_request():
    try:
        data = json.loads(request.data)
    except ValueError:
        return jsonify({'error':'Body of request must be of json-able string'}), 400

    userID = data.get('userID')
    requestID = data.get('requestID')
    if None in (userID, requestID):
        return jsonify({'error':'Data must contain userID and requestID fields'}), 400

    try:
        userID = long(userID)
        requestID = long(requestID)
    except ValueError:
        return jsonify({'error':'userID and requestID must be of type long'}), 400

    if not AuthenticateHelper.authenticate(userID):
        return jsonify({"error":"Not logged in"}), 401

    # userID received requestID
    requests = Requests.Requests.query.filter_by(requestID=requestID).filter_by(toUserID=userID).all()
    requests = list(requests)

    if len(requests) == 0:
        return jsonify({'error':'Request does not exist'}), 404

    request1 = requests[0]
    userRelations = UserRelations.UserRelations.query.filter_by(fromUserID=userID).filter_by(toUserID=request1.fromUserID).all()
    if len(userRelations) == 0:
        db.session.add(UserRelations.UserRelations(userID, request1.fromUserID, UserRelations.RelationEnum.connected))
    else:
        userRelation = userRelations[0]
        if userRelation.relation == UserRelations.RelationEnum.blocked:
            return jsonify({'error':'You cannot accept a request of someone you have blocked'}), 404
        else:
            userRelation.relation = UserRelations.RelationEnum.connected

    db.session.delete(request1)
    chat = Chats.Chats([userID, request1.fromUserID])
    db.session.add(chat)

    try:
        db.session.commit()
    except IntegrityError:
        # chat was deleted
        return jsonify({'error':'User may not exist'}), 404

    chatName1 = random_namepair()
    chatNameObj1 = ChatNames.ChatNames(chat.chatID, request1.toUserID, chatName1)
    chatName2 = random_namepair()
    chatNameObj2 = ChatNames.ChatNames(chat.chatID, request1.fromUserID, chatName2)
    db.session.add(chatNameObj1)
    db.session.add(chatNameObj2)

    message = Messages.Messages(chat.chatID, request1.fromUserID, request1.msg, request1.timeStamp)
    db.session.add(message)
    db.session.commit()

    if changeConnectedIfNotBlocked(request1.fromUserID, userID):
        socketio.emit('accept request', {"chat":chat._to_dict(), "chatName":chatName2, "msg": request1.msg, "userID":userID}, room=str(request1.fromUserID))

    db.session.add(UnseenMsgs.UnseenMsgs(chat.chatID, userID, message.msgID))
    db.session.add(UnseenMsgs.UnseenMsgs(chat.chatID, request1.fromUserID, message.msgID))

    try:
        db.session.commit()
    except IntegrityError:
        # chat was deleted
        return jsonify({'error':'User may not exist'}), 404

    Requests.Requests.query.filter_by(fromUserID=userID).filter_by(toUserID=request1.fromUserID).delete()
    try:
        db.session.commit()
    except IntegrityError:
        pass

    return jsonify({"chat":chat._to_dict(), "chatName":chatName1, "msg": request1.msg, "userID":request1.fromUserID})

def changeConnectedIfNotBlocked(userID, userID2):
    userRelations = UserRelations.UserRelations.query.filter_by(fromUserID=userID).filter_by(toUserID=userID2).all()
    changed = False
    if len(userRelations) == 0:
        db.session.add(UserRelations.UserRelations(userID, userID2, UserRelations.RelationEnum.connected))
        changed = True
    else:
        userRelation = userRelations[0]
        if userRelation.relation != UserRelations.RelationEnum.blocked:
            userRelation.relation = UserRelations.RelationEnum.connected
            changed = True

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        # adding row failed, try again and modify the row added
        return changeConnectedIfNotBlocked(userID, userID2)

    return changed

@app.route('/v1/sendRequest', methods=['POST'])
def handle_send_request():

    try:
        data = json.loads(request.data)
    except ValueError:
        return jsonify({'error':'Body of request must be of json-able string'}), 400

    userID = data.get('userID')
    receiverID = data.get('receiverID')
    msg = data.get('msg')
    position = data.get('position')
    sid = data.get('sid')

    if None in (userID, receiverID, msg):
        return jsonify({'error':'Data must contains userID, requestID, and msg fields'}), 400

    try:
        userID = long(userID)
        receiverID = long(receiverID)
        msg = unicode(msg)
    except ValueError:
        return jsonify({'error':'userID and receiverID must be of type long and msg must be unicode'}), 400

    if not AuthenticateHelper.authenticate(userID):
        return jsonify({"error":"Not logged in"}), 401

    if not AuthenticateHelper.isUser(receiverID):
        return jsonify({"error":"User does not exist"}), 404

    if userID == receiverID:
        return jsonify({'error':'Cannot send yourself a request'}), 400

    nearby = GraphHelper.isNearbyInGraph(userID, receiverID)
    if not nearby:
        return jsonify({'error':'Cannot send a request to someone not nearby'}), 404

    relations1 = UserRelations.UserRelations.query.filter_by(fromUserID=userID).filter_by(toUserID=receiverID).all()
    relations2 = UserRelations.UserRelations.query.filter_by(fromUserID=receiverID).filter_by(toUserID=userID).all()

    if len(relations1) == 1:
        relation1 = relations1[0]
        if relation1.relation in (UserRelations.RelationEnum.connected, UserRelations.RelationEnum.blocked, UserRelations.RelationEnum.longdistance):
            return jsonify({'error':'Cannot send a request to someone you have blocked or are connected to'}), 404

    isBlocked = False
    if len(relations2) == 1:
        relation2 = relations2[0]
        if relation2.relation != UserRelations.RelationEnum.blocked:
            return jsonify({'error':'Cannot send a request to someone you are connected to'}), 400
        else:
            # even though they have blocked you, you don't know that the request didn't go through
            isBlocked = True

    # if userId and receiverID already have request
    request1 = Requests.Requests(userID, receiverID, msg, datetime.datetime.utcnow())
    db.session.add(request1)
    try:
        db.session.commit()
    except IntegrityError:
        return jsonify({'error':'Request already sent from you'}), 400

    if not isBlocked:
        data = {}
        data['request'] = request1._to_dict()
        settings = UserSettings.UserSettings.query.filter_by(userID=userID).all()
        settings = list(settings)
        if len(settings) == 0:
            return jsonify({'error':'Internal error'}), 400
        else:
            tags = settings[0].tags
            data['tags'] = tags

        socketio.emit("send request", data, room=str(receiverID))

    if not logSendRequest(position, sid, userID, receiverID):
        return jsonify({"error":"Invalid logging information"}), 400

    return jsonify({"response":"success"})

def logSendRequest(position, sid, userID, receiverID):
    if None not in (position, sid):
        try:
            position = long(position)
            sid = long(sid)
        except ValueError:
            return False

        sessions = Sessions.Sessions.query.filter_by(sid=sid).filter_by(userID=userID).all()
        sessions = list(sessions)

        if len(sessions) == 1:
            db.session.add(Logs.Logs(sid, receiverID, Logs.ActionEnum.sendrequest, position, datetime.datetime.utcnow()))
            db.session.commit()
        else:
            return False

    return True

@app.route('/v1/declineRequest', methods=['POST'])
def handle_decline_request():
    
    try:
        data = json.loads(request.data)
    except ValueError:
        return jsonify({'error':'Body of request must be of json-able string'}), 400

    userID = data.get('userID')
    requestID = data.get('requestID')

    if None in (userID, requestID):
        return jsonify({'error':'Data must contain userID and requestID'}), 400

    if not AuthenticateHelper.authenticate(userID):
        return jsonify({"error":"Not logged in"}), 401

    return RequestHelper.decline(userID, requestID)

def delete_old_requests():
    since = datetime.datetime.utcnow() - datetime.timedelta(hours=24)
    reqs = Requests.Requests.query.filter(Requests.Requests.timeStamp < since).delete()
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        delete_old_requests()
