import React from 'react';
import PageHeader from '../components/Pageheader';
import StateList from '../containers/Statelist';

export default class State extends React.Component {
  render() {
    return (
        <div className="ui main container">
          <PageHeader name="State" desc="Current state for all services and devices"/>
          <StateList />
        </div>
    );
  }
}
