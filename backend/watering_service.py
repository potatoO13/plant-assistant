import threading
import time
from datetime import datetime, timedelta

from database import SessionLocal
from models import WateringLog


ACK_TIMEOUT_SEC = 15
COOLDOWN_SEC = 30
ALLOWED_DURATIONS = {3, 5, 10}

_stop_event = threading.Event()
_worker_thread = None


def mark_timed_out(db):
    deadline = datetime.now() - timedelta(seconds=ACK_TIMEOUT_SEC)
    logs = (
        db.query(WateringLog)
        .filter(WateringLog.status == "pending", WateringLog.requested_at <= deadline)
        .all()
    )
    for log in logs:
        log.status = "timeout"
        log.ack_at = datetime.now()
        log.message = "control_ack timeout"
    if logs:
        db.commit()
        print(f"[watering] timeout updated count={len(logs)}")


def latest_request(db):
    return (
        db.query(WateringLog)
        .filter(WateringLog.status.in_(("pending", "success", "timeout")))
        .order_by(WateringLog.requested_at.desc())
        .first()
    )


def cooldown_remaining(db):
    latest = latest_request(db)
    if not latest:
        return 0

    elapsed = (datetime.now() - latest.requested_at).total_seconds()
    remaining = COOLDOWN_SEC - int(elapsed)
    return max(0, remaining)


def timeout_worker():
    while not _stop_event.wait(5):
        db = SessionLocal()
        try:
            mark_timed_out(db)
        except Exception as exc:
            db.rollback()
            print(f"[watering] timeout worker failed: {exc}")
        finally:
            db.close()


def start_timeout_worker():
    global _worker_thread
    if _worker_thread and _worker_thread.is_alive():
        return

    _stop_event.clear()
    _worker_thread = threading.Thread(target=timeout_worker, name="watering-timeout-worker", daemon=True)
    _worker_thread.start()


def stop_timeout_worker():
    _stop_event.set()
