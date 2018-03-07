import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';
import RefineSearch from './RefineSearch';
import './Sidebar.scss';
import { breakpoints } from '../../stylesheets/variables.json';

const breakpoint = parseInt(breakpoints.medium, 10);

const propTypes = {
  windowSize: PropTypes.object,
};

const Sidebar = (props) => {
  const content = (props.windowSize.width >= breakpoint) ? <RefineSearch /> : null;
  return (
    <aside className="Sidebar">
      {content}
    </aside>
  );
};

Sidebar.propTypes = propTypes;
const mapStateToProps = state => ({ windowSize: state.windowSize });
export default connect(mapStateToProps, {})(Sidebar);
