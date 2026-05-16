from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models import Plant
from schemas import PlantOut


router = APIRouter(prefix="/plants", tags=["plants"])


@router.get("/search", response_model=list[PlantOut])
def search(keyword: str = Query("", max_length=50), db: Session = Depends(get_db)):
    query = db.query(Plant)
    if keyword:
        query = query.filter(Plant.name.contains(keyword))
    return query.order_by(Plant.id.asc()).all()


@router.get("/{plant_id}", response_model=PlantOut)
def detail(plant_id: int, db: Session = Depends(get_db)):
    plant = db.query(Plant).filter(Plant.id == plant_id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    return plant
