import { createStore, applyMiddleware } from 'redux';
import thunk from 'redux-thunk';
import fseReducer from '../reducers';

export default function configureStore(initialState) {
  return createStore(
    fseReducer,
    initialState,
    applyMiddleware(thunk)
  );
}
