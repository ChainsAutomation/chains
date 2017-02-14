import React from 'react';

import PageHeader from '../components/Pageheader';
import ProfileList from '../containers/profile-list';

export default class Dashboard extends React.Component {
  render() {
    return (
      <div className="ui main text container">
        <PageHeader name="Dashboards" desc="Your most used services and devices" />
        <ProfileList />
      </div>
    );
  }
}
