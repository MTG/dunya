import React from 'react';
import Logo from '../Logo';
import NavLinks from './NavLinks';
import './Navbar.scss';

const Navbar = () => (
  <div className="Navbar">
    <div className="Navbar__content">
      <div className="Navbar__logo-container">
        <a href="https://dunya.compmusic.upf.edu" style={{ verticalAlign: 'top' }}>
          <Logo />
        </a><span style={{ verticalAlign: 'top', top: '20px', margin: '10px'}} className="NavLinks__item">{window.catalogue}</span>
      </div>
      <NavLinks />
    </div>
    <div className="Navbar__divider" />
  </div>
);

export default Navbar;
