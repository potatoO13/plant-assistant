// API centralized configuration.
// Development examples:
// - Local FastAPI backend: http://127.0.0.1:8000
// - Cloud server backend: http://服务器公网IP
// - Production: https://api.zhongtianji.com.cn
const API_BASE_URL = 'https://api.zhongtianji.com.cn';
//const API_BASE_URL = "http://127.0.0.1:8000";

const API = {
  BASE_URL: API_BASE_URL,
  REQUEST_TIMEOUT: 8000,
  HEALTH: `${API_BASE_URL}/api/health`,
  DEVICE_LATEST: `${API_BASE_URL}/api/device/latest`,
  DEVICE_HISTORY: `${API_BASE_URL}/api/device/history`,
  WATERING_MANUAL: `${API_BASE_URL}/api/watering/manual`,
  WATERING_LOGS: `${API_BASE_URL}/api/watering/logs`,
  PLANTS_SEARCH: `${API_BASE_URL}/api/plants/search`,
  PLANT_DETAIL: `${API_BASE_URL}/api/plants`,
  ADVICE_CURRENT: `${API_BASE_URL}/api/advice/current`
};

module.exports = API;
