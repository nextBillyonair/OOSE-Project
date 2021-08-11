from app import app, db, session
from app.models import NearbyUsers, UserSettings, Sessions
from flask import request, jsonify
import datetime
import json
from app.views.helperFunctions import AuthenticateHelper, GraphHelper
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_

MIN_RADIUS = 1
MIN_HOURS = 1
MAX_RADIUS = 4
MAX_HOURS = 24
MIN_MAX_PEOPLE = 1
MAX_MAX_PEOPLE = 100

@app.route('/v1/radius', methods=['POST'])
def setRadius():

    try:
        data = json.loads(request.data)
    except ValueError:
        return jsonify({'error':'Body of request must be of json-able string'}), 400

    userID = data.get('userID')
    radius = data.get('radius')

    if None in (userID, radius):
        return jsonify({'error':'Body of request must contain userID and radius fields'}), 400        

    try:
        userID = long(userID)
        radius = int(radius)
    except ValueError:
        return jsonify({'error':'userID must be of type long and radius of int'}), 400

    if not AuthenticateHelper.authenticate(userID):
        return jsonify({"error":"Not logged in"}), 401

    if radius < MIN_RADIUS or radius > MAX_RADIUS:
        return jsonify({'error':'Radius must be an integer from 1 to 4'}), 400

    settings = UserSettings.UserSettings.query.filter_by(userID=userID).all()
    settings = list(settings)
    if len(settings) == 0:
        return jsonify({'error':'Internal error'}), 500
    else:
        setting = settings[0]
        setting.radius = radius
        try:
            db.session.commit()
        except IntegrityError:
            pass

    # save in database userID, radius
    return jsonify({"radius":radius})

@app.route('/v1/time', methods=['POST'])
def setTime():

    try:
        data = json.loads(request.data)
    except ValueError:
        return jsonify({'error':'Body of request must be of json-able string'}), 400

    userID = data.get('userID')
    hours = data.get('hours')

    if None in (userID, hours):
        return jsonify({'error':'Body of request must contain userID and hours fields'}), 400        

    try:
        userID = long(userID)
        hours = int(hours)
    except ValueError:
        return jsonify({'error':'userID must be of type long and hours of int'}), 400

    if not AuthenticateHelper.authenticate(userID):
        return jsonify({"error":"Not logged in"}), 401

    if hours < MIN_HOURS or hours > MAX_HOURS:
        return jsonify({'error':'Hours must be an integer from 1 to 24'}), 400

    settings = UserSettings.UserSettings.query.filter_by(userID=userID).all()
    settings = list(settings)

    if len(settings) == 0:
        return jsonify({'error':'Internal error'}), 500
    else:
        setting = settings[0]
        setting.hours = hours
        try:
            db.session.commit()
        except IntegrityError:
            pass

    # save in database userID, time
    return jsonify({"hours":hours})

@app.route('/v1/getNearbyUsers/<userID>', methods=['GET'])
def getNearbyUsers(userID):
    return getNearbyUsersMaxPeople(userID)

@app.route('/v1/getNearbyUsers/<userID>/<maxPeople>', methods=['GET'])
def getNearbyUsersMaxPeople(userID, maxPeople = 25):
    
    try:
        userID = long(userID)
    except ValueError:
        return jsonify({'error':'userID must be of type long'}), 400

    try:
        maxPeople = int(maxPeople)
    except ValueError:
        return jsonify({'error':'maxPeople type int'}), 400

    if not AuthenticateHelper.authenticate(userID):
        return jsonify({"error":"Not logged in"}), 401

    if maxPeople < MIN_MAX_PEOPLE or maxPeople > MAX_MAX_PEOPLE:
        return jsonify({'error':'maxPeople must be an integer from 1 to 100'}), 400

    session = Sessions.Sessions(userID)
    db.session.add(session)
    db.session.commit()

    nearbyUsers = GraphHelper.getNearbyUsers(userID, maxPeople=maxPeople, sid=session.sid)
    session.usersInSession = len(nearbyUsers)

    return jsonify({'users':nearbyUsers, 'sid':session.sid})

@app.route('/v1/isNearby/<userID>/<userID2>', methods=['GET'])
def checkIfNearby(userID, userID2):
    try:
        userID = long(userID)
        userID2 = long(userID2)
    except ValueError:
        return jsonify({'error':'userID and userID2 must be of type long'}), 400

    if not AuthenticateHelper.authenticate(userID):
        return jsonify({"error":"Not logged in"}), 401

    if not AuthenticateHelper.isUser(userID2):
        return jsonify({"error":"Invalid userID2"}), 400
    
    if userID == userID2:
        return jsonify({'error':'Cannot send yourself a request'}), 400

    isNearby, time = GraphHelper.isNearbyAndTimeInGraph(userID, userID2)
    if time is not None:
        return jsonify({"nearby":isNearby, "time":time.isoformat()})
    else:
        return jsonify({"nearby":isNearby})

@app.route('/v1/isNearby', methods=['POST'])
def postNearby():
    try:
        data = json.loads(request.data)
    except ValueError:
        return jsonify({'error':'Body of request must be of json-able string'}), 400

    userID = data.get('userID')
    userID2 = data.get('userID2')

    if None in (userID, userID2):
        return jsonify({'error':'Body of request must contain userID and userID2 fields'}), 400        

    try:
        userID = long(userID)
        userID2 = long(userID2)
    except ValueError:
        return jsonify({'error':'userID and userID2 must be of type long'}), 400
    
    if userID == userID2:
        return jsonify({'error':'Cannot send yourself a request'}), 400

    if not AuthenticateHelper.authenticate(userID):
        return jsonify({"error":"Not logged in"}), 401

    if not AuthenticateHelper.isUser(userID2):
        return jsonify({"error":"Invalid userID2"}), 400

    nearbyUsers = NearbyUsers.NearbyUsers.query.filter_by(userID=userID).filter_by(otherUserID=userID2).all()
    nearbyUsers = list(nearbyUsers)

    time = datetime.datetime.utcnow()
    if len(nearbyUsers) == 0:
        nearbyUser = NearbyUsers.NearbyUsers(userID, userID2, time)
        db.session.add(nearbyUser)
    else:
        nearbyUser = nearbyUsers[0]
        nearbyUser.timeStamp = time

    db.session.commit()

    userSettings = UserSettings.UserSettings.query.filter(or_(UserSettings.UserSettings.userID == userID, UserSettings.UserSettings.userID == userID2)).all()
    userSettings = list(userSettings)
    if len(userSettings) != 2:
        return jsonify({'error':'Interval server error'}), 500

    hours = min(userSettings[0].hours, userSettings[1].hours)

    return jsonify({"id":userID2, "time": time + datetime.timedelta(hours=hours)})

def delete_old_graph_edges():
    since = datetime.datetime.utcnow() - datetime.timedelta(hours=24)
    reqs = NearbyUsers.NearbyUsers.query.filter(NearbyUsers.NearbyUsers.timeStamp < since).delete()
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        delete_old_graph_edges()
