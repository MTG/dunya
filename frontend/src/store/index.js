import configureStoreProd from './configureStore.prod';
import configureStoreDev from './configureStore.dev';

if (process.env.NODE_ENV !== 'production') {
  module.exports = configureStoreDev;
} else {
  module.exports = configureStoreProd;
}
