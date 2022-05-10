import { createSelector } from 'reselect';
import sortByName from '../utils/sortByName';
import { SHOW_ONLY_VISIBLE_SELECTED, ID_KEYS } from '../settings';

export const getEntryId = (entry) => {
  let entryID;
  for (const id of ID_KEYS) {
    if (entry[id]) {
      entryID = entry[id];
    }
  }
  return entryID;
};

const getSelectedInCategory = (state, props) => state.filtersData.selectedData[props.category];
const getCategoryEntries = (state, props) => state.filtersData.receivedData[props.category];

/**
 * Returns an array of objects, each one containing the details (from the JSON response)
 * of a selected entry for a given category.
 */
export const makeGetDetailsForCategorySelectedEntries = () => createSelector(
  [getSelectedInCategory, getCategoryEntries],
  (selected, entries) => selected.map(selEntry =>
    entries.find(entry => getEntryId(entry) === selEntry))
);

export const makeIsEntrySelected = entry => createSelector(
  [getSelectedInCategory],
  selected => selected.includes(getEntryId(entry))
);

/**
 * Returns the details of each entry of a specific category.
 * Examples:
 *  category = concerts
 *  state.filtersData.receivedData = { artists: [{a1}, ...], concerts: [{c1}, {c2}...] }
 *  this would return: { concerts: [{c1}, {c2}...] }
 */
const getCategoryData = (state, props) => ({
  categoryName: props.category,
  categoryDataContent: state.filtersData.receivedData[props.category],
});

const getCategorySearchQuery = (state, props) => state.filtersData.searchedData[props.category];

/**
 * Returns the details of each entry for each category different from the selected one.
 * Examples:
 *  category = concerts
 *  state.filtersData.receivedData = { artists: [{a1}...], concerts: [{c1}...], raagas: [{r1}...] }
 *  this would return: { artists: [{a1}...], raagas: [{r1}...] }
 */
const getOtherCategoriesDetails = (state, props) => {
  const keys = Object.keys(state.filtersData.receivedData);
  const otherCategoriesKeys = keys.filter(key => key !== props.category);
  const otherCategoriesData = otherCategoriesKeys.reduce((curState, curKey) =>
    Object.assign(curState, { [curKey]: state.filtersData.receivedData[curKey] }), {});
  return otherCategoriesData;
};

/**
 * Returns the list of selected items for remaining categories.
 * Examples:
 *  category = concerts
 *  state.filtersData.selectedData = { artists: [1, 4 ...], concerts: [3, 8], raagas: [4] }
 *  this would return: { artists: [1, 4 ...], raagas: [4] }
 */
const getSelectedOtherCategories = (state, props) => {
  const keys = Object.keys(state.filtersData.selectedData);
  const otherCategoriesKeys = keys.filter(key => key !== props.category);
  const selectedForOtherCategories = otherCategoriesKeys.reduce((curState, curKey) =>
    Object.assign(curState, { [curKey]: state.filtersData.selectedData[curKey] }), {});
  return selectedForOtherCategories;
};

/** Gets the entry details object given its name */
const getDetailsForSelectedEntry = (entryName, entriesInCategory) =>
  entriesInCategory.find(curEntry => getEntryId(curEntry) === entryName);

/**
 * Given a list of categorized entries, retrieves the details of each entry in a given category.
 * Example:
 *  category = concerts
 *  selectedForCategories = { artists: [1, 4], concerts: [3, 8], raagas: [4] }
 *  entriesForCategories = {artists: [{a1},...], concerts: [{c1},...], raagas: [{r1}, ...]}
 * This would return: [{c3}, {c8}]
 */
const getDetailsForCategoryEntries = (category, selectedForCategories, entriesForCategories) => {
  const selectedInCategory = selectedForCategories[category];
  const objectsInCategory = entriesForCategories[category];
  return selectedInCategory.map(selected =>
    getDetailsForSelectedEntry(selected, objectsInCategory));
};

/**
 * Given a list of categorized entries, retrieves the details of each entry for each category.
 * Example:
 *  category = concerts
 *  selectedForCategories = { artists: [1, 4], concerts: [3, 8], raagas: [4] }
 *  entriesForCategories = {artists: [{a1},...], concerts: [{c1},...], raagas: [{r1}, ...]}
 * This would return: {artists:[{a1}, {a4}], concerts:[{c3}, {c8}], raagas: [{r4}]}
 */
const getSelectedDetailsAllCategories = (selectedForCategories, entriesForCategories) => {
  const categories = Object.keys(selectedForCategories);
  return categories.reduce((curState, category) =>
    Object.assign(curState, {
      [category]: getDetailsForCategoryEntries(category, selectedForCategories,
        entriesForCategories),
    }), {});
};

/**
 * Returns the list of selected items for remaining categories with corresponding details
 * Examples:
 *  category = concerts (the selected category is read from the props)
 *  state.filtersData.selectedData = { artists: [1], concerts: [3, 8], raagas: [2] }
 *  state.filtersData.receivedData = { artists: [{a1}...], concerts: [{c1}...], raagas: [{r1}...] }
 *  this would return: { artists: [{a1}], raagas: [{r2}] }
 */
const getSelectedOtherCategoriesDetails = createSelector(
  [getSelectedOtherCategories, getOtherCategoriesDetails],
  (selectedOtherCategories, otherCategoriesDetails) =>
    getSelectedDetailsAllCategories(selectedOtherCategories, otherCategoriesDetails)
);

const getOwnEntriesThatRespectFilter =
  (selectedEntry, selectedEntryCategoryName, ownCategoryContent) =>
    ownCategoryContent.reduce((ownFilteredEntries, curOwnEntry) => {
      if (curOwnEntry[selectedEntryCategoryName] &&
        curOwnEntry[selectedEntryCategoryName].includes(getEntryId(selectedEntry))) {
        return [...ownFilteredEntries, getEntryId(curOwnEntry)];
      }
      return ownFilteredEntries;
    }, []);

const getEntriesForcedByOtherCategoryFilter =
  (otherCategorySelections, ownCategoryName, otherCategoryName, ownCategoryContent) => {
    let forcedEntries = [];
    otherCategorySelections.forEach((entry) => {
      let entriesForcedByCurrentSelection = [];
      if (entry[ownCategoryName]) {
        /** `entry` could be a super-entity and contain a reference of all other fields.
        e.g. artists is a super-entity because for each of its entries we store all other
        fields, i.e. for each artist we store the instruments/taalas/raagas he plays and so on.
        So if `entry` has been selected and is a super-entity, we can easily get the entries to
        filter in `ownCategory` by just getting the list stored in each super-entity selected.
        */
        entriesForcedByCurrentSelection = entry[ownCategoryName];
      } else {
        /** if `entry` is not a super-entity, it doesn't contain relational information.
        We have to get such relational information by `ownCategory` hoping that `ownCategory`
        is a super-entity. If not, no entries will be forced for `ownCategory` by the selections
        of the current `otherCategory`.
        */
        entriesForcedByCurrentSelection =
          getOwnEntriesThatRespectFilter(entry, otherCategoryName, ownCategoryContent);
      }
      forcedEntries = [...forcedEntries, ...entriesForcedByCurrentSelection];
    });
    // remove duplicates
    const filteredEntries = [...new Set(forcedEntries)];
    return filteredEntries;
  };

/** selector for retrieving entries in category that fulfills filters in others */
const getVisibleByOtherCategoriesSelections = createSelector(
  [getSelectedOtherCategoriesDetails, getCategoryData],
  (selectedInOtherCategories, { categoryName, categoryDataContent }) => {
    let filteredCategoryEntries = [];
    Object.keys(selectedInOtherCategories).forEach((otherCategoryName) => {
      const otherCategorySelections = selectedInOtherCategories[otherCategoryName];
      const entriesForcedByOtherCategoryFilter = getEntriesForcedByOtherCategoryFilter(
        otherCategorySelections, categoryName, otherCategoryName, categoryDataContent);
      filteredCategoryEntries = [...filteredCategoryEntries,
                                 ...entriesForcedByOtherCategoryFilter];
    });
    // remove duplicated entries
    filteredCategoryEntries = [...new Set(filteredCategoryEntries)];
    if (!filteredCategoryEntries.length) {
      // if other categories don't force filtered content, return entire content
      return categoryDataContent.sort(sortByName);
    }
    const filteredCategoryEntriesContent = filteredCategoryEntries.map((entryID) => {
      const correspondingEntry =
        categoryDataContent.find(curEntry => getEntryId(curEntry) === entryID);
      return correspondingEntry;
    });
    return filteredCategoryEntriesContent.sort(sortByName);
  }
);

/** the actual search engine */
const entrySatisfiesSearch = (entry, search) => {
  const preprocessName = name => name.replace(/\W/g, '').toLowerCase();
  const letters = Array.prototype.slice.call(preprocessName(search));
  const alphanumeric = '\\w*';
  const regex = letters.reduce((curRegex, curLetter) =>
    curRegex + curLetter + alphanumeric,
    alphanumeric);
  const aliases = entry.aliases || [];
  const entryNames = [entry.name, ...aliases];
  return entryNames.some(name => Boolean(preprocessName(name).match(new RegExp(regex))));
};

/** selector that returns category entries matched by search and that
fulfill filters in other categories */
export const makeGetVisibleCategoryData = () =>
  createSelector(
    [getVisibleByOtherCategoriesSelections, getCategorySearchQuery],
    (visibleByOtherCategoriesSelections, searchQuery) => {
      if (searchQuery) {
        return visibleByOtherCategoriesSelections.filter(entry =>
          entrySatisfiesSearch(entry, searchQuery));
      }
      return visibleByOtherCategoriesSelections;
    }
  );

export const makeGetVisibleSelected = () =>
  createSelector(
    [getVisibleByOtherCategoriesSelections, getSelectedInCategory],
    (visibleByOtherCategoriesSelections, selectedInCategory) =>
      selectedInCategory.reduce((curVisibleSelected, curSelected) => {
        const visibleSelectedEntry = visibleByOtherCategoriesSelections.find(entry =>
          getEntryId(entry) === curSelected);
        if (visibleSelectedEntry) {
          return [...curVisibleSelected, visibleSelectedEntry];
        }
        return curVisibleSelected;
      }, [])
  );

// aux functions for getAllSelectedEntries
const getAllSelectedData = state => state.filtersData.selectedData;
const getState = state => state;

/**
 * Returns an array of objects, each containing the details (from the JSON response)
 * for the corresponding selected entry.
 */
export const getAllSelectedEntries = createSelector(
  [getAllSelectedData, getState],
  (allSelectedData, state) =>
    Object.keys(allSelectedData).reduce((curSelectedData, category) => {
      const getVisibleSelected = makeGetVisibleSelected();
      const getDetailsForCategorySelectedEntries = makeGetDetailsForCategorySelectedEntries();
      let visibleSelectedInCategory;
      if (SHOW_ONLY_VISIBLE_SELECTED) {
        visibleSelectedInCategory = getVisibleSelected(state, { category });
      } else {
        visibleSelectedInCategory = getDetailsForCategorySelectedEntries(state, { category });
      }
      const enrichedVisibleEntries = visibleSelectedInCategory.map(selectedEntry =>
        Object.assign({}, selectedEntry, { category }));
      return [...curSelectedData, ...enrichedVisibleEntries];
    }, [])
);
