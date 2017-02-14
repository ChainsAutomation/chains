import React from 'react'

export default class PageHeader extends React.Component {
  render() {
    return (
      <h2 className="ui header">
        <img src="/chains-logo.png" />
        <div className="content">
          {this.props.name}
          <div className="sub header">{this.props.desc}</div>
        </div>
      </h2>
    );
  }
}
