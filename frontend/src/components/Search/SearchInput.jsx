import React from 'react';
import { connect } from 'react-redux';
import { toggleFocus, updateSearchInput, getAutocompleteList } from 'actions/search';
import { toggleSelectedEntry } from 'actions/filtersData';
import { getAllSelectedEntries, getEntryId }
  from 'selectors/filtersData';
import SearchTooltip from './SearchTooltip';
import SearchOverviewEntry from './SearchOverviewEntry';
import ShowMobileMenu from '../MobileMenu/ShowMobileMenu';
import { breakpoints } from '../../stylesheets/variables.json';

const breakpoint = parseInt(breakpoints.medium, 10);

const propTypes = {
  allSelectedItems: React.PropTypes.array,
  toggleSelectedEntry: React.PropTypes.func,
  updateSearchInput: React.PropTypes.func,
  getAutocompleteList: React.PropTypes.func,
  toggleFocus: React.PropTypes.func,
  isFocused: React.PropTypes.bool,
  autocompleteResults: React.PropTypes.array,
  windowSize: React.PropTypes.object,
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

const SearchInput = (props) => {
  const isFilteredSearch = props.allSelectedItems.length > 0;
  const tooltip = (shouldShowSearchTooltip) ? <SearchTooltip /> : null;
  let placeHolder = '';
  if (!isFilteredSearch) {
    placeHolder = (props.windowSize.width < breakpoint) ? shortPlaceHolder : longPlaceHolder;
  }
  const selectedItems = props.allSelectedItems.map(entry =>
    <SearchOverviewEntry key={getEntryId(entry)} entry={entry} />);
  const dataList = (props.autocompleteResults) ? (
    <datalist id="recordings-autocomplete">
      {props.autocompleteResults.map(recording =>
        <option value={recording.title} key={getEntryId(recording)} />)}
    </datalist>) : null;
  return (
    <ol className={`SearchInput${(props.isFocused) ? ' focus' : ''}`}>
      <li>
        <button className="SearchInput__search-button" type="submit">
          <i className="fa fa-lg fa-search" aria-hidden />
        </button>
      </li>
      {selectedItems}
      <li>
        {dataList}
        <input
          id="search"
          className="SearchInput__input"
          type="search"
          list={dataList ? 'recordings-autocomplete' : ''}
          placeholder={placeHolder}
          onChange={evt => onInputChange(evt, props)}
          onFocus={props.toggleFocus}
          onBlur={props.toggleFocus}
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
  const { isFocused, autocompleteResults } = state.search;
  const { windowSize } = state;
  return { allSelectedItems, autocompleteResults, isFocused, windowSize };
};

SearchInput.propTypes = propTypes;
export default connect(mapStateToProps, {
  toggleFocus,
  toggleSelectedEntry,
  updateSearchInput,
  getAutocompleteList,
})(SearchInput);
