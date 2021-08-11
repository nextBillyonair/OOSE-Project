import Model from './Model';
import {socketModel} from './SocketModel';

class ChatModel extends Model {

  getChat(chatID, callback) {
    var url = this.url + 'v1/chat/' + this.user.userID + '/' + chatID;
    this.GETRequest(url, callback);
  }

  getIsActive(chatID, callback) {
    var url = this.url + 'v1/isactive/' + this.user.userID + '/' + chatID;
    this.GETRequest(url, callback);
  }

  sendMessage(chatID, data, callback) {
    this.POSTRequest(this.url + 'v1/sendMessage', {
      chatID:chatID,
      msg: data
    }, callback);
  }

  editName(chatID, newName, callback) {
    this.POSTRequest(this.url + 'v1/chatname', {
      chatID:chatID,
      name: newName
    }, callback);
  }

  seenChat(chatID, callback) {
    if (!callback) {
      callback = () => {};
    }

    var url = this.url + 'v1/seenChat/' + this.user.userID + '/' + chatID;

    fetch(url, {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      }
    }).then((response) => JSONbig.parse(response._bodyText))
      .then((response) => {callback(response, null);})
      .catch((error) => {callback(null, error); });
  }

}

export var chatModel = new ChatModel();
