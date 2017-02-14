import React from 'react';
import {bindActionCreators} from 'redux';
import {connect} from 'react-redux';

import { loadStateData } from '../actions/index';

import StateDevice from '../components/Statedevice';
import {dtype, devTimer, devUnknown, devTemperature, devHumidity} from '../chains/devtypes';


class StateList extends React.Component {
  componentDidMount() {
    if(Object.keys(this.props.cstate).length === 0) {
      this.props.loadStateData();
    }
  }

  render() {
    const cstate = this.props.cstate
    let stateServiceNodes = [];
    let stateDevNodes = [];

    for (var srv in cstate) {
      const sid = srv;
      const data = cstate[srv];
      for (var dev in data) {
        if (dev !== "_service") {
          const dName = dev;
          const dType = data[dev]['type'];
          const ddata = dtype(data[dev]);
          stateDevNodes.push(<StateDevice key={dev} name={dName} suid={sid} ddata={ddata}/>);
        }
      }

    }
    return (
      <div className="ui main container">
      <div className="ui cards">
      {/*<div className="ui grid container">*/}
        {stateDevNodes}
      </div>
    </div>
    );
  }
}

function mapStateToProps(state) {
    return {
        cstate: state.cstate
    };
}

function mapDispatchToProps(dispatch){
    return bindActionCreators({loadStateData: loadStateData}, dispatch);
}

export default connect(mapStateToProps, mapDispatchToProps)(StateList);
