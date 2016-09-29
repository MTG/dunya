import dunyaRecordings from './dunya-recordings.json';

const resultsPerPage = 20;

export const getResults = (pageIndex = 0) => new Promise((resolve) => {
  const results = dunyaRecordings.slice(resultsPerPage * pageIndex,
    resultsPerPage * (pageIndex + 1));
  resolve({ results, moreResults: 28, linkToNext: '' });
});
