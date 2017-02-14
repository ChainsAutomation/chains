/*


UNUSED


*/


import React from 'react';

import StateDevice from '../components/Statedevice';

import {devTimer, devUnknown, devTemperature, devHumidity} from '../chains/devtypes';
// Per service render
export default class StateService extends React.Component {

  dtype(data) {
    /*
    console.log('device type');
    console.log(data);
    */
    if (typeof(data) !== "object") {
      data = {};
    }
    if (! data.hasOwnProperty('type')) {
      data.type = 'unknown';
    }
    console.log("device type: " + data.type);
    let newdata = {};
    switch(data.type) {
      case "time":
        newdata = devTimer(data);
        // console.log(JSON.stringify(newdata));
        return newdata;
      default:
        newdata = devUnknown(data);
        // console.log(JSON.stringify(newdata));
        return newdata;
    }
  }
  render() {
    /*
    console.log("StateService");
    console.log(this.props);
    */
    let stateDevNodes = [];
    for (var dev in this.props.sdata) {
      if (dev !== "_service") {
        //console.log(dev);
        const dName = dev;
        const dType = this.props.sdata[dev]['type'];
        //const ddata = this.dtype(this.props.sdata[dev]['data']);
        const ddata = this.dtype(this.props.sdata[dev]);
        stateDevNodes.push(<StateDevice key={dev} name={dName} suid={this.props.suid} ddata={ddata}/>);
      }
    }
    return (
      <span>
        {stateDevNodes}
      </span>
);
  }
}
