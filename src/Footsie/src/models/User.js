class User {

  constructor() {
    this.setToNull();
  }

  setToNull() {
    this.userID = null;
    this.accessToken = null;
    this.name = null;
  }

  setUserID(userID) {
    this.userID = userID;
  }

  setAccessToken(accessToken) {
    this.accessToken = accessToken;
  }

  setName(name) {
    this.name = name;
  }

  getUserID() {
    return this.userID;
  }

  getAccessToken() {
    return this.accessToken;
  }

  getName() {
    return this.name;
  }
}

export var user = new User();
