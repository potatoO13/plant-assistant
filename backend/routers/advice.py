import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from advice_engine import generate_advice
from config import settings
from database import get_db
from models import AdviceLog, Plant, SensorData
from schemas import AdviceOut


router = APIRouter(prefix="/advice", tags=["advice"])


@router.get("/current", response_model=AdviceOut)
def current(db: Session = Depends(get_db)):
    sensor = (
        db.query(SensorData)
        .filter(SensorData.device_id == settings.DEVICE_ID)
        .order_by(SensorData.timestamp.desc())
        .first()
    )
    if not sensor:
        raise HTTPException(status_code=404, detail="No sensor data yet")

    plant = db.query(Plant).filter(Plant.id == settings.DEFAULT_PLANT_ID).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Default plant not found")

    result = generate_advice(sensor, plant)
    db.add(
        AdviceLog(
            plant_id=plant.id,
            sensor_data_id=sensor.id,
            status=result["status"],
            summary=result["summary"],
            advices_json=json.dumps(result["advices"], ensure_ascii=False),
        )
    )
    db.commit()
    return result
