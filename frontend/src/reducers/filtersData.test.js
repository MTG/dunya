import expect from 'expect';
import { toggleSelectedEntryInCategory } from '../actions/filtersData';
import filtersData from './filtersData';
import { GET_FILTERS_DATA_SUCCESS } from '../actions/actionTypes';
import { DATA_FETCH_STATUS } from '../constants';

describe('filtersData reducer', () => {
  const artists = [{ name: 'xx', id: '1' }, { name: 'yy', id: '2' }];
  const concerts = [{ name: 'concX', id: '10' }, { name: 'concY', id: '20' }];
  const receivedData = { artists, concerts };
  const expectedInitialState = {
    receivedData,
    expandedCategories: [],
    searchedData: { artists: '', concerts: '' },
    selectedData: Object.keys(receivedData).reduce((curState, category) =>
      Object.assign(curState, { [category]: [] }), {}),
    status: DATA_FETCH_STATUS.SUCCESS,
  };
  it('correctly stores the received data', () => {
    const action = { data: receivedData, type: GET_FILTERS_DATA_SUCCESS };
    expect(filtersData(undefined, action)).toEqual(expectedInitialState);
  });
  describe('correctly toggles an entry', () => {
    const selected = artists[0].name;
    const category = 'artists';
    const expectedSelectedData = Object.assign({}, expectedInitialState.selectedData, {
      [category]: [selected],
    });
    const expectedState = Object.assign({}, expectedInitialState, {
      selectedData: expectedSelectedData,
    });
    it('correctly selects an entry', () => {
      expect(filtersData(expectedInitialState, toggleSelectedEntryInCategory(selected, category))
        .selectedData)
      .toEqual(expectedState.selectedData);
    });
    it('correctly unselects it', () => {
      expect(filtersData(expectedState, toggleSelectedEntryInCategory(selected, category))
        .selectedData)
        .toEqual(expectedInitialState.selectedData);
    });
  });
});
