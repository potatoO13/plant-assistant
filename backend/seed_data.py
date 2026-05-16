from config import settings
from database import SessionLocal, init_db
from models import Device, Plant


PLANTS = [
    ("绿萝", 18, 30, 40, 70, 500, 3000, "保持土壤微湿，避免长期积水。", "适合明亮散射光，定期修剪黄叶。"),
    ("多肉", 15, 28, 15, 35, 1500, 8000, "干透再浇，少量浇透。", "需要充足光照和良好通风。"),
    ("吊兰", 15, 28, 35, 65, 800, 4000, "土壤表层变干后浇水。", "耐半阴，避免强烈直射光。"),
    ("仙人掌", 12, 35, 10, 30, 2500, 10000, "少浇水，宁干勿湿。", "需要强光和排水良好的土壤。"),
    ("薄荷", 16, 28, 45, 75, 1200, 6000, "保持土壤湿润但不积水。", "喜光，摘心可促进分枝。"),
    ("罗勒", 18, 30, 40, 70, 1500, 7000, "规律浇水，避免萎蔫。", "需要充足光照，及时采摘嫩叶。"),
    ("番茄苗", 18, 32, 45, 75, 2500, 12000, "保持稳定湿度，结果期需水较多。", "需要强光和支撑，注意通风。"),
    ("生菜", 12, 25, 50, 80, 1000, 5000, "保持土壤湿润。", "喜冷凉环境，避免高温暴晒。"),
    ("发财树", 16, 30, 25, 55, 800, 5000, "见干见湿，避免盆底积水。", "耐半阴，冬季注意保温。"),
    ("虎皮兰", 15, 32, 15, 40, 700, 6000, "少浇水，土壤干透后再浇。", "耐阴耐旱，避免低温积水。"),
]


def seed_plants():
    init_db()
    db = SessionLocal()
    try:
        if not db.query(Device).filter(Device.device_id == settings.DEVICE_ID).first():
            db.add(Device(device_id=settings.DEVICE_ID, name="MVP 单设备"))

        for item in PLANTS:
            name = item[0]
            plant = db.query(Plant).filter(Plant.name == name).first()
            if plant:
                continue
            db.add(
                Plant(
                    name=name,
                    temp_min=item[1],
                    temp_max=item[2],
                    soil_moisture_min=item[3],
                    soil_moisture_max=item[4],
                    light_min=item[5],
                    light_max=item[6],
                    watering_advice=item[7],
                    care_advice=item[8],
                )
            )

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed_plants()
    print("Seed data initialized.")
