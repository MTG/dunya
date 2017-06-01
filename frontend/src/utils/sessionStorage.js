export const loadState = (appName) => {
  try {
    const serializedState = sessionStorage.getItem('state_'+appName);
    if (serializedState === null) {
      return undefined;
    }
    return JSON.parse(serializedState);
  } catch (err) {
    return undefined;
  }
};

export const saveState = (state, appName) => {
  try {
    const serializedState = JSON.stringify(state);
    sessionStorage.setItem('state_'+appName, serializedState);
  } catch (err) {
    // ignore for now
  }
};
