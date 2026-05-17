from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel


class SensorDataOut(BaseModel):
    device_id: str
    temperature: Optional[float] = None
    air_humidity: Optional[float] = None
    soil_moisture: Optional[float] = None
    light: float
    timestamp: datetime
    created_at: datetime

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
    duration_sec: Literal[3, 5, 10] = 5


class ManualWateringOut(BaseModel):
    request_id: str
    device_id: str
    duration_sec: int
    status: str
    topic: str
    created_at: datetime


class WateringLogOut(BaseModel):
    request_id: str
    device_id: str
    duration_sec: int
    status: str
    requested_at: datetime
    ack_at: Optional[datetime] = None
    message: Optional[str] = None

    class Config:
        from_attributes = True


class WateringLogsOut(BaseModel):
    items: List[WateringLogOut]


class HealthOut(BaseModel):
    status: str
    mqtt_connected: bool
    device_id: str
    timestamp: datetime
