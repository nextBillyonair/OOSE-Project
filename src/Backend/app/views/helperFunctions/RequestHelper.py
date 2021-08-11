from flask import jsonify
from app import db
from app.models import Requests
from sqlalchemy.exc import IntegrityError

def decline(userID, requestID):
    try:
        userID = long(userID)
        requestID = long(requestID)
    except ValueError:
        return jsonify({'error':'userID and requestID must be of type long'}), 400

    # userID received requestID
    requests = Requests.Requests.query.filter_by(requestID=requestID).all()
    if len(requests) == 0:
        return jsonify({'error':'Request does not exist'}), 404
    else:
        request = requests[0]
        if request.toUserID == long(userID):
            request.completed = True            

            try:           
               db.session.commit()
            except IntegrityError:
                return jsonify({"error":"Failed to decline request"}), 404

            Requests.Requests.query.filter_by(fromUserID=userID).filter_by(toUserID=request.fromUserID).delete()
            try:
                db.session.commit()
            except IntegrityError:
                pass
        else:
            return jsonify({'error':'Invalid requestID'}), 400

    return jsonify({'response': 'success'})
