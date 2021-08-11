from app import app, socketio, session
from flask_socketio import emit, join_room, leave_room
from flask import jsonify
from app.views.helperFunctions import AuthenticateHelper

@socketio.on('new user')
def handle_new_user(data):
    room = data.get('userID')
    accessToken = data.get('accessToken')

    h = AuthenticateHelper.fbAuth(room, accessToken)
    if not h:
        return jsonify({"error":"Incorrect login"}), 401

    session['user'] = h

    try:
        room = long(room)
    except ValueError:
        return jsonify({'error':'Room must be of type long'}), 400

    join_room(str(room))
    emit("New", room=str(room))

@socketio.on('remove user')
def handle_remove_user(data):
    room = data.get('userID')

    if room is None:
        return jsonify({'error':'Body of request must contain userID field'}), 400

    try:
        room = long(room)
    except ValueError:
        return jsonify({'error':'Room must be of type long'}), 400

    if not AuthenticateHelper.authenticate(room):
        emit('not logged in', room=str(room))

    leave_room(str(room))
    emit("User removed", room=str(room))
