import { combineReducers } from 'redux';
import filtersData from './filtersData';
import mobileMenu from './mobileMenu';
import search from './search';
import windowSize from './windowSize';

export default combineReducers({
  filtersData,
  mobileMenu,
  search,
  windowSize,
});
