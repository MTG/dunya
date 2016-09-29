import carnaticRecordings from './carnatic-recordings.json';

export default input => new Promise((resolve) => {
  resolve(carnaticRecordings.slice(0, input.length));
});
