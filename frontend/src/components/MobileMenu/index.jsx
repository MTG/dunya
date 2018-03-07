import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';
import { toggleFiltersMenu } from 'actions/mobileMenu';
import RefineSearch from '../Sidebar/RefineSearch';
import './MobileMenu.scss';
import { breakpoints } from '../../stylesheets/variables.json';

const breakpoint = parseInt(breakpoints.medium, 10);

const propTypes = {
  isVisible: PropTypes.bool,
  windowSize: PropTypes.object,
  toggleFiltersMenu: PropTypes.func,
};

const MobileMenu = (props) => {
  const content = (props.windowSize.width < breakpoint) ? <RefineSearch /> : null;
  return (
    <div className={`MobileMenu${(props.isVisible) ? ' active' : ''}`}>
      <button
        className="MobileMenu__close-button"
        onClick={props.toggleFiltersMenu}
      />
      <div className="MobileMenu__wrapper">
        {content}
      </div>
    </div>
  );
};

MobileMenu.propTypes = propTypes;
const mapStateToProps = state => ({
  isVisible: state.mobileMenu.isVisible,
  windowSize: state.windowSize,
});
export default connect(mapStateToProps, { toggleFiltersMenu })(MobileMenu);
