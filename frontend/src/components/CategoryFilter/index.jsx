import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';
import { toggleExpandCategory } from 'actions/filtersData';
import CategoryFilterList from './CategoryFilterList';
import SearchOverviewEntry from '../Search/SearchOverviewEntry';
import { makeGetVisibleCategoryData, makeGetVisibleSelected, getEntryId,
  makeGetDetailsForCategorySelectedEntries } from '../../selectors/filtersData';
import { SHOW_ONLY_VISIBLE_SELECTED } from '../../settings';
import './CategoryFilter.scss';
import './CategoryFilterSelectedList.scss';
import sortByName from '../../utils/sortByName';

const propTypes = {
  category: PropTypes.string,
  data: PropTypes.array,
  selected: PropTypes.array,
  selectedItemsCount: PropTypes.number,
  toggleExpandCategory: PropTypes.func,
  isExpanded: PropTypes.bool,
};

const CategoryFilter = (props) => {
  const enrichedEntries = props.selected.map(entry =>
    Object.assign({}, entry, { category: props.category }));
  const sortedEntries = enrichedEntries.sort(sortByName);
  return (
    <li
      className={`CategoryFilter${(props.isExpanded) ? ' active' : ''}`}
      role="menuitem"
      aria-haspopup
      aria-labelledby="categoryEntries"
    >
      <a
        tabIndex="0"
        onClick={() => props.toggleExpandCategory(props.category)}
        className="CategoryFilter__title"
      >
        {props.category}
        <i className={`${(props.isExpanded) ? ' fa fa-lg fa-minus-circle' : ' fa fa-lg fa-plus-circle'}`} aria-hidden />
        <span className="CategoryFilter__selected-counter">
          {(props.selectedItemsCount) ? props.selectedItemsCount : null}
        </span>
      </a>
      <div
        className={`CategoryFilter__section-content${(props.isExpanded) ? ' active' : ''}`}
      >
        <header className="CategoryFilter__category-section-header">Available</header>
        <CategoryFilterList data={props.data} category={props.category} />
        <header className="CategoryFilter__category-section-header">Selected</header>
        <ul className="CategoryFilter__category-catalogue-list">
          {sortedEntries.map(entry =>
            <SearchOverviewEntry key={getEntryId(entry)} entry={entry} />)}
        </ul>
      </div>
    </li>
  );
};

const makeMapStateToProps = (_, ownProps) => {
  const { category } = ownProps;
  let { data } = ownProps;
  const getVisibleCategoryData = makeGetVisibleCategoryData();
  const getVisibleSelected = makeGetVisibleSelected();
  const getDetailsForCategorySelectedEntries = makeGetDetailsForCategorySelectedEntries();
  return (state) => {
    data = getVisibleCategoryData(state, ownProps);
    const visibleSelected = getVisibleSelected(state, ownProps);
    const allSelected = getDetailsForCategorySelectedEntries(state, ownProps);
    const selected = (SHOW_ONLY_VISIBLE_SELECTED) ?
      visibleSelected : allSelected;
    const selectedItemsCount = selected.length;
    const isExpanded = state.filtersData.expandedCategories.includes(category);
    return {
      data,
      selected,
      category,
      selectedItemsCount,
      isExpanded,
    };
  };
};

CategoryFilter.propTypes = propTypes;
export default connect(makeMapStateToProps, { toggleExpandCategory })(CategoryFilter);
