from app import db, hashing, session
from app.models import User, UserSettings
from facebook import GraphAPI, GraphAPIError
from sqlalchemy.exc import IntegrityError

FB_APP_ID = '569248390133225'
FB_APP_NAME = 'Footsie'
FB_APP_SECRET = '5a63dd2867cb4e221d393374ef469b0e'

def fbAuth(userID, accessToken):
    if None in (userID, accessToken):
        return None

    try:
        userID = long(userID)
        accessToken = str(accessToken)
    except ValueError:
        return None

    graph = GraphAPI(accessToken)

    try:
        profile = graph.get_object('me')
    except GraphAPIError:
        return None

    if str(userID) == profile.get('id'):
        users = User.User.query.filter_by(userID=userID).all()
        users = list(users)
        if len(users) == 0:
            user = User.User(userID, accessToken)
            db.session.add(user)
        else:
            user = users[0]
            user.accessToken = accessToken

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return fbAuth(userID, accessToken)

        if len(users) == 0:
            userSettings = UserSettings.UserSettings(userID, radius=1, hours=6, tags=["","",""])
            db.session.add(userSettings)

            try:
                db.session.commit()
            except IntegrityError:
                pass

        h = hashing.hash_value(accessToken, salt=FB_APP_SECRET)
        return h

    return None

def authenticate(userID):
    try:
        userID = long(userID)
    except ValueError:
        return False

    users = User.User.query.filter_by(userID=userID).all()
    users = list(users)

    if len(users) == 1 and session.get('user'):
        if hashing.check_value(session.get('user'), users[0].accessToken, salt=FB_APP_SECRET):
            return True
    return False

def isUser(userID):
    try:
        userID = long(userID)
    except ValueError:
        return False

    users = User.User.query.filter_by(userID=userID).all()
    users = list(users)
    if len(users) == 1:
        return True
    return False
