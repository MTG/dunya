import React from 'react';
import App from './components/App';
import configureStore from './store';
import {createRoot} from "react-dom/client";
import reportWebVitals from "./reportWebVitals";

const persistedStore = undefined;
const store = configureStore(persistedStore);

const container = document.getElementById('root')!;
const root = createRoot(container);

// @ts-ignore
window.catalogue = "carnatic";
// @ts-ignore
window.username = "{{ user.username }}";

root.render(
  <React.StrictMode>
    <App store={store} />
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
