import React from 'react';
import { connect } from 'react-redux';
import { SELF_EXPLANATORY_CATEGORY_ITEMS } from 'settings';
import { toggleSelectedEntry } from 'actions/filtersData';
import { getEntryId } from 'selectors/filtersData';
import pluralize from 'utils/pluralRules';
import './SearchOverviewEntry.scss';

const propTypes = {
  entry: React.PropTypes.object,
  toggleSelectedEntry: React.PropTypes.func,
};

const SearchOverviewEntry = (props) => {
  const entryName = props.entry.name;
  const entryCategory = props.entry.category;
  let displayedName = entryName;
  if (!SELF_EXPLANATORY_CATEGORY_ITEMS.includes(entryCategory)) {
    displayedName = `${pluralize(entryCategory, 1)} ${entryName}`;
  }
  return (
    <li className="SearchOverviewEntry">
      <div className="SearchOverviewEntry__entry-name">{displayedName}</div>
      <button
        className="SearchOverviewEntry__remove-entry"
        onClick={() => props.toggleSelectedEntry(getEntryId(props.entry), (props.entry.category))}
      />
    </li>
  );
};

SearchOverviewEntry.propTypes = propTypes;
export default connect(() => ({}), { toggleSelectedEntry })(SearchOverviewEntry);
