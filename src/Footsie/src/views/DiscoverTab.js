import React, {Component}from 'react';
import {  StackNavigator } from 'react-navigation';
import { Icon, ButtonGroup } from 'react-native-elements';
import { EventRegister } from 'react-native-event-listeners';

import DiscoverView from './DiscoverView';
import ChatView from './ChatView';
import {HEADER_CONTENT_COLOR, HEADER_COLOR} from '../Colors.js';
import {styles} from '../StyleConstants.js';

class DiscoverButtonGroup extends Component {
  constructor() {
    super();
    this.state = {
      selectedIndex:0
    };
  }

  render() {
    return <ButtonGroup
        onPress={(selectedIndex) => {
          this.setState({selectedIndex});
          EventRegister.emit('ChangeDiscoverView', selectedIndex);
        }}
        selectedIndex={this.state.selectedIndex}
        buttons={['Tile', 'List']}
        containerStyle={{height: 25}}
        selectedBackgroundColor={'#DDDDDD'}
      />
  }
}

const DiscoverTab = StackNavigator({
  Discover: {
    screen: DiscoverView,
    navigationOptions: {
      title: "Discover",
      headerTitle: <DiscoverButtonGroup/>,
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
      headerLeft:
          <Icon
            name='bars'
            type='font-awesome'
            color={HEADER_CONTENT_COLOR}
            iconStyle={styles.headerLeftIcon}
            underlayColor={HEADER_COLOR}
            onPress={() => {EventRegister.emit('openDiscoverMenu');}} 
          />,
      headerRight:
        <Icon
          name='ios-refresh'
          type='ionicon'
          color={HEADER_CONTENT_COLOR}
          size={40}
          iconStyle={styles.headerRightIcon}
          underlayColor={HEADER_COLOR}
          onPress={() => {EventRegister.emit('refresh discover');}} 
        />, 
    }
  },
  Chat: {
    screen: ChatView, 
       navigationOptions: (state) => ({
        title: state.navigation.state.params.chatName, 
        headerBackTitleStyle:{
          color:HEADER_CONTENT_COLOR
        }, 
        headerStyle: { 
          backgroundColor: HEADER_COLOR 
        }, 
        headerTitleStyle: { 
          color: HEADER_CONTENT_COLOR 
        },
        headerRight:
          <Icon
            name='bars'
            type='font-awesome'
            color={HEADER_CONTENT_COLOR}
            iconStyle={styles.headerRightIcon}
            underlayColor={HEADER_COLOR}
            onPress={() => {EventRegister.emit('openMenu');}} 
          />, 
        headerTintColor: HEADER_CONTENT_COLOR,
      })
    } 
});

export default DiscoverTab;
