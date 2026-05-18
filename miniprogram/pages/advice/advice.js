const api = require('../../utils/api');
const { statusText, statusClass } = require('../../utils/format');

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
      const advices = list.map((item) => ({
        ...item,
        severityText: statusText(item.severity || advice.status),
        tagClass: statusClass(item.severity || advice.status),
        severityClass: item.severity === 'danger' ? 'danger' : (item.severity === 'warning' ? 'warning' : '')
      }));
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
