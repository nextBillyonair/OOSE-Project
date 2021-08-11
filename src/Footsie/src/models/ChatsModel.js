import Model from './Model';

class ChatsModel extends Model {

  getChats(callback) {
    var url = this.url + 'v1/chats/' + this.user.userID;
    this.GETRequest(url, callback);
  }

  getActiveUsers(callback) {
    this.GETRequest(this.url + 'v1/usersMsgd', callback);
  }

}

export var chatsModel = new ChatsModel();
