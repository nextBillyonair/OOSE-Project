import { EventRegister } from 'react-native-event-listeners';
import { user } from './User';
var JSONbig = require('json-bigint');

// export const url = 'http://172.16.121.98:8080/';
// export const url = 'http://10.194.89.143:8080/';
export const url = 'http://10.161.159.82:80/';
// export const url = 'http://localhost:5000/'

class SocketModel {
  constructor() {
    this.socketModel = require('socket.io-client')(url);

    this.socketModel.on('reconnect', function(data) {
      console.log(data);
      console.log('reconnect');
      if (user.userID != null) {
        this.login();
      }
    }.bind(this));

    // socket model on reconnect
    this.socketModel.on("New", function(data) {
      console.log(data);
      console.log('New user reg');
    });

    this.socketModel.on("accept request", function(data) {
      console.log('Accept request', data);
      EventRegister.emit('accept request', data);
    });

    this.socketModel.on("send request", function(data) {
        console.log('send request', data);
      EventRegister.emit('new request', data);
    });

    this.socketModel.on("send message", function(data) {
      console.log(data);
      EventRegister.emit('send message', data);
    });

  }

  login() {
    this.socketModel.emit('new user', {
      userID: user.userID,
      accessToken: user.accessToken
    });
  }

  connect() {
    this.socketModel.connect();
  }

  disconnect() {
    this.socketModel.disconnect();
  }

}

export var socketModel = new SocketModel();
