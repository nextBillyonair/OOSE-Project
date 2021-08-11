import React, { Component } from 'react';
import { Text, View, ActivityIndicator } from 'react-native';
import { SocialIcon } from 'react-native-elements';
import Video from 'react-native-video';
import { EventRegister } from 'react-native-event-listeners';

import { fbModel } from '../models/FBModel';
import { settingsModel } from '../models/SettingsModel'
import { user } from '../models/User';
import { styles } from '../StyleConstants';

class LoginView extends Component {

  componentWillMount() {
    this.setState({
      paused: false,
      loading: false
    });

    fbModel.getAccessToken(this.accessTokenCb.bind(this));
  }

  componentWillUnmount() {
    this.setState({
      paused:true
    });
  }

  accessTokenCb(data) {

    if (data != null){

      user.setUserID(data.userID);
      user.setAccessToken(data.accessToken);
      fbModel.getUserName((err, data) => {
        if (data) {
          user.setName(data.name);
          settingsModel.login((res, err) => {
            if (res) {
              EventRegister.emit('FBLoginSuccess', data);
            } else {
              this.setState({
                paused: false,
                loading: false
              });
            }
          });
        } else {
          alert("Facebook Login Failed");
          this.setState({
            paused: false,
            loading: false
          });
        }
      })
    }
  }

  loginCb(error, result) {
    if (error) {
      alert("Facebook Login Failed");
      this.setState({
        paused: false,
        loading: false
      });
    } else if (result.isCancelled) {
      this.setState({
        paused: false,
        loading: false
      });
    } else {
      fbModel.getAccessToken(this.accessTokenCb.bind(this));
    }
  }

  render() {
    return (
      <View style={styles.loginFullscreen}>
        <Video
          paused={ this.state.paused}
          source={require('../assets/giphy.mp4')}
          rate={1.0}
          volume={0.0}
          muted={true}
          resizeMode={"cover"}
          repeat
          style={styles.backgroundVideo}
        />
        <Text style={styles.titleText}>
          FOOTSIE
        </Text>
        <SocialIcon
          title='Sign In With Facebook'
          button
          type='facebook'
          iconSize={24}
          style={styles.buttonCenter}
          onPress={(() => {
            this.setState({
              paused: true,
              loading: true
            });
            fbModel.login(this.loginCb.bind(this))();
            
          }).bind(this)}
          button={true}
        />
        {this.state.loading &&
          <View style={styles.loading}>
            <ActivityIndicator size='large' />
          </View>
        }
      </View>
    ) ;
  }
};

export default LoginView;
