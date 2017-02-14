import React from 'react';
import { Link } from 'react-router'

// Per service render
export default class ManagerDetail extends React.Component {

  render() {
    /*
    console.log("ManagerDetail");
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
            <li>ID: {this.props.mid}</li>
            <li>Heartbeat: {this.props.heartbeat}</li>
            <li>Status: {String(this.props.status)}</li>
          </ul>
        </div>
      );
  }
}
