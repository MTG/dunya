import React from 'react';
import { connect } from 'react-redux';
import { DATA_FETCH_STATUS } from 'constants';
import { getSearchResults } from 'actions/search';
import SearchInput from './SearchInput';
import SearchButton from './SearchButton';
import './Search.scss';

const propTypes = {
  getSearchResults: React.PropTypes.func,
  isSearchEnabled: React.PropTypes.bool,
};

const Search = props => (
  <div className="Search">
    <form
      onSubmit={(evt) => {
        evt.preventDefault();
        props.getSearchResults();
      }}
    >
      <label className="Search__label" htmlFor="search">
        <header>Search</header>
        <SearchInput />
      </label>
      <SearchButton isEnabled={props.isSearchEnabled} />
    </form>
  </div>
);

const mapStateToProps = state => ({
  isSearchEnabled: state.search.status !== DATA_FETCH_STATUS.PROGRESS,
});

Search.propTypes = propTypes;
export default connect(mapStateToProps, { getSearchResults })(Search);
