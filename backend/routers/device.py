from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from models import SensorData
from schemas import HistoryOut, SensorDataOut


router = APIRouter(prefix="/device", tags=["device"])


@router.get("/latest", response_model=SensorDataOut)
def latest(db: Session = Depends(get_db)):
    item = (
        db.query(SensorData)
        .filter(SensorData.device_id == settings.DEVICE_ID)
        .order_by(SensorData.id.desc())
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="No sensor data yet")
    return item


@router.get("/history", response_model=HistoryOut)
def history(range: str = Query("day", pattern="^(day|week)$"), db: Session = Depends(get_db)):
    since = datetime.now() - (timedelta(days=1) if range == "day" else timedelta(days=7))
    items = (
        db.query(SensorData)
        .filter(SensorData.device_id == settings.DEVICE_ID, SensorData.timestamp >= since)
        .order_by(SensorData.timestamp.asc())
        .all()
    )
    return {"range": range, "items": items}
