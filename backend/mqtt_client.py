import json
from datetime import datetime

import paho.mqtt.client as mqtt

from config import settings
from database import SessionLocal
from models import Device, SensorData, WateringLog


class MqttService:
    def __init__(self):
        self.connected = False
        self.client = self._create_client()
        if settings.MQTT_USERNAME:
            self.client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)

        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

    @staticmethod
    def _create_client():
        if hasattr(mqtt, "CallbackAPIVersion"):
            return mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id="plant-assistant-backend")
        return mqtt.Client(client_id="plant-assistant-backend")

    def start(self):
        try:
            self.client.connect(settings.MQTT_HOST, settings.MQTT_PORT, settings.MQTT_KEEPALIVE)
            self.client.loop_start()
        except Exception as exc:
            print(f"[mqtt] connect failed: {exc}")

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()

    def publish_control(self, payload):
        message = json.dumps(payload, ensure_ascii=False)
        result = self.client.publish(settings.MQTT_CONTROL_TOPIC, message, qos=1)
        return result.rc

    def on_connect(self, client, userdata, flags, rc):
        self.connected = rc == 0
        if not self.connected:
            print(f"[mqtt] connect failed rc={rc}")
            return

        print("[mqtt] connected")
        client.subscribe(settings.MQTT_TELEMETRY_TOPIC, qos=1)
        client.subscribe(settings.MQTT_CONTROL_ACK_TOPIC, qos=1)
        print(f"[mqtt] subscribed {settings.MQTT_TELEMETRY_TOPIC}")
        print(f"[mqtt] subscribed {settings.MQTT_CONTROL_ACK_TOPIC}")

    def on_disconnect(self, client, userdata, rc):
        self.connected = False
        print(f"[mqtt] disconnected rc={rc}")

    def on_message(self, client, userdata, msg):
        payload_text = msg.payload.decode("utf-8", errors="replace")
        try:
            payload = json.loads(payload_text)
        except json.JSONDecodeError:
            print(f"[mqtt] invalid json on {msg.topic}: {payload_text}")
            return

        if msg.topic == settings.MQTT_TELEMETRY_TOPIC:
            self.handle_telemetry(payload)
        elif msg.topic == settings.MQTT_CONTROL_ACK_TOPIC:
            self.handle_control_ack(payload)

    @staticmethod
    def parse_timestamp(value):
        if not value:
            return datetime.now()
        try:
            return datetime.fromisoformat(str(value))
        except ValueError:
            return datetime.now()

    def handle_telemetry(self, payload):
        required = ["device_id", "temperature", "air_humidity", "soil_moisture", "light"]
        if any(key not in payload for key in required):
            print(f"[mqtt] telemetry missing fields: {payload}")
            return

        db = SessionLocal()
        try:
            timestamp = self.parse_timestamp(payload.get("timestamp"))
            sensor = SensorData(
                device_id=str(payload["device_id"]),
                temperature=float(payload["temperature"]),
                air_humidity=float(payload["air_humidity"]),
                soil_moisture=float(payload["soil_moisture"]),
                light=float(payload["light"]),
                timestamp=timestamp,
            )
            db.add(sensor)

            device = db.query(Device).filter(Device.device_id == sensor.device_id).first()
            if device:
                device.status = "online"
                device.last_seen_at = timestamp

            db.commit()
            print(f"[mqtt] telemetry saved: {payload}")
        except Exception as exc:
            db.rollback()
            print(f"[mqtt] telemetry save failed: {exc}")
        finally:
            db.close()

    def handle_control_ack(self, payload):
        request_id = payload.get("request_id")
        if not request_id:
            print(f"[mqtt] control_ack missing request_id: {payload}")
            return

        db = SessionLocal()
        try:
            log = db.query(WateringLog).filter(WateringLog.request_id == request_id).first()
            if not log:
                print(f"[mqtt] control_ack request not found: {request_id}")
                return

            log.status = str(payload.get("status", "ack"))
            log.ack_at = self.parse_timestamp(payload.get("timestamp"))
            log.message = json.dumps(payload, ensure_ascii=False)
            db.commit()
            print(f"[mqtt] watering log updated: {request_id} -> {log.status}")
        except Exception as exc:
            db.rollback()
            print(f"[mqtt] control_ack update failed: {exc}")
        finally:
            db.close()


mqtt_service = MqttService()
