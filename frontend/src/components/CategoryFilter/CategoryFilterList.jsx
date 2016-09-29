import React from 'react';
import CategoryFilterEntry from './CategoryFilterEntry';
import CategoryFilterSearch from './CategoryFilterSearch';
import { getEntryId } from '../../selectors/filtersData';
import './CategoryFilterList.scss';

const propTypes = {
  category: React.PropTypes.string,
  data: React.PropTypes.array,
};

const CategoryFilterList = props => (
  <div className="CategoryFilter__category-catalogue">
    <ul
      className="CategoryFilter__category-all-entries-list"
      role="menu"
    >
    {props.data.map(entry =>
      <CategoryFilterEntry key={getEntryId(entry)} category={props.category} entry={entry} />)}
    </ul>
    <CategoryFilterSearch category={props.category} />
  </div>
);

CategoryFilterList.propTypes = propTypes;
export default CategoryFilterList;
