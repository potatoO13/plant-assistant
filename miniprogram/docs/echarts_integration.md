# ECharts for 微信小程序接入说明

## 1. 当前项目的接入方式

历史数据页已经使用组件方式接入图表：

```json
{
  "usingComponents": {
    "ec-canvas": "../../components/ec-canvas/ec-canvas"
  }
}
```

WXML：

```xml
<ec-canvas id="historyChart" canvas-id="historyChart"></ec-canvas>
```

JS：

```js
const echarts = require('../../components/ec-canvas/echarts');

component.init((canvas) => {
  const chart = echarts.init(canvas);
  chart.setOption(option);
  return chart;
});
```

## 2. 为什么ZIP中内置轻量实现

为了保证本压缩包在离线环境下也能直接打开和演示，`components/ec-canvas/echarts.js` 内置了一个轻量接口兼容层，支持折线图的基础绘制和ECharts风格的 `setOption` 写法。

正式开发中如需完整ECharts能力，请替换为官方ECharts微信小程序版文件：

1. 下载官方 `echarts-for-weixin` 示例项目。
2. 复制官方 `ec-canvas` 目录到本项目 `components/ec-canvas`。
3. 保留 `pages/history/history.js` 中的 `setOption` 配置。
4. 在微信开发者工具中重新编译。

## 3. 当前折线图option结构

```js
const option = {
  legend: { data: ['温度', '土壤湿度', '光照'] },
  xAxis: { type: 'category', data: labels },
  yAxis: { type: 'value' },
  series: [
    { name: '温度', type: 'line', data: temperature },
    { name: '土壤湿度', type: 'line', data: soil },
    { name: '光照', type: 'line', data: light }
  ]
};
```

## 4. 后端历史数据建议

推荐返回：

```json
{
  "range": "day",
  "labels": ["08:00", "09:00", "10:00"],
  "series": {
    "temperature": [23.1, 23.8, 24.5],
    "soil_moisture": [45, 43, 41],
    "light": [280, 620, 1100]
  }
}
```

