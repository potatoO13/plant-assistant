from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from database import Base


class Device(Base):
    __tablename__ = "device"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False, default="ESP32 Plant Device")
    status = Column(String(20), nullable=False, default="offline")
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    last_seen_at = Column(DateTime, nullable=True)


class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(64), index=True, nullable=False)
    temperature = Column(Float, nullable=True)
    air_humidity = Column(Float, nullable=True)
    soil_moisture = Column(Float, nullable=True)
    light = Column(Float, nullable=False)
    timestamp = Column(DateTime, index=True, default=datetime.now, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)


class Plant(Base):
    __tablename__ = "plant"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    temp_min = Column(Float, nullable=False)
    temp_max = Column(Float, nullable=False)
    soil_moisture_min = Column(Float, nullable=False)
    soil_moisture_max = Column(Float, nullable=False)
    light_min = Column(Float, nullable=False)
    light_max = Column(Float, nullable=False)
    watering_advice = Column(Text, nullable=False)
    care_advice = Column(Text, nullable=False)


class WateringLog(Base):
    __tablename__ = "watering_log"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String(64), unique=True, index=True, nullable=False)
    device_id = Column(String(64), index=True, nullable=False)
    duration_sec = Column(Integer, nullable=False)
    source = Column(String(30), nullable=False, default="manual")
    status = Column(String(20), nullable=False, default="requested")
    requested_at = Column(DateTime, default=datetime.now, nullable=False)
    ack_at = Column(DateTime, nullable=True)
    message = Column(Text, nullable=True)

    @property
    def created_at(self):
        return self.requested_at

    @property
    def finished_at(self):
        return self.ack_at


class AdviceLog(Base):
    __tablename__ = "advice_log"

    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(Integer, ForeignKey("plant.id"), nullable=False)
    sensor_data_id = Column(Integer, ForeignKey("sensor_data.id"), nullable=True)
    status = Column(String(20), nullable=False)
    summary = Column(Text, nullable=False)
    advices_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    plant = relationship("Plant")
