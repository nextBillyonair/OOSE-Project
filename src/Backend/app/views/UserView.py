from app import app, db, session
from app.models import ChatNames, Chats, FeatureVectors, Logs, Messages, NearbyUsers, Requests, Sessions, User, UnseenMsgs, UserRelations, UserSettings
from flask import request, jsonify
import json
from sqlalchemy.exc import IntegrityError
from app.views.helperFunctions import AuthenticateHelper

@app.route('/')
def index():
    return "Hello World"

@app.route('/v1/login', methods=['POST'])
def login():
    try:
        data = json.loads(request.data)
    except ValueError:
        return jsonify({'error':'Body of request must be of json-able string'}), 400

    userID = data.get('userID')
    accessToken = data.get('accessToken')

    h = AuthenticateHelper.fbAuth(userID, accessToken)
    if h:
        session['user'] = h
        session['nearby'] = {}
        return jsonify({"response":"success"})

    return jsonify({"error":"Incorrect login"}), 401

@app.route('/v1/logout', methods=['POST'])
def logout():
    session['user'] = None
    session['nearby'] = {}
    return jsonify({"response":"success"})

@app.route('/v1/deactivate/<userID>', methods=['POST'])
def deactivate(userID):
    try:
        userID = long(userID)
    except ValueError:
        return jsonify({'error':'userID must be of type long'}), 400

    if not AuthenticateHelper.authenticate(userID):
        return jsonify({"error":"Not logged in"}), 401

    deleteUserID(userID)

    return jsonify({"response":"success"})

def deleteUserID(userID):
    for chat in db.session.query(Chats.Chats).filter(Chats.Chats.users.any(userID)):
        chatDict = chat._to_dict()
        ChatNames.ChatNames.query.filter_by(chatID=chatDict['chatID']).delete()
        UnseenMsgs.UnseenMsgs.query.filter_by(chatID=chatDict['chatID']).delete()
        Messages.Messages.query.filter_by(chatID=chatDict['chatID']).delete()
        db.session.delete(chat)

    for session in db.session.query(Sessions.Sessions).filter_by(userID=userID):
        sessionDict = session._to_dict()
        sid = sessionDict['sid']
        FeatureVectors.FeatureVectors.query.filter_by(sid=sid).delete()
        Logs.Logs.query.filter_by(sid=sid).delete()
        db.session.delete(session)

    Requests.Requests.query.filter_by(fromUserID=userID).delete()
    Requests.Requests.query.filter_by(toUserID=userID).delete()
    UserRelations.UserRelations.query.filter_by(fromUserID=userID).delete()
    UserRelations.UserRelations.query.filter_by(toUserID=userID).delete()
    NearbyUsers.NearbyUsers.query.filter_by(userID=userID).delete()
    NearbyUsers.NearbyUsers.query.filter_by(otherUserID=userID).delete()
    UserSettings.UserSettings.query.filter_by(userID=userID).delete()
    User.User.query.filter_by(userID=userID).delete()
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        deleteUserID(userID)
