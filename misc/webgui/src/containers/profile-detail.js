import React, {Component} from 'react';
import {connect} from 'react-redux';

/*
 * We need "if(!this.props.profile)" because we set state to null by default
 * */

class ProfileDetail extends Component {
    render() {
      /*
        console.log("ProfileDetail");
        console.log(this.props);
        */
        if (!this.props.profile) {
            return (<li className="profile" style={{float: 'right'}}>Select a profile...</li>);
        }
        return (
            <li className="profile" style={{float: 'right'}}>
                Description: {this.props.profile.description}
            </li>
        );
    }
}

// "state.activeProfile" is set in reducers/index.js
function mapStateToProps(state) {
    return {
        profile: state.activeProfile
    };
}

export default connect(mapStateToProps)(ProfileDetail);
