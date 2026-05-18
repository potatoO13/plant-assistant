# 种田记：微信小程序前端

《种田记：基于 ESP32 和微信小程序的种植助手》微信小程序前端工程。当前轮次支持首页 Dashboard、历史光照折线图，以及控制页模拟浇水闭环联调。

## 本轮功能

- 首页 Dashboard：调用 `GET /api/device/latest`，展示 `device_id`、`light`、`temperature`、`air_humidity`、`soil_moisture`、`created_at`。
- 历史数据页：调用 `GET /api/device/history?range=day` 和 `GET /api/device/history?range=week`，优先绘制光照强度折线图。
- 控制页：支持 3 秒、5 秒、10 秒模拟浇水指令下发，显示 `request_id`，轮询浇水记录直到 `success/failed/rejected/timeout`。

## API Base URL 配置

所有 API 地址集中配置在：

```text
config/api.js
```

修改 `API_BASE_URL` 后全局生效：

```js
const API_BASE_URL = 'https://api.zhongtianji.com.cn';
```

开发阶段可选地址：

- 本地后端：`http://127.0.0.1:8000`
- 云服务器后端：`http://服务器公网IP`
- 正式环境：`https://api.zhongtianji.com.cn`

当前正式联调、真机调试、云端验收请使用 `https://api.zhongtianji.com.cn`。`127.0.0.1` 只适合电脑本地调试。

## 微信开发者工具设置

开发阶段请在微信开发者工具中打开：

```text
详情 → 本地设置 → 勾选“不校验合法域名、web-view（业务域名）、TLS版本以及HTTPS证书”
```

正式发布时需要使用 HTTPS，并在小程序后台配置合法域名。

微信小程序后台 request 合法域名需要配置：

```text
https://api.zhongtianji.com.cn
```

## 调试验证步骤

1. 浏览器访问 `https://api.zhongtianji.com.cn/api/device/latest`，确认能看到 `device_id` 和数字类型 `light`。
2. 浏览器访问 `https://api.zhongtianji.com.cn/api/device/history?range=day`，确认返回 `items` 数组。
3. 打开小程序首页，确认 `light` 显示为真实 lux 数值。
4. 改变 BH1750 光照，等待 ESP32 上报，再点击首页“刷新数据”，确认 `light` 变化。
5. 打开历史页，确认“今日 / 本周”可以切换，并显示光照折线图。
6. 确认 `temperature`、`air_humidity`、`soil_moisture` 为 `null` 时页面显示 `--` 且不报错。

## 小程序控制页模拟浇水联调

当前阶段只做模拟浇水闭环，不接真实水泵，不让小程序直连 MQTT。小程序只调用后端 HTTP API，后端再通过 MQTT 通知 ESP32 模拟执行。

控制页使用接口：

- `POST /api/watering/manual`
- `GET /api/watering/logs`
- `GET /api/device/latest`

一键浇水请求体示例：

```json
{
  "duration_sec": 5
}
```

页面状态流转：

```text
未开始 → 发送中 → pending/执行中 → success/failed/rejected/timeout
```

验收步骤：

1. 打开小程序“控制”页。
2. 确认默认选择 5 秒。
3. 点击“一键浇水5秒”。
4. 页面显示后端返回的 `request_id`，按钮进入禁用状态。
5. 观察 ESP32 串口是否收到 `plant/device001/control` 并模拟执行。
6. 等待页面轮询 `GET /api/watering/logs`，状态变为 `success` 后显示“浇水完成”。
7. 查看“最近浇水记录”，确认能看到 `request_id`、`duration_sec`、`status`、`source`、`created_at`、`finished_at`、`message`。

异常测试：

- 点击控制页底部“开发测试：发送15秒请求”，用于验证后端或 ESP32 的拒绝、失败、超时逻辑。该入口仅用于开发验收，不代表正式浇水档位。
- 快速连续点击“一键浇水”时，前端会在发送中或轮询中禁用按钮并拦截重复提交，避免多个 `request_id` 覆盖页面状态。

## 目录说明

```text
config/api.js                 # API Base URL 与接口地址
utils/request.js              # wx.request GET/POST Promise 封装
utils/api.js                  # 页面使用的业务 API 函数
pages/index/                  # 首页 Dashboard
pages/history/                # 历史数据页
pages/control/                # 模拟浇水闭环控制页
components/ec-canvas/         # ECharts for 微信小程序兼容组件
```

## 当前接口假设

最新数据接口：

```json
{
  "device_id": "device001",
  "temperature": null,
  "air_humidity": null,
  "soil_moisture": null,
  "light": 108,
  "created_at": "2026-05-16 21:00:00"
}
```

历史数据接口优先读取 `items`，同时兼容 `data`、`records`、`list` 或后端直接返回数组。
