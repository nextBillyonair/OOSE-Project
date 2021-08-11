import React, { Component } from 'react';
import {
  Text, View, ListView, Keyboard,
  TextInput, Dimensions, Animated, Easing,
  ActivityIndicator, AlertIOS, TouchableHighlight
} from 'react-native';
import PopupDialog, { DialogTitle, SlideAnimation, ScaleAnimation } from 'react-native-popup-dialog';
import { Button, List, ListItem, Avatar } from 'react-native-elements';
import { EventRegister } from 'react-native-event-listeners';

import NearbyUserModel from '../models/NearbyUserModel';
import { requestModel } from '../models/RequestModel';
import { usersModel } from '../models/UsersModel';
import { fbModel } from '../models/FBModel';
import {
  DISMISS_COLOR, ACCEPT_COLOR, 
  AVATAR_BACKGROUND_COLOR, TITLE_UNDERLAY_COLOR,
  POPUP_BACKGROUND
} from '../Colors.js';
import {
  styles, isiPhone5, 
  isiPhone, isiPhoneX, isiPhonePlus
} from '../StyleConstants.js';

const FBSDK = require('react-native-fbsdk');
const {
  LoginButton,
  AccessToken,
} = FBSDK; 

var {height, width} = Dimensions.get('window')

const scaleAnimation =  new ScaleAnimation();

const menuSlideAnimation = new SlideAnimation({
  slideFrom: 'left',
});

const discoverList = [];
const indexList = {};

export default class DiscoverView extends Component {
  constructor(props, context) {
    super(props, context);

    this.isPopupShown=false;
    this.maxPeople = 25;
    
    this.refreshListener = EventRegister.addEventListener('refresh discover', this.refresh.bind(this));
    this.discoverMenuListener = EventRegister.addEventListener('openDiscoverMenu', this.openMenu.bind(this));;
    this.changeDiscoverViewListener = EventRegister.addEventListener('ChangeDiscoverView', this.changeView.bind(this));

    var ds = new ListView.DataSource({rowHasChanged: (r1, r2) => {
      var update = r1.update;
      r1.update = false;
      return update;
    }});

    this.state = {
      text: '',
      user: {},
      dataSource: ds.cloneWithRows(discoverList),
      popupHeight:'20%',
      offsetY: new Animated.Value(0),
      loading:false,
      tags:[],
      selectedIndex:0,
    };
    
    this.animatedValue = new Animated.Value(0);
  }

  componentDidMount() {
    this.nearbyUserModel = new NearbyUserModel(this.updateNewPeer.bind(this), this.updateLostPeer.bind(this), this.maxPeople);
    this.refresh();
  }

  refresh() {
    if (!this.state.loading && this.nearbyUserModel.processed) {
      discoverList = [];
      indexList = {};

      this.setState({dataSource: this.state.dataSource.cloneWithRows(discoverList),})
      this.nearbyUserModel.refresh();
      if (this.popupDialog) {
        this.popupDialog.dismiss();
      }
      if (this.menu) {
        this.menu.dismiss();
        Keyboard.dismiss();
      }
    }
  }

  componentWillMount () {
    this.keyboardDidShowListener = Keyboard.addListener('keyboardWillShow', this._keyboardDidShow.bind(this));
    this.keyboardDidHideListener = Keyboard.addListener('keyboardWillHide', this._keyboardDidHide.bind(this));
  }

  componentWillUnmount () {
    this.keyboardDidShowListener.remove();
    this.keyboardDidHideListener.remove();
    this.nearbyUserModel.unmount();    
    EventRegister.removeEventListener(this.changeDiscoverViewListener);
    EventRegister.removeEventListener(this.refreshListener);
    EventRegister.removeEventListener(this.discoverMenuListener);
  }

  _keyboardDidShow () {
    this.animatedValue.setValue(0)
    Animated.timing(
      this.animatedValue,
      {
        toValue: 1,
        duration: 100,
        easing: Easing.linear
      }
    ).start()
  }

  _keyboardDidHide () {
    Animated.timing(
      this.animatedValue,
      {
        toValue: 0,
        duration: 100,
        easing: Easing.linear
      }
    ).start()

  }

  changeView(selectedIndex) {
    this.setState({selectedIndex});
  }

  openMenu() {
    if (!this.isPopupShown) {
      Keyboard.dismiss();
      this.menu.show();
      this.isPopupShown = true;
    } else {
      Keyboard.dismiss();
      this.menu.dismiss();
      this.isPopupShown = false;
    }
  }

  closePopup() {
    this.isPopupShown = false;
  }
  
  updateNewPeer(data) {

    data.id = data.id.toString();
    if (data.id in indexList) {
      return;
    }
    var index = discoverList.length;

    if (discoverList.length >= this.maxPeople) {
      return;
    }

    indexList[data.id] = index;
    var newPeer = {
      id: data.id,
      name: data.name,
      avatar_url: data.avatar_url,
      tags:data.tags
    };
    discoverList[index] = newPeer;

    this.setState({
      dataSource: this.state.dataSource.cloneWithRows(discoverList),
    });

    if (!data.avatar_url) {
      fbModel.getFBPP(data.id, this.newImage.bind(this));
    }
    if (!data.tags) {
      usersModel.getTags(data.id, this.updateTags.bind(this));
    }
  }

  newImage(err, res) {
    if (!err) {
      id = res.id;
      url = res.picture.data.url;

      this.nearbyUserModel.savePictureUrl(id, url);

      if (indexList[id] != null && discoverList[indexList[id]]) {

        discoverList[indexList[id]]["avatar_url"] = url;
        discoverList[indexList[id]]["update"] = true;

        this.setState({
          dataSource: this.state.dataSource.cloneWithRows(discoverList),
        });
      }
    }
  }

  updateTags(res, err) {
    if (!err && res) {
      id = res.id;
      tags = res.tags;

      this.nearbyUserModel.saveTags(id, tags);

      if (indexList[id] != null && discoverList[indexList[id]]) {
        discoverList[indexList[id]]["update"] = true;
        discoverList[indexList[id]]["tags"] = tags;
        this.setState({
          dataSource: this.state.dataSource.cloneWithRows(discoverList),
        });
      }
    }
  }

  updateLostPeer(data) {
    if (indexList[data.id] != null) {
      delete discoverList[indexList[data.id]];
      delete indexList[data.id];
    }

    this.setState({
      dataSource: this.state.dataSource.cloneWithRows(discoverList),
    });
  }

  openMessageRequest(l, r) {

    this.setState({
      loading: true,
      position:r
    });
    usersModel.getIsConnected(l.id, this.nearbyUserModel.sid, r, (res, err) => {

      this.setState({
        loading: false
      });

      if (!err && !res) {
        return;
      }

      if (err || !res) {
        AlertIOS.alert(
         'Alert',
         'Could Not Open Message Request!'
        );
        return;
      }
      if (res.connected) {
        res.chat['avatar_url'] = l.avatar_url;
        this.props.navigation.navigate("Chat", res.chat);
      } else {
        this.state.user = l;
        this.state.text = '';
        this.popupDialog.show();
        this.setState({
                  text: '',
                  user: l,
                  tags: (l.tags != null ? l.tags : [])
                  });
      }
    });
  }

  dismissPopup() {
    this.popupDialog.dismiss();
    Keyboard.dismiss();
  }

  sendRequestCb(res, err) {
    this.setState({
      loading: false
    });

    if (!err && !res) {
      return;
    }
    if (err || !res) {
      AlertIOS.alert(
         'Alert',
         'Could Not Send Request!'
      );
      return;
    }
    
    this.nearbyUserModel.updateFilteredUsers(this.state.user.id);
    this.popupDialog.dismiss();
    Keyboard.dismiss();

  }

  sendRequest() {
    this.setState({
      loading: true
    });
    requestModel.sendRequest(this.state.user.id, this.state.text, this.nearbyUserModel.sid, this.state.position, this.sendRequestCb.bind(this));
  }

  adjustNumberShown(numberToShow) {
    this.maxPeople = numberToShow;
    this.nearbyUserModel.setMaxPeople(numberToShow);
    this.isPopupShown = false;
    this.menu.dismiss();
    this.refresh();
  }

  getButtonWidth(){
    if (isiPhone5) {
      return {width:'40%'}
    } else {
      return {width:'35%'}
    }
  }

  getButtonTop(){
    if (isiPhone5) {
      return {top:'4%'}
    } else {
      return {top:'3%'}
    }
  }

  getAnimationSize() {
    if (isiPhone5) {
      return '37%'
    } else if (isiPhone) {
      return '27%'
    } else if (isiPhoneX) {
      return '25%'
    } else {
      return '20%'
    }
  }

  getPopupHeight() {
    return {height:'84%'}
  }

  getHeight() {
    if (this.numberOfTags() == 0) {
       if (isiPhone5) {
        return .52
      }
      if (isiPhone) {
        return .45
      }
      if (isiPhonePlus) {
        return .40
      }
      return .37
    } else {
      if (isiPhone5) {
        return .60
      }
      if (isiPhone) {
        return .50
      }
      if (isiPhonePlus) {
        return .47
      }
      return .42
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
    items = this.numberOfTags();

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

  constructTagString(tags) {
    var str = "";
    if (!tags || tags[0] == "") {
      return "This person has no tags";
    }
    if (tags[1] && tags[1] != "") {
      str += tags[1];
    }
    if (tags[2] && tags[2] != "") {
      str += ", " + tags[2];
    }
    return str;
  }

  getListHeight() {
    if (isiPhoneX) {
      return height - 170;
    } else {
      return height - 115;
    }
  }

  render() {

    const marginBottom = this.animatedValue.interpolate({
      inputRange: [0, 1],
      outputRange: ['20%', this.getAnimationSize()]
    })

    if (Object.keys(discoverList).length == 0) {
      var view = (
        <View style={styles.container}>
          <Text style={styles.text}>
              There is no one nearby. Are you in the middle of nowhere?
          </Text>
        </View>
        );
    } else if (this.state.selectedIndex == 0){
      var view = (
          <View style={styles.container}>
          <ListView contentContainerStyle={styles.list}
            automaticallyAdjustContentInsets={false}
            dataSource={this.state.dataSource}
            renderRow={(l,i,r) => 
              <ListItem style={styles.item}
              roundAvatar
              avatar={<Avatar
                  rounded
                  large
                  source={l.avatar_url && {uri: l.avatar_url}}
                  title={l.name}
                />}
              key={i}
              title={l.chatName}
              onPress={
                () => this.openMessageRequest(l, r)
              }
              activeOpacity={0.7}
              hideChevron={true}
              />
            }
          />
          </View>
        );
    } else {
      var view = (
          <List style={{height:this.getListHeight(), backgroundColor: 'white',}}>
          <ListView 
            automaticallyAdjustContentInsets={false}
            dataSource={this.state.dataSource}

            renderRow={(l,i,r) => {
              return (<ListItem
                roundAvatar
                avatar={l.avatar_url && {uri:l.avatar_url}}
                key={i}
                title={l.tags && l.tags[0]}
                hideChevron={true}
                onPress={
                  () => this.openMessageRequest(l, r)
                }
                activeOpacity={0.7}
                subtitle={this.constructTagString(l.tags)}
              />);
            }
            }
          />
          </List>
        );
    }

    var menu = (
        <PopupDialog
          dialogAnimation={menuSlideAnimation}
          onDismissed={() => this.closePopup()}
          width={2*width/3}
          height={height}
          dialogStyle={[{right:width/6, top:-21}, styles.flexCol]}
          ref={(menu) => { this.menu = menu; }}
        >
          <View>
            <List>
              <ListItem
                title={"Show 10 people"}
                titleStyle={styles.discoverMenuButton}
                hideChevron={true}
                onPress={this.adjustNumberShown.bind(this, 10)}
                activeOpacity={0.7}
              />
              <ListItem
                title={"Show 25 people"}
                titleStyle={styles.discoverMenuButton}
                hideChevron={true}
                onPress={this.adjustNumberShown.bind(this, 25)}
                activeOpacity={0.7}
              />
              <ListItem
                title={"Show 50 people"}
                titleStyle={styles.discoverMenuButton}
                hideChevron={true}
                onPress={this.adjustNumberShown.bind(this, 50)}
                activeOpacity={0.7}
              />
              <ListItem
                title={"Show 100 people"}
                titleStyle={styles.discoverMenuButton}
                hideChevron={true}
                onPress={this.adjustNumberShown.bind(this, 100)}
                activeOpacity={0.7}
              />
            </List>
          </View>
        </PopupDialog>);

    var popupDialog = (<PopupDialog
          dialogTitle={
            <TouchableHighlight 
              style={styles.borderRadiusPopup} 
              onPress={() => Keyboard.dismiss()} 
              underlayColor={TITLE_UNDERLAY_COLOR} 
              activeOpacity={1}>
              <View style={styles.dialogTitleView}>
                <Text style={styles.dialogTitleText}>
                  Send Request
                </Text>
              </View>
            </TouchableHighlight>
          }
          dialogAnimation={scaleAnimation}
          onDismissed={() => Keyboard.dismiss()}
          width={0.9}
          height={this.getHeight()}
          dialogStyle={[{ bottom:marginBottom}, styles.popupBase]}
          ref={(popupDialog) => { this.popupDialog = popupDialog; }}
          >
          <TouchableHighlight 
            style={[this.getPopupHeight(), styles.borderRadiusPopup]} 
            onPress={() => Keyboard.dismiss()} 
            underlayColor={POPUP_BACKGROUND} 
            activeOpacity={1} >
          <Animated.View style={[{transform: [{translateX: this.state.offsetY}]}, styles.flexOne, styles.flexCol]}>
            <View style={[{ height:'60%'}, styles.flexCol, styles.center]}>
            <Avatar style={{ backgroundColor:AVATAR_BACKGROUND_COLOR}}
              rounded
              xlarge
              source={this.state.user.avatar_url && {uri: this.state.user.avatar_url}}
            />
            </View>
            {this.renderTags()}
            <View style={[styles.flexCol, styles.center]}>
            <TextInput
              style={styles.textInput}
              placeholder="Please accept my request!"
              onChangeText={(text) => this.setState({text:text})}
              value={this.state.text}
            />
            </View>
            <View style={[styles.flexRow, styles.center, this.getButtonTop()]}>
              <Button
                raised
                rounded
                title="Dismiss"
                fontWeight="bold"
                fontSize={16}
                containerViewStyle={this.getButtonWidth()}
                backgroundColor={DISMISS_COLOR}
                onPress={() => this.dismissPopup() } />
              <Button
                raised
                rounded
                title="  Send  "
                fontSize={16}
                fontWeight="bold"
                containerViewStyle={this.getButtonWidth()}
                backgroundColor={ACCEPT_COLOR}
                onPress={() => this.sendRequest()} />
            </View>
          </Animated.View>
          </TouchableHighlight>
        </PopupDialog>);

    return (
      <View style={styles.fullscreen}>
      {view}
      {popupDialog}
      {this.state.loading &&
        <View style={styles.loading}>
          <ActivityIndicator size='large' />
        </View>
      }
      {menu}
      </View>
    );
  }

}
  
