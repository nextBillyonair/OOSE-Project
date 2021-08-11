import React, { Component } from 'react';
import {
  Text, View, ListView, 
  ActivityIndicator, AlertIOS
} from 'react-native';
import { EventRegister } from 'react-native-event-listeners';
import { Button, ListItem, Avatar } from 'react-native-elements';
import PopupDialog, { DialogTitle, ScaleAnimation } from 'react-native-popup-dialog';

import { fbModel } from '../models/FBModel';
import { usersModel} from '../models/UsersModel';
import {
  DISMISS_COLOR, ACCEPT_COLOR, 
  AVATAR_BACKGROUND_COLOR,
} from '../Colors.js';
import {
  styles, isiPhone5, 
  isiPhone, isiPhonePlus, 
} from '../StyleConstants';

const scaleAnimation =  new ScaleAnimation();

var blockedUsersList = [];

export default class BlockedUsersView extends Component {
  
  constructor(props, context) {
    super(props, context);

    this.ds = new ListView.DataSource({rowHasChanged: (r1, r2) => r1 !== r2});

    this.state = {
      dataSource: this.ds.cloneWithRows(blockedUsersList),
      user:{},
      text:'',
      loading:false,
    };

    this.refreshListener = EventRegister.addEventListener('refresh blocked users', this.refresh.bind(this));
  }

  componentDidMount() {
    this.refresh();
  }

  componentWillUnmount() {
    blockedUsersList = [];
    EventRegister.removeEventListener(this.refreshListener);
  }

  refresh() {
    if (!this.state.loading) {
      usersModel.getBlockedUsers(this.getBlockedUsers.bind(this));
    }
  }

  getBlockedUsers(res, err) {
    if (!res && !err) {
      return;
    }
    
    if (err || !res) {
      AlertIOS.alert(
         'Alert',
         'Could Not Get Blocked Users!'
      );
      return;
    }
    
    blockedUsersList = res;
    userIds = []
    for (var i = 0; i < res.length; i++) {
      userID = res[i]['userID'];
      userIds.push(userID.toString());
    }

    fbModel.getFBPPList(userIds, (err, res) => {
      for (var i = 0; i < blockedUsersList.length; i++) {
        if (blockedUsersList[i]['userID'].toString() == res.id) {
          blockedUsersList[i]['avatar_url'] = res.picture.data.url;
          break;
        }
      }
      this.setState({dataSource:this.ds.cloneWithRows(blockedUsersList)});
    });
  }

  showUnblockUser(l) {
    this.state.user = l;
    this.state.text = l.message
    this.setState(this.state);
    this.popupDialog.show();
  }

  unblockUser() {

    this.setState({
      loading: true
    });

    usersModel.unblockUser(this.state.user.userID.toString(), (res, err) => {

      this.setState({loading:false});
      if (!err && !res) {
        return;
      }

      if (err || !res) {
        AlertIOS.alert(
         'Alert',
         'Could Not Unblock User!'
        );
      }

      for (var i =0; i < blockedUsersList.length; i++) {
        if (blockedUsersList[i]['userID'].toString() == this.state.user.userID) {
          blockedUsersList.splice(i, 1);
          break;
        }
      }
      this.setState({
        dataSource:this.ds.cloneWithRows(blockedUsersList)
      });
      this.popupDialog.dismiss();
    });

  }

  dismissPopup() {
    this.popupDialog.dismiss();
  }

  renderRow(l, i) {
    return (<ListItem
            roundAvatar
            avatar={{uri:l.avatar_url}}
            key={i}
            title={"Blocked User"}
            onPress={this.showUnblockUser.bind(this, l)}
            activeOpacity={0.7}
            rightIcon={{name:'ios-eye-off',type:'ionicon'}}
          />)
  }

  getButtonWidth(){
    return {width:'40%'}
  }

  getAvatarHeight(){
    return '70%'
  }

  getPopupHeight() {
    if (isiPhone5) {
      return .45
    } if (isiPhone) {
      return .40
    } else if (isiPhonePlus) {
      return .37
    } else {
      return .33
    }
  }

  render() {

    if (blockedUsersList.length == 0) {
      var view = (
        <View style={styles.container}>
            <Text style={styles.text}>
              You have not blocked anyone
            </Text>
          </View>
        );
    } else {
      var view = (
        <View style={styles.container}>
          <ListView contentContainerStyle={styles.list}
            dataSource={this.state.dataSource}
            renderRow={(l,i) => 
              <ListItem style={styles.item}
              roundAvatar
              avatar={<Avatar
                  rounded
                  large
                  source={l.avatar_url && {uri: l.avatar_url}}
                  title={l.name}
                />}
              key={i}
              onPress={() => this.showUnblockUser(l)}
              activeOpacity={0.7}
              hideChevron={true}
              />
            }
          />
          </View>
        );
    }

    return (
      <View style={styles.fullscreen}>
        {view}
          <PopupDialog
          dialogTitle={<DialogTitle title="Unblock User" />}
          dialogAnimation={scaleAnimation}
          width={0.9}
          height={this.getPopupHeight()}
          dialogStyle={[styles.popupBase, {bottom:'20%'}]}
          ref={(popupDialog) => { this.popupDialog = popupDialog; }}
          >
          <View>
            <View style={[{ height:this.getAvatarHeight()}, styles.center]}>
              <Avatar style={{backgroundColor:AVATAR_BACKGROUND_COLOR}}
                rounded
                xlarge
                source={this.state.user.avatar_url && {uri: this.state.user.avatar_url}}
              />
            </View>
            <View style={styles.popupTwoButtons}>
              <Button
                raised
                rounded
                title='Cancel'
                fontSize={16}
                fontWeight="bold"
                containerViewStyle={this.getButtonWidth()}
                backgroundColor={DISMISS_COLOR}
                onPress={this.dismissPopup.bind(this)} />
              <Button
                raised
                rounded
                title='Unblock'
                fontSize={16}
                fontWeight="bold"
                containerViewStyle={this.getButtonWidth()}
                backgroundColor={ACCEPT_COLOR}
                onPress={this.unblockUser.bind(this)} />
            </View>
          </View>
        </PopupDialog>
        {
          this.state.loading &&
          <View style={styles.loading}>
            <ActivityIndicator size='large' />
          </View>
        }
        </View>
    );
  }
}
