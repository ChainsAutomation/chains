import React from 'react';
import {bindActionCreators} from 'redux';
import {connect} from 'react-redux';

import { loadServicesData } from '../actions/index';

import ServiceDetail from '../components/ServiceDetail';

class ServicesList extends React.Component {
  componentDidMount() {
    /*
    console.log("ServiceList");
    console.log(this.props);
    */
    if(Object.keys(this.props.services).length === 0) {
      this.props.loadServicesData();
    }
  }

  render() {
    /*
    var serviceNodes = this.props.services.map(function(service, index) {
      return (
        <ServiceDetail name={service.name} status={service.online} key={index}>
          {service.id}
        </ServiceDetail>
      );
    });
    */
    // var serviceNodes = this.props.services;
    let serviceNodesLeft = [];
    let serviceNodesRight = [];
    var scount = 0;
    for (var srv in this.props.services) {
      if(scount % 2 === 0) {
        var serviceNodes = serviceNodesLeft;
      } else {
        var serviceNodes = serviceNodesRight;
      }
      const sid = this.props.services[srv]['id'];
      const sname = this.props.services[srv]['name'];
      const sonline = this.props.services[srv]['online'];
      const sclass = this.props.services[srv]['class'];
      const sautostart = this.props.services[srv]['autostart'];
      const smanager = this.props.services[srv]['manager'];
      let heartdate = "offline";
      if (this.props.services[srv]['heartbeat'] !== 0) {
        const d = new Date(this.props.services[srv]['heartbeat'] * 1000);
        heartdate = d.toLocaleTimeString() + ' - ' + d.toLocaleDateString();
      }
      const srvdet = <ServiceDetail key={sid} name={sname} status={sonline} sclass={sclass} autostart={sautostart} manager={smanager} heartbeat={heartdate}/>;
      if(sonline) {
        serviceNodes.unshift(srvdet);
        //serviceNodes.unshift(<ServiceDetail key={sid} name={sname} status={sonline} sclass={sclass} autostart={sautostart} manager={smanager} heartbeat={heartdate}/>);
      } else {
        serviceNodes.push(srvdet);
        //serviceNodes.push(<ServiceDetail key={sid} name={sname} status={sonline} sclass={sclass} autostart={sautostart} manager={smanager} heartbeat={heartdate}/>);
      }
      scount++;
    }
    return (
      <div className="ui two column grid">
        <div className="column">
            {serviceNodesLeft}
        </div>
        <div className="column">
            {serviceNodesRight}
        </div>
      </div>
    );
  }
}

function mapStateToProps(state) {
    return {
        services: state.services
    };
}

function mapDispatchToProps(dispatch){
    return bindActionCreators({loadServicesData: loadServicesData}, dispatch);
}

export default connect(mapStateToProps, mapDispatchToProps)(ServicesList);
