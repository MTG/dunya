import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';
import { toggleFocus, updateSearchInput, getAutocompleteList, resetAutocompleteResults }
  from 'actions/search';
import { toggleSelectedEntry } from 'actions/filtersData';
import { getAllSelectedEntries, getEntryId }
  from 'selectors/filtersData';
import SearchTooltip from './SearchTooltip';
import SearchOverviewEntry from './SearchOverviewEntry';
import AutoComplete from './AutoComplete';
import ShowMobileMenu from '../MobileMenu/ShowMobileMenu';
import { breakpoints } from '../../stylesheets/variables.json';

const breakpoint = parseInt(breakpoints.medium, 10);

const propTypes = {
  allSelectedItems: PropTypes.array,
  input: PropTypes.string,
  toggleSelectedEntry: PropTypes.func,
  updateSearchInput: PropTypes.func,
  getAutocompleteList: PropTypes.func,
  resetAutocompleteResults: PropTypes.func,
  toggleFocus: PropTypes.func,
  isFocused: PropTypes.bool,
  autocompleteResults: PropTypes.array,
  windowSize: PropTypes.object,
};

const shouldShowSearchTooltip = false;
const longPlaceHolder = 'Search by recording name or by selected filters';
const shortPlaceHolder = 'Search recordings';

const onInputChange = (evt, props) => {
  const inputContent = evt.target.value;
  props.updateSearchInput(inputContent);
  props.getAutocompleteList(inputContent);
};

const unselectLatestEntry = (props) => {
  const entry = props.allSelectedItems[props.allSelectedItems.length - 1];
  if (entry) {
    props.toggleSelectedEntry(getEntryId(entry), entry.category);
  }
};

const autoCompleteListID = 'recordings-autocomplete';

const SearchInput = (props) => {
  const isFilteredSearch = props.allSelectedItems.length > 0;
  const tooltip = (shouldShowSearchTooltip) ? <SearchTooltip /> : null;
  let placeHolder = '';
  if (!isFilteredSearch) {
    placeHolder = (props.windowSize.width < breakpoint) ? shortPlaceHolder : longPlaceHolder;
  }
  const selectedItems = props.allSelectedItems.map(entry =>
    <SearchOverviewEntry key={getEntryId(entry)} entry={entry} />);
  return (
    <ol className={`SearchInput${(props.isFocused) ? ' focus' : ''}`}>
      <li>
        <button className="SearchInput__search-button" type="submit">
          <i className="fa fa-lg fa-search" aria-hidden />
        </button>
      </li>
      {selectedItems}
      <li>
        <AutoComplete
          results={props.autocompleteResults}
          toggleSelectedEntry={props.toggleSelectedEntry}
          updateSearchInput={props.updateSearchInput}
          id={autoCompleteListID}
          searchInput={props.input}
        />
        <input
          id="search"
          className="SearchInput__input"
          type="search"
          data-list={(props.autocompleteResults.length) ? `#${autoCompleteListID}` : ''}
          placeholder={placeHolder}
          value={props.input}
          onChange={evt => onInputChange(evt, props)}
          onFocus={props.toggleFocus}
          autoComplete="off"
          onBlur={() => {
            props.resetAutocompleteResults();
            props.toggleFocus();
          }}
          onKeyDown={(evt) => {
            if (evt.keyCode === 8 && !evt.target.value) {
              // unselect latest entry when user presses delete key
              unselectLatestEntry(props);
            }
          }}
        />
      </li>
      <ShowMobileMenu />
      {tooltip}
    </ol>
  );
};

const mapStateToProps = (state) => {
  const allSelectedItems = getAllSelectedEntries(state);
  const { isFocused, autocompleteResults, input } = state.search;
  const { windowSize } = state;
  return { allSelectedItems, autocompleteResults, input, isFocused, windowSize };
};

SearchInput.propTypes = propTypes;
export default connect(mapStateToProps, {
  toggleFocus,
  toggleSelectedEntry,
  updateSearchInput,
  getAutocompleteList,
  resetAutocompleteResults,
})(SearchInput);
