from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class SensorDataOut(BaseModel):
    device_id: str
    temperature: float
    air_humidity: float
    soil_moisture: float
    light: float
    timestamp: datetime

    class Config:
        from_attributes = True


class HistoryOut(BaseModel):
    range: str
    items: List[SensorDataOut]


class PlantOut(BaseModel):
    id: int
    name: str
    temp_min: float
    temp_max: float
    soil_moisture_min: float
    soil_moisture_max: float
    light_min: float
    light_max: float
    watering_advice: str
    care_advice: str

    class Config:
        from_attributes = True


class AdviceOut(BaseModel):
    status: str
    summary: str
    advices: List[str]


class ManualWateringIn(BaseModel):
    duration_sec: int = Field(default=5, ge=1, le=10)


class ManualWateringOut(BaseModel):
    request_id: str
    device_id: str
    duration_sec: int
    status: str
    topic: str


class HealthOut(BaseModel):
    status: str
    mqtt_connected: bool
    device_id: str
    timestamp: datetime
