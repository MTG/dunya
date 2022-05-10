import pluralize from 'pluralize';

// look at https://www.npmjs.com/package/pluralize#usage to learn how to add more
pluralize.addSingularRule(/raagas$/i, 'raaga');

export default pluralize;
