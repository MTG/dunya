// API address to get data to fill up filters section
export const FILTERS_DATA_URL = {
  carnatic: 'http://dunya.compmusic.upf.edu/new/filters.json',
  hindustani: 'https://whatever',
};

export const SEARCH_URL = {
  carnatic: 'https://whatever',
  hindustani: 'https://whatever',
};

export const AUTOCOMPLETE_URL = {
  carnatic: undefined,
};

// whether to show in selected list only entries that fulfill all filters
export const SHOW_ONLY_VISIBLE_SELECTED = false;

// categories whose selected items don't need a reference to the category itself
export const SELF_EXPLANATORY_CATEGORY_ITEMS = ['artists', 'concerts', 'instruments'];

// whether to interpret links starting with / as locals or remote ones
// N.B. it MUST be false on dunya production
export const USE_REMOTE_SOURCES = true;
export const REMOTE_URL = 'http://dunya.compmusic.upf.edu';

// whether to store application state on localSession
export const STORE_APPLICATION_STATE = true;

// possible keys for ids in responses
export const ID_KEYS = ['mbid', 'uuid', 'id'];

// max number of suggestions with autocomplete
export const MAX_AUTOCOMPLETE_SUGGESTIONS = 5;
