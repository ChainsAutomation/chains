import React from 'react'
import PageHeader from '../components/Pageheader';

export default class Settings extends React.Component {
  render() {
    return (
        <div className="ui main container">
          <PageHeader name="Settings" desc="Configure chains settings here"/>
        </div>
    );
  }
}
