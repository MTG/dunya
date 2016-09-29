import React from 'react';
import { connect } from 'react-redux';
import pluralize from '../../utils/pluralRules';
import { setSearchCategory, resetSearchCategory } from '../../actions/filtersData';

const propTypes = {
  category: React.PropTypes.string,
  currentSearch: React.PropTypes.string,
  setSearchCategory: React.PropTypes.func,
  resetSearchCategory: React.PropTypes.func,
};

const updateCategorySearch = (evt, category, setSearch) => {
  const search = evt.target.value;
  setSearch(search, category);
};

const CategoryFilterSearch = props => (
  <div className="CategoryFilter__category-catalogue-search">
    <i
      className="fa fa-search CategoryFilter__category-catalogue-search__search-icon"
      aria-hidden
    />
    <input
      type="text"
      className="CategoryFilter__category-catalogue-search__input"
      placeholder={`Enter ${pluralize(props.category, 1)} name`}
      onChange={evt => updateCategorySearch(evt, props.category, props.setSearchCategory)}
      value={props.currentSearch}
      onKeyDown={(evt) => {
        if (evt.keyCode === 27) {
          // reset search when pressing escape
          props.resetSearchCategory(props.category);
        }
      }}
    />
  </div>
);

const makeMapStateToProps = (_, ownProps) => {
  const { category } = ownProps;
  return (state) => {
    const currentSearch = state.filtersData.searchedData[category];
    return { category, currentSearch };
  };
};

CategoryFilterSearch.propTypes = propTypes;
export default connect(makeMapStateToProps, {
  setSearchCategory,
  resetSearchCategory,
})(CategoryFilterSearch);
