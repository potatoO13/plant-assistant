const API = require('../config/api');

function buildQuery(data = {}) {
  return Object.keys(data)
    .filter((key) => data[key] !== undefined && data[key] !== null && data[key] !== '')
    .map((key) => `${encodeURIComponent(key)}=${encodeURIComponent(data[key])}`)
    .join('&');
}

function appendQuery(url, data = {}) {
  const query = buildQuery(data);
  if (!query) return url;
  return `${url}${url.indexOf('?') >= 0 ? '&' : '?'}${query}`;
}

function normalizeErrorMessage(err, fallback = '请求失败') {
  if (!err) return fallback;
  if (typeof err === 'string') return err;
  return err.errMsg || err.message || fallback;
}

function detailToText(detail) {
  if (!detail) return '';
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === 'string') return item;
        return item.msg || item.message || JSON.stringify(item);
      })
      .join('；');
  }
  return detail.message || detail.msg || JSON.stringify(detail);
}

function getResponseMessage(data) {
  if (!data) return '';
  return data.message || detailToText(data.detail) || data.error || '';
}

function request(method, url, data = {}, options = {}) {
  const upperMethod = method.toUpperCase();
  const requestUrl = upperMethod === 'GET' ? appendQuery(url, data) : url;
  const timeout = options.timeout || API.REQUEST_TIMEOUT || 8000;

  return new Promise((resolve, reject) => {
    wx.request({
      url: requestUrl,
      method: upperMethod,
      data: upperMethod === 'GET' ? {} : data,
      timeout,
      header: {
        'content-type': 'application/json'
      },
      success(res) {
        const statusCode = res.statusCode || 0;
        if (statusCode < 200 || statusCode >= 300) {
          const message = getResponseMessage(res.data);
          const error = new Error(message || `接口异常：HTTP ${statusCode}`);
          error.statusCode = statusCode;
          error.response = res.data;
          reject(error);
          return;
        }
        resolve(res.data);
      },
      fail(err) {
        reject(new Error(`请求失败：${normalizeErrorMessage(err)}`));
      }
    });
  });
}

function get(url, data = {}, options = {}) {
  return request('GET', url, data, options);
}

function post(url, data = {}, options = {}) {
  return request('POST', url, data, options);
}

module.exports = {
  request,
  get,
  post,
  appendQuery
};
