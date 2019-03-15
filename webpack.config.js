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
    './frontend/src/index',
  ]),
  output: {
    path: path.join(__dirname, 'frontend', 'static', 'frontend'),
    filename: 'bundle.js',
    publicPath: '/dist/',
  },
  plugins: getPlugins([
    new webpack.DefinePlugin({
      'process.env': {
        NODE_ENV: JSON.stringify(process.env.NODE_ENV),
      },
    }),
  ]),
  module: {
    rules: [
      {
        test: /\.jsx?$/,
        use: ['babel-loader'],
        include: path.join(__dirname, 'frontend', 'src'),
      },
      {
        test: /\.scss$/,
        use: [
            'style-loader',
            'css-loader',
            // From https://github.com/postcss/postcss-loader#plugins
            // sets postcss options without using a postcss.config.js
            // Default plugins from https://github.com/postcss/postcss#usage
            {loader: 'postcss-loader',
                ident: 'postcss',
                options: { plugins: () => [precss, autoprefixer]}},
            {loader: 'sass-loader',
             options: {importer: jsonImporter()}},
        ],
        include: [
          path.resolve(__dirname, 'frontend', 'src/stylesheets'),
          path.resolve(__dirname, 'frontend', 'src/components'),
        ],
      },
      {
        test: /\.css$/,
        use: [
          'style-loader',
          'css-loader',
        ],
      },
      {
        test: /\.(ttf|eot|png|jpg|svg)(\?.*$|$)$/,
        use: [
          {
            loader: 'file-loader',
            options: {
              file: 'name=[name].[ext]'
            }
          }
        ]
      },
      {
        test: /\.woff(2)?(\?v=[0-9]\.[0-9]\.[0-9])?$/,
        use: [
          {
            loader: 'url-loader',
            options: {
              limit: '10000',
              mimetype: 'application/font-woff'
            }
          }
        ]
      },
    ],
  },
  resolve: {
    extensions: ['.js', '.jsx'],
  },
};
