'use strict';

import React, { Component } from 'react';
import {
  View, TabBarIOS
} from 'react-native';
import { EventRegister } from 'react-native-event-listeners';
import Icon from 'react-native-vector-icons/Ionicons';

import ChatsTab from './ChatsTab';
import DiscoverTab from './DiscoverTab';
import SettingsTab from './SettingsTab';
import {TAB_UNSELECTED_COLOR, 
  TAB_SELECTED_COLOR, 
  TAB_COLOR,
  BADGE_COLOR
} from '../Colors.js';
import { styles } from '../StyleConstants.js';

class TabBarView extends Component {

  constructor() {
    super()
    this.state = {
      selectedTab: 'discoverTab',
      notifCount: 0,
    };

    this.chatID = null;

    this.newRequestListener = EventRegister.addEventListener('new request', this.updateNotif.bind(this));
    this.acceptRequestListener = EventRegister.addEventListener('accept request', this.updateNotif.bind(this));
    this.sendMessageListener = EventRegister.addEventListener('send message', this.updateNotif.bind(this));
    this.openChatListener = EventRegister.addEventListener('openChat', this.openChat.bind(this));
    this.closeChatListener = EventRegister.addEventListener('closeChat', this.closeChat.bind(this));

  }

  componentWillUnmount() {
    EventRegister.removeEventListener(this.newChatListener);
    EventRegister.removeEventListener(this.newRequestListener);
    EventRegister.removeEventListener(this.acceptRequestListener);
    EventRegister.removeEventListener(this.sendMessageListener);
    EventRegister.removeEventListener(this.openChatListener);
    EventRegister.removeEventListener(this.closeChatListener);
  }

  closeChat() {
    this.chatID = null;
    if (this.state.selectedTab == "chatsTab") { 
      this.setState({
        notifCount: 0
      });
    }
  }

  openChat(chatID) {
    this.chatID = chatID;
  }

  updateNotif(data) {
    if (this.chatID != null) {
      if (!(data.chatID && data.chatID == this.chatID)) {
        this.setState({
          notifCount: this.state.notifCount + 1
        });
      }
    } else if (this.state.selectedTab != "chatsTab") {
      this.setState({
        notifCount: this.state.notifCount + 1
      });
    }
  }

  _renderDiscover() {
    return (
      <View style={styles.tabContent}>
      <DiscoverTab/>
      </View>
    );
  }
  _renderChats() {
    return (
      <View style={styles.tabContent}>
      <ChatsTab/>
      </View>
    );
  }
  _renderSettings() {
    return (
      <View style={styles.tabContent}>
      <SettingsTab/>
      </View>
    );
  }

  render() {
    return (
      <TabBarIOS
        unselectedItemTintColor={TAB_UNSELECTED_COLOR}
        tintColor={TAB_SELECTED_COLOR}
        barTintColor={TAB_COLOR}>
        <Icon.TabBarItemIOS
        iconName="ios-people"
        selected={this.state.selectedTab === 'discoverTab'}
        onPress={() => {
            this.setState({
              selectedTab: 'discoverTab',
            });
          }}
        >
       {this._renderDiscover()}
        </Icon.TabBarItemIOS>

        <Icon.TabBarItemIOS
        iconName="ios-chatbubbles"
        badge={this.state.notifCount > 0 ? this.state.notifCount : undefined}
        badgeColor={BADGE_COLOR}
        selected={this.state.selectedTab === 'chatsTab'}
        onPress={() => {
            this.setState({
              notifCount: 0,
              selectedTab: 'chatsTab',
            });
          }}
        >
        {this._renderChats()}
        </Icon.TabBarItemIOS>
        <Icon.TabBarItemIOS
        iconName="ios-settings"
        selected={this.state.selectedTab === 'settingsTab'}
        onPress={() => {
            this.setState({
              selectedTab: 'settingsTab',
            });
          }}
        >
        {this._renderSettings()}
        </Icon.TabBarItemIOS>
            
      </TabBarIOS>
    );
  }

};

export default TabBarView;
