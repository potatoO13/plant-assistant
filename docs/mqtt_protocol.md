# MQTT Protocol

## Broker

本地开发可使用 Mosquitto 或 EMQX。

默认连接：

- Host：`localhost`
- Port：`1883`
- Device ID：`device001`

## Topics

| Topic | 方向 | 说明 |
| --- | --- | --- |
| `plant/device001/telemetry` | ESP32 -> 后端 | 传感器数据上报 |
| `plant/device001/control` | 后端 -> ESP32 | 控制指令 |
| `plant/device001/control_ack` | ESP32 -> 后端 | 控制执行确认 |

## Telemetry

Topic：`plant/device001/telemetry`

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

字段说明：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `device_id` | string | 设备 ID |
| `temperature` | number | 温度，单位摄氏度 |
| `air_humidity` | number | 空气湿度，百分比 |
| `soil_moisture` | number | 土壤湿度，百分比 |
| `light` | number | 光照，单位 lux |
| `timestamp` | string | ISO 8601 时间 |

## Control

Topic：`plant/device001/control`

```json
{
  "command": "water",
  "duration_sec": 5,
  "request_id": "9fb3b55e2cf34fd5a912ac932e66b7be",
  "timestamp": "2026-05-08T20:30:00"
}
```

规则：

- `duration_sec` 最大 10 秒
- ESP32 端也必须做 10 秒上限保护
- `request_id` 用于后端关联 `watering_log`

## Control ACK

Topic：`plant/device001/control_ack`

```json
{
  "device_id": "device001",
  "request_id": "9fb3b55e2cf34fd5a912ac932e66b7be",
  "command": "water",
  "duration_sec": 5,
  "status": "done",
  "timestamp": "2026-05-08T20:30:05"
}
```

常见状态：

- `done`：执行完成
- `failed`：执行失败
- `interrupted`：被新指令中断
