import Model from './Model';
import React from 'react-native';
import { socketModel } from './SocketModel';
import { EventRegister } from 'react-native-event-listeners';

class SettingsModel extends Model {

  constructor() {
    super();
    this.logoutListener = EventRegister.addEventListener('FBLogoutSuccess', this.logoutApp.bind(this));
  }

  logoutApp() {
    this.user.setToNull();
  }

  login(callback) {

    socketModel.connect();

    socketModel.login();
    
    this.POSTRequest(this.url + 'v1/login', {
      accessToken: this.user.accessToken
    }, callback);
  }

  logout(callback) {
    socketModel.disconnect();
    this.POSTRequest(this.url + 'v1/logout', {}, callback);
  }

  deactivateAccount(callback) {
    socketModel.disconnect();
    this.POSTRequest(this.url + 'v1/deactivate/' + this.user.userID, {}, callback);
  }

}

export var settingsModel = new SettingsModel();
