import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from models import WateringLog
from mqtt_client import mqtt_service
from schemas import ManualWateringIn, ManualWateringOut, WateringLogsOut
from watering_service import ALLOWED_DURATIONS, cooldown_remaining, mark_timed_out


router = APIRouter(prefix="/watering", tags=["watering"])
SAFETY_LIMIT_MESSAGE = "浇水时长超过安全限制，最大允许10秒"
ALLOWED_DURATION_MESSAGE = "浇水时长只允许3、5、10秒"


@router.post("/manual", response_model=ManualWateringOut)
def manual_watering(body: ManualWateringIn, db: Session = Depends(get_db)):
    mark_timed_out(db)

    now = datetime.now().replace(microsecond=0)
    request_id = f"water_{uuid.uuid4().hex[:16]}"
    source = (body.source or "manual")[:30]

    if body.duration_sec not in ALLOWED_DURATIONS:
        message = SAFETY_LIMIT_MESSAGE if body.duration_sec > 10 else ALLOWED_DURATION_MESSAGE
        log = WateringLog(
            request_id=request_id,
            device_id=settings.DEVICE_ID,
            duration_sec=body.duration_sec,
            source=source,
            status="rejected",
            requested_at=now,
            message=message,
        )
        db.add(log)
        db.commit()
        return {
            "request_id": request_id,
            "device_id": settings.DEVICE_ID,
            "duration_sec": body.duration_sec,
            "source": source,
            "status": "rejected",
            "topic": settings.MQTT_CONTROL_TOPIC,
            "created_at": now,
            "message": message,
        }

    remaining = cooldown_remaining(db)
    if remaining > 0:
        raise HTTPException(
            status_code=429,
            detail=f"Watering cooldown active, retry after {remaining} seconds",
        )

    log = WateringLog(
        request_id=request_id,
        device_id=settings.DEVICE_ID,
        duration_sec=body.duration_sec,
        source=source,
        status="pending",
        requested_at=now,
    )
    db.add(log)
    db.commit()

    payload = {
        "command": "water",
        "duration_sec": body.duration_sec,
        "request_id": request_id,
        "source": source,
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
        "source": source,
        "message": log.message,
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
