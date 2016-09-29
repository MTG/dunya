export default (objectA, objectB) => {
  if (objectA.name > objectB.name) {
    return 1;
  }
  if (objectA.name < objectB.name) {
    return -1;
  }
  return 0;
};
