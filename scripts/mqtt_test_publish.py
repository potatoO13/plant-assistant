import argparse
import json
from datetime import datetime

import paho.mqtt.client as mqtt


def create_client():
    if hasattr(mqtt, "CallbackAPIVersion"):
        return mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id="mqtt-test-publisher")
    return mqtt.Client(client_id="mqtt-test-publisher")


def main():
    parser = argparse.ArgumentParser(description="Publish one test telemetry message")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=1883)
    parser.add_argument("--topic", default="plant/device001/telemetry")
    args = parser.parse_args()

    payload = {
        "device_id": "device001",
        "temperature": 23.6,
        "air_humidity": 58.2,
        "soil_moisture": 42.5,
        "light": 1260,
        "timestamp": datetime.now().replace(microsecond=0).isoformat(),
    }

    client = create_client()
    client.connect(args.host, args.port, 60)
    client.publish(args.topic, json.dumps(payload, ensure_ascii=False), qos=1)
    client.disconnect()
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
