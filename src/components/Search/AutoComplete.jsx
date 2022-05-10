import PropTypes from 'prop-types';
import React from 'react';
import { getEntryId } from '../../selectors/filtersData';
import './AutoComplete.scss';

const propTypes = {
  results: PropTypes.array,
  id: PropTypes.string,
  toggleSelectedEntry: PropTypes.func,
  updateSearchInput: PropTypes.func,
  searchInput: PropTypes.string,
};

const computeRemainingInputOnClick = (searchInput, matched = '') => {
  const input = searchInput.split(' ');
  const remainingWords = input.filter(word => word !== matched);
  return remainingWords.join(' ');
};

const AutoComplete = (props) => {
  if (props.results.length) {
    return (
      <ul id={props.id} className="AutoComplete">
        {props.results.map(suggestion =>
          <li
            onMouseDown={() => {
              props.toggleSelectedEntry(getEntryId(suggestion), suggestion.category);
              const newInput = computeRemainingInputOnClick(props.searchInput, suggestion.matchFor);
              props.updateSearchInput(newInput);
            }}
            key={getEntryId(suggestion)}
            className="AutoComplete__entry"
          >
            <div className="AutoComplete__entry-name">{suggestion.name}</div>
            <div className="AutoComplete__entry-category">{suggestion.category}</div>
            {(suggestion.matchFor) ?
              <div className="AutoComplete__entry-matchFor">{`match for '${suggestion.matchFor}'`}</div>
              : null
            }
          </li>
        )}
      </ul>);
  }
  return null;
};

AutoComplete.propTypes = propTypes;
export default AutoComplete;
