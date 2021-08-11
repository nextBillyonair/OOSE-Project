from app import app, db, session
from app.models import UserSettings
from flask import request, jsonify
import json
from sqlalchemy.exc import IntegrityError
from app.views.helperFunctions import AuthenticateHelper

@app.route('/v1/userSettings/<userID>', methods=['GET'])
def getUserSettings(userID):
    try:
        userID = long(userID)
    except ValueError:
        return jsonify({'error':'userID must be of type long'}), 400

    if not AuthenticateHelper.authenticate(userID):
        return jsonify({"error":"Not logged in"}), 401

    # return from  database userID, radius, time
    settings = UserSettings.UserSettings.query.filter_by(userID=userID).all()
    settings = list(settings)

    if len(settings) == 0:
        return jsonify({'error':'Internal error'}), 500
    else:
        return jsonify(settings[0]._to_dict())

@app.route('/v1/tags/<userID>/<userID2>', methods=['GET'])
def getTags(userID, userID2):
    try:
        userID = long(userID)
        userID2 = long(userID2)
    except ValueError:
        return jsonify({'error':'userID and userID2 must be of type long'}), 400

    if not AuthenticateHelper.authenticate(userID):
        return jsonify({"error":"Not logged in"}), 401

    if not AuthenticateHelper.isUser(userID2):
        return jsonify({"error":"User does not exist"}), 404

    # return from  database userID, radius, time
    settings = UserSettings.UserSettings.query.filter_by(userID=userID2).all()
    settings = list(settings)

    if len(settings) == 0:
        return jsonify({'error':'Internal error'}), 500
    else:
        return jsonify({"id":userID2, "tags":settings[0].tags})

@app.route('/v1/tags', methods=['POST'])
def postTags():
    try:
        data = json.loads(request.data)
    except ValueError:
        return jsonify({'error':'Body of request must be of json-able string'}), 400

    userID = data.get('userID')
    tags = data.get('tags')

    if None in (userID, tags):
        return jsonify({'error':'Data must contain userID and tags fields'}), 400

    try:
        userID = long(userID)
        tags = list(tags)
    except ValueError:
        return jsonify({'error':'userID must be of type long and tags a list'}), 400

    if len(tags) != 3:
        return jsonify({'error':'There must be 3 tags'}), 400

    try:
        for i in range(3):
            tags[i] = unicode(tags[i])
    except ValueError:
        return jsonify({'error':'Tags must be of type unicode'}), 400

    if not AuthenticateHelper.authenticate(userID):
        return jsonify({"error":"Not logged in"}), 401

    newTags = ["", "", ""]
    i = 0
    for tag in tags:
        if tag != "":
            newTags[i] = tag
            i += 1

    settings = UserSettings.UserSettings.query.filter_by(userID=userID).all()
    settings = list(settings)

    if len(settings) == 0:
        return jsonify({'error':'Internal error'}), 500
    else:
        settings[0].tags = newTags
        try:
            db.session.commit()
        except IntegrityError:
            pass

        return jsonify({"tags":newTags})
