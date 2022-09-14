const path = require('path');
const { merge } = require("webpack-merge");
const common = require("./webpack.common.js");
const { stylePaths } = require("../stylePaths");
const HOST = process.env.HOST || "localhost";
const PORT = process.env.PORT || "8080";

module.exports = merge(common('development'), {
  mode: "development",
  devtool: "eval-source-map",
  devServer: {
    static: "./dist",
    host: HOST,
    port: PORT,
    compress: true,
    historyApiFallback: true,
    open: true,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
      "Access-Control-Allow-Headers": "X-Requested-With, content-type, Authorization"
    },
    proxy: {
      '/api': {
        target: 'http://localhost:9000',
        changeOrigin: true,
        ws: true
      },
      '/ping': {
        target: 'http://localhost:9000',
        changeOrigin: true,
        ws: true
      }
    }
  },
  module: {
    rules: [
      {
        test: /\.(sa|sc|c)ss$/i,
        use: [
          "style-loader",
          "css-loader",
          "postcss-loader",
          "sass-loader",
        ],
      }
    ]
  }
});
