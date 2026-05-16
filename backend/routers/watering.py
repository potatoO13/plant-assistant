import uuid
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from models import WateringLog
from mqtt_client import mqtt_service
from schemas import ManualWateringIn, ManualWateringOut


router = APIRouter(prefix="/watering", tags=["watering"])


@router.post("/manual", response_model=ManualWateringOut)
def manual_watering(body: ManualWateringIn, db: Session = Depends(get_db)):
    request_id = uuid.uuid4().hex
    log = WateringLog(
        request_id=request_id,
        device_id=settings.DEVICE_ID,
        duration_sec=body.duration_sec,
        status="requested",
    )
    db.add(log)
    db.commit()

    payload = {
        "command": "water",
        "duration_sec": body.duration_sec,
        "request_id": request_id,
        "timestamp": datetime.now().replace(microsecond=0).isoformat(),
    }
    rc = mqtt_service.publish_control(payload)
    if rc == 0:
        log.status = "sent"
    else:
        log.status = "publish_failed"
        log.message = f"mqtt publish rc={rc}"
    db.commit()

    return {
        "request_id": request_id,
        "device_id": settings.DEVICE_ID,
        "duration_sec": body.duration_sec,
        "status": log.status,
        "topic": settings.MQTT_CONTROL_TOPIC,
    }
