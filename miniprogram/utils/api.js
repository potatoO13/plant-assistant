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

function searchPlants(keyword = '') {
  return request.get(API.PLANTS_SEARCH, { keyword });
}

function getPlantDetail(id) {
  return request.get(`${API.PLANT_DETAIL}/${id}`);
}

function getCurrentAdvice() {
  return request.get(API.ADVICE_CURRENT);
}

module.exports = {
  health,
  getLatest,
  getHistory,
  manualWatering,
  getWateringLogs,
  searchPlants,
  getPlantDetail,
  getCurrentAdvice
};
