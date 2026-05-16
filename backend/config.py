import os


class Settings:
    APP_NAME = "Plant Assistant API"
    API_PREFIX = "/api"

    DEVICE_ID = os.getenv("DEVICE_ID", "device001")
    DEFAULT_PLANT_ID = int(os.getenv("DEFAULT_PLANT_ID", "1"))

    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./plant_assistant.db")

    MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
    MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
    MQTT_USERNAME = os.getenv("MQTT_USERNAME")
    MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
    MQTT_KEEPALIVE = int(os.getenv("MQTT_KEEPALIVE", "60"))

    MQTT_TELEMETRY_TOPIC = os.getenv("MQTT_TELEMETRY_TOPIC", f"plant/{DEVICE_ID}/telemetry")
    MQTT_CONTROL_TOPIC = os.getenv("MQTT_CONTROL_TOPIC", f"plant/{DEVICE_ID}/control")
    MQTT_CONTROL_ACK_TOPIC = os.getenv("MQTT_CONTROL_ACK_TOPIC", f"plant/{DEVICE_ID}/control_ack")


settings = Settings()
