from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/fiscality", tags=["fiscality"])


@router.get("", response_model=list[schemas.FiscalityResponse])
def list_fiscalities(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_fiscalities(db, skip=skip, limit=limit)


@router.get("/{fiscality_id}", response_model=schemas.FiscalityResponse)
def get_fiscality(fiscality_id: int, db: Session = Depends(get_db)):
    fiscality = crud.get_fiscality(db, fiscality_id)
    if not fiscality:
        raise HTTPException(status_code=404, detail="Fiscality not found")
    return fiscality


@router.post("", response_model=schemas.FiscalityResponse, status_code=201)
def create_fiscality(fiscality: schemas.FiscalityCreate, db: Session = Depends(get_db)):
    return crud.create_fiscality(db, fiscality)


@router.put("/{fiscality_id}", response_model=schemas.FiscalityResponse)
def update_fiscality(
    fiscality_id: int, fiscality: schemas.FiscalityUpdate, db: Session = Depends(get_db)
):
    updated = crud.update_fiscality(db, fiscality_id, fiscality)
    if not updated:
        raise HTTPException(status_code=404, detail="Fiscality not found")
    return updated


@router.delete("/{fiscality_id}", status_code=204)
def delete_fiscality(fiscality_id: int, db: Session = Depends(get_db)):
    if not crud.delete_fiscality(db, fiscality_id):
        raise HTTPException(status_code=404, detail="Fiscality not found")
