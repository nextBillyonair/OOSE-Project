import React from 'react';
import { StackNavigator } from 'react-navigation';
import { EventRegister } from 'react-native-event-listeners';
import { Icon } from 'react-native-elements';

import SettingsView from './SettingsView';
import BlockedUsersView from './BlockedUsersView';
import {HEADER_CONTENT_COLOR, HEADER_COLOR} from '../Colors.js';
import {styles} from '../StyleConstants.js';


const SettingsTab = StackNavigator({
  Settings: {
    screen: SettingsView, 
    navigationOptions: {
      title: "Settings",
      headerBackTitleStyle: {
        color:HEADER_CONTENT_COLOR
      }, 
      headerStyle: { 
        backgroundColor: HEADER_COLOR 
      },
      headerTitleStyle: { 
        color: HEADER_CONTENT_COLOR 
      },
      headerTintColor: HEADER_CONTENT_COLOR,
      headerRight:
        <Icon
          name='ios-refresh'
          type='ionicon'
          color={HEADER_CONTENT_COLOR}
          size={40}
          iconStyle={styles.headerRightIcon}
          underlayColor={HEADER_COLOR}
          onPress={() => {EventRegister.emit('refresh settings');}} 
        />, 
    }
  },
  BlockedUsers: {
    screen: BlockedUsersView, 
    navigationOptions: {
      title: "Blocked Users",
      headerBackTitleStyle: {
        color:HEADER_CONTENT_COLOR 
      },
      headerStyle: { 
        backgroundColor: HEADER_COLOR 
      },
      headerTitleStyle: { color: HEADER_CONTENT_COLOR },
      headerTintColor: HEADER_CONTENT_COLOR,
      headerRight:
        <Icon
          name='ios-refresh'
          type='ionicon'
          color={HEADER_CONTENT_COLOR}
          size={40}
          iconStyle={styles.headerRightIcon}
          underlayColor={HEADER_COLOR}
          onPress={() => {EventRegister.emit('refresh blocked users');}} 
        />, 
    }
  }
});

export default SettingsTab;
