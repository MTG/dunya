import { GET_FILTERS_DATA_REQUEST, GET_FILTERS_DATA_SUCCESS, GET_FILTERS_DATA_FAILURE,
  TOGGLE_SELECTED_ENTRY, TOGGLE_EXPAND_CATEGORY, RESET_CATEGORY_SELECTIONS,
  SET_SEARCH_CATEGORY, RESET_SEARCH_CATEGORY }
  from '../actions/actionTypes';
import { DATA_FETCH_STATUS } from '../constants';

const selectedDataCategory = (state = [], action, categoryName, selectionType) => {
  if (action.category !== categoryName) {
    return state;
  }
  switch (action.type) {
    case TOGGLE_SELECTED_ENTRY: {
      if (state.includes(action.entryID)) {
        // remove entry if already selected ...
        return state.filter(entryID => entryID !== action.entryID);
      }
      if (selectionType === 'single') {
        return [action.entryID];
      }
      // ... otherwise add it to the list of selected items
      return [...state, action.entryID];
    }
    default:
      return state;
  }
};

const selectedData = (state = {}, action, selectionTypes) => {
  switch (action.type) {
    case GET_FILTERS_DATA_SUCCESS:
    case RESET_CATEGORY_SELECTIONS: {
      // data is the receivedData if GET_FILTERS_DATA_SUCCESS, existing stored data otherwise
      const data = action.receivedData || state;
      return Object.keys(data).reduce((curState, curCategory) =>
        Object.assign(curState, { [curCategory]: [] }), {});
    }
    case TOGGLE_SELECTED_ENTRY: {
      return Object.keys(state).reduce((curState, curCategory) =>
        Object.assign(curState, {
          [curCategory]: selectedDataCategory(
            state[curCategory], action, curCategory, selectionTypes[curCategory]),
        }), {});
    }
    default:
      return state;
  }
};

const receivedData = (state = {}, action) => {
  switch (action.type) {
    case GET_FILTERS_DATA_SUCCESS:
      return Object.keys(action.receivedData).reduce((curState, curCategory) =>
        Object.assign(curState, { [curCategory]: action.receivedData[curCategory].data }), {});
    default:
      return state;
  }
};

const expandedCategories = (state = [], action) => {
  switch (action.type) {
    case TOGGLE_EXPAND_CATEGORY: {
      if (state.includes(action.category)) {
        return state.filter(category => category !== action.category);
      }
      return [...state, action.category];
    }
    default:
      return state;
  }
};

const searchedData = (state = '', action) => {
  switch (action.type) {
    case GET_FILTERS_DATA_SUCCESS: {
      const data = action.receivedData || state;
      return Object.keys(data).reduce((curState, curCategory) =>
        Object.assign(curState, { [curCategory]: '' }), {});
    }
    case SET_SEARCH_CATEGORY:
    case RESET_SEARCH_CATEGORY: {
      const { category, search } = action;
      return Object.assign({}, state, { [category]: search || '' });
    }
    default:
      return state;
  }
};

const status = (state = DATA_FETCH_STATUS.NOT_ASKED, action) => {
  switch (action.type) {
    case GET_FILTERS_DATA_REQUEST:
      return DATA_FETCH_STATUS.PROGRESS;
    case GET_FILTERS_DATA_SUCCESS:
      return DATA_FETCH_STATUS.SUCCESS;
    case GET_FILTERS_DATA_FAILURE:
      return DATA_FETCH_STATUS.FAILURE;
    default:
      return state;
  }
};

const categorySelectionType = (state = {}, action) => {
  if (action.type !== GET_FILTERS_DATA_SUCCESS) {
    return state;
  }
  return Object.keys(action.receivedData).reduce((curState, curCategory) =>
    Object.assign(curState, {
      [curCategory]: action.receivedData[curCategory].selectionType,
    }), {});
};

const filtersData = (state = {}, action) => ({
  categorySelectionType: categorySelectionType(state.categorySelectionType, action),
  selectedData: selectedData(state.selectedData, action, state.categorySelectionType),
  receivedData: receivedData(state.receivedData, action),
  expandedCategories: expandedCategories(state.expandedCategories, action),
  searchedData: searchedData(state.searchedData, action),
  status: status(state.status, action),
});

export default filtersData;
