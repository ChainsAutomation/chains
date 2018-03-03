import React from 'react';
import PageHeader from '../components/Pageheader';

export default class About extends React.Component {
  render() {
    return (
      <div className="ui main container">
        <PageHeader name="About" desc="Information about the Chains project"/>
      </div>
    );
  }
}
