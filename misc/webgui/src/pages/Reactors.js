import React from 'react';
import ReactorsList from '../containers/Reactorslist';
import PageHeader from '../components/Pageheader';


export default class Reactors extends React.Component {
  render() {
    return (
      <div className="ui main text container">
        <PageHeader name="Reactors" desc="Registered Chains Reactors"/>
        <ReactorsList />
      </div>
    );
  }
}
