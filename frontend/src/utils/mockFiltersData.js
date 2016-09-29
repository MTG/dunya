import dunyaMetadata from './dunya-metadata-aliases.json';

const useWestCatalogue = true;

const getArtists = numOfArtists =>
  [...Array(numOfArtists).keys()].map(index => ({
    name: `Cool Artist ${index}`,
    id: `a${index}`,
    concerts: [`${(index % 2) === 0 ? 'c1' : 'c2'}`, 'c5'],
    raagas: ['r1', `${(index % 2) === 0 ? 'r3' : 'r5'}`],
    taalas: [`${(index % 2) === 0 ? 't1' : 't3'}`, 't4'],
    instruments: [`${(index % 2) === 0 ? 'i1' : 'i4'}`, 'i5'],
  }));

const getConcerts = concertsIds =>
  concertsIds.map((concertID, index) => ({
    name: `Cool Concert ${index}`,
    id: concertID,
    raagas: ['r1', `${(index % 2) === 0 ? 'r3' : 'r5'}`],
    taalas: [`${(index % 2) === 0 ? 't1' : 't3'}`, 't4'],
    instruments: [`${(index % 2) === 0 ? 'i1' : 'i4'}`, 'i5'],
  }));

const getRefineGenericCategory = (categoryName, categoryIDs) =>
  categoryIDs.map((id, index) => ({
    id,
    name: `Cool ${categoryName} ${index}`,
  }));


const brianEno = {
  name: 'Brian Eno',
  id: 'a1',
  discs: ['c1', 'c2'],
  instruments: ['i1'],
  genres: ['g1'],
};

const ozzyOsbourne = {
  name: 'Ozzy Osbourne',
  id: 'a2',
  discs: ['c3'],
  instruments: ['i2'],
  genres: ['g2'],
};

const ambientVol1 = {
  name: 'Ambient Volume 1',
  id: 'c1',
  genres: ['g1'],
  instruments: ['i1', 'i2'],
};
const ambientVol2 = Object.assign({}, ambientVol1, { id: 'c2', name: 'Ambient Volume 2' });
const theBlack = {
  name: 'The black',
  id: 'c3',
  genres: ['g2'],
  instruments: ['i2'],
};

const synth = { name: 'Synthetizer', id: 'i1' };
const voice = { name: 'Voice', id: 'i2' };

const ambient = { id: 'g1', name: 'Ambient' };
const rock = { id: 'g2', name: 'Rock' };

const getIndianData = () => ({
  artists: getArtists(10),
  concerts: getConcerts(['c1', 'c2', 'c5']),
  instruments: getRefineGenericCategory('instrument', ['i1', 'i4', 'i5']),
  raagas: getRefineGenericCategory('raaga', ['r1', 'r3', 'r5']),
  taalas: getRefineGenericCategory('taala', ['t1', 't3', 't4']),
});

const getWesternData = () => ({
  artists: [brianEno, ozzyOsbourne],
  albums: [ambientVol1, ambientVol2, theBlack],
  instrumentation: [synth, voice],
  genres: [ambient, rock],
});

export const receivedData = (() => {
  if (useWestCatalogue) {
    return getWesternData();
  }
  return dunyaMetadata;
})();
