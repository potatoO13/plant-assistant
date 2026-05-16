# Backend

FastAPI 后端负责：

- 提供小程序 HTTP API
- 维护 SQLite 数据库
- 连接 MQTT Broker
- 接收 ESP32 telemetry 并写库
- 发布手动浇水控制消息
- 接收 control_ack 并更新浇水记录
- 生成规则型养护建议

## 启动

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python seed_data.py
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 配置环境变量

- `DEVICE_ID`：默认 `device001`
- `DEFAULT_PLANT_ID`：默认 `1`
- `DATABASE_URL`：默认 `sqlite:///./plant_assistant.db`
- `MQTT_HOST`：默认 `localhost`
- `MQTT_PORT`：默认 `1883`
- `MQTT_USERNAME`
- `MQTT_PASSWORD`

## 核心接口

- `GET /api/health`
- `GET /api/device/latest`
- `GET /api/device/history?range=day`
- `GET /api/plants/search?keyword=绿萝`
- `GET /api/plants/{plant_id}`
- `GET /api/advice/current`
- `POST /api/watering/manual`
