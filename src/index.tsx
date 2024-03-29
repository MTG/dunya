import React from 'react';
import App from './components/App';
import configureStore from './store';
import {createRoot} from "react-dom/client";

const persistedStore = undefined;
const store = configureStore(persistedStore);

const container = document.getElementById('root')!;
const root = createRoot(container);

root.render(
  <React.StrictMode>
    <App store={store} />
  </React.StrictMode>
);
