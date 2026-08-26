import json
import os
import time
import urllib.request
from datetime import datetime

import paho.mqtt.client as mqtt


DEVICE_ID = os.getenv("DEVICE_ID", "device001")
MQTT_HOST = os.getenv("MQTT_HOST", "59.110.139.200")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
API_BASE = os.getenv("API_BASE", "https://api.zhongtianji.com.cn")
CONTROL_TOPIC = f"plant/{DEVICE_ID}/control"
ACK_TOPIC = f"plant/{DEVICE_ID}/control_ack"
TELEMETRY_TOPIC = f"plant/{DEVICE_ID}/telemetry"


def now_iso():
    return datetime.now().replace(microsecond=0).isoformat()


def http_json(method, url, payload=None):
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    username = os.getenv("MQTT_USERNAME")
    password = os.getenv("MQTT_PASSWORD")
    result = {
        "connected": False,
        "telemetry_published": False,
        "watering_request": None,
        "control_received": None,
        "ack_published": False,
        "final_log": None,
    }

    def on_connect(client, userdata, flags, rc):
        result["connected"] = rc == 0
        print(f"mqtt_connected={result['connected']} rc={rc}", flush=True)
        if rc == 0:
            client.subscribe(CONTROL_TOPIC, qos=1)

    def on_message(client, userdata, msg):
        text = msg.payload.decode("utf-8", errors="replace")
        print(f"control_payload={text}", flush=True)
        payload = json.loads(text)
        result["control_received"] = payload
        ack = {
            "device_id": DEVICE_ID,
            "request_id": payload.get("request_id"),
            "command": "water",
            "status": "success",
            "message": "revival cloud loop test completed",
            "duration_sec": payload.get("duration_sec"),
            "finished_at": now_iso(),
        }
        client.publish(ACK_TOPIC, json.dumps(ack, ensure_ascii=False), qos=1)
        result["ack_published"] = True
        print(f"ack_payload={json.dumps(ack, ensure_ascii=False)}", flush=True)

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id=f"revival-test-{int(time.time())}")
    if username:
        client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_HOST, MQTT_PORT, 60)
    client.loop_start()

    deadline = time.time() + 10
    while not result["connected"] and time.time() < deadline:
        time.sleep(0.2)
    if not result["connected"]:
        raise RuntimeError("MQTT connect failed")

    telemetry = {
        "device_id": DEVICE_ID,
        "temperature": 25.6,
        "air_humidity": 61.2,
        "soil_moisture": 42.3,
        "light": 888,
        "timestamp": now_iso(),
    }
    client.publish(TELEMETRY_TOPIC, json.dumps(telemetry, ensure_ascii=False), qos=1)
    result["telemetry_published"] = True
    print(f"telemetry_payload={json.dumps(telemetry, ensure_ascii=False)}", flush=True)

    time.sleep(1)
    result["watering_request"] = http_json(
        "POST",
        f"{API_BASE}/api/watering/manual",
        {"duration_sec": 3, "source": "revival_cloud_loop_test"},
    )
    print(f"watering_request={json.dumps(result['watering_request'], ensure_ascii=False)}", flush=True)

    request_id = result["watering_request"]["request_id"]
    deadline = time.time() + 12
    while result["control_received"] is None and time.time() < deadline:
        time.sleep(0.2)

    time.sleep(2)
    logs = http_json("GET", f"{API_BASE}/api/watering/logs?limit=10")
    result["final_log"] = next(
        (item for item in logs.get("items", []) if item.get("request_id") == request_id),
        None,
    )
    print(f"final_log={json.dumps(result['final_log'], ensure_ascii=False)}", flush=True)

    client.loop_stop()
    client.disconnect()

    ok = (
        result["connected"]
        and result["telemetry_published"]
        and result["control_received"] is not None
        and result["ack_published"]
        and result["final_log"]
        and result["final_log"].get("status") == "success"
    )
    print(f"revival_cloud_loop_ok={ok}", flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
