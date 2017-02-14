export default function (state = {}, action) {
    switch (action.type) {
        case 'LOAD_REACTORS_SUCCESS':
          return action.payload;
        default:
          return state;
    }
}
