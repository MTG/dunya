import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';

const propTypes = {
  isVisible: PropTypes.bool,
};

const SearchTooltip = (props) => (
  <div className={`SearchTooltip${(props.isVisible) ? ' active' : ''}`}>
    Search by recording name or by selected filters
  </div>
);

const mapStateToProps = (state) => ({ isVisible: state.search.isTooltipVisible });

SearchTooltip.propTypes = propTypes;
export default connect(mapStateToProps, {})(SearchTooltip);
