import carnaticRecordings from './carnatic-recordings.json';

const mockAutocompleteResults = [
  {
    name: 'aadi',
    category: 'taalas',
    uuid: 'c788c38a-b53a-48cb-b7bf-d11769260c4d',
    matchFor: 'aa',
  }, {
    name: '594- K. V. Narayanaswami concert at USA, 1981',
    category: 'concerts',
    uuid: '6bbc582c-6deb-4d76-9b43-c3ce53407c9e',
    matchFor: '594',
  },
];

export default input => new Promise((resolve) => {
  if (input) {
    resolve(mockAutocompleteResults);
  } else {
    resolve([]);
  }
});
