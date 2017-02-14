var webpack = require('webpack');
var path = require('path');

module.exports = {
  devtool: 'sourcemap',
  entry: './src/app.js',
  output: {
    path: path.join(__dirname, 'dist', 'js'),
    filename: 'app.bundle.js'
  },
  module: {
    loaders: [
      {
        test: /.jsx?$/,
        loader: 'babel-loader',
        exclude: /node_modules/,
        query: {
          presets: ['es2015', 'react']
        }
      }
    ]
  }
}
