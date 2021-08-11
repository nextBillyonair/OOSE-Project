import sys                                                                                                                                         
sys.path.insert(0, './helperFunctions')  
import os
sys.path.append(os.path.abspath("../../src/Backend"))

import UserHelperFuns, RequestHelperFuns, ChatHelperFuns, ChatsHelperFuns, GraphHelperFuns
import json
from app import app, db, socketio
from app.models import NearbyUsers
import db_commands
from app.views.helperFunctions import GraphHelper

def test_position_sid():

    users = [
        (113989906059772, "EAAIFungVNekBAKacZAfBEQiZBpPWRuC6cnWZA91t5hsxV04EBlfUWdnsdkfIaaeqOyudOvxBngYhLA2ik8a0vhvVXo1NoAdB1cjE86ZCJ6LPEWoEEyMugdYQPgxZCGbg1bltVf2r4qeCPdHhZCZBZBEWvzC0xvUPAQZBc7XYiqRprbdH1dGCw7tDARKIarUxzNtsw21jLhT00d1o5xcQLnAxIWqnsRf47dkhpkwvAw9G3VgZDZD"),
        (105243400270751, "EAAIFungVNekBAHhauiBZAL8WTohZCR22OPIFgNEsUZBwfvmJNjdzK4SBB5l3y5w32sca8Uh9LZBcjlD0rd67CQyjvGBU5WZCrlxjo7UBq1kNHtu8NrDZAOXSFDiMqudlsKJXRpVt1puUL0dP7ZCDjh1SptIlL8Mobq8hh3TZCbQ22DIFaxWZCc3wvyXJPqgrBCmG7ddaZAhdYPUwZApZAOa42GakNYwVfl29Kgkm7cs8qQSrawZDZD"),
        (114055959386765, "EAAIFungVNekBANSTRfQuBZAZCNNLJTsj5nGZCrc558pV55t8WZBGEd7PfpJsVeYdWiZCxswN2hXMWhwXBV1iJsWLbVtCZC0EZBBx6ptQlr6XCRyaZCTO9fXt6NN2ab55hG4MbyibDKqc9E5h2wn1lFOLxDuT7TfRPIFzdVKWrKFEOXRAapj82pNVI2Yb4ScDRxqZAi4wGAZCU9kShFCRD1s9yu8mG8rKZC1B5bPrsMCIBlnDwZDZD"),
        (115852912540399, "EAAIFungVNekBAGosOSufuEHlzXppkRcnAWwKp5A7PNVCAwDcJ1NHYeuwqbgbKADZAEx6f9jVGljVQvRlsgEDacoKEjpalk2IqFTXKIVXCI4Jax6ZBWDFoZCLgGZCypLdxzGx8sQCTB1I2Jp3ZBt7QOzaIlNLyJ6e1gU4lxisPWzdAszKTdRtBw1ZBlw0gPcbLpL1YN2y8sZAymShXmLiv6BY8FOSZB5cvEhNs0XDoKqJXQZDZD"),
        (116436555814180, "EAAIFungVNekBAEMur8T3MYvOafmNhKjOYhlzX8Bi0WDqcJQm1YotdKzWrD3RUrEUEc2QEaJZA09O73pBtWryBzeJ6uZBFcIOFSwUZAJjqqTy948z4ZAQ534JJshgtvYNH0wigp7yD6DUq7YwXVbvVjobCmYrpZChb7nWkQxEYINeD00i9qhPlZCZBelLG4Kh0DXtJUrPlmZAn2SOgODPNS2hfthmlZA1GQOYaDGyi1ZBW1tQZDZD"),
        (112066866253400, "EAAIFungVNekBAFRnZAPGVyIXUjJWd8gB60uuZB9EYx2BcMfS4U5Iv5sb8BhMi6ZAXjEEPqkh6cJxuJ0r4xZAPHNBvc2icHVrOR8AEVpZCLAzylFA5tm4mSO90mSf5904gmxjEjR5Lnb0FXz1OpuOq8y9GGLeydFyghQkrGqDoZBRvdMozA6NjS3vPSPxkC9kOiO5CdyMoV3s8eScyP7EtJ8J8USL6qVSIUe7cD79okqQZDZD"),
        (114282436030382, "EAAIFungVNekBAGiZAYC5neO1wF45xUiZBLzoU6z30OA01CIdCydG5e9U0hsTjRoRgGbkEEzkRbZB4OecC52tTwDAqMNOs2ZB6jTiHRIFFC5bRciGYVsW94dg0GnzBtsmnWCBmFlufW6r7fYrvANqZAI1SDjl7uIjXoXvXI3a6XM8zaVBr1zevrtaGGjO0IehnRT7Ww8A5cN0GDY4OpX9MOc8RNb2H6kxRZCETsWt4tRgZDZD"),
        (115478412577076, "EAAIFungVNekBABg4vkQ2TLZAYmvs4OobG1aOPWW20EVs5pZBIWhPNMERO4v57mJ0hJmpsnMT7Ka34mbPZBrOTGBY3b210BASDRxs0R7LPCtoeRD1lPtO41ulZCsciGH9evI33VFuLWo1VPQ2XXR2gmLXXQWO1gsG2BSJOmj6vjNdZBakYCZC7slFEtpO8CcwNpquDDSZAbWkp7ASdqRd2vYHFOMx1WgxRnZAR9cZB0ZB8iswZDZD"),
        (115396019251967, "EAAIFungVNekBAFBZCNOTaFfyvMsilYBPPyl5OLI2kLYmOvFM76VZAy9CChKguEFNLdKgmMfFBCE5YmdQTFbhCprlCkVL8bqxQK9WIxL6vDvEwq5E9G8hvydbDTorK6vzPXTzz9aIfE90nLTqGFykp8wlnXwqfP1T5XR2mZCDmwjMwTF2JbDpB4NVN2nmY7GNPkX7ZBLBRJpJCc9DxGyDHOTcqlNGPoxxf0CmjGS7yQZDZD"),
        (128133937974484, "EAAIFungVNekBAExZAWSpLdYDfTv3Q4VOKQnU7dMZB5Wfu1UYZBQrFegluaW5inWkKGOIZCaZADriowII5Yc62wrk4b3IvjOQf4ZCAYv10HEjtVVvH695sFxQ3ht7VcL8xukOvWlWT21p4zs31bzMx0kuZAz0373f2Dw49KHVKAqM5HPMYuC3w0nasBZCZAsBRO6pB4C4kGruZCDmbS3RogcLbyck92utGqxZA3s0oPepLHWuAZDZD")
    ]

    # set up database
    db_commands.close_session()
    db_commands.clear_db()

    db_commands.create_db()

    def createUser(userID, accessToken):
        test_client = app.test_client()

        socket_client = socketio.test_client(app)
        socket_client.get_received()

        h = GraphHelperFuns.hacky_login(userID, accessToken)
        test_client.post('/v1/setSession', data=json.dumps({'h':h}))

        socket_client.emit('set session', {'h':h, 'userID':userID})
        recvd = socket_client.get_received()

        assert len(recvd) == 1

        assert recvd[0]['name'] == 'New'

        assert recvd[0]['args'] == [None]

        return test_client, socket_client

    # set up users
    test_clients = []
    socket_clients = []
    for userID, accessToken in users:
        test_client, socket_client = createUser(userID, accessToken)
        GraphHelperFuns.setRadiusMax(userID, test_client)
        GraphHelperFuns.setTimeMax(userID, test_client)
        test_clients.append(test_client)
        socket_clients.append(socket_client)

    my_test_client = app.test_client()
    my_socket_client = socketio.test_client(app)
    myUserID = UserHelperFuns.createUser1(my_test_client, my_socket_client)
    GraphHelperFuns.setRadiusMax(myUserID, my_test_client)
    GraphHelperFuns.setTimeMax(myUserID, my_test_client)

    UserHelperFuns.postTags(my_test_client, myUserID, ['AI','Footbal','Engineer'])

    UserHelperFuns.postTags(test_clients[0], users[0][0], ['','',''])

    UserHelperFuns.postTags(test_clients[1], users[1][0], ['','',''])

    UserHelperFuns.postTags(test_clients[2], users[2][0], ['Football','Engineering','Spanish'])

    # Request
    UserHelperFuns.postTags(test_clients[3], users[3][0], ['AI','ML','NLP'])

    # Request
    UserHelperFuns.postTags(test_clients[4], users[4][0], ['','',''])

    # Long Distance Chat
    UserHelperFuns.postTags(test_clients[5], users[5][0], ['','',''])

    UserHelperFuns.postTags(test_clients[6], users[6][0], ['Football','Engineering','Spanish'])

    UserHelperFuns.postTags(test_clients[7], users[7][0], ['OOSE','Observer','Courtouis'])

    UserHelperFuns.postTags(test_clients[8], users[8][0], ['Economics','Supply','Demand'])

    # Chat 
    UserHelperFuns.postTags(test_clients[9], users[9][0], ['Cooking','Pwasta','Beef Wellington'])

    # one hop
    # have chat with this person
    GraphHelperFuns.postNearby(my_test_client, myUserID, users[0][0])
    GraphHelperFuns.postNearby(test_clients[0], users[0][0], myUserID)

    GraphHelperFuns.postNearby(my_test_client, myUserID, users[1][0])
    GraphHelperFuns.postNearby(test_clients[1], users[1][0], myUserID)

    GraphHelperFuns.postNearby(my_test_client, myUserID, users[2][0])
    GraphHelperFuns.postNearby(test_clients[2], users[2][0], myUserID)

    # decline this request
    GraphHelperFuns.postNearby(my_test_client, myUserID, users[3][0])
    GraphHelperFuns.postNearby(test_clients[3], users[3][0], myUserID)

    GraphHelperFuns.postNearby(my_test_client, myUserID, users[4][0])
    GraphHelperFuns.postNearby(test_clients[4], users[4][0], myUserID)

    data = GraphHelperFuns.getNearbyUsers(my_test_client, myUserID)
    sid = data['sid']

    msg = "Wanna talk?"
    UserHelperFuns.checkIfConnected(my_test_client, myUserID, users[0][0], connected=False, position=0, sid=sid)
    RequestHelperFuns.sendRequest(my_test_client, myUserID, users[0][0], msg, position=0, sid=10, success=False)
    RequestHelperFuns.sendRequest(my_test_client, myUserID, users[0][0], msg, position=0, sid=sid, success=False)
    requestID = RequestHelperFuns.getReceivedRequest(socket_clients[0], myUserID, users[0][0], msg=msg)
    my_socket_client.get_received()

    data = RequestHelperFuns.acceptRequest(test_clients[0], users[0][0], requestID)
    chatID = ChatHelperFuns.getChatIDAcceptRequest(my_socket_client, myUserID, msg=msg)
    ChatHelperFuns.sendMessage(test_clients[0], users[0][0], chatID, "What are the physical implications of infinity over infinity?")

    msg = "I really wanna talk to you"
    UserHelperFuns.checkIfConnected(test_clients[3], users[3][0], myUserID, connected=False)
    RequestHelperFuns.sendRequest(test_clients[3], users[3][0], myUserID, msg)

    # block this request
    msg = "I'm the trench coat guy in the corner"
    UserHelperFuns.checkIfConnected(test_clients[4], users[4][0], myUserID, connected=False)
    RequestHelperFuns.sendRequest(test_clients[4], users[4][0], myUserID, msg)

    UserHelperFuns.checkIfConnected(my_test_client, myUserID, users[2][0], connected=False, position=0, sid=sid)
    UserHelperFuns.checkIfConnected(my_test_client, myUserID, users[3][0], connected=False, position=0, sid=sid)
    UserHelperFuns.checkIfConnected(my_test_client, myUserID, users[4][0], connected=False, position=0, sid=sid)

    # have chat with person, remove this nearby edges, add longdistance permission
    GraphHelperFuns.postNearby(my_test_client, myUserID, users[5][0])
    GraphHelperFuns.postNearby(test_clients[5], users[5][0], myUserID)
    data = GraphHelperFuns.getNearbyUsers(my_test_client, myUserID)
    sid = data['sid']

    msg = "Let's go to Whole Foods!"
    UserHelperFuns.checkIfConnected(my_test_client, myUserID, users[5][0], connected=False, position=0, sid=sid)
    RequestHelperFuns.sendRequest(my_test_client, myUserID, users[5][0], msg, position=0, sid=sid)
    requestID = RequestHelperFuns.getReceivedRequest(socket_clients[5], myUserID, users[5][0], msg=msg)
    my_socket_client.get_received()

    data = RequestHelperFuns.acceptRequest(test_clients[5], users[5][0], requestID)

    chatID = ChatHelperFuns.getChatIDAcceptRequest(my_socket_client, myUserID, msg=msg)

    ChatHelperFuns.sendMessage(test_clients[5], users[5][0], chatID, "Yeah, let's do it")

    NearbyUsers.NearbyUsers.query.filter_by(userID=myUserID).filter_by(otherUserID=users[5][0]).delete()
    NearbyUsers.NearbyUsers.query.filter_by(otherUserID=myUserID).filter_by(userID=users[5][0]).delete()
    db.session.commit()

    UserHelperFuns.postLongDistance(test_clients[5], users[5][0], myUserID)

    # two hops
    GraphHelperFuns.postNearby(test_clients[6], users[6][0], users[0][0])
    GraphHelperFuns.postNearby(test_clients[0], users[0][0], users[6][0])

    GraphHelperFuns.postNearby(test_clients[7], users[7][0], users[0][0])
    GraphHelperFuns.postNearby(test_clients[0], users[0][0], users[7][0])

    GraphHelperFuns.postNearby(test_clients[7], users[7][0], users[1][0])
    GraphHelperFuns.postNearby(test_clients[1], users[1][0], users[7][0])

    GraphHelperFuns.postNearby(test_clients[8], users[8][0], users[1][0])
    GraphHelperFuns.postNearby(test_clients[1], users[1][0], users[8][0])

    GraphHelperFuns.postNearby(test_clients[8], users[8][0], users[2][0])
    GraphHelperFuns.postNearby(test_clients[2], users[2][0], users[8][0])

    UserHelperFuns.checkIfConnected(my_test_client, myUserID, users[6][0], connected=False, position=0, sid=sid)
    UserHelperFuns.checkIfConnected(my_test_client, myUserID, users[7][0], connected=False, position=0, sid=sid)

    # have chat with this person
    GraphHelperFuns.postNearby(test_clients[9], users[9][0], users[2][0])
    GraphHelperFuns.postNearby(test_clients[2], users[2][0], users[9][0])

    data = GraphHelperFuns.getNearbyUsers(my_test_client, myUserID)
    sid = data['sid']

    msg = "Do you need help on Physics?"
    UserHelperFuns.checkIfConnected(my_test_client, myUserID, users[9][0], connected=False, position=0, sid=sid)
    RequestHelperFuns.sendRequest(my_test_client, myUserID, users[9][0], msg, position=0, sid=sid)
    requestID = RequestHelperFuns.getReceivedRequest(socket_clients[9], myUserID, users[9][0], msg=msg)
    my_socket_client.get_received()

    data = RequestHelperFuns.acceptRequest(test_clients[9], users[9][0], requestID)

    chatID = ChatHelperFuns.getChatIDAcceptRequest(my_socket_client, myUserID, msg=msg)

    ChatHelperFuns.sendMessage(test_clients[9], users[9][0], chatID, "What are the physical implications of infinity over infinity?")

    GraphHelperFuns.setRadius(myUserID, my_test_client, 1)
    GraphHelperFuns.setTime(myUserID, my_test_client, 6)

    UserHelperFuns.checkIfConnected(my_test_client, myUserID, users[8][0], connected=False, position=0, sid=10, success=False)

    my_test_client.post('v1/logout')
    for test_client in test_clients:
        test_client.post('v1/logout')

    assert db_commands.close_session() == "DB Session Ended"
    assert db_commands.clear_db() == "DB Tables dropped"

def testErrorCheckingGetTags():
    test_client, test_client2, socket_client, socket_client2, userID1, userID2 = UserHelperFuns.startTwoUserTest()

    response = test_client.get('/v1/tags/' + "NotaLong" + '/' + str(userID2), data=json.dumps(dict(userID=userID1, userID2=userID2)))
    assert response.status != '200 OK'

    response = test_client.get('/v1/tags/' + str(userID1) + '/' + "NotaLong", data=json.dumps(dict(userID=userID1, userID2=userID2)))
    assert response.status != '200 OK'

    response = test_client.get('/v1/tags/' + "NotaLong" + '/' + "NotaLong", data=json.dumps(dict(userID=userID1, userID2=userID2)))
    assert response.status != '200 OK'

    response = test_client.get('/v1/tags/' + str(userID1) + '/' + "42", data=json.dumps(dict(userID=userID1, userID2=userID2)))
    assert response.status != '200 OK'

    UserHelperFuns.getTags(test_client, userID1, userID2)

    socket_client.emit('remove user', {'userID':userID1})
    test_client.post('v1/logout')
    socket_client2.emit('remove user', {'userID':userID2})
    test_client2.post('v1/logout')
    UserHelperFuns.getTags(test_client, userID1, userID2, success=False)
    assert db_commands.close_session() == "DB Session Ended"
    assert db_commands.clear_db() == "DB Tables dropped"

def testErrorCheckingPostTags():
    test_client, test_client2, socket_client, socket_client2, userID1, userID2 = UserHelperFuns.startTwoUserTest()

    response = test_client.post('v1/tags', data=json.dumps({'userID':userID1, 'tags':['','','']}))

    response = test_client.post('v1/tags', data={'test':42})
    assert response.status != '200 OK'

    response = test_client.post('v1/tags', data=json.dumps({'userID':userID1}))
    assert response.status != '200 OK'

    response = test_client.post('v1/tags', data=json.dumps({'tags':['','','']}))
    assert response.status != '200 OK'

    response = test_client.post('v1/tags', data=json.dumps({}))
    assert response.status != '200 OK'

    response = test_client.post('v1/tags', data=json.dumps({'userID':"NotaLong", 'tags':"NotaList"}))
    assert response.status != '200 OK'

    response = test_client.post('v1/tags', data=json.dumps({'userID':"NotaLong", 'tags':['','','']}))
    assert response.status != '200 OK'

    response = test_client.post('v1/tags', data=json.dumps({'userID':userID1, 'tags':"NotaLong"}))
    assert response.status != '200 OK'

    UserHelperFuns.postTags(test_client, userID1, ['','','',''], success=False)

    UserHelperFuns.postTags(test_client, userID1, ['',''], success=False)

    socket_client.emit('remove user', {'userID':userID1})
    test_client.post('v1/logout')
    socket_client2.emit('remove user', {'userID':userID2})
    test_client2.post('v1/logout')
    UserHelperFuns.postTags(test_client, userID1, ['','',''], success=False)
    assert db_commands.close_session() == "DB Session Ended"
    assert db_commands.clear_db() == "DB Tables dropped"
    