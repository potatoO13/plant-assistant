import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from models import WateringLog
from mqtt_client import mqtt_service
from schemas import ManualWateringIn, ManualWateringOut, WateringLogsOut
from watering_service import cooldown_remaining, mark_timed_out


router = APIRouter(prefix="/watering", tags=["watering"])


@router.post("/manual", response_model=ManualWateringOut)
def manual_watering(body: ManualWateringIn, db: Session = Depends(get_db)):
    mark_timed_out(db)

    remaining = cooldown_remaining(db)
    if remaining > 0:
        raise HTTPException(
            status_code=429,
            detail=f"Watering cooldown active, retry after {remaining} seconds",
        )

    now = datetime.now().replace(microsecond=0)
    request_id = f"water_{uuid.uuid4().hex[:16]}"
    log = WateringLog(
        request_id=request_id,
        device_id=settings.DEVICE_ID,
        duration_sec=body.duration_sec,
        status="pending",
        requested_at=now,
    )
    db.add(log)
    db.commit()

    payload = {
        "command": "water",
        "duration_sec": body.duration_sec,
        "request_id": request_id,
        "source": "manual",
        "created_at": now.isoformat(),
    }
    rc = mqtt_service.publish_control(payload)
    if rc != 0:
        log.status = "failed"
        log.message = f"mqtt publish rc={rc}"
        db.commit()

    return {
        "request_id": request_id,
        "device_id": settings.DEVICE_ID,
        "duration_sec": body.duration_sec,
        "status": log.status,
        "topic": settings.MQTT_CONTROL_TOPIC,
        "created_at": now,
    }


@router.get("/logs", response_model=WateringLogsOut)
def watering_logs(limit: int = 50, db: Session = Depends(get_db)):
    mark_timed_out(db)
    items = (
        db.query(WateringLog)
        .filter(WateringLog.device_id == settings.DEVICE_ID)
        .order_by(WateringLog.requested_at.desc())
        .limit(min(max(limit, 1), 100))
        .all()
    )
    return {"items": items}
