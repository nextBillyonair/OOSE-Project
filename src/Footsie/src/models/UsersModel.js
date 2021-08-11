import Model from './Model';

class UsersModel extends Model {

  blockUser(userID, callback) {
    var url = this.url + 'v1/block/' + userID
    this.POSTRequest(url, {}, callback);
  }

  unblockUser(userID, callback) {
    var url = this.url + 'v1/unblock/' + userID
    this.POSTRequest(url, {}, callback);
  }

  getBlockedUsers(callback) {
    var url = this.url + 'v1/block/' + this.user.userID;
    this.GETRequest(url, callback);
  }

  disableLongDistance(userID, callback) {
    var url = this.url + 'v1/notlongdistance/' + userID;
    this.POSTRequest(url, {}, callback);
  }

  enableLongDistance(userID, callback) {
    var url = this.url + 'v1/longdistance/' + userID;
    this.POSTRequest(url, {}, callback); 
  }

  isLongDistance(userID, callback) {
    var url = this.url + 'v1/longdistance/' + this.user.userID + '/' + userID;
    this.GETRequest(url, callback); 
  }

  getFilteredUsers(callback) {
    var url = this.url + 'v1/filtered/' + this.user.userID;
    this.GETRequest(url, callback);
  }

  getIsConnected(userID, sid, position, callback) {
    var url = this.url + 'v1/isConnected/' + this.user.userID + '/' + userID + '/' + sid + '/' + position;
    this.GETRequest(url, callback);
  }

  getUserSettings(callback) {
    var url = this.url + 'v1/userSettings/' + this.user.userID;
    this.GETRequest(url, callback);
  }

  postTags(tags, callback) {
    var url = this.url + 'v1/tags';
    this.POSTRequest(url, {"tags":tags}, callback);
  }

  getTags(userID, callback) {
    var url = this.url + 'v1/tags/' + this.user.userID + '/' + userID;
    this.GETRequest(url, callback);
  }

}

export var usersModel = new UsersModel();
