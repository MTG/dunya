import React from 'react';
import './SearchButton.scss';

const propTypes = {
  isEnabled: React.PropTypes.bool,
};

const SearchButton = props =>
  <button className="SearchButton" type="submit" disabled={!props.isEnabled}>Search</button>;

SearchButton.propTypes = propTypes;
export default SearchButton;
