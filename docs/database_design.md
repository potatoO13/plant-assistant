# Database Design

SQLite 数据库文件默认位于 `backend/plant_assistant.db`。

## device

设备表。MVP 只使用 `device001`。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | integer | 主键 |
| `device_id` | string | 设备唯一 ID |
| `name` | string | 设备名称 |
| `status` | string | `online` 或 `offline` |
| `created_at` | datetime | 创建时间 |
| `last_seen_at` | datetime | 最近 telemetry 时间 |

## sensor_data

传感器数据表。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | integer | 主键 |
| `device_id` | string | 设备 ID |
| `temperature` | float | 温度 |
| `air_humidity` | float | 空气湿度 |
| `soil_moisture` | float | 土壤湿度 |
| `light` | float | 光照 |
| `timestamp` | datetime | 设备上报时间 |
| `created_at` | datetime | 入库时间 |

## plant

植物知识表。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | integer | 主键 |
| `name` | string | 植物名称 |
| `temp_min` | float | 适宜最低温度 |
| `temp_max` | float | 适宜最高温度 |
| `soil_moisture_min` | float | 适宜最低土壤湿度 |
| `soil_moisture_max` | float | 适宜最高土壤湿度 |
| `light_min` | float | 适宜最低光照 |
| `light_max` | float | 适宜最高光照 |
| `watering_advice` | text | 浇水建议 |
| `care_advice` | text | 养护建议 |

## watering_log

浇水控制记录表。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | integer | 主键 |
| `request_id` | string | 控制请求 ID |
| `device_id` | string | 设备 ID |
| `duration_sec` | integer | 浇水时长 |
| `status` | string | `requested`、`sent`、`done`、`publish_failed` 等 |
| `requested_at` | datetime | 请求时间 |
| `ack_at` | datetime | 设备确认时间 |
| `message` | text | ACK 原始 JSON |

## advice_log

建议记录表。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | integer | 主键 |
| `plant_id` | integer | 植物 ID |
| `sensor_data_id` | integer | 传感器数据 ID |
| `status` | string | `ok` 或 `warning` |
| `summary` | text | 建议摘要 |
| `advices_json` | text | 建议数组 JSON |
| `created_at` | datetime | 生成时间 |
