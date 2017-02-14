import React from 'react';
import { Link } from 'react-router';

export default class Nav extends React.Component {
  render() {
    return (
          <div className="ui fixed inverted menu">
            <div className="ui container">
              <div className="item"><img src="/chains-logo.png" /></div>
              <Link className="item" activeClassName="active" activeOnlyWhenExact to="/" >Dashboards</Link>
              <Link className="item" activeClassName="active" activeOnlyWhenExact to="/Services">Services</Link>
              <Link className="item" activeClassName="active" activeOnlyWhenExact to="/State">State</Link>
              <Link className="item" activeClassName="active" activeOnlyWhenExact to="/Managers">Managers</Link>
              <Link className="item" activeClassName="active" activeOnlyWhenExact to="/Reactors">Reactors</Link>
              <Link className="item" activeClassName="active" activeOnlyWhenExact to="/Settings">Settings</Link>
              <Link className="item" activeClassName="active" activeOnlyWhenExact to="/About">About</Link>
            </div>
          </div>
    );
  }
}
