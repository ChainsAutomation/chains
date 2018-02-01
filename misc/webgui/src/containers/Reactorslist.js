import React from 'react';
import {bindActionCreators} from 'redux';
import {connect} from 'react-redux';

import { loadReactorsData } from '../actions/index';

import ReactorDetail from '../components/ReactorDetail';

class ReactorsList extends React.Component {
  componentDidMount() {
    /*
    console.log("ReactorsList");
    console.log(this.props);
    */
    if(Object.keys(this.props.reactors).length === 0) {
      this.props.loadReactorsData();
    }

  }
  render() {
    let reactorNodes = []
    for (var srv in this.props.reactors) {
      const name = srv
      const heartbeat = this.props.reactors[srv]['heartbeat'];
      const rid = this.props.reactors[srv]['id'];
      const status = this.props.reactors[srv]['online'];
      reactorNodes.push(
        <div className="column">
          <ReactorDetail key={rid} rid={rid} name={name} heartbeat={heartbeat} status={status}/>
        </div>
      )
    }
    return (
      <div className="ui main container">
        <div className="ui two column stackable grid">
          {reactorNodes}
        </div>
      </div>
    );
  }
}

function mapStateToProps(state) {
    return {
        reactors: state.reactors
    };
}

function mapDispatchToProps(dispatch){
    return bindActionCreators({loadReactorsData: loadReactorsData}, dispatch);
}

export default connect(mapStateToProps, mapDispatchToProps)(ReactorsList);
