import React from 'react';
import { Match, Link, BrowserRouter } from 'react-router';

import Nav from '../components/Nav';
import Footer from '../components/Footer';
// import ProfileDetail from '../containers/profile-detail';
import Dashboard from './Dashboard';
import Services from './Services';
import ServiceInfo from './Serviceinfo';
import State from './State';
import Managers from './Managers';
import Reactors from './Reactors';
import Settings from './Settings';
import About from './About';
import NotFound from './Notfound';

export default class Layout extends React.Component {
  render() {
    return (
      <BrowserRouter>
        <div>
          <Nav />
          <div className="pusher" style={{paddingTop: '50px'}}>
          </div>
          {/*<div className="ui main text container">*/}
            <Match exactly pattern="/" component={Dashboard} />
            <Match exactly pattern="/Services" component={Services} />
            <Match exactly pattern="/State" component={State} />
            <Match pattern="/Services/:serviceid" component={ServiceInfo} />
            <Match exactly pattern="/Managers" component={Managers} />
            <Match exactly pattern="/Reactors" component={Reactors} />
            <Match exactly pattern="/Settings" component={Settings} />
            <Match exactly pattern="/About" component={About} />
            { /* <Match exactly pattern='*' component={NotFound} /> */ }
          {/*</div>*/}
          <Footer name="" />
        </div>
      </BrowserRouter>
    );
  }
}
