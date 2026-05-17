import json
import os
from datetime import datetime

import paho.mqtt.client as mqtt

from config import settings
from database import SessionLocal
from models import Device, SensorData, WateringLog


class MqttService:
    def __init__(self):
        self.connected = False
        self.client = None
        self.started = False

    def _build_client(self):
        client = self._create_client()
        if settings.MQTT_USERNAME:
            client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)

        client.on_connect = self.on_connect
        client.on_disconnect = self.on_disconnect
        client.on_message = self.on_message
        client.reconnect_delay_set(min_delay=1, max_delay=30)
        return client

    @staticmethod
    def _create_client():
        client_id = f"plant-assistant-backend-{os.getpid()}"
        if hasattr(mqtt, "CallbackAPIVersion"):
            return mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id=client_id)
        return mqtt.Client(client_id=client_id)

    def start(self):
        if self.started:
            return

        self.client = self._build_client()
        try:
            self.client.connect_async(settings.MQTT_HOST, settings.MQTT_PORT, settings.MQTT_KEEPALIVE)
            self.client.loop_start()
            self.started = True
        except Exception as exc:
            self.client = None
            self.started = False
            print(f"[mqtt] connect failed: {exc}")

    def stop(self):
        if not self.client:
            return

        self.client.loop_stop()
        self.client.disconnect()
        self.client = None
        self.connected = False
        self.started = False

    def publish_control(self, payload):
        if not self.client:
            return mqtt.MQTT_ERR_NO_CONN

        message = json.dumps(payload, ensure_ascii=False)
        result = self.client.publish(settings.MQTT_CONTROL_TOPIC, message, qos=1, retain=False)
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
        print(f"[mqtt] 收到MQTT数据 topic={msg.topic} payload={payload_text}")
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

    @staticmethod
    def optional_float(value):
        if value is None or value == "":
            return None
        return float(value)

    @staticmethod
    def required_float(value):
        if value is None or value == "":
            return None
        return float(value)

    def handle_telemetry(self, payload):
        device_id = str(payload.get("device_id", ""))
        if device_id != settings.DEVICE_ID:
            print(f"[mqtt] telemetry ignored: unexpected device_id={device_id}")
            return

        if "light" not in payload:
            print(f"[mqtt] telemetry missing light: {payload}")
            return

        db = SessionLocal()
        try:
            light = self.required_float(payload.get("light"))
            if light is None:
                print(f"[mqtt] telemetry skipped: light is null payload={payload}")
                return

            timestamp = self.parse_timestamp(payload.get("timestamp") or payload.get("created_at"))
            sensor = SensorData(
                device_id=device_id,
                temperature=self.optional_float(payload.get("temperature")),
                air_humidity=self.optional_float(payload.get("air_humidity")),
                soil_moisture=self.optional_float(payload.get("soil_moisture")),
                light=light,
                timestamp=timestamp,
                created_at=timestamp,
            )
            db.add(sensor)

            device = db.query(Device).filter(Device.device_id == sensor.device_id).first()
            if device:
                device.status = "online"
                device.last_seen_at = timestamp

            db.commit()
            print(f"[mqtt] 写入数据库成功 sensor_data.id={sensor.id} light={sensor.light}")
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

            status = str(payload.get("status", "")).lower()
            if status in {"success", "done", "ok"}:
                log.status = "success"
            elif status == "rejected":
                log.status = "rejected"
            elif status == "failed":
                log.status = "failed"
            else:
                log.status = "failed"

            log.ack_at = self.parse_timestamp(payload.get("timestamp") or payload.get("created_at"))
            log.message = json.dumps(payload, ensure_ascii=False)
            db.commit()
            print(f"[mqtt] watering log updated: {request_id} -> {log.status}")
        except Exception as exc:
            db.rollback()
            print(f"[mqtt] control_ack update failed: {exc}")
        finally:
            db.close()


mqtt_service = MqttService()
