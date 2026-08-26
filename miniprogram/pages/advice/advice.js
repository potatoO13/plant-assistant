const api = require('../../utils/api');
const { statusText, statusClass } = require('../../utils/format');

function normalizeAdviceItem(item, index, fallbackStatus) {
  if (typeof item === 'string') {
    return {
      type: `advice_${index}`,
      severity: fallbackStatus || 'normal',
      title: item.length > 14 ? item.slice(0, 14) : item,
      text: item,
      suggest_watering: item.indexOf('浇水') >= 0 && item.indexOf('暂停浇水') < 0
    };
  }
  return item || {};
}

Page({
  data: {
    advice: {},
    advices: [],
    statusText: '--',
    statusClass: 'tag-normal'
  },

  onLoad() {
    this.loadAdvice();
  },

  onShow() {
    this.loadAdvice();
  },

  onPullDownRefresh() {
    this.loadAdvice().finally(() => wx.stopPullDownRefresh());
  },

  async loadAdvice() {
    try {
      wx.showLoading({ title: '加载中' });
      const advice = await api.getCurrentAdvice();
      const list = advice.advices || [];
      const advices = list.map((item, index) => {
        const normalized = normalizeAdviceItem(item, index, advice.status);
        const severity = normalized.severity || advice.status || 'normal';
        return {
          ...normalized,
          severityText: statusText(severity),
          tagClass: statusClass(severity),
          severityClass: severity === 'danger' ? 'danger' : (severity === 'warning' ? 'warning' : '')
        };
      });
      this.setData({
        advice,
        advices,
        statusText: statusText(advice.status || 'normal'),
        statusClass: statusClass(advice.status || 'normal')
      });
    } catch (err) {
      console.error(err);
      wx.showToast({ title: '建议加载失败', icon: 'none' });
    } finally {
      wx.hideLoading();
    }
  },

  goControl() {
    wx.switchTab({ url: '/pages/control/control' });
  }
});
