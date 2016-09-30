import { SEARCH_URL, AUTOCOMPLETE_URL } from 'constants';
import { SHOW_TOOLTIP, HIDE_TOOLTIP, TOGGLE_FOCUS, SEARCH_REQUEST,
  SEARCH_SUCCESS, SEARCH_FAILURE, UPDATE_SEARCH_INPUT, SEARCH_APPEND,
  AUTOCOMPLETE_REQUEST, AUTOCOMPLETE_SUCCESS, AUTOCOMPLETE_FAILURE } from './actionTypes';
import makeActionCreator from './makeActionCreator';
import mockAutocomplete from '../utils/mockAutocomplete';

export const showSearchTooltip = makeActionCreator(SHOW_TOOLTIP);
export const hideSearchTooltip = makeActionCreator(HIDE_TOOLTIP);
export const toggleFocus = makeActionCreator(TOGGLE_FOCUS);

const searchRequest = makeActionCreator(SEARCH_REQUEST);
const searchSuccess = makeActionCreator(SEARCH_SUCCESS, 'data');
const searchFailure = makeActionCreator(SEARCH_FAILURE, 'error');
const searchAppend = makeActionCreator(SEARCH_APPEND);

export const updateSearchInput = makeActionCreator(UPDATE_SEARCH_INPUT, 'input');

let pageIndex = 0;

const getResults = serializedQuery => new Promise((resolve, reject) => {
  const baseSearchURL = SEARCH_URL[window.catalogue];
  const searchUrl = `${baseSearchURL}?${serializedQuery}`;
  fetch(searchUrl)
    .then(response => response.json())
    .then(parsedResponse => resolve(parsedResponse))
    .catch(error => reject(error));
});

const serializeQuery = (query, selectedData) => {
  const encode = encodeURIComponent; // short-hand
  let serializedQuery = (query) ? `recording=${encode(query)}` : '';
  Object.keys(selectedData).forEach((category) => {
    if (selectedData[category].length) {
      const categoryEntries = selectedData[category].reduce((curStr, entry, index) => {
        if (index === selectedData[category].length - 1) {
          return curStr + encode(entry);
        }
        return `${curStr}${encode(entry)}+`;
      }, '');
      serializedQuery += `&${encode(category)}=${categoryEntries}`;
    }
  });
  if (pageIndex) {
    serializedQuery += `&page=${pageIndex}`;
  }
  return serializedQuery;
};

export const getSearchResults = () => (dispatch, getStore) => {
  pageIndex = 0;
  const state = getStore();
  const query = state.search.input;
  const { selectedData } = state.filtersData;
  const serializedQuery = serializeQuery(query, selectedData);
  dispatch(searchRequest());
  getResults(serializedQuery).then(
    data => dispatch(searchSuccess(data)),
    error => dispatch(searchFailure(error)));
};

export const getMoreResults = () => (dispatch) => {
  pageIndex += 1;
  dispatch(searchAppend());
  setTimeout(() => {
    getResults(pageIndex).then(data => dispatch(searchSuccess(data)),
    error => dispatch(searchFailure(error)));
  }, 1000);
};

export const getAutocompleteList = input => (dispatch) => {
  const autocompleteURL = AUTOCOMPLETE_URL[window.catalogue];
  if (!autocompleteURL) {
    return;
  }
  dispatch({ type: AUTOCOMPLETE_REQUEST });
  mockAutocomplete(input).then(datalist => dispatch({ type: AUTOCOMPLETE_SUCCESS, datalist }));
};
