import Config from '../config';

// actions
//
export const selectProfile = (profile) => {
    // console.log("You clicked on profile: ", profile.name);
    return {
        type: 'PROFILE_SELECTED',
        payload: profile
    };
};


/*
export const stateLoading = (loading) => {
  return {
    type: "STATE_LOADING",
    loading
  };
};

export const ServicesLoading = (loading) => {
  return {
    type: "SERVICES_LOADING",
    loading
  };
};
*/


export function loadStateData() {
  return dispatch => fetch(`${Config.apiUrl}/state`, {credentials: 'same-origin'}) // Redux Thunk handles these
    .then(res => res.json())
    .then(
      data => dispatch({ type: 'LOAD_STATE_SUCCESS', payload: data['data'] }),
      err => dispatch({ type: 'LOAD_STATE_FAILURE', err })
    );
}

export function loadServicesData() {
  return dispatch => fetch(`${Config.apiUrl}/services`, {credentials: 'same-origin'}) // Redux Thunk handles these
    .then(res => res.json())
    .then(
      data => dispatch({ type: 'LOAD_SERVICES_SUCCESS', payload: data }),
      err => dispatch({ type: 'LOAD_SERVICES_FAILURE', err })
    );
}

export function loadManagersData() {
  return dispatch => fetch(`${Config.apiUrl}/managers`, {credentials: 'same-origin'}) // Redux Thunk handles these
    .then(res => res.json())
    .then(
      data => dispatch({ type: 'LOAD_MANAGERS_SUCCESS', payload: data }),
      err => dispatch({ type: 'LOAD_MANAGERS_FAILURE', err })
    );
}

export function loadReactorsData() {
  // console.log("Running loadReactorsData...");
  return dispatch => fetch(`${Config.apiUrl}/reactors`, {credentials: 'same-origin'}) // Redux Thunk handles these
    .then(res => res.json())
    .then(
      data => dispatch({ type: 'LOAD_REACTORS_SUCCESS', payload: data }),
      err => dispatch({ type: 'LOAD_REACTORS_FAILURE', err })
    );
}
