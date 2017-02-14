import React from 'react';
import { Link } from 'react-router'

// Per service render
export default class ServiceDetail extends React.Component {

  render() {
    /*
    console.log("ServiceDetail");
    console.log(this.props);
    */
    return (
        <div className="ui raised segment">
              {this.props.status ? (
                <a className="ui green ribbon label">Online</a>
              ) : (
                <a className="ui red ribbon label">Offline</a>
              )}
              <span><strong>{this.props.name}</strong></span>
                <ul>
                  <li>Class: {this.props.sclass}</li>
                  <li>Manager: {this.props.manager}</li>
                  <li>Heartbeat: {this.props.heartbeat}</li>
                  <li>Autostart: {String(this.props.autostart)}</li>
                  <li>Status: {String(this.props.status)}</li>
                </ul>
      </div>
);
  }
}
