from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database import init_db
from mqtt_client import mqtt_service
from routers import advice, device, plants, watering
from schemas import HealthOut
from seed_data import seed_plants


app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()
    seed_plants()
    mqtt_service.start()


@app.on_event("shutdown")
def on_shutdown():
    mqtt_service.stop()


@app.get("/api/health", response_model=HealthOut)
def health():
    return {
        "status": "ok",
        "mqtt_connected": mqtt_service.connected,
        "device_id": settings.DEVICE_ID,
        "timestamp": datetime.now(),
    }


app.include_router(device.router, prefix=settings.API_PREFIX)
app.include_router(plants.router, prefix=settings.API_PREFIX)
app.include_router(advice.router, prefix=settings.API_PREFIX)
app.include_router(watering.router, prefix=settings.API_PREFIX)
