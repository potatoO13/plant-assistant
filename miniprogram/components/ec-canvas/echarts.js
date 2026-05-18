/**
 * MVP内置ECharts接口兼容层。
 * 页面代码按ECharts setOption写法组织；如需正式能力，可将本文件替换为Apache ECharts官方微信小程序版echarts.js，
 * 并保留ec-canvas组件调用方式。
 */
function getSeriesColor(index) {
  const colors = ['#2FA66A', '#F2A33A', '#4C86D9', '#D95757'];
  return colors[index % colors.length];
}

function toNumberList(list = []) {
  return list.map((item) => {
    if (item === null || item === undefined || item === '') return null;
    const num = Number(item);
    return Number.isNaN(num) ? null : num;
  });
}

function getTextWidth(text) {
  return String(text).length * 6;
}

class TinyEChart {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.ctx;
    this.width = canvas.width || 320;
    this.height = canvas.height || 260;
    this.option = null;
  }

  setOption(option) {
    this.option = option;
    this.draw();
  }

  clear() {
    const ctx = this.ctx;
    ctx.clearRect(0, 0, this.width, this.height);
    ctx.draw(true);
  }

  resize() {
    this.draw();
  }

  dispatchAction() {
    // 轻量实现中暂不处理交互事件，保留接口避免页面报错。
  }

  drawBackground() {
    const ctx = this.ctx;
    ctx.setFillStyle('#FFFFFF');
    ctx.fillRect(0, 0, this.width, this.height);
  }

  drawLegend(series) {
    const ctx = this.ctx;
    let x = 16;
    const y = 22;
    series.forEach((item, index) => {
      const color = item.color || getSeriesColor(index);
      ctx.setFillStyle(color);
      ctx.beginPath();
      ctx.arc(x + 5, y - 4, 5, 0, Math.PI * 2);
      ctx.fill();
      ctx.setFillStyle('#53685A');
      ctx.setFontSize(11);
      ctx.fillText(item.name || `系列${index + 1}`, x + 16, y);
      x += getTextWidth(item.name || '') + 62;
    });
  }

  draw() {
    const ctx = this.ctx;
    const option = this.option || {};
    const xData = (option.xAxis && option.xAxis.data) || [];
    const series = (option.series || []).map((item, index) => ({
      ...item,
      data: toNumberList(item.data || []),
      color: item.color || getSeriesColor(index)
    }));

    this.drawBackground();
    this.drawLegend(series);

    const padding = { left: 42, right: 18, top: 48, bottom: 42 };
    const chartWidth = this.width - padding.left - padding.right;
    const chartHeight = this.height - padding.top - padding.bottom;
    const values = [];
    series.forEach((item) => {
      item.data.forEach((value) => {
        if (value !== null && value !== undefined && !Number.isNaN(value)) values.push(value);
      });
    });
    const rawMin = values.length ? Math.min(...values) : 0;
    const rawMax = values.length ? Math.max(...values) : 100;
    const span = rawMax - rawMin || 1;
    const min = Math.max(0, Math.floor(rawMin - span * 0.15));
    const max = Math.ceil(rawMax + span * 0.15);

    ctx.setStrokeStyle('#E4EFE7');
    ctx.setLineWidth(1);
    ctx.setFontSize(10);
    ctx.setFillStyle('#8A9A8E');

    for (let i = 0; i <= 4; i += 1) {
      const y = padding.top + (chartHeight / 4) * i;
      ctx.beginPath();
      ctx.moveTo(padding.left, y);
      ctx.lineTo(this.width - padding.right, y);
      ctx.stroke();
      const label = Math.round(max - ((max - min) / 4) * i);
      ctx.fillText(String(label), 8, y + 4);
    }

    const xCount = Math.max(xData.length, 1);
    xData.forEach((label, index) => {
      const show = xData.length <= 7 || index % 2 === 0 || index === xData.length - 1;
      if (!show) return;
      const x = padding.left + (xCount === 1 ? 0 : (chartWidth / (xCount - 1)) * index);
      ctx.setFillStyle('#8A9A8E');
      ctx.fillText(String(label), Math.max(0, x - 16), this.height - 14);
    });

    series.forEach((item) => {
      if (!item.data.length) return;
      let hasStarted = false;
      ctx.beginPath();
      ctx.setStrokeStyle(item.color);
      ctx.setLineWidth(2);
      item.data.forEach((value, index) => {
        if (value === null || value === undefined || Number.isNaN(value)) {
          hasStarted = false;
          return;
        }
        const x = padding.left + (item.data.length === 1 ? 0 : (chartWidth / (item.data.length - 1)) * index);
        const y = padding.top + chartHeight - ((value - min) / (max - min)) * chartHeight;
        if (!hasStarted) {
          ctx.moveTo(x, y);
          hasStarted = true;
        }
        else ctx.lineTo(x, y);
      });
      ctx.stroke();

      item.data.forEach((value, index) => {
        if (value === null || value === undefined || Number.isNaN(value)) return;
        const x = padding.left + (item.data.length === 1 ? 0 : (chartWidth / (item.data.length - 1)) * index);
        const y = padding.top + chartHeight - ((value - min) / (max - min)) * chartHeight;
        ctx.setFillStyle('#FFFFFF');
        ctx.beginPath();
        ctx.arc(x, y, 3.5, 0, Math.PI * 2);
        ctx.fill();
        ctx.setStrokeStyle(item.color);
        ctx.setLineWidth(1.5);
        ctx.beginPath();
        ctx.arc(x, y, 3.5, 0, Math.PI * 2);
        ctx.stroke();
      });
    });

    ctx.draw();
  }
}

function init(canvas) {
  return new TinyEChart(canvas);
}

module.exports = {
  init
};
