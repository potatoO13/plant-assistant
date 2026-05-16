# API Spec

Base URL：`http://127.0.0.1:8000`

## GET /api/health

返回服务状态。

```json
{
  "status": "ok",
  "mqtt_connected": true,
  "device_id": "device001",
  "timestamp": "2026-05-08T20:30:00"
}
```

## GET /api/device/latest

返回最新传感器数据。

```json
{
  "device_id": "device001",
  "temperature": 23.6,
  "air_humidity": 58.2,
  "soil_moisture": 42.5,
  "light": 1260,
  "timestamp": "2026-05-08T20:30:00"
}
```

## GET /api/device/history?range=day

参数：

- `range=day`：最近 1 天
- `range=week`：最近 7 天

返回：

```json
{
  "range": "day",
  "items": [
    {
      "device_id": "device001",
      "temperature": 23.6,
      "air_humidity": 58.2,
      "soil_moisture": 42.5,
      "light": 1260,
      "timestamp": "2026-05-08T20:30:00"
    }
  ]
}
```

## GET /api/plants/search?keyword=xxx

搜索植物，`keyword` 为空时返回全部植物。

## GET /api/plants/{plant_id}

返回植物详情。

```json
{
  "id": 1,
  "name": "绿萝",
  "temp_min": 18,
  "temp_max": 30,
  "soil_moisture_min": 40,
  "soil_moisture_max": 70,
  "light_min": 500,
  "light_max": 3000,
  "watering_advice": "保持土壤微湿，避免长期积水。",
  "care_advice": "适合明亮散射光，定期修剪黄叶。"
}
```

## GET /api/advice/current

基于最新传感器数据和默认植物阈值返回规则建议。

浇水建议只基于 `soil_moisture`，不基于 `air_humidity`。

```json
{
  "status": "warning",
  "summary": "当前环境有需要关注的项目。",
  "advices": [
    "土壤湿度偏低，当前 32.0%，建议适量浇水。"
  ]
}
```

## POST /api/watering/manual

请求体：

```json
{
  "duration_sec": 5
}
```

限制：

- `duration_sec` 最小 1 秒
- `duration_sec` 最大 10 秒

返回：

```json
{
  "request_id": "9fb3b55e2cf34fd5a912ac932e66b7be",
  "device_id": "device001",
  "duration_sec": 5,
  "status": "sent",
  "topic": "plant/device001/control"
}
```
