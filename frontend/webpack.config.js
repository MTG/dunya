const path = require('path');
const webpack = require('webpack');
const autoprefixer = require('autoprefixer');
const precss = require('precss');
const jsonImporter = require('node-sass-json-importer');

function getEntrySources(sources) {
  if (process.env.NODE_ENV !== 'production') {
    sources.push('webpack-hot-middleware/client');
    sources.unshift('react-hot-loader/patch');
  }
  return sources;
}

function getPlugins(plugins) {
  if (process.env.NODE_ENV !== 'production') {
    plugins.push(new webpack.HotModuleReplacementPlugin());
  }
  return plugins;
}

module.exports = {
  devtool: (process.env.NODE_ENV !== 'production') ? 'eval' : '',
  entry: getEntrySources([
    './src/index',
  ]),
  output: {
    path: path.join(__dirname, 'dist/'),
    filename: 'bundle.js',
    publicPath: '/dist/',
  },
  plugins: getPlugins([
    new webpack.DefinePlugin({
      'process.env': {
        NODE_ENV: JSON.stringify(process.env.NODE_ENV),
      },
    }),
    new webpack.optimize.OccurenceOrderPlugin(),
  ]),
  module: {
    loaders: [
      {
        test: /\.jsx?$/,
        loaders: ['babel'],
        include: path.join(__dirname, 'src'),
      },
      {
        test: /\.scss$/,
        loaders: [
          'style-loader',
          'css-loader',
          'postcss-loader',
          'sass',
        ],
        include: [
          path.resolve(__dirname, 'src/stylesheets'),
          path.resolve(__dirname, 'src/components'),
        ],
      },
      {
        test: /\.css$/,
        loaders: [
          'style',
          'css',
        ],
      },
      {
        test: /\.(ttf|eot|png|jpg|svg)(\?.*$|$)$/,
        loader: 'file?name=[name].[ext]',
      },
      {
        test: /\.woff(2)?(\?v=[0-9]\.[0-9]\.[0-9])?$/,
        loader: 'url-loader?limit=10000&mimetype=application/font-woff',
      },
      {
        test: /\.json$/,
        loader: 'json',
      },
    ],
  },
  resolve: {
    extensions: ['', '.js', '.jsx'],
  },
  postcss() {
    return [autoprefixer, precss];
  },
  sassLoader: {
    // Apply the JSON importer via sass-loader's options.
    importer: jsonImporter,
  },
};
