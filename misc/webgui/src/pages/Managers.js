import React from 'react'
import PageHeader from '../components/Pageheader';
import ManagersList from '../containers/Managerslist';

export default class Managers extends React.Component {
  render() {
    return (
        <div className="ui main text container">
          <PageHeader name="Managers" desc="Registered Chains Managers"/>
          <ManagersList />
        </div>
    );
  }
}
