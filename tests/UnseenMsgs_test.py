import sys
sys.path.insert(0, './helperFunctions')  
import UserHelperFuns, RequestHelperFuns, ChatHelperFuns

def testUnseenMsgs():
    test_client, test_client2, socket_client, socket_client2, userID1, userID2 = UserHelperFuns.startTwoUserTest()

    # userID1 sends request
    RequestHelperFuns.sendRequest(test_client, userID1, userID2)

    # user2 get socketio msg
    requestID = RequestHelperFuns.getReceivedRequest(socket_client2, userID1, userID2)

    # check no current relations
    UserHelperFuns.checkRelation(userID1, userID2, "", 0)

    # accept request
    RequestHelperFuns.acceptRequest(test_client2, userID2, requestID)

    UserHelperFuns.checkNumSocketMessages(socket_client, 1)

    UserHelperFuns.checkNumSocketMessages(socket_client2, 0)

    # request not still in db
    RequestHelperFuns.checkNumRequests(requestID, 0)

    ChatHelperFuns.checkUnseenMsgs(test_client, userID1, True)

    data = test_client.post('v1/seenChat/' + str(userID1) + '/' + str(1))

    ChatHelperFuns.checkUnseenMsgs(test_client, userID1, False)

    UserHelperFuns.endTwoUserSession(test_client, test_client2, socket_client, socket_client2, userID1, userID2)