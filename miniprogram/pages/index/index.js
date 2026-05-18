const api = require('../../utils/api');

function isEmpty(value) {
  return value === null || value === undefined || value === '';
}

function displayValue(value, digits = 1) {
  if (isEmpty(value)) return '--';
  const num = Number(value);
  if (Number.isNaN(num)) return '--';
  return digits === 0 ? String(Math.round(num)) : num.toFixed(digits);
}

function parseDate(value) {
  if (!value) return null;
  if (value instanceof Date) return value;
  const text = String(value).replace(/-/g, '/');
  const date = new Date(text);
  if (!Number.isNaN(date.getTime())) return date;

  const isoDate = new Date(value);
  return Number.isNaN(isoDate.getTime()) ? null : isoDate;
}

function getFreshStatus(createdAt) {
  const date = parseDate(createdAt);
  if (!date) {
    return {
      text: '状态未知',
      className: 'tag-warning'
    };
  }

  const diff = Date.now() - date.getTime();
  if (diff >= 0 && diff <= 2 * 60 * 1000) {
    return {
      text: '在线 / 数据正常',
      className: 'tag-normal'
    };
  }

  return {
    text: '数据可能延迟',
    className: 'tag-warning'
  };
}

Page({
  data: {
    latest: null,
    deviceIdText: '--',
    lightText: '--',
    temperatureText: '--',
    airHumidityText: '--',
    soilMoistureText: '--',
    latestTimeText: '--',
    statusText: '状态未知',
    statusClass: 'tag-warning',
    loading: false,
    errorText: '',
    hasData: false
  },

  onLoad() {
    this.loadLatest();
  },

  onShow() {
    this.loadLatest(false);
  },

  onPullDownRefresh() {
    this.loadLatest(false).finally(() => wx.stopPullDownRefresh());
  },

  refreshData() {
    this.loadLatest(true);
  },

  async loadLatest(showToast = false) {
    if (this.data.loading) return;
    this.setData({ loading: true, errorText: '' });

    try {
      const latest = await api.getLatest();
      this.applyLatest(latest || {});
      if (showToast) {
        wx.showToast({ title: '数据已刷新', icon: 'success' });
      }
    } catch (err) {
      const message = err && err.message ? err.message : '最新数据加载失败';
      this.setData({ errorText: message });
      wx.showToast({ title: '数据加载失败', icon: 'none' });
    } finally {
      this.setData({ loading: false });
    }
  },

  applyLatest(latest) {
    const createdAt = latest.created_at || latest.timestamp || latest.time || '';
    const status = getFreshStatus(createdAt);
    const hasData = Object.keys(latest).length > 0;

    this.setData({
      latest,
      hasData,
      deviceIdText: latest.device_id || '--',
      lightText: displayValue(latest.light, 0),
      temperatureText: displayValue(latest.temperature, 1),
      airHumidityText: displayValue(latest.air_humidity, 1),
      soilMoistureText: displayValue(latest.soil_moisture, 1),
      latestTimeText: createdAt || '--',
      statusText: status.text,
      statusClass: status.className
    });
  },

  goHistory() {
    wx.switchTab({ url: '/pages/history/history' });
  },

  goControl() {
    wx.switchTab({ url: '/pages/control/control' });
  }
});
