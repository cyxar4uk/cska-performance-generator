const { createProxyMiddleware } = require('http-proxy-middleware');

const BACKEND_URL = process.env.BACKEND_URL || 'http://127.0.0.1:8000';

module.exports = function(app) {
  app.use(
    '/api',
    createProxyMiddleware({
      target: BACKEND_URL,
      changeOrigin: true,
      router: function(req) {
        return BACKEND_URL;
      },
      onProxyReq: function(proxyReq, req, res) {
        // Путь уже содержит /api, ничего не меняем
        console.log('Proxying:', req.method, req.url);
      },
    })
  );
};
