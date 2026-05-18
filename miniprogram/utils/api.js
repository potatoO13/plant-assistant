const API = require('../config/api');
const request = require('./request');

function health() {
  return request.get(API.HEALTH);
}

function getLatest() {
  return request.get(API.DEVICE_LATEST);
}

function getHistory(range = 'day') {
  return request.get(API.DEVICE_HISTORY, { range });
}

function manualWatering(durationSec) {
  return request.post(API.WATERING_MANUAL, { duration_sec: durationSec });
}

function getWateringLogs(params = {}) {
  return request.get(API.WATERING_LOGS, params);
}

module.exports = {
  health,
  getLatest,
  getHistory,
  manualWatering,
  getWateringLogs
};
