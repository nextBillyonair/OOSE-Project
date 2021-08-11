import Model from './Model';
import {socketModel} from './SocketModel';

class RequestModel extends Model {

  acceptRequest(requestID, callback) {
    this.POSTRequest(this.url + 'v1/acceptRequest', {
      requestID: requestID
    }, callback);
  }

  declineRequest(requestID, callback) {
    this.POSTRequest(this.url + 'v1/declineRequest', {
      requestID: requestID
    }, callback);
  }

  getRequests(callback) {
    var url  = this.url + 'v1/requests/' + this.user.userID;
    this.GETRequest(url, callback);
  }

  sendRequest(receiverID, data, sid, position, callback) {
    this.POSTRequest(this.url + 'v1/sendRequest', {
      receiverID: receiverID,
      msg: data,
      sid: sid,
      position: position
    }, callback);
  }

}

export var requestModel = new RequestModel();
