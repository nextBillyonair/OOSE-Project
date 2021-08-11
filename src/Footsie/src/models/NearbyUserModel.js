import { AlertIOS } from 'react-native';

import { EventRegister } from 'react-native-event-listeners';
import Model from './Model';
import { usersModel } from './UsersModel';
import { bluetoothModel } from './BluetoothModel';
import { fbModel } from './FBModel';
import { graphModel } from './GraphModel';

const timer = require('react-native-timer');

const filteredList = {};
const nearbyUsers = {};

export default class NearbyUserModel extends Model {
  
  constructor(updateNewPeer, updateLostPeer, maxPeople) {
    super();

    this.updateNewPeer = updateNewPeer;
    this.updateLostPeer = updateLostPeer;
    this.maxPeople = maxPeople;
    this.sid = null;
    this.newPeerListener = EventRegister.addEventListener('peerFound', this.onPeerFound.bind(this));;
    this.peerLostListener = EventRegister.addEventListener('peerLost', this.onPeerLost.bind(this));;
    this.blockUserListener = EventRegister.addEventListener('block user from chat', this.blockUserUpdate.bind(this));
    this.newRequestListener = EventRegister.addEventListener('new request', this.newRequest.bind(this));
    this.acceptRequestListener = EventRegister.addEventListener('accept request', this.acceptRequest.bind(this));
    this.localAcceptRequestListener = EventRegister.addEventListener('local accept request', this.acceptRequest.bind(this));
    this.processed = true;
  }

  unmount() {

    for (id in bluetoothModel.getNearbyUsers()) {
      graphModel.addNewEdge(id);
    }

    bluetoothModel.stop();
    this.clearNearbyUsers();
    
    EventRegister.removeEventListener(this.newPeerListener);
    EventRegister.removeEventListener(this.peerLostListener);
    EventRegister.removeEventListener(this.blockUserListener);
    EventRegister.removeEventListener(this.newRequestListener);
    EventRegister.removeEventListener(this.acceptRequestListener);
    EventRegister.removeEventListener(this.localAcceptRequestListener);
  }

  refresh() {
    this.processed = false;
    this.clearFilterdList();
    this.clearNearbyUsers();

    bluetoothModel.setPeerID();

    usersModel.getFilteredUsers(((res, err) => {

      if (err || !res) {
        AlertIOS.alert(
         'Alert',
         'Could Not Get Filtered Users!'
        );
      }

      filteredList = {};

      for (var i = 0; i < res.length; i++) {
        filteredList[res[i].id] = "Filter";
      } 

      this.getNearbyUsers();

    }).bind(this));
  }

  setMaxPeople(maxPeople) {
    this.maxPeople = maxPeople;
  }

  clearFilterdList() {
    filteredList = null;
  }

  clearNearbyUsers() {
    for (id in nearbyUsers) {
      timer.clearTimeout(id.toString());
    }
    nearbyUsers = null;
  }

  getNearbyUsersCb(res, err) {
    console.log(res, err);
    if (err || !res) {
      AlertIOS.alert(
       'Alert',
       'Could Not Get Other Nearby Users!'
      );
      return;
    }

    this.sid = res.sid;

    nearbyUsers = {};

    var offset = new Date().getTimezoneOffset();
    var ids = [];
    
    for (var i = 0; i < res.users.length; i++) {
      var user = res.users[i];
      var id = user.id;
      var time = user.time;
      this.addNewNearbyUser(id, time);
      this.addNewUser(id);
    }

    for (id in bluetoothModel.getNearbyUsers()) {
      this.onPeerFound(bluetoothModel.getNearbyUsers()[id], true);
    }
    this.processed = true;

  }

  endOfTimer(id) {
    id = id.toString();
    return () => {

      delete nearbyUsers[id];
      if (id in bluetoothModel.getNearbyUsers()) {
        graphModel.addNewEdge(id, this.addEdgeInGraph.bind(this));
      } else {
        this.updateLostPeer({id:id});
      }
    };
  }

  getNearbyUsers() {
    graphModel.getNearbyUsers(this.maxPeople, this.getNearbyUsersCb.bind(this));
  }

  blockUserUpdate(data) {
    var userID = data.userID;
    filteredList[userID] = "Filter";
    this.updateFilteredUsers(userID);
  }

  newRequest(request) {
    request = request.request;
    var userID = request.fromUserID;
    filteredList[userID] = "Filter";
    this.updateFilteredUsers(userID);
  }

  acceptRequest(data) {
    console.log(data);
    var id = data.userID;
    delete filteredList[id];
    this.addNewUser(id);
  }

  addNewUser(id) {

    id = id.toString();
    if (filteredList == null) {
      return;
    }

    if (nearbyUsers != null && id in nearbyUsers) {
      if (filteredList != null && !(id in filteredList)) {
        var nearbyUser = nearbyUsers[id];
        this.updateNewPeer(nearbyUser);
      }
      return;
    }

    if (id in bluetoothModel.getNearbyUsers()) {
      if (filteredList != null && !(id in filteredList)) {
        var nearbyUser = bluetoothModel.getNearbyUsers()[id];
        this.updateNewPeer(nearbyUser);
      }
      return;
    }
  }


  savePictureUrl(id, url) {
    if (nearbyUsers == null) {
      return;
    }
    id = id.toString();
    if (id in nearbyUsers) {
      nearbyUsers[id]['avatar_url'] = url;
    }
    if (id in bluetoothModel.getNearbyUsers()) {
      bluetoothModel.getNearbyUsers()[id]['avatar_url'] = url;
    }
  }

  saveTags(id, tags) {
    if (nearbyUsers == null) {
      return;
    }
    id = id.toString();
    if (id in nearbyUsers) {
      nearbyUsers[id]['tags'] = tags;
    }
    if (id in bluetoothModel.getNearbyUsers()) {
      bluetoothModel.getNearbyUsers()[id]['tags'] = tags;
    }
  }

  updateFilteredUsers(id) {
    id = id.toString();
    filteredList[id] = "Filter";
    this.updateLostPeer({id:id})
  }

  addEdgeInGraph(res, err) {
    if (err || !res) {
      return;
    }

    this.addNewNearbyUser(res.id, res.time);
    this.addNewUser(res.id);
  }

  addNewNearbyUser(id, time) {
    if (nearbyUsers == null) {
      return;
    }
    id = id.toString();
    nearbyUsers[id] = {id:id, time:time};

    time = new Date(Date.parse(time));
    var currentTime = new Date();
    timer.setTimeout(id.toString(), this.endOfTimer(id).bind(this), time - currentTime);
  }

  onPeerFound(data, processed=false) {

    if (!this.processed && !processed) {
      return;
    }

    graphModel.addNewEdge(data.id, this.addEdgeInGraph.bind(this));

    if (data.id in nearbyUsers) {
      return;
    }

    this.addNewUser(data.id);
  }

  onPeerLost(data) {

    if (!this.processed) {
      return;
    }

    graphModel.addNewEdge(data.id, this.addEdgeInGraph.bind(this));
    if (data.id in nearbyUsers) {
      return;
    }
    this.updateLostPeer(data);
  }

}
