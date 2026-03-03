from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/purchases", tags=["purchases"])


@router.get("", response_model=list[schemas.PurchaseResponse])
def list_purchases(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_purchases(db, skip=skip, limit=limit)


@router.get("/{purchase_id}", response_model=schemas.PurchaseResponse)
def get_purchase(purchase_id: int, db: Session = Depends(get_db)):
    purchase = crud.get_purchase(db, purchase_id)
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
    return purchase


@router.post("", response_model=schemas.PurchaseResponse, status_code=201)
def create_purchase(purchase: schemas.PurchaseCreate, db: Session = Depends(get_db)):
    return crud.create_purchase(db, purchase)


@router.put("/{purchase_id}", response_model=schemas.PurchaseResponse)
def update_purchase(
    purchase_id: int, purchase: schemas.PurchaseUpdate, db: Session = Depends(get_db)
):
    updated = crud.update_purchase(db, purchase_id, purchase)
    if not updated:
        raise HTTPException(status_code=404, detail="Purchase not found")
    return updated


@router.delete("/{purchase_id}", status_code=204)
def delete_purchase(purchase_id: int, db: Session = Depends(get_db)):
    if not crud.delete_purchase(db, purchase_id):
        raise HTTPException(status_code=404, detail="Purchase not found")
