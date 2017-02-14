import React, {Component} from 'react';
import {bindActionCreators} from 'redux';
import {connect} from 'react-redux';
import {selectProfile} from '../actions/index';
import ProfileDetail from './profile-detail';

class ProfileList extends Component {

    renderList() {
      /*
        console.log("ProfileList");
        console.log(this.props);
      */
        return this.props.profiles.map((profile) => {
            return (
                <div
                    className="item"
                    key={profile.id}
                    onClick={() => this.props.selectProfile(profile)}
                >
                    <img className="ui avatar image" src={profile.thumbnail} />
                    <div className="content">
                      <div className="header">{profile.name}</div>
                      {profile.description}
                    </div>
                </div>
            );
        });
    }

    render() {
        // console.log(<ProfileDetail />);
        return (
            <div className="ui horizontal list">
                {this.renderList()}
                <ProfileDetail />
            </div>
        );
    }

}

// Get apps state and pass it as props to ProfileList
//      > whenever state changes, the ProfileList will automatically re-render
function mapStateToProps(state) {
    return {
        profiles: state.profiles
    };
}

// Get actions and pass them as props to to ProfileList
//      > now ProfileList has this.props.selectProfile
function mapDispatchToProps(dispatch){
    return bindActionCreators({selectProfile: selectProfile}, dispatch);
}

// We don't want to return the plain ProfileList (component) anymore, we want to return the smart Container
//      > ProfileList is now aware of state and actions
export default connect(mapStateToProps, mapDispatchToProps)(ProfileList);
