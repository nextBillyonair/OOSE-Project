import sys
import os
sys.path.append(os.path.abspath("../Backend"))
from app.models import *
from app import db
from sqlalchemy.orm import aliased
from sqlalchemy import and_, func

logs = aliased(Logs.Logs)
fv = aliased(FeatureVectors.FeatureVectors)

def clickCount(table):
    results = db.session.query(func.count()).filter(table.action == Logs.ActionEnum.clicked).all()
    return results

def requestsCount(table):
    results = db.session.query(func.count()).filter(table.action == Logs.ActionEnum.sendrequest).all()
    return results

def actionsCount(table):
    results = db.session.query(table.action, func.count()).group_by(table.action).all()
    return results

# How many clicks/request per position
def positionCount(table):
    results = db.session.query(table.position, func.count()).group_by(table.position).all()
    return results

def avgPosition(table):
    # Average position clicked
    results = db.session.query(func.avg(table.position)).all()
    return results

def avgPositionByAcion(table):
    # Average position clicked
    results = db.session.query(table.action, func.avg(table.position)).group_by(table.action).all()
    return results

# Number of requests and number of clicks that don't lead to requests
def bestActionSubquery():
    subquery = db.session.query(logs.sid, logs.otherUserID, func.max(logs.action).label('action'))
    subquery = subquery.group_by(logs.sid, logs.otherUserID)
    subquery = subquery.subquery('bestAction')
    return subquery

# JOIN WITH feature_vectors (on SID and USERID)
def noBluetoothSubquery():
    subquery = db.session.query(logs.sid, logs.otherUserID, logs.action, logs.position, logs.timeStamp)
    subquery = subquery.join(fv, and_(fv.sid == logs.sid, fv.otherUserID == logs.otherUserID))
    noBluetoothSubquery = subquery.subquery('noBluetooth')
    return noBluetoothSubquery


print('Number of Total Clicks', clickCount(logs)[0][0])
print('Number of Total Requests Sent', requestsCount(logs)[0][0])
print('Count Given Actions', actionsCount(logs))
print('Count Given Actions, Removing Duplicates', actionsCount(bestActionSubquery().c))
print('Count Given Actions, Removing Bluetooth Users', actionsCount(noBluetoothSubquery().c))
print('Average Position', avgPosition(logs))
print('Average Position Per Action', avgPositionByAction(logs))
