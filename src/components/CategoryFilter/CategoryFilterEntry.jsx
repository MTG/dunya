import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';
import { toggleSelectedEntry } from '../../actions/filtersData';
import { getEntryId, makeIsEntrySelected } from '../../selectors/filtersData';

const propTypes = {
  category: PropTypes.string,
  isSelected: PropTypes.bool,
  toggleSelectedEntry: PropTypes.func,
  entry: PropTypes.object,
};

const CategoryFilterEntry = props => (
  <li
    key={getEntryId(props.entry)}
    className={`CategoryFilter__category-entry${(props.isSelected) ? ' active' : ''}`}
    role="menuitem"
    tabIndex="0"
    onClick={() => props.toggleSelectedEntry(getEntryId(props.entry), props.category)}
  >{props.entry.name}
  </li>
);

const makeMapStateToProps = (_, ownProps) => {
  const { entry, category } = ownProps;
  const isEntrySelected = makeIsEntrySelected(entry);
  return (state) => {
    const isSelected = isEntrySelected(state, ownProps);
    return {
      name: entry.name,
      category,
      isSelected,
      entry,
    };
  };
};

CategoryFilterEntry.propTypes = propTypes;
export default connect(makeMapStateToProps, { toggleSelectedEntry })(CategoryFilterEntry);
