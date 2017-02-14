/*
 * Chains webgui 
 *
 */

// TODO in v1
// dashboard page
// services page - /services
// per service pages - /services/:serviceid
// per device page - /services/:serviceid/:deviceName
// system page, holds whole system info - /system
// reactor page - /system/reactor
// per reactor page (?) - /system/reactor/:reactorid
// managers page - /system/managers
// per manager page - /system/managers/:managerid

import React from 'react';
import ReactDOM from 'react-dom';
import { Router, Route, IndexRoute, hashHistory } from 'react-router';
import { Provider } from 'react-redux';
import { createStore, applyMiddleware } from 'redux';
import thunk from 'redux-thunk';
import { composeWithDevTools } from 'redux-devtools-extension';

// imports from project
import allReducers from './reducers';

// containers and components
import Layout from './pages/Layout';

const app = document.getElementById('content');

const defaultState = {
  cstate: {},
  services: {},
  profiles: [],
  activeProfile: false,
  managers: {},
  reactors: {}
};


// init store with normal redux
// const store = createStore(allReducers);

// init store with redux devtools browser plugin support
//const store = createStore(allReducers, composeWithDevTools());

const store = createStore(allReducers, defaultState, composeWithDevTools(applyMiddleware(thunk)));
console.log("app.js");
console.log(store);

ReactDOM.render(
  <Provider store={store}>
    <Layout />
  </Provider>,
  app
);
