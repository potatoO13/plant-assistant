# 种田记小程序API契约

## 1. GET /api/health

用于检查后端是否可用。

推荐返回：

```json
{
  "status": "ok",
  "time": "2026-05-16T10:00:00+08:00"
}
```

## 2. GET /api/device/latest

用于首页Dashboard展示最新环境数据。

推荐返回：

```json
{
  "plant_id": 1,
  "plant_name": "绿萝",
  "device_id": "device001",
  "device_status": "online",
  "temperature": 23.6,
  "air_humidity": 58.2,
  "soil_moisture": 42.5,
  "light": 1260,
  "created_at": "2026-05-16T10:00:00+08:00"
}
```

字段说明：

| 字段 | 类型 | 说明 |
|---|---|---|
| plant_id | number | 当前植物ID |
| plant_name | string | 当前植物名称 |
| device_id | string | 设备编号，MVP固定device001 |
| device_status | string | online/offline |
| temperature | number | 温度，单位℃ |
| air_humidity | number | 空气湿度，单位% |
| soil_moisture | number | 土壤湿度，单位% |
| light | number | 光照强度，单位lux |
| created_at | string | 数据时间 |

## 3. GET /api/device/history?range=day或week

用于历史数据页折线图。

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

小程序也兼容如下列表格式：

```json
{
  "items": [
    {"time": "08:00", "temperature": 23.1, "soil_moisture": 45, "light": 280}
  ]
}
```

## 4. POST /api/watering/manual

用于一键浇水。

请求体：

```json
{
  "duration_sec": 5
}
```

推荐返回：

```json
{
  "request_id": "water_20260516_001",
  "status": "pending",
  "message": "watering command published",
  "duration_sec": 5
}
```

说明：

- 小程序端只提供3、5、10秒三档。
- 后端必须再次校验最大10秒。
- 后端应写入watering_log并向MQTT `plant/device001/control` 发布控制消息。

## 5. GET /api/watering/logs?limit=5

用于控制页展示最近浇水记录。

推荐返回：

```json
[
  {
    "id": 1,
    "request_id": "water_20260516_001",
    "device_id": "device001",
    "duration_sec": 5,
    "source": "manual",
    "status": "success",
    "created_at": "2026-05-16T10:00:00+08:00",
    "finished_at": "2026-05-16T10:00:05+08:00"
  }
]
```

## 6. GET /api/plants/search?keyword=绿萝

用于植物百科搜索。

推荐返回：

```json
[
  {
    "id": 1,
    "name": "绿萝",
    "alias": "黄金葛、魔鬼藤"
  }
]
```

## 7. GET /api/plants/{plant_id}

用于植物详情展示。

推荐返回：

```json
{
  "id": 1,
  "name": "绿萝",
  "alias": "黄金葛、魔鬼藤",
  "temp_min": 18,
  "temp_max": 28,
  "soil_min": 35,
  "soil_max": 70,
  "light_min": 300,
  "light_max": 2500,
  "light_desc": "明亮散射光，避免强烈直射",
  "watering_advice": "保持盆土微湿，表层土变干后再补水。",
  "care_tips": "适合室内养护，注意通风，冬季减少浇水。",
  "common_problems": "叶片发黄多与积水、低温或光照不足有关。"
}
```

## 8. GET /api/advice/current

用于首页建议卡片和建议页。

推荐返回：

```json
{
  "status": "warning",
  "summary": "当前绿萝存在土壤偏干、光照偏弱两项提醒。",
  "advices": [
    {
      "type": "soil_moisture",
      "severity": "warning",
      "title": "土壤偏干",
      "text": "当前土壤湿度低于绿萝适宜范围，建议短时补水后观察。",
      "suggest_watering": true
    }
  ]
}
```

状态枚举：

| 值 | 含义 |
|---|---|
| normal | 正常 |
| warning | 提醒 |
| danger | 异常 |

