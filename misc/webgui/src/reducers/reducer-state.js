export default function (cstate = [], action) {
    switch (action.type) {
        case 'LOAD_STATE_SUCCESS':
          return action.payload;
        default:
          return cstate;
    }
}
