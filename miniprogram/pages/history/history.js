const echarts = require('../../components/ec-canvas/echarts');
const api = require('../../utils/api');

function normalizeHistoryResponse(res) {
  if (!res) return [];
  if (Array.isArray(res)) return res;

  const candidates = [res.items, res.data, res.records, res.list];
  for (let i = 0; i < candidates.length; i += 1) {
    if (Array.isArray(candidates[i])) return candidates[i];
  }

  if (res.data && typeof res.data === 'object') {
    return normalizeHistoryResponse(res.data);
  }

  return [];
}

function isNumberLike(value) {
  if (value === null || value === undefined || value === '') return false;
  return !Number.isNaN(Number(value));
}

function toChartValue(value) {
  return isNumberLike(value) ? Number(value) : null;
}

function getTimeLabel(item, index) {
  const raw = item.created_at || item.timestamp || item.time || '';
  if (!raw) return String(index + 1);
  const text = String(raw);
  if (text.length >= 16) return text.slice(5, 16);
  return text;
}

function hasAnyNumber(values) {
  return values.some((value) => value !== null && value !== undefined && !Number.isNaN(Number(value)));
}

function buildSeries(name, data, color) {
  if (!hasAnyNumber(data)) return null;
  return {
    name,
    type: 'line',
    data,
    color,
    smooth: true,
    connectNulls: false
  };
}

function average(values) {
  const nums = values.filter(isNumberLike).map(Number);
  if (!nums.length) return '--';
  const result = nums.reduce((sum, value) => sum + value, 0) / nums.length;
  return result.toFixed(0);
}

Page({
  data: {
    range: 'day',
    rangeText: '今日',
    loading: false,
    errorText: '',
    emptyText: '',
    items: [],
    avgLight: '--'
  },

  onLoad() {
    this.chart = null;
    this.loadHistory();
  },

  async changeRange(e) {
    const range = e.currentTarget.dataset.range;
    if (!range || range === this.data.range) return;
    this.setData({
      range,
      rangeText: range === 'week' ? '本周' : '今日'
    });
    await this.loadHistory();
  },

  async loadHistory() {
    this.setData({ loading: true, errorText: '', emptyText: '' });

    try {
      const raw = await api.getHistory(this.data.range);
      const items = normalizeHistoryResponse(raw);
      const chartData = this.buildChartData(items);

      this.setData({
        items,
        avgLight: average(chartData.light),
        emptyText: items.length ? '' : '暂无历史数据'
      });

      this.renderChart(chartData);
    } catch (err) {
      const message = err && err.message ? err.message : '历史数据加载失败';
      this.setData({ errorText: message, items: [], avgLight: '--' });
      this.renderChart({ labels: [], series: [], light: [] });
      wx.showToast({ title: '历史数据加载失败', icon: 'none' });
    } finally {
      this.setData({ loading: false });
    }
  },

  buildChartData(items) {
    const labels = items.map(getTimeLabel);
    const light = items.map((item) => toChartValue(item.light));
    const temperature = items.map((item) => toChartValue(item.temperature));
    const airHumidity = items.map((item) => toChartValue(item.air_humidity));
    const soilMoisture = items.map((item) => toChartValue(item.soil_moisture));

    const series = [
      buildSeries('光照强度', light, '#F2A33A'),
      buildSeries('温度', temperature, '#2FA66A'),
      buildSeries('空气湿度', airHumidity, '#4C86D9'),
      buildSeries('土壤湿度', soilMoisture, '#8A6BE8')
    ].filter(Boolean);

    return {
      labels,
      light,
      series
    };
  },

  renderChart(chartData) {
    const option = {
      title: { text: '光照历史数据' },
      tooltip: { trigger: 'axis' },
      legend: { data: chartData.series.map((item) => item.name) },
      xAxis: {
        type: 'category',
        data: chartData.labels
      },
      yAxis: {
        type: 'value',
        name: 'lux'
      },
      series: chartData.series
    };

    if (this.chart) {
      this.chart.setOption(option);
      return;
    }

    const component = this.selectComponent('#historyChart');
    if (!component) return;

    component.init((canvas) => {
      const chart = echarts.init(canvas);
      chart.setOption(option);
      this.chart = chart;
      return chart;
    });
  }
});
