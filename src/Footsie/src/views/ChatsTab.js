import React from 'react';
import { EventRegister } from 'react-native-event-listeners';
import { StackNavigator } from 'react-navigation';
import { Icon } from 'react-native-elements';

import ChatsView from './ChatsView';
import ChatView from './ChatView';
import {HEADER_CONTENT_COLOR, HEADER_COLOR} from '../Colors.js';
import {styles} from '../StyleConstants.js';

const ChatsTab = StackNavigator({
  Chats: {
    screen: ChatsView, 
	  navigationOptions: {
      title: "Messages",
      headerRight:
        <Icon
          name='ios-refresh'
          type='ionicon'
          color={HEADER_CONTENT_COLOR}
          size={40}
          iconStyle={styles.headerRightIcon}
          underlayColor={HEADER_COLOR}
          onPress={() => {EventRegister.emit('refresh chats');}} 
        />, 
      headerBackTitleStyle: {
        color: HEADER_CONTENT_COLOR
      }, 
      headerStyle: { 
        backgroundColor: HEADER_COLOR 
      }, 
      headerTitleStyle: { 
        color: HEADER_CONTENT_COLOR
      },
    }
  },
  Chat: {
    screen: ChatView, 
	  navigationOptions: (state) => (
      {
        title: state.navigation.state.params.chatName, 
        headerRight:
          <Icon
            name='bars'
            type='font-awesome'
            color={HEADER_CONTENT_COLOR}
            iconStyle={styles.headerRightIcon}
            underlayColor={HEADER_COLOR}
            onPress={() => {EventRegister.emit('openMenu');}} 
          />, 
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
      }
    )
  }
});

export default ChatsTab;