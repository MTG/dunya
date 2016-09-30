import { FILTERS_DATA_URL } from 'settings';
import makeActionCreator from './makeActionCreator';
import { GET_FILTERS_DATA_REQUEST, GET_FILTERS_DATA_SUCCESS, GET_FILTERS_DATA_FAILURE,
  TOGGLE_SELECTED_ENTRY, TOGGLE_EXPAND_CATEGORY, RESET_CATEGORY_SELECTIONS,
  SET_SEARCH_CATEGORY, RESET_SEARCH_CATEGORY }
  from './actionTypes';
import { getSearchResults } from './search';

const getFiltersDataRequest = makeActionCreator(GET_FILTERS_DATA_REQUEST);
const getFiltersDataSuccess = makeActionCreator(GET_FILTERS_DATA_SUCCESS, 'receivedData');
const getFiltersDataFailure = makeActionCreator(GET_FILTERS_DATA_FAILURE, 'error');

const fetchFiltersData = () => new Promise((resolve, reject) => {
  fetch(FILTERS_DATA_URL[window.catalogue])
    .then(response => response.json())
    .then(parsedResponse => resolve(parsedResponse))
    .catch(() => reject());
});

export const getFiltersData = () => (dispatch) => {
  // TODO: read it from window.catalogueName and use it as param of fetchFiltersData
  dispatch(getFiltersDataRequest());
  fetchFiltersData().then(
    data => dispatch(getFiltersDataSuccess(data)),
    error => dispatch(getFiltersDataFailure(error)));
};

export const toggleSelectedEntryInCategory = makeActionCreator(TOGGLE_SELECTED_ENTRY, 'entryID', 'category');

export const toggleSelectedEntry = (entryID, category) => (dispatch) => {
  dispatch(toggleSelectedEntryInCategory(entryID, category));
  dispatch(getSearchResults());
};
export const toggleExpandCategory = makeActionCreator(TOGGLE_EXPAND_CATEGORY, 'category');

// action to update the content of the search box specific to a single category
export const setSearchCategory = makeActionCreator(SET_SEARCH_CATEGORY, 'search', 'category');
export const resetSearchCategory = makeActionCreator(RESET_SEARCH_CATEGORY, 'category');

export const resetSearchAllCategories = () => (dispatch, getStore) => {
  const store = getStore();
  const categories = Object.keys(store.filtersData.searchedData);
  categories.forEach(category => dispatch(resetSearchCategory(category)));
};
