from sqlalchemy.orm import Session

from app.models import Department, Employee, Fiscality, Purchase, Sale
from app.schemas import (
    DepartmentCreate,
    DepartmentUpdate,
    EmployeeCreate,
    EmployeeUpdate,
    FiscalityCreate,
    FiscalityUpdate,
    PurchaseCreate,
    PurchaseUpdate,
    SaleCreate,
    SaleUpdate,
)


# ─── Employee ─────────────────────────────────────────────────────────────────


def get_employee(db: Session, employee_id: int) -> Employee | None:
    return db.query(Employee).filter(Employee.id == employee_id).first()


def get_employees(db: Session, skip: int = 0, limit: int = 100) -> list[Employee]:
    return db.query(Employee).offset(skip).limit(limit).all()


def create_employee(db: Session, employee: EmployeeCreate) -> Employee:
    db_employee = Employee(**employee.model_dump())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


def update_employee(
    db: Session, employee_id: int, employee: EmployeeUpdate
) -> Employee | None:
    db_employee = get_employee(db, employee_id)
    if not db_employee:
        return None
    update_data = employee.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_employee, field, value)
    db.commit()
    db.refresh(db_employee)
    return db_employee


def delete_employee(db: Session, employee_id: int) -> bool:
    db_employee = get_employee(db, employee_id)
    if not db_employee:
        return False
    db.delete(db_employee)
    db.commit()
    return True


# ─── Department ───────────────────────────────────────────────────────────────


def get_department(db: Session, department_id: int) -> Department | None:
    return db.query(Department).filter(Department.id == department_id).first()


def get_departments(db: Session, skip: int = 0, limit: int = 100) -> list[Department]:
    return db.query(Department).offset(skip).limit(limit).all()


def create_department(db: Session, department: DepartmentCreate) -> Department:
    db_department = Department(**department.model_dump())
    db.add(db_department)
    db.commit()
    db.refresh(db_department)
    return db_department


def update_department(
    db: Session, department_id: int, department: DepartmentUpdate
) -> Department | None:
    db_department = get_department(db, department_id)
    if not db_department:
        return None
    for field, value in department.model_dump(exclude_unset=True).items():
        setattr(db_department, field, value)
    db.commit()
    db.refresh(db_department)
    return db_department


def delete_department(db: Session, department_id: int) -> bool:
    db_department = get_department(db, department_id)
    if not db_department:
        return False
    db.delete(db_department)
    db.commit()
    return True


# ─── Sale ─────────────────────────────────────────────────────────────────────


def get_sale(db: Session, sale_id: int) -> Sale | None:
    return db.query(Sale).filter(Sale.id == sale_id).first()


def get_sales(db: Session, skip: int = 0, limit: int = 100) -> list[Sale]:
    return db.query(Sale).offset(skip).limit(limit).all()


def create_sale(db: Session, sale: SaleCreate) -> Sale:
    db_sale = Sale(**sale.model_dump())
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    return db_sale


def update_sale(db: Session, sale_id: int, sale: SaleUpdate) -> Sale | None:
    db_sale = get_sale(db, sale_id)
    if not db_sale:
        return None
    for field, value in sale.model_dump(exclude_unset=True).items():
        setattr(db_sale, field, value)
    db.commit()
    db.refresh(db_sale)
    return db_sale


def delete_sale(db: Session, sale_id: int) -> bool:
    db_sale = get_sale(db, sale_id)
    if not db_sale:
        return False
    db.delete(db_sale)
    db.commit()
    return True


# ─── Purchase ─────────────────────────────────────────────────────────────────


def get_purchase(db: Session, purchase_id: int) -> Purchase | None:
    return db.query(Purchase).filter(Purchase.id == purchase_id).first()


def get_purchases(db: Session, skip: int = 0, limit: int = 100) -> list[Purchase]:
    return db.query(Purchase).offset(skip).limit(limit).all()


def create_purchase(db: Session, purchase: PurchaseCreate) -> Purchase:
    db_purchase = Purchase(**purchase.model_dump())
    db.add(db_purchase)
    db.commit()
    db.refresh(db_purchase)
    return db_purchase


def update_purchase(
    db: Session, purchase_id: int, purchase: PurchaseUpdate
) -> Purchase | None:
    db_purchase = get_purchase(db, purchase_id)
    if not db_purchase:
        return None
    for field, value in purchase.model_dump(exclude_unset=True).items():
        setattr(db_purchase, field, value)
    db.commit()
    db.refresh(db_purchase)
    return db_purchase


def delete_purchase(db: Session, purchase_id: int) -> bool:
    db_purchase = get_purchase(db, purchase_id)
    if not db_purchase:
        return False
    db.delete(db_purchase)
    db.commit()
    return True


# ─── Fiscality ────────────────────────────────────────────────────────────────


def get_fiscality(db: Session, fiscality_id: int) -> Fiscality | None:
    return db.query(Fiscality).filter(Fiscality.id == fiscality_id).first()


def get_fiscalities(db: Session, skip: int = 0, limit: int = 100) -> list[Fiscality]:
    return db.query(Fiscality).offset(skip).limit(limit).all()


def create_fiscality(db: Session, fiscality: FiscalityCreate) -> Fiscality:
    db_fiscality = Fiscality(**fiscality.model_dump())
    db.add(db_fiscality)
    db.commit()
    db.refresh(db_fiscality)
    return db_fiscality


def update_fiscality(
    db: Session, fiscality_id: int, fiscality: FiscalityUpdate
) -> Fiscality | None:
    db_fiscality = get_fiscality(db, fiscality_id)
    if not db_fiscality:
        return None
    for field, value in fiscality.model_dump(exclude_unset=True).items():
        setattr(db_fiscality, field, value)
    db.commit()
    db.refresh(db_fiscality)
    return db_fiscality


def delete_fiscality(db: Session, fiscality_id: int) -> bool:
    db_fiscality = get_fiscality(db, fiscality_id)
    if not db_fiscality:
        return False
    db.delete(db_fiscality)
    db.commit()
    return True
