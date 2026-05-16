import argparse
import json
import random
import signal
import time
from datetime import datetime

import paho.mqtt.client as mqtt


DEVICE_ID = "device001"


def create_client(client_id):
    if hasattr(mqtt, "CallbackAPIVersion"):
        return mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id=client_id)
    return mqtt.Client(client_id=client_id)


class MockEsp32:
    def __init__(self, args):
        self.host = args.host
        self.port = args.port
        self.interval = args.interval
        self.device_id = args.device_id
        self.telemetry_topic = f"plant/{self.device_id}/telemetry"
        self.control_topic = f"plant/{self.device_id}/control"
        self.ack_topic = f"plant/{self.device_id}/control_ack"
        self.running = True
        self.soil_moisture = random.uniform(35.0, 55.0)

        self.client = create_client(f"mock-esp32-{self.device_id}")
        if args.username:
            self.client.username_pw_set(args.username, args.password)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    @staticmethod
    def now_iso():
        return datetime.now().replace(microsecond=0).isoformat()

    def on_connect(self, client, userdata, flags, rc):
        if rc != 0:
            print(f"[mqtt] connect failed rc={rc}")
            return
        print(f"[mqtt] connected {self.host}:{self.port}")
        client.subscribe(self.control_topic, qos=1)
        print(f"[mqtt] subscribed {self.control_topic}")

    def on_message(self, client, userdata, msg):
        text = msg.payload.decode("utf-8", errors="replace")
        print(f"[control] {msg.topic}: {text}")
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            return

        if payload.get("command") != "water":
            return

        duration_sec = min(int(payload.get("duration_sec", 1)), 10)
        request_id = payload.get("request_id")
        print(f"[watering] start {duration_sec}s request_id={request_id}")
        time.sleep(duration_sec)
        self.soil_moisture = min(100.0, self.soil_moisture + random.uniform(8.0, 18.0))

        ack = {
            "device_id": self.device_id,
            "request_id": request_id,
            "command": "water",
            "duration_sec": duration_sec,
            "status": "done",
            "timestamp": self.now_iso(),
        }
        self.publish(self.ack_topic, ack)
        print(f"[watering] done request_id={request_id}")

    def sensor_payload(self):
        self.soil_moisture = max(0.0, self.soil_moisture - random.uniform(0.1, 0.4))
        daylight = 6 <= datetime.now().hour <= 18
        return {
            "device_id": self.device_id,
            "temperature": round(random.uniform(22.0, 28.5), 1),
            "air_humidity": round(random.uniform(48.0, 72.0), 1),
            "soil_moisture": round(self.soil_moisture, 1),
            "light": random.randint(800, 3000) if daylight else random.randint(0, 80),
            "timestamp": self.now_iso(),
        }

    def publish(self, topic, payload):
        message = json.dumps(payload, ensure_ascii=False)
        self.client.publish(topic, message, qos=1)
        print(f"[publish] {topic}: {message}")

    def run(self):
        self.client.connect(self.host, self.port, 60)
        self.client.loop_start()
        try:
            while self.running:
                self.publish(self.telemetry_topic, self.sensor_payload())
                for _ in range(self.interval):
                    if not self.running:
                        break
                    time.sleep(1)
        finally:
            self.client.loop_stop()
            self.client.disconnect()


def main():
    parser = argparse.ArgumentParser(description="Mock ESP32 for Plant Assistant")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=1883)
    parser.add_argument("--username")
    parser.add_argument("--password")
    parser.add_argument("--device-id", default=DEVICE_ID)
    parser.add_argument("--interval", type=int, default=30)
    args = parser.parse_args()

    device = MockEsp32(args)

    def stop(signum, frame):
        device.running = False

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    device.run()


if __name__ == "__main__":
    main()
