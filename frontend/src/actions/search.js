import { SHOW_TOOLTIP, HIDE_TOOLTIP, TOGGLE_FOCUS, SEARCH_REQUEST,
  SEARCH_SUCCESS, SEARCH_FAILURE, UPDATE_SEARCH_INPUT, SEARCH_APPEND,
  AUTOCOMPLETE_REQUEST, AUTOCOMPLETE_SUCCESS, AUTOCOMPLETE_FAILURE } from './actionTypes';
import makeActionCreator from './makeActionCreator';
import { getResults } from '../utils/mockResults';
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

export const getSearchResults = () => (dispatch, getStore) => {
  pageIndex = 0;
  const state = getStore();
  const query = state.search.input;
  const { selectedData } = state.filtersData;
  dispatch(searchRequest());
  setTimeout(() => {
    getResults().then(data => dispatch(searchSuccess(data)),
    error => dispatch(searchFailure(error)));
  }, 1000);
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
  dispatch({ type: AUTOCOMPLETE_REQUEST });
  mockAutocomplete(input).then(datalist => dispatch({ type: AUTOCOMPLETE_SUCCESS, datalist }));
};
