import React, { DeviceEventEmitter, NativeEventEmitter, NativeModules } from 'react-native';
import { EventRegister } from 'react-native-event-listeners';
import Model from './Model';
var JSONbig = require('json-bigint');

let RCTMultipeerConnectivity = NativeModules.MultipeerConnectivity; 

class BluetoothModel extends Model {
  
  constructor() {
    super();
    console.log('constructed');
    const myModuleEvt = new NativeEventEmitter(NativeModules.MultipeerConnectivity);
    this._peers = {};

    var peerFound = myModuleEvt.addListener(
      'RCTMultipeerConnectivityPeerFound',
      ((event) => {
        console.log('Peer Found');
        console.log(event.peer);
        var peer = this.newPeer(event.peer.id, event.peer.discoverInfo.name);
        if (!peer) {
          return;
        }
        this._peers[peer.id] = peer;
        EventRegister.emit('peerFound', peer);
      }).bind(this));
      
    var peerLost = myModuleEvt.addListener(
      'RCTMultipeerConnectivityPeerLost',
      ((event) => {
        console.log('Peer Lost');
        console.log(event.peer);
        var peer = this._peers[event.peer.id];
        if (!peer) {
          return;
        }
        delete this._peers[event.peer.id];
        EventRegister.emit('peerLost', { id: peer.id });
      }).bind(this));
    
    var invited = myModuleEvt.addListener(
      'RCTMultipeerConnectivityInviteReceived',
      ((event) => {
        console.log('Invite Received');
        event.sender = this._peers[event.sender.id];
        EventRegister.emit('invite', event);
      }).bind(this));
  }

  setPeerID() {
    peerId = this.user.getUserID();
    name = this.user.getName()[0];

    if (!peerId) {
      throw 'The userId is null';
    }
    if (!name) {
      throw 'The name is null';
    }

    RCTMultipeerConnectivity.setPeerId(peerId, (() => {
      console.log('Peer Id');
      RCTMultipeerConnectivity.advertise("channel1", {"name":name});
      RCTMultipeerConnectivity.browse("channel1");
    }).bind(this));
  }
  
  newPeer(id, name) {
    return {"id":id, "name":name};
  }

  getNearbyUsers() {
    return this._peers;
  }
  
  stop() {
    RCTMultipeerConnectivity.stop(()=>{});
  }
  
}

export var bluetoothModel = new BluetoothModel();
