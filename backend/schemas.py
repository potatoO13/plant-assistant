from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


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
    duration_sec: int = Field(default=5)
    source: str = "manual"


class ManualWateringOut(BaseModel):
    request_id: str
    device_id: str
    duration_sec: int
    status: str
    topic: str
    created_at: datetime
    source: str = "manual"
    message: Optional[str] = None


class WateringLogOut(BaseModel):
    request_id: str
    device_id: str
    duration_sec: int
    source: str = "manual"
    status: str
    requested_at: datetime
    created_at: datetime
    ack_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
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
