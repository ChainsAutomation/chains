import { combineReducers } from 'redux';
import ProfileReducer from './reducer-profile';
import ActiveProfileReducer from './reducer-active-profile';
import ServicesReducer from './reducer-services';
import StateReducer from './reducer-state';
import ManagersReducer from './reducer-managers';
import ReactorsReducer from './reducer-reactors';

const allReducers = combineReducers({
    profiles: ProfileReducer,
    activeProfile: ActiveProfileReducer,
    services: ServicesReducer,
    cstate: StateReducer,
    managers: ManagersReducer,
    reactors: ReactorsReducer
});

export default allReducers;
