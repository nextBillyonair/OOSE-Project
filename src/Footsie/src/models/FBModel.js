import Model from './Model';

const FBSDK = require('react-native-fbsdk');
const {
  AccessToken,
  GraphRequest,
  GraphRequestManager,
  LoginManager
} = FBSDK;

class FBModel extends Model {

  login(cb) {
    return () => {
      FBSDK.LoginManager.logInWithReadPermissions(['public_profile']).then(
        function(result) {
          cb(null, result);
        },
        function(error) {
          cb(error, null);
        }
      );
    }
  }

  logout(cb) {
    LoginManager.logOut();
    cb();
  }

  getAccessToken(cb) {
    AccessToken.getCurrentAccessToken().then(cb);
  }

  getUserName(cb) {
    if (!this.user.accessToken) {
      throw 'AccessToken is null';
    }

    const infoRequest = new GraphRequest('/' + this.user.userID, {
      accessToken: '569248390133225|5a63dd2867cb4e221d393374ef469b0e',
      // accessToken: this.user.accessToken,
        parameters: {
          fields: {
            string: 'name'
          }
        }
      }, cb);

      new GraphRequestManager()
        .addRequest(infoRequest)
        .start();
  }

  getFBPP(userID, cb) {
    if (!this.user.accessToken) {
      throw 'AccessToken is null';
    }

    if (userID == "me") {
      userID = this.user.userID;
    }

    const infoRequest = new GraphRequest('/' + userID, {
      accessToken: '569248390133225|5a63dd2867cb4e221d393374ef469b0e',
      // accessToken: this.user.accessToken,
        parameters: {
          fields: {
            string: 'picture.type(large)'
          }
        }
      }, cb);

      new GraphRequestManager()
        .addRequest(infoRequest)
        .start();
  }

  getFBPPList(userIdLst, cb) {
    if (!this.user.accessToken) {
      throw 'AccessToken is null';
    }

    var manager = new GraphRequestManager();
    for (var i = 0; i < userIdLst.length; i++) {
      var userID = userIdLst[i];
      if (userID == "me") {
        userID = this.user.userID;
      }
      const infoRequest = new GraphRequest('/' + userID, {
        accessToken: '569248390133225|5a63dd2867cb4e221d393374ef469b0e',
        // accessToken: this.user.accessToken,
          parameters: {
            fields: {
              string: 'picture.type(large)'
            }
          }
        }, cb);
      manager = manager.addRequest(infoRequest);
    }

    if (userIdLst.length == 0) {
      return;
    }

    manager.start();
  }
}

export var fbModel = new FBModel();
