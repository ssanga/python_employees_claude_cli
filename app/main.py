from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Employees API",
    description="REST API for managing employees using FastAPI + SQLAlchemy + SQLite",
    version="1.0.0",
)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@app.get(
    "/employees", response_model=list[schemas.EmployeeResponse], tags=["employees"]
)
def list_employees(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_employees(db, skip=skip, limit=limit)


@app.get(
    "/employees/{employee_id}",
    response_model=schemas.EmployeeResponse,
    tags=["employees"],
)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = crud.get_employee(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@app.post(
    "/employees",
    response_model=schemas.EmployeeResponse,
    status_code=201,
    tags=["employees"],
)
def create_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    return crud.create_employee(db, employee)


@app.put(
    "/employees/{employee_id}",
    response_model=schemas.EmployeeResponse,
    tags=["employees"],
)
def update_employee(
    employee_id: int, employee: schemas.EmployeeUpdate, db: Session = Depends(get_db)
):
    updated = crud.update_employee(db, employee_id, employee)
    if not updated:
        raise HTTPException(status_code=404, detail="Employee not found")
    return updated


@app.delete("/employees/{employee_id}", status_code=204, tags=["employees"])
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    if not crud.delete_employee(db, employee_id):
        raise HTTPException(status_code=404, detail="Employee not found")
