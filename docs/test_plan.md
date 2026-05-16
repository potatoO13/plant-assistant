# Test Plan

## 目标

在真实 ESP32 到货前，用 `scripts/mock_esp32.py` 验证完整链路：

```text
mock_esp32 -> MQTT telemetry -> FastAPI 后端 -> SQLite
FastAPI 手动浇水 API -> MQTT control -> mock_esp32 -> MQTT control_ack -> SQLite
```

## 准备

1. 启动 MQTT Broker：

```powershell
mosquitto -v
```

2. 启动后端：

```powershell
cd plant-assistant\backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

3. 启动模拟 ESP32：

```powershell
cd plant-assistant
python scripts\mock_esp32.py
```

## 测试项

### 1. 健康检查

```powershell
curl http://127.0.0.1:8000/api/health
```

期望：

- `status` 为 `ok`
- MQTT Broker 正常时 `mqtt_connected` 为 `true`

### 2. telemetry 入库

等待 mock ESP32 发布一次 telemetry 后：

```powershell
curl http://127.0.0.1:8000/api/device/latest
```

期望：

- 返回 `device_id=device001`
- 包含温度、空气湿度、土壤湿度、光照、时间戳

### 3. 历史数据

```powershell
curl "http://127.0.0.1:8000/api/device/history?range=day"
curl "http://127.0.0.1:8000/api/device/history?range=week"
```

期望：

- 返回数组，按时间升序排列

### 4. 植物搜索

```powershell
curl "http://127.0.0.1:8000/api/plants/search?keyword=绿萝"
curl http://127.0.0.1:8000/api/plants/1
```

期望：

- 返回植物阈值和养护建议

### 5. 当前建议

```powershell
curl http://127.0.0.1:8000/api/advice/current
```

期望：

- 返回 `status`
- 返回 `summary`
- 返回 `advices`
- 浇水建议只由 `soil_moisture` 决定

### 6. 手动浇水闭环

```powershell
curl -X POST http://127.0.0.1:8000/api/watering/manual -H "Content-Type: application/json" -d "{\"duration_sec\":5}"
```

期望：

- 后端返回 `request_id`
- mock ESP32 收到 `plant/device001/control`
- mock ESP32 等待 5 秒
- mock ESP32 发布 `plant/device001/control_ack`
- 后端将对应 `watering_log.status` 更新为 `done`

### 7. 浇水上限

```powershell
curl -X POST http://127.0.0.1:8000/api/watering/manual -H "Content-Type: application/json" -d "{\"duration_sec\":11}"
```

期望：

- API 返回 422
- 不发布 MQTT 控制指令
