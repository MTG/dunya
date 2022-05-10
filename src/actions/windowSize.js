import { UPDATE_WINDOW_SIZE } from './actionTypes';
import makeActionCreator from './makeActionCreator';

export const updateWindowSize = makeActionCreator(UPDATE_WINDOW_SIZE, 'newSize');
