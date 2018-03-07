import PropTypes from 'prop-types';
import React from 'react';
import './LoadMoreResultsButton.scss';

const propTypes = {
  moreResults: PropTypes.number,
};

const LoadMoreResultsButton = props =>
  <button className="LoadMoreResultsButton" type="submit">
    Load More
  </button>;

LoadMoreResultsButton.propTypes = propTypes;
export default LoadMoreResultsButton;
