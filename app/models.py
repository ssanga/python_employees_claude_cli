import datetime

from sqlalchemy import Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    budget: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    employees: Mapped[list["Employee"]] = relationship("Employee", back_populates="department_rel")
    sales: Mapped[list["Sale"]] = relationship("Sale", back_populates="department")
    purchases: Mapped[list["Purchase"]] = relationship("Purchase", back_populates="department")
    fiscalities: Mapped[list["Fiscality"]] = relationship("Fiscality", back_populates="department")


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    surname: Mapped[str] = mapped_column(String(100), nullable=False)
    department_id: Mapped[int] = mapped_column(Integer, ForeignKey("departments.id"), nullable=False)
    salary: Mapped[float] = mapped_column(Float, nullable=False)

    department_rel: Mapped["Department"] = relationship("Department", back_populates="employees")
    sales: Mapped[list["Sale"]] = relationship("Sale", back_populates="employee")


class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id"), nullable=False)
    department_id: Mapped[int] = mapped_column(Integer, ForeignKey("departments.id"), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    sale_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    employee: Mapped["Employee"] = relationship("Employee", back_populates="sales")
    department: Mapped["Department"] = relationship("Department", back_populates="sales")


class Purchase(Base):
    __tablename__ = "purchases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    department_id: Mapped[int] = mapped_column(Integer, ForeignKey("departments.id"), nullable=False)
    vendor: Mapped[str] = mapped_column(String(200), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    purchase_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    department: Mapped["Department"] = relationship("Department", back_populates="purchases")


class Fiscality(Base):
    __tablename__ = "fiscality"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    department_id: Mapped[int] = mapped_column(Integer, ForeignKey("departments.id"), nullable=False)
    tax_year: Mapped[int] = mapped_column(Integer, nullable=False)
    tax_rate: Mapped[float] = mapped_column(Float, nullable=False)
    taxable_amount: Mapped[float] = mapped_column(Float, nullable=False)
    tax_paid: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)

    department: Mapped["Department"] = relationship("Department", back_populates="fiscalities")
