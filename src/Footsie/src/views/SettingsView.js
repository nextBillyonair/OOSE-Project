import React, { Component } from 'react';
import {
  Text, View, TextInput,
  ScrollView, Dimensions,
  ActivityIndicator, AlertIOS, Keyboard
} from 'react-native';
import { EventRegister } from 'react-native-event-listeners';
import { List, ListItem, Avatar, Slider } from 'react-native-elements';
import TextInputState from 'TextInputState';

import { fbModel } from '../models/FBModel';
import { settingsModel} from '../models/SettingsModel';
import { graphModel } from '../models/GraphModel';
import { usersModel } from '../models/UsersModel';

import { 
	DEACTIVATE_COLOR, FONT, 
	MAX_SLIDER_COLOR,
	MIN_SLIDER_COLOR,
	SLIDER_THUMB_COLOR} from '../Colors';
import { styles, isiPhone5, isiPhonePlus, isiPhone } from '../StyleConstants';

var {height, width} = Dimensions.get('window');

class InputScrollView extends React.Component {

  constructor(props, ctx) {
      super(props, ctx);
      this.handleCapture = this.handleCapture.bind(this);
  }

  render() {
    return (
      <ScrollView keyboardShouldPersistTaps="always" keyboardDismissMode='on-drag' ref={(input)=>{this.scrollView = input;}}>
        <View onStartShouldSetResponderCapture={this.handleCapture}>
          {this.props.children}
        </View>
      </ScrollView>
    );
  }

  handleCapture(e) {
    const focusField = TextInputState.currentlyFocusedField();
    const target = e.nativeEvent.target;
    if (focusField != null && target != focusField){
        Keyboard.dismiss();
    }
  }

  scrollTo(obj) {
    this.scrollView.scrollTo(obj);
  }
}

export default class SettingView extends Component {

  constructor(props, context) {
		super(props, context);
		console.log(props);
		this.state={radius:1, time:1, loading:false, url:undefined, tags:["", "", ""]}
	  this.refreshListener = EventRegister.addEventListener('refresh settings', this.refresh.bind(this));
  }

  componentDidMount() {
    this.refresh();
  }

  componentWillMount() {
    this.keyboardDidShowListener = Keyboard.addListener('keyboardWillShow', this._keyboardDidShow.bind(this));
    this.keyboardDidHideListener = Keyboard.addListener('keyboardWillHide', this._keyboardDidHide.bind(this));
  }

  getScrollPosition() {
    if (isiPhone5) {
      return 185;
    } else if (isiPhone) {
      return 130;
    } else if (isiPhonePlus) {
      return 100;
    }
    return 85;
  }

  _keyboardDidShow () {
    // save current x,y values of scrollView
    this.scrollView.scrollTo({
      y:this.getScrollPosition(),
      x:0,
      animated:true
    });
    
  }

  _keyboardDidHide () {
    // save tags
    this.setState({loading:true});
    usersModel.postTags(this.state.tags, this.updateTagsCb.bind(this));
  }

  updateTagsCb(res, err) {
    this.setState({loading:false});
    if (!err && !res) {
      return;
    }
    if (err || !res) {
      AlertIOS.alert(
       'Alert',
       'Could Not Save Tags!'
      );
      return;
    }

    this.setState({tags:res.tags});
  }

  refresh() {
    this.setState({loading:true})
    this.fetchUserImage();
    usersModel.getUserSettings(((res, err) => {

      this.setState({
        loading:false
      });

      if (!err && !res) {
        return;
      }
      if (err || !res ) {

        AlertIOS.alert(
         'Alert',
         'Could not get user settings'
        );
        return;
      }

      this.setState(
        {
          radius:res.radius,
          time:res.hours,
          tags:res.tags,
        }
      );

    }).bind(this));
  }

  componentWillUnmount() {
    EventRegister.removeEventListener(this.refreshListener);
    this.keyboardDidShowListener.remove();
    this.keyboardDidHideListener.remove();
  }

  toBlockedUsers() {
	  this.props.navigation.navigate("BlockedUsers");
  }

  logout() {
    settingsModel.logout();
    fbModel.logout(() => {EventRegister.emit('FBLogoutSuccess', null);});
  }

  logoutPrompt() {
    AlertIOS.alert(
     'Logout',
     'Would you like to logout?',
     [
       {text: 'Yes', onPress: () => this.logout(), style: 'cancel'},
       {text: 'No', onPress: () => {}},
     ],
    );
  }

  deactivateAccount() {
    this.setState({loading:true});
    settingsModel.deactivateAccount(((res, err) => {
      this.setState({loading:false});
      if (!err && !res) {
        return;
      }

      if (err || !res) {
        AlertIOS.alert(
         'Alert',
         'Could Not Deactivate Account!'
        );
        return;
      }

      this.logout();
    }).bind(this)); 
  }

  deactivateAccountPrompt() {
    AlertIOS.alert(
     'Deactivate Account!',
     'Would you like to deactivate your account?',
     [
       {text: 'Yes', onPress: () => this.deactivateAccount(), style: 'cancel'},
       {text: 'No', onPress: () => {}},
     ],
    );
  }

  fetchUserImage() {
  	fbModel.getFBPP("me", ((err, res) => {
  		if (err) {
  			return;
  		}

  		var pictureURL = res.picture.data.url;
  		this.setState({url:pictureURL});
  	}).bind(this));
  }

  updateRadiusCb(res, err) {
    if (!err && !res) {
      return;
    }
    if (err || !res) {
      AlertIOS.alert(
       'Alert',
       'Could Not Save Radius!'
      );
      return;
    }

    this.setState({radius:res.radius});
  }

  updateRadius(radius) {
    this.setState({radius});
    graphModel.saveRadius(radius, this.updateRadiusCb.bind(this));
  }

  updateTimeCb(res, err) {
    if (!err && !res) {
      return;
    }
    if (err || !res) {
      AlertIOS.alert(
       'Alert',
       'Could Not Save Time!'
      );
      return;
    }
    this.setState({time:res.hours});
  }

  updateTime(time) {
    this.setState({time});
    graphModel.saveTime(time, this.updateTimeCb.bind(this));
  }

  renderRadiusText() {
    var text = this.state.radius;
    if (this.state.radius == 1) {
      return text + " hop"
    } else {
      return text + " hops"
    }
  }

  renderTimeText() {
    var text = this.state.time;
    if (this.state.time == 1) {
      return text + " hour"
    } else {
      return text + " hours"
    }
  }

  updateTag(index, tag) {
    tags = this.state.tags;
    tags[index] = tag;
    this.setState({tags:tags})
  }

  renderTagComponent(index) {
    return(
      <TextInput
        style={[styles.textInput, {width:"97%", height:27}]}
        placeholder="Add a Tag!"
        onChangeText={(text) => this.updateTag(index, text)}
        value={this.state.tags[index]}
        maxLength={30}
      />
    )
  }

  renderTagItem(index) {
    return (
      <ListItem 
        title={this.renderTagComponent(index)}
        titleStyle={styles.fullWidthButtonText}
        activeOpacity={1}
        hideChevron={true}
      />
    )
  }

  renderTags() {
    return(
      <List>
        {this.renderTagItem(0)}
        {this.renderTagItem(1)}
        {this.renderTagItem(2)}
      </List>
    )
  }

  render() {
		const navigate = this.props.navigation.navigate;
		return (
		  <View style={styles.fullscreen}>
		  	<InputScrollView scrollEnabled={true}
          ref={(input)=>{this.scrollView = input;}}>
		  		<View style={styles.settingAvatar}>
			  		<Avatar
					  // xlarge
            width = {width/1.5}
					  rounded
					  source={{uri: this.state.url}}
					  activeOpacity={0.7}
					/>
				</View>
        <Text style={styles.requestTitle}>Tags</Text>
        {this.renderTags()}
				<List>
					<ListItem
				  	title={
              <View style={styles.sliderTitle}>
                <Text style={styles.textFont}>Radius</Text>
                <Text style={styles.textFont}>{this.renderRadiusText()}</Text>
              </View>}
				  	subtitle={
				  			<View style={styles.slider}>
							  <Slider
							    value={this.state.radius}
							    step={1}
							    minimumValue={1}
							    maximumValue={4}
						   		minimumTrackTintColor={MIN_SLIDER_COLOR}
		            	maximumTrackTintColor={MAX_SLIDER_COLOR}
  	            	thumbTintColor={SLIDER_THUMB_COLOR}
		            	onValueChange={(radius)=>this.setState({radius})}
							    onSlidingComplete={this.updateRadius.bind(this)} />
							</View>
				  		}
				  		hideChevron={true}
				  />
				  <ListItem
			  		title={
              <View style={styles.sliderTitle}>
                <Text style={styles.textFont}>Time</Text>
                <Text style={styles.textFont}>{this.renderTimeText()}</Text>
              </View>}
			  		subtitle={
				    <View style={styles.slider}>
					  <Slider
					    value={this.state.time}
					    step={1}
					    minimumValue={1}
					    maximumValue={24}
					    minimumTrackTintColor={MIN_SLIDER_COLOR}
	            maximumTrackTintColor={MAX_SLIDER_COLOR}
	            thumbTintColor={SLIDER_THUMB_COLOR}
	            onValueChange={(time)=>this.setState({time})}
					    onSlidingComplete={this.updateTime.bind(this)} />
					  </View>}
					hideChevron={true}/>
				 	<ListItem 
						title={"Blocked Users"}
						titleStyle={styles.fullWidthButtonText}
						onPress={this.toBlockedUsers.bind(this)}
						activeOpacity={0.7}
				  	/>
				 	<ListItem
						title={"Logout"}
						titleStyle={styles.fullWidthButtonText}
						onPress={this.logoutPrompt.bind(this)}
						activeOpacity={0.7}
						hideChevron={true}
				  	/>
			  	<ListItem
						title={"Deactivate Account"}
						titleStyle={[styles.fullWidthButtonText, {color:DEACTIVATE_COLOR, fontWeight:"bold"}]}
						onPress={this.deactivateAccountPrompt.bind(this)}
						activeOpacity={0.7}
						hideChevron={true}
            />
  			</List> 
			</InputScrollView>
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




