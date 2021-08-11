import { user } from './User';
import {AlertIOS} from 'react-native';
var JSONbig = require('json-bigint');
import { url } from './SocketModel'
import { connectionListener } from './ConnectionListener';

import { fbModel } from './FBModel';
import { EventRegister } from 'react-native-event-listeners';

export default class Model {

  constructor() {
    this.user = user;
    this.url = url;
  }

  HTTPRequest(url, body, callback) {
    if (!callback) {
      callback = () => {};
    }

    if (!connectionListener.isConnected()) {
      AlertIOS.alert(
         'Alert',
         'Network Failure'
        );
      return;
    }

    fetch(url, body).then(
        (response) => {
            if (response.status == 401) {
              AlertIOS.alert(
                'Alert',
                'Something goofed. Login again!'
              );
              fbModel.logout(() => { EventRegister.emit('FBLogoutSuccess', null); });
            } else if (response.status == 404) {
              AlertIOS.alert(
                'Alert',
                JSONbig.parse(response._bodyText).error
              );
              callback(null, null);
            } else if (response.status >= 400) {
              callback(null, response);
            } else {
              callback(JSONbig.parse(response._bodyText), null);
            }
        })
      .catch(
        (error) => {
          console.log(error);
          AlertIOS.alert(
           'Alert',
           'Network Failure'
          );
          callback(null, null);
        });
  }

  GETRequest(url, callback) {

    this.HTTPRequest(url, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      }
    }, callback);

  }

  POSTRequest(url, body, callback) {

    body['userID'] = this.user.userID;

    this.HTTPRequest(url, {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body)
    }, callback);

  }
}