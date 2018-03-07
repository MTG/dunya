import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';
import { toggleFiltersMenu } from 'actions/mobileMenu';
import './MobileMenu.scss';

const propTypes = {
  toggleFiltersMenu: PropTypes.func,
};

const ShowMobileMenu = props =>
  <li className="ShowMobileMenu">
    <button onClick={props.toggleFiltersMenu}>
      <i className="fa fa-navicon" aria-hidden />
      Show filters
    </button>
  </li>;

ShowMobileMenu.propTypes = propTypes;
export default connect(() => ({}), { toggleFiltersMenu })(ShowMobileMenu);
