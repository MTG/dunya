import PropTypes from 'prop-types';
import React from 'react';
import { Provider } from 'react-redux';
import Navbar from '../Navbar';
import LoginModal from '../LoginModal';
import Sidebar from '../Sidebar';
import MainBody from '../MainBody';
import ResizeListener from '../ResizeListener';
import MobileMenu from '../MobileMenu';
import './App.scss';

const propTypes = {
  store: PropTypes.object,
};

const App = props => (
  <Provider store={props.store}>
    <div>
      <Navbar />
      <div className="flex-content-row">
        <Sidebar />
        <MainBody />
      </div>
      <LoginModal />
      <MobileMenu />
      <ResizeListener />
    </div>
  </Provider>
);

App.propTypes = propTypes;
export default App;
