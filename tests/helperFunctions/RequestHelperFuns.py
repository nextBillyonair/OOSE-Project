import sys
import os
sys.path.append(os.path.abspath("../src/Backend"))
from app.models import Requests
import json
from app import db

# emit a send request message from socket_client from user1 with userID1 to user2 with userID2, optional msg
def sendRequest(test_client, userID1, userID2, msg="", success=True, position=None, sid=None):
    response = test_client.post('v1/sendRequest', data=json.dumps(dict(userID=userID1, receiverID=userID2, msg=msg, position=position, sid=sid)))
    if success:
    	data = json.loads(response.get_data(as_text=True))
        assert response.status == '200 OK'
        assert data.get('response') == 'success'
    else:
        assert response.status != '200 OK'
# emit an accept request message from socket_client to userID with requestID
def acceptRequest(test_client, userID, requestID, success=True):
    response = test_client.post('v1/acceptRequest', data=json.dumps(dict(userID=userID, requestID=requestID)))
    if success:
        assert response.status == '200 OK'
        data = json.loads(response.get_data(as_text=True))
        return data
    else:
        assert response.status != '200 OK'

# emit an decline request message from socket_client to userID with requestID
def declineRequest(test_client, userID, requestID, success=True):
    response = test_client.post('v1/declineRequest', data=json.dumps(dict(userID=userID, requestID=requestID)))
    if success:
        assert response.status == '200 OK'
        data = json.loads(response.get_data(as_text=True))
        assert data.get('response') == 'success'
    else:
        assert response.status != '200 OK'

# gets all the requests for the given userID
def getRequests(test_client, userID, success=True):
    response = test_client.get('/v1/requests/' + str(userID), data=json.dumps(dict(userID=userID)))
    if success:
        assert response.status == '200 OK'
        data = json.loads(response.get_data(as_text=True))
        return data
    else:
        assert response.status != '200 OK'

# check socket_client messages for single sent request from user1 with userID1 to user2 with userID2
def getReceivedRequest(socket_client, userID1, userID2, msg=""):
    recvd = socket_client.get_received()
    assert len(recvd) == 1

    assert recvd[0]['name'] == 'send request'

    args = recvd[0]['args']
    assert len(args) == 1

    arg = args[0]
    assert arg.get('request') != None

    request = arg['request']
    assert request.get('requestID') != None
    assert request.get('fromUserID') == str(userID1)
    assert request.get('toUserID') == str(userID2)
    assert request.get('msg') == msg
    assert request.get('timeStamp') != None
    assert request.get('completed') == False

    return request['requestID']

# check for target amount of db requests with requestID
def checkNumRequests(requestID, target):
    count = 0
    for request in db.session.query(Requests.Requests).filter(Requests.Requests.requestID == requestID):
        count += 1
    assert count == target
    