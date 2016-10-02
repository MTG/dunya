import { combineReducers } from 'redux';
import { DATA_FETCH_STATUS } from 'constants';
import { MAX_AUTOCOMPLETE_SUGGESTIONS } from 'settings';
import { SHOW_TOOLTIP, HIDE_TOOLTIP, TOGGLE_FOCUS, SEARCH_REQUEST, SEARCH_APPEND,
  SEARCH_SUCCESS, SEARCH_FAILURE, UPDATE_SEARCH_INPUT, AUTOCOMPLETE_REQUEST,
  AUTOCOMPLETE_SUCCESS, AUTOCOMPLETE_FAILURE, RESET_AUTOCOMPLETE_RESULTS }
  from '../actions/actionTypes';

const isTooltipVisible = (state = false, action) => {
  switch (action.type) {
    case SHOW_TOOLTIP:
      return true;
    case HIDE_TOOLTIP:
      return false;
    default:
      return state;
  }
};

const isFocused = (state = false, action) => {
  switch (action.type) {
    case TOGGLE_FOCUS:
      return !state;
    default:
      return state;
  }
};

const status = (state = DATA_FETCH_STATUS.NOT_ASKED, action) => {
  switch (action.type) {
    case SEARCH_REQUEST:
    case SEARCH_APPEND:
      return DATA_FETCH_STATUS.PROGRESS;
    case SEARCH_SUCCESS:
      return DATA_FETCH_STATUS.SUCCESS;
    case SEARCH_FAILURE:
      return DATA_FETCH_STATUS.FAILURE;
    default:
      return state;
  }
};

const results = (state = [], action) => {
  switch (action.type) {
    case SEARCH_REQUEST:
      return [];
    case SEARCH_SUCCESS: {
      const searchResults = action.data.results;
      return [...state, ...searchResults];
    }
    default:
      return state;
  }
};

const input = (state = '', action) => {
  switch (action.type) {
    case UPDATE_SEARCH_INPUT:
      return action.input;
    default:
      return state;
  }
};

const moreResults = (state = 0, action) => {
  switch (action.type) {
    case SEARCH_SUCCESS:
      return action.data.moreResults;
    default:
      return state;
  }
};

const autocompleteResults = (state = [], action) => {
  switch (action.type) {
    case RESET_AUTOCOMPLETE_RESULTS:
    case AUTOCOMPLETE_REQUEST:
    case AUTOCOMPLETE_FAILURE: {
      return [];
    }
    case AUTOCOMPLETE_SUCCESS: {
      return action.datalist.slice(0, MAX_AUTOCOMPLETE_SUGGESTIONS);
    }
    default:
      return state;
  }
};

export default combineReducers({
  isTooltipVisible,
  isFocused,
  status,
  results,
  input,
  autocompleteResults,
  moreResults,
});
