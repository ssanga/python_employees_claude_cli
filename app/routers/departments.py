from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/departments", tags=["departments"])


@router.get("", response_model=list[schemas.DepartmentResponse])
def list_departments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_departments(db, skip=skip, limit=limit)


@router.get("/{department_id}", response_model=schemas.DepartmentResponse)
def get_department(department_id: int, db: Session = Depends(get_db)):
    department = crud.get_department(db, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    return department


@router.post("", response_model=schemas.DepartmentResponse, status_code=201)
def create_department(department: schemas.DepartmentCreate, db: Session = Depends(get_db)):
    return crud.create_department(db, department)


@router.put("/{department_id}", response_model=schemas.DepartmentResponse)
def update_department(
    department_id: int, department: schemas.DepartmentUpdate, db: Session = Depends(get_db)
):
    updated = crud.update_department(db, department_id, department)
    if not updated:
        raise HTTPException(status_code=404, detail="Department not found")
    return updated


@router.delete("/{department_id}", status_code=204)
def delete_department(department_id: int, db: Session = Depends(get_db)):
    if not crud.delete_department(db, department_id):
        raise HTTPException(status_code=404, detail="Department not found")
