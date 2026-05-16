from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import declarative_base, sessionmaker

from config import settings


connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db():
    import models

    migrate_sqlite_schema()
    Base.metadata.create_all(bind=engine)


def migrate_sqlite_schema():
    if not settings.DATABASE_URL.startswith("sqlite"):
        return

    with engine.begin() as conn:
        tables = {
            row["name"]
            for row in conn.execute(
                text("SELECT name FROM sqlite_master WHERE type = 'table'")
            ).mappings()
        }

        if "sensor_data_old" in tables:
            rebuild_sensor_data_table(conn, "sensor_data_old", drop_current=True)
            return

        if "sensor_data" not in tables:
            return

        rows = conn.execute(text("PRAGMA table_info(sensor_data)")).mappings().all()
        if not rows:
            return

        notnull = {row["name"]: row["notnull"] for row in rows}
        needs_rebuild = any(notnull.get(name) for name in ("temperature", "air_humidity", "soil_moisture"))
        if not needs_rebuild:
            return

        rebuild_sensor_data_table(conn, "sensor_data")


def rebuild_sensor_data_table(conn, source_table, drop_current=False):
    for index_name in ("ix_sensor_data_id", "ix_sensor_data_device_id", "ix_sensor_data_timestamp"):
        conn.execute(text(f"DROP INDEX IF EXISTS {index_name}"))

    if drop_current:
        conn.execute(text("DROP TABLE IF EXISTS sensor_data"))
    else:
        conn.execute(text("ALTER TABLE sensor_data RENAME TO sensor_data_old"))
        source_table = "sensor_data_old"

    conn.execute(
        text(
            """
            CREATE TABLE sensor_data (
                id INTEGER NOT NULL,
                device_id VARCHAR(64) NOT NULL,
                temperature FLOAT,
                air_humidity FLOAT,
                soil_moisture FLOAT,
                light FLOAT NOT NULL,
                timestamp DATETIME NOT NULL,
                created_at DATETIME NOT NULL,
                PRIMARY KEY (id)
            )
            """
        )
    )
    conn.execute(
        text(
            f"""
            INSERT INTO sensor_data (
                id, device_id, temperature, air_humidity, soil_moisture,
                light, timestamp, created_at
            )
            SELECT
                id, device_id, temperature, air_humidity, soil_moisture,
                light, timestamp, created_at
            FROM {source_table}
            """
        )
    )
    conn.execute(text(f"DROP TABLE {source_table}"))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
