import React from 'react'
import ServicesList from '../containers/ServicesList'
import PageHeader from '../components/Pageheader';

export default class Services extends React.Component {
  render() {
    return (
      <div className="ui main container">
        <PageHeader name="Services" desc="All configured services"/>
        <ServicesList />
      </div>
    );
  }
}
