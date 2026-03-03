import datetime

from pydantic import BaseModel, ConfigDict, Field


# ─── Department ───────────────────────────────────────────────────────────────


class DepartmentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    budget: float = Field(..., ge=0)


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    budget: float | None = Field(None, ge=0)


class DepartmentResponse(DepartmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


# ─── Employee ─────────────────────────────────────────────────────────────────


class EmployeeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    surname: str = Field(..., min_length=1, max_length=100)
    department_id: int = Field(..., gt=0)
    salary: float = Field(..., gt=0)


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    surname: str | None = Field(None, min_length=1, max_length=100)
    department_id: int | None = Field(None, gt=0)
    salary: float | None = Field(None, gt=0)


class EmployeeResponse(EmployeeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


# ─── Sale ─────────────────────────────────────────────────────────────────────


class SaleBase(BaseModel):
    employee_id: int = Field(..., gt=0)
    department_id: int = Field(..., gt=0)
    amount: float = Field(..., gt=0)
    sale_date: datetime.date
    description: str | None = Field(None, max_length=500)


class SaleCreate(SaleBase):
    pass


class SaleUpdate(BaseModel):
    employee_id: int | None = Field(None, gt=0)
    department_id: int | None = Field(None, gt=0)
    amount: float | None = Field(None, gt=0)
    sale_date: datetime.date | None = None
    description: str | None = Field(None, max_length=500)


class SaleResponse(SaleBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


# ─── Purchase ─────────────────────────────────────────────────────────────────


class PurchaseBase(BaseModel):
    department_id: int = Field(..., gt=0)
    vendor: str = Field(..., min_length=1, max_length=200)
    amount: float = Field(..., gt=0)
    purchase_date: datetime.date
    description: str | None = Field(None, max_length=500)


class PurchaseCreate(PurchaseBase):
    pass


class PurchaseUpdate(BaseModel):
    department_id: int | None = Field(None, gt=0)
    vendor: str | None = Field(None, min_length=1, max_length=200)
    amount: float | None = Field(None, gt=0)
    purchase_date: datetime.date | None = None
    description: str | None = Field(None, max_length=500)


class PurchaseResponse(PurchaseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


# ─── Fiscality ────────────────────────────────────────────────────────────────


class FiscalityBase(BaseModel):
    department_id: int = Field(..., gt=0)
    tax_year: int = Field(..., ge=2000, le=2100)
    tax_rate: float = Field(..., ge=0.0, le=1.0)
    taxable_amount: float = Field(..., ge=0)
    tax_paid: float = Field(..., ge=0)
    notes: str | None = Field(None, max_length=500)


class FiscalityCreate(FiscalityBase):
    pass


class FiscalityUpdate(BaseModel):
    department_id: int | None = Field(None, gt=0)
    tax_year: int | None = Field(None, ge=2000, le=2100)
    tax_rate: float | None = Field(None, ge=0.0, le=1.0)
    taxable_amount: float | None = Field(None, ge=0)
    tax_paid: float | None = Field(None, ge=0)
    notes: str | None = Field(None, max_length=500)


class FiscalityResponse(FiscalityBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
