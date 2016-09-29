import { UPDATE_WINDOW_SIZE } from 'actions/actionTypes';

const initialState = {
  width: window.innerWidth,
  height: window.innerHeight,
};

const windowSize = (state = initialState, action) => {
  switch (action.type) {
    case UPDATE_WINDOW_SIZE: {
      const { newSize } = action;
      const { width, height } = newSize;
      return { width, height };
    }
    default:
      return state;
  }
};

export default windowSize;
