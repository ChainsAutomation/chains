import React from 'react';

// Per service render
export default class StateDevice extends React.Component {

  render() {
    /*
    console.log("StateDevice");
    console.log(this.props);
    //*/
    const ddata = this.props.ddata;
    let devData = [];
    for (var dev in ddata['data']) {
      const dItem = dev;
      const dVal = ddata['data'][dev]['value'];
      const attr = <div key={dItem}><div className="header">{dItem}</div><div className="meta">{dVal}</div></div>;
      //console.log(attr);
      devData.push(attr);
    }
    return (
      <div className="ui raised card">
        <div className="content">
          <div className="header">{this.props.name}</div>
            <div className="meta">
              <span className="category">{ddata.class}</span>
            </div>
            <div className="description">
              {devData}
            </div>
          </div>
          <div className="extra content">
            <div className="right floated author">
              <img className="ui avatar image" src={ddata.icon} /> {ddata.type}
            </div>
          </div>
        </div>
);
  }
}


/*



<div className="card">
  <div className="image">
      <img src="http://mrg.bz/IxQIgC" />
  </div>
  <div className="content">
    {devData}
  </div>
  <div className="ui bottom attached basic buttons">
    <button className="ui button"><i className="pencil icon"></i></button>
    <button className="ui button"><i className="trash icon"></i></button>
  </div>
</div>





*/
