import { TOGGLE_FILTERS_MENU } from 'actions/actionTypes';

const initialState = {
  isVisible: false,
};

export default (state = initialState, action) => {
  switch (action.type) {
    case TOGGLE_FILTERS_MENU: {
      return Object.assign({}, state, {
        isVisible: !state.isVisible,
      });
    }
    default: {
      return state;
    }
  }
};
