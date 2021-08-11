import React, { Component } from 'react';
import {
  View, Keyboard,
  AlertIOS, Dimensions, 
  ActivityIndicator, TouchableHighlight, Text
} from 'react-native';
import { Icon, List, ListItem, Avatar } from 'react-native-elements';
import PopupDialog, { SlideAnimation, ScaleAnimation } from 'react-native-popup-dialog';
import { GiftedChat, Bubble, Send, MessageText } from 'react-native-gifted-chat';

import { chatModel } from '../models/ChatModel';
import { user } from '../models/User';
import { EventRegister } from 'react-native-event-listeners';
import { usersModel } from '../models/UsersModel';
import {
  EDIT_CHAT_NAME_COLOR,
  BLOCK_USER_MENU_COLOR, CHAT_BUBBLE_COLOR,
  INACTIVE_LEFT_TEXT, INACTIVE_LEFT_BUBBLE,
  INACTIVE_RIGHT_BUBBLE, INACTIVE_SEND,
  REFRESH_MENU_COLOR, OFFLINE_MENU_COLOR,
  AVATAR_BACKGROUND_COLOR
} from '../Colors.js';
import { styles, isiPhoneX, isiPhonePlus, isiPhone, isiPhone5 } from '../StyleConstants.js';

const timer = require('react-native-timer');
const slideAnimation = new SlideAnimation({
  slideFrom: 'right',
});
const popAnimation =  new ScaleAnimation();

var {height, width} = Dimensions.get('window')

export default class ChatView extends Component {

  constructor(props, context) {
    super(props, context);
    
    this.isPopupShown=false;

    this.chat = this.props.navigation.state.params;
  }

  componentWillMount() {
    this.refresh();

    EventRegister.emit('openChat', this.chat.chatID);

    this.chatMenuListener = EventRegister.addEventListener('openMenu', this.openMenu.bind(this));
    this.newMessageListener = EventRegister.addEventListener('send message', this.newMessage.bind(this));
  }

  componentWillUnmount() {
    timer.clearTimeout(this.chat.chatID);
    EventRegister.emit('closeChat');
    EventRegister.removeEventListener(this.chatMenuListener);
    EventRegister.removeEventListener(this.newMessageListener);
  }


  refresh() {
    this.setState({
      messages: [],
      loading: true,
      editable: false,
      tags: [],
    });

    var userID = null;
    for (var i =0; i < this.chat.users.length; i++) {
      if (this.chat.users[i] != user.userID) {
        userID = this.chat.users[i];
        break;
      }
    }
    if (userID != null) {
      usersModel.getTags(userID, ((res, err) => {
        if (res) {
          this.setState({tags:res.tags});
        }
      }).bind(this)); 
    }

    chatModel.getChat(this.chat.chatID, this.getChat.bind(this));
    chatModel.getIsActive(this.chat.chatID, this.isActive.bind(this));
  }

  refreshButton() {
    this.refresh();
    this.popupDialog.dismiss();
  }

  newMessage(data) {
    if (!data || data.chatID != this.chat.chatID) {
      return;
    }

    EventRegister.emit('seen message', {
      chatID:this.chat.chatID
    });

    var message = this.createNewMessage(data.msgID, data.msg, data.timeStamp, 2);

    chatModel.seenChat(this.chat.chatID);

    this.setState((previousState) => ({
      messages: GiftedChat.append(previousState.messages, message),
    }));
  }

  isActive(res, err) {
    console.log(res, err);
    if (!err && !res) {
      return;
    }
    if (err || !res) {
      AlertIOS.alert(
         'Alert',
         'Could Not Get If Chat Is Active!'
      );
      return;
    }

    this.setState({editable:res.active});
    if (res.active && res.time) {
      var time = new Date(Date.parse(res.time));
      var currentTime = new Date();
      if (time - currentTime < 0) {
        this.setState({editable:false});
      } else {
        timer.setTimeout(this.chat.chatID, this.endOfTimer.bind(this), time - currentTime);
      }
    }
  }

  getChat(res, err) {

    this.setState({
      loading:false
    });

    if(!err && !res) {
      return;
    }

    if (err || !res) {
      AlertIOS.alert(
         'Alert',
         'Could Not Get Chat Messages!'
      );
      return;
    }

    chatModel.seenChat(this.chat.chatID);

    var messages = [];
    for (var i = 0; i < res.length; i++) {
      var time = res[i].timeStamp;
      
      if (res[i].userID == user.userID) {
        var id = 1;
      } else {
        var id = 2;
      }

      var message = this.createNewMessage(res[i].msgID, res[i].msg, time, id);
      messages.push(message);
    }

    this.setState((previousState) => ({
      messages: GiftedChat.append(previousState.messages, messages),
    }));
  }

  endOfTimer() {
    this.setState({editable:false});
    AlertIOS.alert(
     'Alert',
     'This Chat is not Active Anymore!'
    );
  }

  createNewMessage(msgID, msg, time, id) {
    var offset = new Date().getTimezoneOffset();
    var time = new Date((new Date(Date.parse(time))) - offset*60*1000);
    // var time = new Date(Date.parse(time))
    var message = {
      _id: msgID,
      text: msg,
      createdAt: time,
      user: {
        _id: id
      }
    };
    if (id == 2) {
      message.user.avatar = this.chat.avatar_url;
    }
    return message;
  }

  openMenu() {
    if (!this.isPopupShown) {
      Keyboard.dismiss();
      this.popupDialog.show();
      this.isPopupShown = true;

      // look up if this user allows, on cb, due this
      this.setState({
        loading:true
      });

      var userID = 0;
      for (var i =0; i < this.chat.users.length; i++) {
        if (this.chat.users[i].toString() != user.userID) {
          userID = this.chat.users[i].toString();
          break;
        }
      }
      usersModel.isLongDistance(userID, ((res, err) => {
        this.setState({
          loading:false
        });

        if (!err && !res) {
          return;
        }

        if (err || !res) {
          AlertIOS.alert(
           'Alert',
           'Could Not Get Information'
          );
          return;
        }

        this.setState({
          longdistance:res.longdistance
        });
        this.popupDialog.show();
        this.isPopupShown = true;

      }).bind(this));

    } else {
      this.popupDialog.dismiss();
      this.isPopupShown = false;
      Keyboard.dismiss();
    }
  }

  closePopup() {
    this.isPopupShown = false;
    Keyboard.dismiss();
  }

  block() {

    this.popupDialog.dismiss();

    this.setState({
      loading: true
    });

    var userID = 0;
    for (var i =0; i < this.chat.users.length; i++) {
      if (this.chat.users[i].toString() != user.userID) {
        userID = this.chat.users[i].toString();
        break;
      }
    }

    usersModel.blockUser(userID, (res, err) => {
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
      }
    });

    EventRegister.emit('block user from chat', {chatID:this.chat.chatID, userID:userID});
    this.props.navigation.goBack();
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

  editChatName(text) {

    this.setState({
      loading: true
    });

    chatModel.editName(this.chat.chatID, text, (res, err) => {

      this.setState({
        loading: false
      });

      if (!err && !res) {
        return;
      }

      if (err || !res) {
        AlertIOS.alert(
         'Alert',
         'Could Not Edit Chat Name!'
        );
      }
    });

    this.chat.chatName = text;
    this.props.navigation.setParams({ chatName: text });
    EventRegister.emit('change name', {chatID:this.chat.chatID, chatName:text})
    this.popupDialog.dismiss()
  }

  onConfirm(text) {
    this.editChatName(text);
  }

  editChatNameAlert() {
    AlertIOS.prompt(
     'Edit Chat Name',
     'Enter a new name for your chat',
     [
       {text: 'Cancel', onPress: () => console.log('cancel'), style: 'cancel'},
       {text: 'Confirm', onPress: this.onConfirm.bind(this)},
     ],
    );
  }

  sendMessageCb(msgID, res, err) {
    if (err || !res) {
      if (err.status == 405) {
        this.setState({editable:false});
        AlertIOS.alert(
         'Alert',
         'This Chat is not Active Anymore!'
        );
      } else {
        AlertIOS.alert(
           'Alert',
           'Could Not Send Message!'
        );
      }

      this.setState((previousState) => ({
        messages: previousState.messages.filter(message=>message['_id'] != msgID)
      }));
      return;
    }

    EventRegister.emit('new message', res);
  }

  onSend(messages = []) { 
    if (!this.state.editable) {
      return;
    }

    console.log(messages);    
    
    if (messages.length == 0) {   
      return;   
    }   

    chatModel.sendMessage(this.chat.chatID, messages[0].text, this.sendMessageCb.bind(this, messages[0]["_id"]));
    this.setState((previousState) => ({   
      messages: GiftedChat.append(previousState.messages, messages),    
    }));    
  }

  takeOffline() {
    var question = "";
    if (this.state.longdistance) {
      question = "Would you like to disable long distance?";
    } else {
      question = "Would you like to enable long distance?";
    }

    var userID = 0;
    for (var i =0; i < this.chat.users.length; i++) {
      if (this.chat.users[i].toString() != user.userID) {
        userID = this.chat.users[i].toString();
        break;
      }
    }
    AlertIOS.alert(
     'Attention!',
     question,
     [
       {text: 'Yes', onPress: () => {
        this.setState({
          loading:true
        });

        if (this.state.longdistance) {
          usersModel.disableLongDistance(userID, this.changeLongDistanceCb.bind(this));
        } else {
          usersModel.enableLongDistance(userID, this.changeLongDistanceCb.bind(this));
        }

       }, style: 'cancel'},
       {text: 'No', onPress: () => {}},
     ],
    );
  }

  changeLongDistanceCb(res, err) {
    console.log(res, err);
    this.setState({
      loading:false
    });

    if (!res && !err) {
      return;
    }

    if (err || !res) {
      AlertIOS.alert(
         'Alert',
         'Could Not Change Relation!'
      );
      return;
    }

    this.setState({
      longdistance:!this.state.longdistance
    });

    if (!this.state.longdistance && this.state.editable) {
      chatModel.getIsActive(this.chat.chatID, this.isActive.bind(this));
    }
  }

  renderMessageText(props) {
    return (
      <MessageText
        {...props}
        textStyle={{
          left:{
            color: INACTIVE_LEFT_TEXT
          }
        }}
        linkStyle={{
          right:{
            color: INACTIVE_LEFT_TEXT
          }
        }}
      />
      )
  }

  renderBubble(props) {
    if (!this.state.editable) {
      return (
          <Bubble
            {...props}
            wrapperStyle={{
              left: {
                backgroundColor: INACTIVE_LEFT_BUBBLE,
              },
              right: {
                backgroundColor: INACTIVE_RIGHT_BUBBLE,
              },
              renderMessageText:this.renderMessageText
            }}
          />
        );
    } else {
      return (
        <Bubble {...props}
          wrapperStyle={{right:{backgroundColor:CHAT_BUBBLE_COLOR}}}
        />
      )
    }
  }

  renderSend(props) {
    if (!this.state.editable) {
      return(
        <Send
          {...props}
          textStyle={
            {
              color: INACTIVE_SEND
            }
          }
        />
      )
    } else {
      return(
        <Send {...props} />
      )
    }
  }

  fullScreenStyle() {
    if (isiPhoneX) {
      return styles.fullscreen, {
        height:height - 171
      } 
    } else {
      return styles.fullscreen, {
        height:height - 114
      }
    }
  }

  longDistanceTitle() {
    if (this.state.longdistance) {
      return "Disable Long Distance"
    } else {
      return "Enable Long Distance"
    }
  }
  
  showAvatar() {
    this.avatar.show();
  }

  closeAvatar() {
    this.avatar.dismiss();
  }

  renderSingleTag(tag, items) {
    if (!tag || tag == "" ){
      return
    }
    return (
      <Text
        style={[styles.chatTags, styles.center, {textAlign:'center'}]}
        selectable={false}
      > {tag} </Text>
    );
  }

  getPopupTop() {
    if (isiPhone5) {
      return {top:"40%"}
    }
    if (isiPhone) {
      return {top:"45%"}
    }
    if (isiPhonePlus) {
      return {top:"50%"}
    }
    if (isiPhoneX) {
      return {top:'40%'}
    }
  }

  numberOfTags() {
    tags = this.state.tags;
    items = 0;
    for (var i = tags.length - 1; i >= 0; i--) {
      if (tags[i] && tags[i] != "") {
        items += 1;
      }
    }
    return items;
  }

  getAvatarSize() {
    if (isiPhone5) {
      return (width*6)/8
    } else {
      return (width*7)/8
    }
  }

  getTagTop() {
    if (isiPhone5) {
      return {top:120}
    } else {
      return {top:180}
    }
  }

  renderTags() {
    tags = this.state.tags;
    console.log(tags);
    items = this.numberOfTags();

    var tag1 = this.renderSingleTag(tags[0], items);
    var tag2 = this.renderSingleTag(tags[1], items);
    var tag3 = this.renderSingleTag(tags[2], items);
    return (
      <View style={[styles.flexCol, styles.center, this.getTagTop()]}>
      {tag1}
      {tag2}
      {tag3}
      </View>
    );
  }

  render() {
    var bottomOffset = 50;
    if (isiPhoneX) {
      bottomOffset = 85;
    }

    return (
    <View style={this.fullScreenStyle()}>
        <GiftedChat 
          messages={this.state.messages}
          placeholder={"Type a message..."}
          onSend={(messages) => this.onSend(messages)}
          renderBubble={this.renderBubble.bind(this)}
          renderSend={this.renderSend.bind(this)}
          onPressAvatar={this.showAvatar.bind(this)}
          bottomOffset={bottomOffset}
          textInputProps={{editable:this.state.editable}}
          user={{
            _id: 1,
          }}
        />
        <PopupDialog
          dialogAnimation={popAnimation}
          overlayOpacity={0.75}
          dialogStyle={styles.avatarPopup}
          ref={(avatar) => { this.avatar = avatar; }}
        >
        <TouchableHighlight style={this.getPopupTop()} underlayColor='transparent' activeOpacity={1} onPress={() => this.avatar.dismiss()}>
          <View>
            <View style={styles.avatarStyle}>
              <Avatar style={{ backgroundColor:AVATAR_BACKGROUND_COLOR}}
                rounded
                width={this.getAvatarSize()}
                source={this.chat.avatar_url && {uri: this.chat.avatar_url}}
              />
            </View>
            {this.renderTags()}
            </View>
          </TouchableHighlight>
        </PopupDialog>
        <PopupDialog
          dialogAnimation={slideAnimation}
          onDismissed={() => this.closePopup()}
          width={2*width/3}
          height={height}
          dialogStyle={[{left:width/6, top:-21}, styles.flexCol]}
          ref={(popupDialog) => { this.popupDialog = popupDialog; }}
        >
          <View>
            <List>
              <ListItem
                title={"Edit Chat Name"}
                titleStyle={styles.chatMenuButton}
                hideChevron={true}
                leftIcon={
                  <Icon
                    name='pencil'
                    type='font-awesome'
                    color={EDIT_CHAT_NAME_COLOR}
                    size={20}
                    onPress={() => this.blockUser()} 
                  />
                }
                onPress={this.editChatNameAlert.bind(this)}
                activeOpacity={0.7}
              />
              <ListItem
                title={"Block User"}
                titleStyle={styles.chatMenuButton}
                leftIcon={
                  <Icon
                    name='ios-eye-off'
                    type='ionicon'
                    color={BLOCK_USER_MENU_COLOR}
                    size={20}
                    onPress={() => this.blockUser()} 
                  />
                }
                onPress={() => this.blockUser()}
                hideChevron={true}
                activeOpacity={0.7}
              />
              <ListItem
                title={"Refresh"}
                titleStyle={styles.chatMenuButton}
                leftIcon={
                  <Icon
                    name='md-refresh'
                    type='ionicon'
                    color={REFRESH_MENU_COLOR}
                    size={20}
                    onPress={() => this.refreshButton()} 
                  />
                }
                onPress={() => this.refreshButton()}
                hideChevron={true}
                activeOpacity={0.7}
              />
              <ListItem
                title={this.longDistanceTitle()}
                titleStyle={styles.chatMenuButton}
                leftIcon={
                  <Icon
                    name='signal'
                    type='entypo'
                    color={OFFLINE_MENU_COLOR}
                    size={20}
                    onPress={() => this.takeOffline()} 
                  />
                }
                onPress={() => this.takeOffline()}
                hideChevron={true}
                activeOpacity={0.7}
              />
            </List>

            {this.state.loading &&
            <View style={styles.loading}>
             <ActivityIndicator size='large' />
            </View>
          }
          </View>
        </PopupDialog>
      </View>
    );
  }
}
