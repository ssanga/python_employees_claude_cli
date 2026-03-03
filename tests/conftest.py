import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import crud
from app.database import Base, get_db
from app.main import app
from app.schemas import DepartmentCreate, EmployeeCreate, FiscalityCreate, PurchaseCreate, SaleCreate

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def sample_department(db_session):
    return crud.create_department(
        db_session,
        DepartmentCreate(name="Engineering", description="Test department", budget=100000.0),
    )


@pytest.fixture
def sample_employee(db_session, sample_department):
    return crud.create_employee(
        db_session,
        EmployeeCreate(
            name="John",
            surname="Doe",
            department_id=sample_department.id,
            salary=60000.0,
        ),
    )


@pytest.fixture
def sample_sale(db_session, sample_employee, sample_department):
    return crud.create_sale(
        db_session,
        SaleCreate(
            employee_id=sample_employee.id,
            department_id=sample_department.id,
            amount=5000.0,
            sale_date=datetime.date(2024, 1, 15),
            description="Test sale",
        ),
    )


@pytest.fixture
def sample_purchase(db_session, sample_department):
    return crud.create_purchase(
        db_session,
        PurchaseCreate(
            department_id=sample_department.id,
            vendor="ACME Corp",
            amount=1000.0,
            purchase_date=datetime.date(2024, 1, 10),
            description="Test purchase",
        ),
    )


@pytest.fixture
def sample_fiscality(db_session, sample_department):
    return crud.create_fiscality(
        db_session,
        FiscalityCreate(
            department_id=sample_department.id,
            tax_year=2023,
            tax_rate=0.21,
            taxable_amount=100000.0,
            tax_paid=21000.0,
            notes="Test fiscal record",
        ),
    )
