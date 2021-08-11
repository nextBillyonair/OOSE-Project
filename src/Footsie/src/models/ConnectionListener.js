import { NetInfo, AlertIOS } from 'react-native';

class ConnectionListener {

	constructor() {
	    this.connectionListener = NetInfo.addEventListener('connectionChange', this.updateConnectionStatus.bind(this));
	    this.connectionType = 'none';
  	}

  	updateConnectionStatus(connectionInfo) {
    	this.connectionType = connectionInfo.type;
  	}

  	getConnectionStatus() {
  		return this.connectionType;
  	}

  	isConnected() {
  		return this.connectionType != 'none';
  	}

}


export var connectionListener = new ConnectionListener();
