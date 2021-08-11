import React, { Component } from 'react';
import { EventRegister } from 'react-native-event-listeners';

import LoginView from './views/LoginView.js';
import TabBarView from './views/TabBarView.js';

import { fbModel } from './models/FBModel';
import { user } from './models/User';

import { createTransition, FlipX, SlideUp, SlideDown } from 'react-native-transition';


const Transition = createTransition();

export default class Footsie extends Component {
  constructor(){
    super();
    console.disableYellowBox = true;
    this.state = {
      viewOne: true
    };

  }

  login() {
    Transition.show(
      <TabBarView/>
    , SlideUp);
  }

  logout() {
    Transition.show(
      <LoginView/>
    , SlideDown);
  }

  componentWillMount() {
    this.loginListener = EventRegister.addEventListener('FBLoginSuccess', this.login.bind(this));
    this.logoutListener = EventRegister.addEventListener('FBLogoutSuccess', this.logout.bind(this));
  }

  componentWillUnmount() {
    EventRegister.removeEventListener(this.loginListener)
    EventRegister.removeEventListener(this.logoutListener)
  }

  render() {
    if (this.state.viewOne) {
      return (
        <Transition>
          <LoginView />
        </Transition>
      );
    } else {
      return (
        <Transition>
          <TabBarView />
        </Transition>
      );
    }
  }
};

