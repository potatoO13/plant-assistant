# 基于 ESP32 和微信小程序的智能种植助手

这是项目 MVP 初始框架：单用户、单设备、单植物，不包含复杂登录、多设备绑定和权限系统。

## 目录

- `backend/`：FastAPI 后端、SQLite 数据库、MQTT 客户端、规则建议模块
- `scripts/`：ESP32 模拟器和 MQTT 测试脚本
- `firmware/`：ESP32 固件占位框架
- `data/`：植物种子数据
- `docs/`：协议、API、数据库和测试文档

## 本地启动

1. 启动 MQTT Broker，例如 Mosquitto：

```powershell
mosquitto -v
```

2. 启动后端：

```powershell
cd plant-assistant\backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python seed_data.py
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

3. 启动 ESP32 模拟器：

```powershell
cd plant-assistant
python scripts\mock_esp32.py
```

4. 访问健康检查：

```text
http://127.0.0.1:8000/api/health
```

5. 手动浇水：

```powershell
curl -X POST http://127.0.0.1:8000/api/watering/manual -H "Content-Type: application/json" -d "{\"duration_sec\":5}"
```

## 当前 MVP 默认值

- 设备 ID：`device001`
- 默认植物：`plant.id = 1`，即绿萝
- Telemetry Topic：`plant/device001/telemetry`
- Control Topic：`plant/device001/control`
- Control ACK Topic：`plant/device001/control_ack`
- SQLite 文件：`backend/plant_assistant.db`

## 微信小程序对接建议

域名备案完成前，可以先使用本地局域网 IP 或内网穿透调试小程序请求。MVP 页面建议先做：

- 首页：展示最新温度、空气湿度、土壤湿度、光照
- 趋势页：调用 `/api/device/history?range=day`
- 植物页：调用 `/api/plants/search` 和 `/api/plants/{plant_id}`
- 建议页：调用 `/api/advice/current`
- 浇水按钮：调用 `/api/watering/manual`
