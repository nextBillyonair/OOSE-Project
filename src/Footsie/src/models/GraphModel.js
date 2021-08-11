import Model from './Model';

class GraphModel extends Model {

  saveRadius(radius, callback) {
    var url = this.url + 'v1/radius';
    this.POSTRequest(url, {radius:radius},callback);
  }

  saveTime(hours, callback) {
    var url = this.url + 'v1/time';
    this.POSTRequest(url, {hours:hours},callback);
  }

  getNearbyUsers(maxPeople, callback) {
    var url = this.url + 'v1/getNearbyUsers/' + this.user.userID + '/' + maxPeople;
    this.GETRequest(url, callback);
  }

  addNewEdge(otherUserID, callback) {
    this.POSTRequest(this.url + 'v1/isNearby', {
      userID2:otherUserID
    }, callback);
  }

}

export var graphModel = new GraphModel();
