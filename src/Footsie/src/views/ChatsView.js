import React, { Component } from 'react';
import {
  Text, View, ListView,
  NavigatorIOS, TextInput, 
  AlertIOS, ActivityIndicator,
} from 'react-native';
import PopupDialog, { DialogTitle, ScaleAnimation } from 'react-native-popup-dialog';
import { StackNavigator } from 'react-navigation';
import { Button, List, ListItem, Avatar, Icon } from 'react-native-elements';
import { EventRegister } from 'react-native-event-listeners';

import { requestModel } from '../models/RequestModel';
import { usersModel } from '../models/UsersModel';
import { fbModel } from '../models/FBModel';
import { chatsModel } from '../models/ChatsModel';
import { user } from '../models/User';
import { connectionListener } from '../models/ConnectionListener';
import {
  DISMISS_COLOR, 
  ACCEPT_COLOR, BOLD_COLOR, 
  AVATAR_BACKGROUND_COLOR,
  BLOCK_COLOR, FONT
} from '../Colors.js';
import {
  styles, isiPhone5, 
  isiPhone, isiPhonePlus, 
} from '../StyleConstants.js';

const scaleAnimation =  new ScaleAnimation();

var reqList = [];

var chatsList = [];

export default class ChatsView extends Component {

  constructor(props, context) {
    super(props, context);

    this.refreshListener = EventRegister.addEventListener('refresh chats', this.refresh.bind(this));
    this.acceptRequestListener = EventRegister.addEventListener('accept request', this.newChat.bind(this));
    this.sendMessageListener = EventRegister.addEventListener('new message', this.newMessage(false).bind(this));
    this.sendMessageListener = EventRegister.addEventListener('send message', this.newMessage(true).bind(this));
    this.seenMessageListener = EventRegister.addEventListener('seen message', this.seenMessage.bind(this));
    this.changeNameListener = EventRegister.addEventListener('change name', this.changeChatName.bind(this));
    this.blockUserListener = EventRegister.addEventListener('block user from chat', this.blockUserUpdate.bind(this));
    this.newRequestListener = EventRegister.addEventListener('new request', this.newRequest.bind(this));
    this.ds = new ListView.DataSource({rowHasChanged: (r1, r2) => r1 !== r2});

    this.state = {
      text: '',
      user: {},
      loading: false,
      reqDataSource: this.ds.cloneWithRows(reqList),
      chatsDataSource: this.ds.cloneWithRows(chatsList),
      tags:[],
    };
  }

  componentWillMount() {
    this.refresh();
  }

  componentWillUnmount() {
    EventRegister.removeEventListener(this.refreshListener);
    EventRegister.removeEventListener(this.newChatListener);
    EventRegister.removeEventListener(this.acceptRequestListener);
    EventRegister.removeEventListener(this.sendMessageListener);
    EventRegister.removeEventListener(this.sendMessageListener);
    EventRegister.removeEventListener(this.changeNameListener);
    EventRegister.removeEventListener(this.blockUserListener);
    EventRegister.removeEventListener(this.newRequestListener);
  }

  refresh() {
    if (!this.state.loading) {
      reqList = [];
      chatsList = [];
      if (connectionListener.isConnected()) {
        requestModel.getRequests(this.getRequests.bind(this));
        chatsModel.getChats(this.getChats.bind(this));
      } else {
        AlertIOS.alert(
           'Alert',
           'Network Failure'
        );
      }
    }
  }

  newMessage(unseen) {
    return (data) => {
      var chatID = data.chatID;
      var msg = data.msg;
      for (var i = 0; i < chatsList.length; i++) {
        if (chatsList[i].chatID == chatID) {
          var users = chatsList[i].users.slice();
          var chatName = chatsList[i].chatName;
          var avatar_url = chatsList[i].avatar_url;
          chatsList.splice(i, 1);
          chatsList.unshift({
            users:users,
            chatName:chatName,
            chatID:chatID,
            avatar_url:avatar_url,
            msg:msg,
            unseen:unseen
          });
          this.setState({chatsDataSource:this.ds.cloneWithRows(chatsList)});
          return;
        }
      }
      chatsList.unshift({
        chatID:chatID,
        msg:msg
      });
    }
  }

  seenMessage(data) {
    var chatID = data.chatID;
    for (var i = 0; i < chatsList.length; i++) {
      console.log(chatsList[i].chatID, chatID);
      if (chatsList[i].chatID == chatID) {
        chatsList[i].unseen = false;
        this.setState({chatsDataSource:this.ds.cloneWithRows(chatsList)});
        return;
      }
    }
  }
  
  getRequests(res, err) {

    if (!err && !res) {
      return;
    }

    if (err || !res) {
      AlertIOS.alert(
       'Alert',
       'Could Not Retrieve Requests!'
      );
      return;
    }

    userIds = []
    var size = reqList.length;
    for (var i = 0; i < res.length; i++) {
      var found = false;
      for (var j = 0; j < size; j++) {
        if (res[i].requestID == reqList[j].requestID) {
          found = true;
        }
      }
      if (found) {
        continue;
      }
      reqList.push(res[i]);
      fromUserID = res[i]['fromUserID'];
      userIds.push(fromUserID.toString());
    }

    fbModel.getFBPPList(userIds, this.addFBPPReq.bind(this));

    this.setState({reqDataSource:this.ds.cloneWithRows(reqList)});
  }

  addFBPPReq(err, res) {
    if (err || !res) {
      return;
    }

    for (var i = 0; i < reqList.length; i++) {
      if (reqList[i]['fromUserID'].toString() == res.id) {
        reqList[i]['avatar_url'] = res.picture.data.url;
        break;
      }
    }

    this.setState({reqDataSource:this.ds.cloneWithRows(reqList)});
  }

  getChats(res, err) {

    if (!res && !err) {
      return;
    }

    if (err || !res) {
        AlertIOS.alert(
         'Alert',
         'Could Not Retrieve Chats!'
        );
        return;
    }

    this.setState({chatsDataSource:this.ds.cloneWithRows(chatsList)});
    if (res.length == 0) {return;}

    userIds = [];
    var size = chatsList.length;

    for (var i = 0; i < res.length; i++) {
      var found = false;
      for (var j =0; j < size; j++) {
        if (chatsList[j].chatID == res[i].chatID) {
          found = true;
          break;
        }
      }

      if (!found) {
        chatsList.push(res[i]);
        for (var j = 0; j < res[i]['users'].length;j++) {
          if (res[i]['users'][j].toString() != user.userID) {
            userIds.push(res[i]['users'][j]);
            break;
          }
        }
      }
    }

    fbModel.getFBPPList(userIds, this.addFBPPChats.bind(this));
    this.setState({chatsDataSource:this.ds.cloneWithRows(chatsList)});
  }

  addFBPPChats(err, res) {
    if (err || !res) {
      return;
    }
    for (var i = 0; i < chatsList.length; i++) {
      var found = false;
      for (var j = 0; j < chatsList[i]['users'].length; j++) {
        if (chatsList[i]['users'][j].toString() == res.id) {
          chatsList[i]['avatar_url'] = res.picture.data.url;
          found = true;
          break;
        }
      }
      if (found) {
        break;
      }
    }
    this.setState({chatsDataSource:this.ds.cloneWithRows(chatsList)});
  }

  newChat(data) {
    var chat = data.chat;
    var chatName = data.chatName;
    var msg = data.msg;

    chatsList.unshift({
      users: chat.users,
      chatName: chatName,
      chatID: chat.chatID,
      msg: msg,
      unseen: true
    });

    for (var j = 0; j < chat.users.length; j++) {
      var userID = chat.users[j].toString();
      if (userID != user.userID) {
        break;
      }
    }

    fbModel.getFBPP(userID, this.addFBPPChats.bind(this));
    this.setState({chatsDataSource:this.ds.cloneWithRows(chatsList)});
  }
  
  changeChatName(data) {
    var chatID = data.chatID;
    var name = data.chatName;
    for (var i = 0; i < chatsList.length; i++) {
      if (chatsList[i].chatID == chatID) {
        chatsList[i].chatName = name;
        this.setState({chatsDataSource:this.ds.cloneWithRows(chatsList)});
        return;
      }
    }
  }

  blockUserUpdate(data) {
    var chatID = data.chatID;
    for (var i = 0; i < chatsList.length; i++) {
      if (chatsList[i].chatID == chatID) {
        chatsList.splice(i,1);
        this.setState({chatsDataSource:this.ds.cloneWithRows(chatsList)});
        return;
      }
    }
  }

  newRequest(request) {
    console.log(request);
    request.request['tags'] = request.tags;
    request = request.request;
    reqList.unshift(request);
    fbModel.getFBPP(request.fromUserID, this.addFBPPReq.bind(this));
    this.setState({reqDataSource:this.ds.cloneWithRows(reqList)});
  }

  toChatView(l) {
    return () => {
      l.unseen = false;
      this.props.navigation.navigate("Chat", l);
      this.setState({chatsDataSource:this.ds.cloneWithRows(chatsList)});
    }
  }

  openMessageRequest(l) {
    this.state.user = l;
    this.state.text = l.msg;
    this.state.tags = l.tags;
    this.setState(this.state);
    this.popupDialog.show();
  }

  removeReqID(requestID) {
    for (var i = 0; i < reqList.length; i++) {
      if (reqList[i]['requestID'] == requestID) {
        reqList.splice(i,1);
        break;
      }
    }
    this.setState({reqDataSource:this.ds.cloneWithRows(reqList)});
  }

  declineCb(res, err) {
    
    this.setState({
      loading: false
    });

    if (!err && !res) {
      return;
    }

    if (err || !res) {
      AlertIOS.alert(
         'Alert',
         'Could Not Decline Request!'
      );
      return;
    }

    this.removeReqID(this.state.user.requestID);
    this.popupDialog.dismiss();
  }

  blockCb(res, err) {
    this.setState({
      loading: false
    });

    if (!err && !res) {
      return;
    }

    if (err || !res) {
      AlertIOS.alert(
         'Alert',
         'Could Not Block User!'
      ); 
      return;
    }

    this.removeReqID(this.state.user.requestID);
    this.popupDialog.dismiss();
  }

  decline() {
    this.setState({
      loading: true
    });
    requestModel.declineRequest(this.state.user.requestID, this.declineCb.bind(this));
  }

  block() {
    this.setState({
      loading: true
    });
    usersModel.blockUser(this.state.user.fromUserID.toString(), this.blockCb.bind(this));
  }

  blockUser() {
    AlertIOS.alert(
     'Attention!',
     'Would you like to block this user?',
     [
       {text: 'Yes', onPress: () => this.block(), style: 'cancel'},
       {text: 'No', onPress: () => {}},
     ],
    );
  }

  acceptCb(res, err) {
    
    this.setState({
      loading: false
    });

    if (!err && !res) {
      return;
    }

    if (err || !res) {
      AlertIOS.alert(
         'Alert',
         'Could Not Accept Request!'
      );
    }
    
    this.newChat(res);
    this.declineCb(res, err);
  }

  acceptRequest() {
    this.setState({
      loading: true
    });
    EventRegister.emit('local accept request', {userID:this.state.user.fromUserID});
    requestModel.acceptRequest(this.state.user.requestID, this.acceptCb.bind(this));
  }

  isUnseen(unseen) {
    if (unseen) {
      return {
        color:BOLD_COLOR,
        fontWeight:"bold"
      };
    }
    return {};
  }

  renderRow(l, i) {
    return (<ListItem
            roundAvatar
            avatar={{uri:l.avatar_url}}
            key={i}
            title={l.chatName}
            titleStyle={this.isUnseen(l.unseen)}
            subtitle={l.subtitle}
            subtitleStyle={this.isUnseen(l.unseen)}
            onPress={this.toChatView(l).bind(this)}
            activeOpacity={0.7}
            subtitle={l.msg}
          />)
  }


  renderCol(l, i) {
    return (
      <ListItem style={styles.requestItem}
        roundAvatar
        avatar={
          <Avatar
            rounded
            medium
            source={l.avatar_url && {uri: l.avatar_url}}
          />
        }
        key={i}
        onPress={() => this.openMessageRequest(l)}
        activeOpacity={0.7}
        hideChevron={true}
      />
    )
  }

  getButtonWidth(){
    if (isiPhone5) {
      return {width:'26%'}
    } else {
      return {width:'27%'}
    }
  }

  getAvatarHeight(){
    if (isiPhone5) {
      return '55%'
    } else {
      return '50%'
    }
  }

  getPopupWidth(){
    if (isiPhone5) {
      return .97
    } else {
      return .95
    }
  }

  getPopupHeight() {
    if (this.numberOfTags() == 0) {
      if (isiPhone5) {
        return .55
      } else if (isiPhone) {
        return .50
      } else if (isiPhonePlus) {
        return .47
      } else {
        return .43
      }
    } else {
      if (isiPhone5) {
        return .63
      } else if (isiPhone) {
        return .57
      } else if (isiPhonePlus) {
        return .52
      } else {
        return .48
      }
    }
  }

  getButtonTop() {
    if (isiPhone5) {
      return '0%'
    } else if (isiPhone || isiPhonePlus) {
      return '2%'
    } else {
      return '4%'
    }
  }

  getFontSize() {
    if (isiPhone5) {
      return 12
    } else {
      return 16
    }
  }

  getRequestHeight() {
    if (isiPhone5) {
      return '14.5%'
    } else {
      return '11.5%'
    }
  }

  getChatListHeight() {
    if (isiPhone5) {
      return '72.5%'
    } else if (isiPhone) {
      return '76.5%'
    } else if (isiPhonePlus) {
      return '78.5%'
    } else {
      return '74.6%'
    }
  }

  getTagWidth(items) {
    if (items == 0) {
      return "90%"
    } else if (items == 1) {
      return "90%"
    } else if (items == 2) {
      return "40%"
    } else {
      return "25%"
    }
  }

  renderSingleTag(tag, items) {
    if (!tag || tag == "" ){
      return
    }
    return (
      <Text
        style={[{width:this.getTagWidth(items)}, styles.tags, styles.border, styles.center, {textAlign:'center', paddingLeft:5, paddingRight:5}]}
        selectable={true}
        numberOfLines={1}
      >
      {tag}
      </Text>
    );
  }

  numberOfTags() {
    tags = this.state.tags;
    if (!tags) {
      return 0;
    }
    items = 0;
    for (var i = tags.length - 1; i >= 0; i--) {
      if (tags[i] && tags[i] != "") {
        items += 1;
      }
    }
    return items;
  }

  renderTags() {
    tags = this.state.tags;
    if (!tags) {
      tags = ["","",""];
    }
    items = this.numberOfTags();

    console.log(tags);
    console.log(items);

    var tag1 = this.renderSingleTag(tags[0], items);
    var tag2 = this.renderSingleTag(tags[1], items);
    var tag3 = this.renderSingleTag(tags[2], items);
    return (
      <View style={[styles.flexRow, styles.center, {paddingBottom:10}]}>
      {tag1}
      {tag2}
      {tag3}
      </View>
    );
  }

  render() {
    const navigate = this.props.navigation.navigate;

    var view = (
        <Text style={styles.requestTitle}>
          Requests
        </Text>);

      if (reqList.length == 0) {
      var view2 = (
        <List containerStyle={styles.requestText}>
          <Text style={styles.text}>
            You have no pending requests
          </Text>
        </List>
      );
    } else {
      var view2 = (
        <List containerStyle={{top:'0%', height:this.getRequestHeight()}}>
          {
            <ListView
              horizontal={true}
              renderRow={this.renderCol.bind(this)}
              dataSource={this.state.reqDataSource}
            />
          }
        </List>
      );
    }

    if (chatsList.length == 0) {
      var view3 = (
        <List containerStyle={styles.flexOne}>
          <Text style={styles.text}>
            You have no chats, go and discover new friends
          </Text>
        </List>
        );
    } else {
      var view3 = (
      <List containerStyle={{height:this.getChatListHeight()}}>
        {
          <ListView
            renderRow={this.renderRow.bind(this)}
            dataSource={this.state.chatsDataSource}
          />
        }
        </List>
      );
    }

    var popupDialog = (
      <PopupDialog
        dialogTitle={<DialogTitle title="New Request" />}
        dialogAnimation={scaleAnimation}
        width={this.getPopupWidth()}
        height={this.getPopupHeight()}
        dialogStyle={[{ bottom:"10%"}, styles.popupBase]}
        ref={(popupDialog) => { this.popupDialog = popupDialog; }}
      >
        <View style={styles.flexCol}>
          <View style={[{ height:this.getAvatarHeight()}, styles.center]}>
            <Avatar style={{ backgroundColor:AVATAR_BACKGROUND_COLOR}}
              rounded
              xlarge
              source={this.state.user.avatar_url && {uri: this.state.user.avatar_url}}
            />
          </View>
          {this.renderTags()}
          <View style={styles.requestMessage}>
            <TextInput
              style={[{height:(this.getFontSize()+1)*4, fontSize:this.getFontSize()}, styles.requestMessageStyle]}
              textAlign={'center'}
              maxHeight={(this.getFontSize()+1)*4}
              multiline={true}
              editable={false}
              onChangeText={(text) => (text)}
              value={this.state.text}
            />
          </View>
          <View style={[{top:this.getButtonTop()}, styles.flexRow , styles.center]}>
            <Button
              raised
              rounded
              title='Reject'
              fontWeight="bold"
              fontSize={this.getFontSize()}
              backgroundColor={DISMISS_COLOR}
              containerViewStyle={this.getButtonWidth()}
              onPress={() => this.decline()} />
            <Button
              raised
              rounded
              title='Block'
              fontWeight="bold"
              fontSize={this.getFontSize()}
              backgroundColor={BLOCK_COLOR}
              containerViewStyle={this.getButtonWidth()}
              onPress={() => this.blockUser()} />
            <Button
              raised
              rounded
              title='Accept'
              fontWeight="bold"
              fontSize={this.getFontSize()}
              backgroundColor={ACCEPT_COLOR}
              containerViewStyle={this.getButtonWidth()}
              onPress={() => this.acceptRequest()} />
          </View>
        </View>
      </PopupDialog>
    );
    return (
      <View style={styles.fullscreen}>
        {view}
        {view2}
        {view3}
        {popupDialog}
        {this.state.loading &&
    <View style={styles.loading}>
      <ActivityIndicator size='large' />
    </View>
}
      </View>
    );
  }
}
