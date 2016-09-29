import 'babel-polyfill';
import 'normalize.css';
import 'whatwg-fetch';
import React from 'react';
import { render } from 'react-dom';
import { AppContainer } from 'react-hot-loader';
import { loadState, saveState } from 'utils/sessionStorage';
import { STORE_APPLICATION_STATE } from 'settings';
import App from 'components/App';
import configureStore from 'store';

const persistedStore = (STORE_APPLICATION_STATE) ? loadState() : undefined;
const store = configureStore(persistedStore);

if (STORE_APPLICATION_STATE) {
  store.subscribe(() => {
    saveState(store.getState());
  });
}

render(<AppContainer><App store={store} /></AppContainer>, document.getElementById('app'));

if (module.hot) {
  module.hot.accept('./components/App', () => {
    const AppComponent = require('./components/App').default; // eslint-disable-line

    render(
      <AppContainer>
        <AppComponent store={store} />
      </AppContainer>,
      document.getElementById('app')
    );
  });
}
