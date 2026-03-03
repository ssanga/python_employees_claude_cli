"""Unit tests for CRUD operations and schemas."""
import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import crud
from app.database import Base
from app.models import Employee
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

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def sample_department(db):
    return crud.create_department(
        db, DepartmentCreate(name="Engineering", description="Test dept", budget=100000.0)
    )


@pytest.fixture
def sample_employee(db, sample_department):
    return crud.create_employee(
        db,
        EmployeeCreate(
            name="John", surname="Doe", department_id=sample_department.id, salary=60000.0
        ),
    )


@pytest.fixture
def sample_sale(db, sample_employee, sample_department):
    return crud.create_sale(
        db,
        SaleCreate(
            employee_id=sample_employee.id,
            department_id=sample_department.id,
            amount=5000.0,
            sale_date=datetime.date(2024, 1, 15),
            description="Test sale",
        ),
    )


@pytest.fixture
def sample_purchase(db, sample_department):
    return crud.create_purchase(
        db,
        PurchaseCreate(
            department_id=sample_department.id,
            vendor="ACME Corp",
            amount=1000.0,
            purchase_date=datetime.date(2024, 1, 10),
        ),
    )


@pytest.fixture
def sample_fiscality(db, sample_department):
    return crud.create_fiscality(
        db,
        FiscalityCreate(
            department_id=sample_department.id,
            tax_year=2023,
            tax_rate=0.21,
            taxable_amount=100000.0,
            tax_paid=21000.0,
        ),
    )


# ─── Employee CRUD ────────────────────────────────────────────────────────────


class TestCrudCreateEmployee:
    def test_creates_employee_with_correct_fields(self, db, sample_department):
        data = EmployeeCreate(
            name="Alice", surname="Smith", department_id=sample_department.id, salary=45000.0
        )
        employee = crud.create_employee(db, data)

        assert employee.id is not None
        assert employee.name == "Alice"
        assert employee.surname == "Smith"
        assert employee.department_id == sample_department.id
        assert employee.salary == 45000.0

    def test_assigns_unique_ids(self, db, sample_department):
        data1 = EmployeeCreate(
            name="Alice", surname="Smith", department_id=sample_department.id, salary=45000.0
        )
        data2 = EmployeeCreate(
            name="Bob", surname="Jones", department_id=sample_department.id, salary=55000.0
        )
        emp1 = crud.create_employee(db, data1)
        emp2 = crud.create_employee(db, data2)

        assert emp1.id != emp2.id


class TestCrudGetEmployee:
    def test_returns_employee_by_id(self, db, sample_employee):
        result = crud.get_employee(db, sample_employee.id)

        assert result is not None
        assert result.id == sample_employee.id
        assert result.name == sample_employee.name

    def test_returns_none_for_missing_id(self, db):
        result = crud.get_employee(db, 9999)

        assert result is None


class TestCrudGetEmployees:
    def test_returns_all_employees(self, db, sample_department):
        crud.create_employee(
            db, EmployeeCreate(name="A", surname="B", department_id=sample_department.id, salary=1000.0)
        )
        crud.create_employee(
            db, EmployeeCreate(name="C", surname="D", department_id=sample_department.id, salary=2000.0)
        )

        result = crud.get_employees(db)

        assert len(result) == 2

    def test_returns_empty_list_when_no_employees(self, db):
        result = crud.get_employees(db)

        assert result == []

    def test_skip_and_limit(self, db, sample_department):
        for i in range(5):
            crud.create_employee(
                db,
                EmployeeCreate(
                    name=f"Emp{i}", surname="Test", department_id=sample_department.id, salary=1000.0
                ),
            )

        result = crud.get_employees(db, skip=2, limit=2)

        assert len(result) == 2


class TestCrudUpdateEmployee:
    def test_updates_specified_fields(self, db, sample_employee, sample_department):
        update = EmployeeUpdate(salary=75000.0, department_id=sample_department.id)
        updated = crud.update_employee(db, sample_employee.id, update)

        assert updated.salary == 75000.0
        assert updated.department_id == sample_department.id
        assert updated.name == sample_employee.name

    def test_returns_none_for_missing_id(self, db):
        update = EmployeeUpdate(salary=75000.0)
        result = crud.update_employee(db, 9999, update)

        assert result is None

    def test_partial_update_does_not_clear_other_fields(self, db, sample_employee):
        update = EmployeeUpdate(name="Jane")
        updated = crud.update_employee(db, sample_employee.id, update)

        assert updated.name == "Jane"
        assert updated.surname == sample_employee.surname
        assert updated.salary == sample_employee.salary


class TestCrudDeleteEmployee:
    def test_deletes_existing_employee(self, db, sample_employee):
        result = crud.delete_employee(db, sample_employee.id)

        assert result is True
        assert crud.get_employee(db, sample_employee.id) is None

    def test_returns_false_for_missing_id(self, db):
        result = crud.delete_employee(db, 9999)

        assert result is False


class TestEmployeeSchemas:
    def test_employee_create_valid(self):
        data = EmployeeCreate(name="Test", surname="User", department_id=1, salary=30000.0)
        assert data.name == "Test"

    def test_employee_create_rejects_empty_name(self):
        with pytest.raises(Exception):
            EmployeeCreate(name="", surname="User", department_id=1, salary=30000.0)

    def test_employee_create_rejects_negative_salary(self):
        with pytest.raises(Exception):
            EmployeeCreate(name="Test", surname="User", department_id=1, salary=-100.0)

    def test_employee_update_all_fields_optional(self):
        update = EmployeeUpdate()
        assert update.name is None
        assert update.surname is None
        assert update.department_id is None
        assert update.salary is None

    def test_employee_response_from_orm(self):
        from app.schemas import EmployeeResponse

        emp = Employee(id=1, name="Ana", surname="Lopez", department_id=1, salary=50000.0)
        response = EmployeeResponse.model_validate(emp)
        assert response.id == 1
        assert response.name == "Ana"


# ─── Department CRUD ──────────────────────────────────────────────────────────


class TestCrudCreateDepartment:
    def test_creates_department_with_correct_fields(self, db):
        data = DepartmentCreate(name="Finance", description="Accounting", budget=200000.0)
        dept = crud.create_department(db, data)

        assert dept.id is not None
        assert dept.name == "Finance"
        assert dept.description == "Accounting"
        assert dept.budget == 200000.0

    def test_assigns_unique_ids(self, db):
        d1 = crud.create_department(db, DepartmentCreate(name="Dept1", budget=1000.0))
        d2 = crud.create_department(db, DepartmentCreate(name="Dept2", budget=2000.0))

        assert d1.id != d2.id


class TestCrudGetDepartment:
    def test_returns_department_by_id(self, db, sample_department):
        result = crud.get_department(db, sample_department.id)

        assert result is not None
        assert result.id == sample_department.id
        assert result.name == sample_department.name

    def test_returns_none_for_missing_id(self, db):
        assert crud.get_department(db, 9999) is None


class TestCrudGetDepartments:
    def test_returns_all_departments(self, db):
        crud.create_department(db, DepartmentCreate(name="D1", budget=1000.0))
        crud.create_department(db, DepartmentCreate(name="D2", budget=2000.0))

        assert len(crud.get_departments(db)) == 2

    def test_returns_empty_list_when_none(self, db):
        assert crud.get_departments(db) == []

    def test_skip_and_limit(self, db):
        for i in range(5):
            crud.create_department(db, DepartmentCreate(name=f"D{i}", budget=1000.0))

        result = crud.get_departments(db, skip=2, limit=2)

        assert len(result) == 2


class TestCrudUpdateDepartment:
    def test_updates_specified_fields(self, db, sample_department):
        updated = crud.update_department(
            db, sample_department.id, DepartmentUpdate(budget=999.0)
        )

        assert updated.budget == 999.0
        assert updated.name == sample_department.name

    def test_returns_none_for_missing_id(self, db):
        assert crud.update_department(db, 9999, DepartmentUpdate(budget=1.0)) is None

    def test_partial_update_preserves_other_fields(self, db, sample_department):
        updated = crud.update_department(
            db, sample_department.id, DepartmentUpdate(name="NewName")
        )

        assert updated.name == "NewName"
        assert updated.budget == sample_department.budget


class TestCrudDeleteDepartment:
    def test_deletes_existing_department(self, db, sample_department):
        assert crud.delete_department(db, sample_department.id) is True
        assert crud.get_department(db, sample_department.id) is None

    def test_returns_false_for_missing_id(self, db):
        assert crud.delete_department(db, 9999) is False


class TestDepartmentSchemas:
    def test_create_valid(self):
        data = DepartmentCreate(name="HR", budget=50000.0)
        assert data.name == "HR"

    def test_rejects_empty_name(self):
        with pytest.raises(Exception):
            DepartmentCreate(name="", budget=50000.0)

    def test_rejects_negative_budget(self):
        with pytest.raises(Exception):
            DepartmentCreate(name="HR", budget=-1.0)

    def test_update_all_fields_optional(self):
        update = DepartmentUpdate()
        assert update.name is None
        assert update.budget is None


# ─── Sale CRUD ────────────────────────────────────────────────────────────────


class TestCrudCreateSale:
    def test_creates_sale_with_correct_fields(self, db, sample_employee, sample_department):
        data = SaleCreate(
            employee_id=sample_employee.id,
            department_id=sample_department.id,
            amount=8000.0,
            sale_date=datetime.date(2024, 6, 1),
            description="Big deal",
        )
        sale = crud.create_sale(db, data)

        assert sale.id is not None
        assert sale.amount == 8000.0
        assert sale.employee_id == sample_employee.id
        assert sale.department_id == sample_department.id

    def test_assigns_unique_ids(self, db, sample_employee, sample_department):
        s1 = crud.create_sale(
            db,
            SaleCreate(
                employee_id=sample_employee.id,
                department_id=sample_department.id,
                amount=100.0,
                sale_date=datetime.date(2024, 1, 1),
            ),
        )
        s2 = crud.create_sale(
            db,
            SaleCreate(
                employee_id=sample_employee.id,
                department_id=sample_department.id,
                amount=200.0,
                sale_date=datetime.date(2024, 1, 2),
            ),
        )

        assert s1.id != s2.id


class TestCrudGetSale:
    def test_returns_sale_by_id(self, db, sample_sale):
        result = crud.get_sale(db, sample_sale.id)

        assert result is not None
        assert result.id == sample_sale.id

    def test_returns_none_for_missing_id(self, db):
        assert crud.get_sale(db, 9999) is None


class TestCrudGetSales:
    def test_returns_all_sales(self, db, sample_employee, sample_department):
        for i in range(3):
            crud.create_sale(
                db,
                SaleCreate(
                    employee_id=sample_employee.id,
                    department_id=sample_department.id,
                    amount=float(1000 * (i + 1)),
                    sale_date=datetime.date(2024, 1, i + 1),
                ),
            )

        assert len(crud.get_sales(db)) == 3

    def test_returns_empty_list_when_none(self, db):
        assert crud.get_sales(db) == []

    def test_skip_and_limit(self, db, sample_employee, sample_department):
        for i in range(5):
            crud.create_sale(
                db,
                SaleCreate(
                    employee_id=sample_employee.id,
                    department_id=sample_department.id,
                    amount=float(1000 * (i + 1)),
                    sale_date=datetime.date(2024, 1, i + 1),
                ),
            )

        assert len(crud.get_sales(db, skip=2, limit=2)) == 2


class TestCrudUpdateSale:
    def test_updates_specified_fields(self, db, sample_sale):
        updated = crud.update_sale(db, sample_sale.id, SaleUpdate(amount=9999.0))

        assert updated.amount == 9999.0
        assert updated.employee_id == sample_sale.employee_id

    def test_returns_none_for_missing_id(self, db):
        assert crud.update_sale(db, 9999, SaleUpdate(amount=1.0)) is None

    def test_partial_update_preserves_other_fields(self, db, sample_sale):
        updated = crud.update_sale(db, sample_sale.id, SaleUpdate(description="Updated"))

        assert updated.description == "Updated"
        assert updated.amount == sample_sale.amount


class TestCrudDeleteSale:
    def test_deletes_existing_sale(self, db, sample_sale):
        assert crud.delete_sale(db, sample_sale.id) is True
        assert crud.get_sale(db, sample_sale.id) is None

    def test_returns_false_for_missing_id(self, db):
        assert crud.delete_sale(db, 9999) is False


class TestSaleSchemas:
    def test_create_valid(self):
        data = SaleCreate(
            employee_id=1, department_id=1, amount=100.0, sale_date=datetime.date(2024, 1, 1)
        )
        assert data.amount == 100.0

    def test_rejects_zero_amount(self):
        with pytest.raises(Exception):
            SaleCreate(
                employee_id=1, department_id=1, amount=0.0, sale_date=datetime.date(2024, 1, 1)
            )

    def test_update_all_fields_optional(self):
        update = SaleUpdate()
        assert update.amount is None
        assert update.sale_date is None


# ─── Purchase CRUD ────────────────────────────────────────────────────────────


class TestCrudCreatePurchase:
    def test_creates_purchase_with_correct_fields(self, db, sample_department):
        data = PurchaseCreate(
            department_id=sample_department.id,
            vendor="Microsoft",
            amount=5000.0,
            purchase_date=datetime.date(2024, 3, 1),
        )
        purchase = crud.create_purchase(db, data)

        assert purchase.id is not None
        assert purchase.vendor == "Microsoft"
        assert purchase.amount == 5000.0

    def test_assigns_unique_ids(self, db, sample_department):
        p1 = crud.create_purchase(
            db,
            PurchaseCreate(
                department_id=sample_department.id,
                vendor="V1",
                amount=100.0,
                purchase_date=datetime.date(2024, 1, 1),
            ),
        )
        p2 = crud.create_purchase(
            db,
            PurchaseCreate(
                department_id=sample_department.id,
                vendor="V2",
                amount=200.0,
                purchase_date=datetime.date(2024, 1, 2),
            ),
        )

        assert p1.id != p2.id


class TestCrudGetPurchase:
    def test_returns_purchase_by_id(self, db, sample_purchase):
        result = crud.get_purchase(db, sample_purchase.id)

        assert result is not None
        assert result.id == sample_purchase.id

    def test_returns_none_for_missing_id(self, db):
        assert crud.get_purchase(db, 9999) is None


class TestCrudGetPurchases:
    def test_returns_all_purchases(self, db, sample_department):
        for i in range(3):
            crud.create_purchase(
                db,
                PurchaseCreate(
                    department_id=sample_department.id,
                    vendor=f"V{i}",
                    amount=float(100 * (i + 1)),
                    purchase_date=datetime.date(2024, 1, i + 1),
                ),
            )

        assert len(crud.get_purchases(db)) == 3

    def test_returns_empty_list_when_none(self, db):
        assert crud.get_purchases(db) == []

    def test_skip_and_limit(self, db, sample_department):
        for i in range(5):
            crud.create_purchase(
                db,
                PurchaseCreate(
                    department_id=sample_department.id,
                    vendor=f"V{i}",
                    amount=float(100 * (i + 1)),
                    purchase_date=datetime.date(2024, 1, i + 1),
                ),
            )

        assert len(crud.get_purchases(db, skip=2, limit=2)) == 2


class TestCrudUpdatePurchase:
    def test_updates_specified_fields(self, db, sample_purchase):
        updated = crud.update_purchase(db, sample_purchase.id, PurchaseUpdate(amount=9999.0))

        assert updated.amount == 9999.0
        assert updated.vendor == sample_purchase.vendor

    def test_returns_none_for_missing_id(self, db):
        assert crud.update_purchase(db, 9999, PurchaseUpdate(amount=1.0)) is None

    def test_partial_update_preserves_other_fields(self, db, sample_purchase):
        updated = crud.update_purchase(
            db, sample_purchase.id, PurchaseUpdate(vendor="NewVendor")
        )

        assert updated.vendor == "NewVendor"
        assert updated.amount == sample_purchase.amount


class TestCrudDeletePurchase:
    def test_deletes_existing_purchase(self, db, sample_purchase):
        assert crud.delete_purchase(db, sample_purchase.id) is True
        assert crud.get_purchase(db, sample_purchase.id) is None

    def test_returns_false_for_missing_id(self, db):
        assert crud.delete_purchase(db, 9999) is False


class TestPurchaseSchemas:
    def test_create_valid(self):
        data = PurchaseCreate(
            department_id=1, vendor="AWS", amount=500.0, purchase_date=datetime.date(2024, 1, 1)
        )
        assert data.vendor == "AWS"

    def test_rejects_empty_vendor(self):
        with pytest.raises(Exception):
            PurchaseCreate(
                department_id=1, vendor="", amount=500.0, purchase_date=datetime.date(2024, 1, 1)
            )

    def test_update_all_fields_optional(self):
        update = PurchaseUpdate()
        assert update.vendor is None
        assert update.amount is None


# ─── Fiscality CRUD ───────────────────────────────────────────────────────────


class TestCrudCreateFiscality:
    def test_creates_fiscality_with_correct_fields(self, db, sample_department):
        data = FiscalityCreate(
            department_id=sample_department.id,
            tax_year=2022,
            tax_rate=0.25,
            taxable_amount=200000.0,
            tax_paid=50000.0,
            notes="Test record",
        )
        fiscality = crud.create_fiscality(db, data)

        assert fiscality.id is not None
        assert fiscality.tax_year == 2022
        assert fiscality.tax_rate == 0.25
        assert fiscality.taxable_amount == 200000.0

    def test_assigns_unique_ids(self, db, sample_department):
        f1 = crud.create_fiscality(
            db,
            FiscalityCreate(
                department_id=sample_department.id,
                tax_year=2021,
                tax_rate=0.21,
                taxable_amount=100000.0,
                tax_paid=21000.0,
            ),
        )
        f2 = crud.create_fiscality(
            db,
            FiscalityCreate(
                department_id=sample_department.id,
                tax_year=2022,
                tax_rate=0.21,
                taxable_amount=100000.0,
                tax_paid=21000.0,
            ),
        )

        assert f1.id != f2.id


class TestCrudGetFiscality:
    def test_returns_fiscality_by_id(self, db, sample_fiscality):
        result = crud.get_fiscality(db, sample_fiscality.id)

        assert result is not None
        assert result.id == sample_fiscality.id

    def test_returns_none_for_missing_id(self, db):
        assert crud.get_fiscality(db, 9999) is None


class TestCrudGetFiscalities:
    def test_returns_all_fiscalities(self, db, sample_department):
        for year in [2021, 2022, 2023]:
            crud.create_fiscality(
                db,
                FiscalityCreate(
                    department_id=sample_department.id,
                    tax_year=year,
                    tax_rate=0.21,
                    taxable_amount=100000.0,
                    tax_paid=21000.0,
                ),
            )

        assert len(crud.get_fiscalities(db)) == 3

    def test_returns_empty_list_when_none(self, db):
        assert crud.get_fiscalities(db) == []

    def test_skip_and_limit(self, db, sample_department):
        for year in range(2018, 2023):
            crud.create_fiscality(
                db,
                FiscalityCreate(
                    department_id=sample_department.id,
                    tax_year=year,
                    tax_rate=0.21,
                    taxable_amount=100000.0,
                    tax_paid=21000.0,
                ),
            )

        assert len(crud.get_fiscalities(db, skip=2, limit=2)) == 2


class TestCrudUpdateFiscality:
    def test_updates_specified_fields(self, db, sample_fiscality):
        updated = crud.update_fiscality(
            db, sample_fiscality.id, FiscalityUpdate(tax_paid=99999.0)
        )

        assert updated.tax_paid == 99999.0
        assert updated.tax_year == sample_fiscality.tax_year

    def test_returns_none_for_missing_id(self, db):
        assert crud.update_fiscality(db, 9999, FiscalityUpdate(tax_paid=1.0)) is None

    def test_partial_update_preserves_other_fields(self, db, sample_fiscality):
        updated = crud.update_fiscality(
            db, sample_fiscality.id, FiscalityUpdate(notes="Updated note")
        )

        assert updated.notes == "Updated note"
        assert updated.taxable_amount == sample_fiscality.taxable_amount


class TestCrudDeleteFiscality:
    def test_deletes_existing_fiscality(self, db, sample_fiscality):
        assert crud.delete_fiscality(db, sample_fiscality.id) is True
        assert crud.get_fiscality(db, sample_fiscality.id) is None

    def test_returns_false_for_missing_id(self, db):
        assert crud.delete_fiscality(db, 9999) is False


class TestFiscalitySchemas:
    def test_create_valid(self):
        data = FiscalityCreate(
            department_id=1,
            tax_year=2023,
            tax_rate=0.21,
            taxable_amount=100000.0,
            tax_paid=21000.0,
        )
        assert data.tax_rate == 0.21

    def test_rejects_invalid_tax_year(self):
        with pytest.raises(Exception):
            FiscalityCreate(
                department_id=1,
                tax_year=1999,
                tax_rate=0.21,
                taxable_amount=100000.0,
                tax_paid=21000.0,
            )

    def test_rejects_tax_rate_above_one(self):
        with pytest.raises(Exception):
            FiscalityCreate(
                department_id=1,
                tax_year=2023,
                tax_rate=1.5,
                taxable_amount=100000.0,
                tax_paid=21000.0,
            )

    def test_update_all_fields_optional(self):
        update = FiscalityUpdate()
        assert update.tax_year is None
        assert update.tax_rate is None
        assert update.tax_paid is None
