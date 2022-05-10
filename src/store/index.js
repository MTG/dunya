import fseReducer from '../reducers';
import {applyMiddleware, createStore} from "redux";
import thunkMiddleware from 'redux-thunk'
import { composeWithDevTools } from 'redux-devtools-extension'


export default function configureStore(preloadedState) {
  const composedEnhancer = composeWithDevTools(applyMiddleware(thunkMiddleware))
  const store = createStore(fseReducer, preloadedState, composedEnhancer)

  return store
}

