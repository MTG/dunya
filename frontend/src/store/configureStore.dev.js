import { createStore, applyMiddleware, compose } from 'redux';
import thunk from 'redux-thunk';
import { default as mainReducer } from '../reducers';

export default function configureStore(initialState) {
  const store = createStore(
    mainReducer,
    initialState,
    compose(
      applyMiddleware(thunk),
      // use the redux devtools extension
      window.devToolsExtension && window.devToolsExtension()
    )
  );

  if (module.hot) {
    // Enable Webpack hot module replacement for reducers
    module.hot.accept('../reducers', () => {
      store.replaceReducer(mainReducer);
    });
  }

  return store;
}
