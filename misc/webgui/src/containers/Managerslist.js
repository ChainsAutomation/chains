import React from 'react';
import {bindActionCreators} from 'redux';
import {connect} from 'react-redux';

import { loadManagersData } from '../actions/index';

import ManagerDetail from '../components/ManagerDetail';

class ManagersList extends React.Component {
  componentDidMount() {
    /*
    console.log("ManagersList");
    console.log(this.props);
    */
    if(Object.keys(this.props.managers).length === 0) {
      this.props.loadManagersData();
    }

  }
  render() {
    let managerNodes = []
    for (var srv in this.props.managers) {
      const name = srv
      const heartbeat = this.props.managers[srv]['heartbeat'];
      const mid = this.props.managers[srv]['id'];
      const status = this.props.managers[srv]['online'];
      managerNodes.push(
        <div className="column">
          <ManagerDetail key={mid} mid={mid} name={name} heartbeat={heartbeat} status={status}/>
        </div>
      )
    }
    return (
      <div className="ui two column stackable grid">
        {managerNodes}
      </div>
    );
  }
}

function mapStateToProps(state) {
    return {
        managers: state.managers
    };
}

function mapDispatchToProps(dispatch){
    return bindActionCreators({loadManagersData: loadManagersData}, dispatch);
}

export default connect(mapStateToProps, mapDispatchToProps)(ManagersList);
