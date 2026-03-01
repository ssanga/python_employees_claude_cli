"""Unit tests for CRUD operations and schemas."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import crud
from app.database import Base
from app.models import Employee
from app.schemas import EmployeeCreate, EmployeeUpdate

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
def sample_employee(db):
    data = EmployeeCreate(name="John", surname="Doe", department="Engineering", salary=60000.0)
    return crud.create_employee(db, data)


class TestCrudCreateEmployee:
    def test_creates_employee_with_correct_fields(self, db):
        data = EmployeeCreate(name="Alice", surname="Smith", department="HR", salary=45000.0)
        employee = crud.create_employee(db, data)

        assert employee.id is not None
        assert employee.name == "Alice"
        assert employee.surname == "Smith"
        assert employee.department == "HR"
        assert employee.salary == 45000.0

    def test_assigns_unique_ids(self, db):
        data1 = EmployeeCreate(name="Alice", surname="Smith", department="HR", salary=45000.0)
        data2 = EmployeeCreate(name="Bob", surname="Jones", department="IT", salary=55000.0)
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
    def test_returns_all_employees(self, db):
        crud.create_employee(db, EmployeeCreate(name="A", surname="B", department="X", salary=1000.0))
        crud.create_employee(db, EmployeeCreate(name="C", surname="D", department="Y", salary=2000.0))

        result = crud.get_employees(db)

        assert len(result) == 2

    def test_returns_empty_list_when_no_employees(self, db):
        result = crud.get_employees(db)

        assert result == []

    def test_skip_and_limit(self, db):
        for i in range(5):
            crud.create_employee(db, EmployeeCreate(name=f"Emp{i}", surname="Test", department="Dept", salary=1000.0))

        result = crud.get_employees(db, skip=2, limit=2)

        assert len(result) == 2


class TestCrudUpdateEmployee:
    def test_updates_specified_fields(self, db, sample_employee):
        update = EmployeeUpdate(salary=75000.0, department="Management")
        updated = crud.update_employee(db, sample_employee.id, update)

        assert updated.salary == 75000.0
        assert updated.department == "Management"
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


class TestSchemas:
    def test_employee_create_valid(self):
        data = EmployeeCreate(name="Test", surname="User", department="Ops", salary=30000.0)
        assert data.name == "Test"

    def test_employee_create_rejects_empty_name(self):
        with pytest.raises(Exception):
            EmployeeCreate(name="", surname="User", department="Ops", salary=30000.0)

    def test_employee_create_rejects_negative_salary(self):
        with pytest.raises(Exception):
            EmployeeCreate(name="Test", surname="User", department="Ops", salary=-100.0)

    def test_employee_update_all_fields_optional(self):
        update = EmployeeUpdate()
        assert update.name is None
        assert update.surname is None
        assert update.department is None
        assert update.salary is None

    def test_employee_response_from_orm(self):
        from app.schemas import EmployeeResponse
        emp = Employee(id=1, name="Ana", surname="Lopez", department="Finance", salary=50000.0)
        response = EmployeeResponse.model_validate(emp)
        assert response.id == 1
        assert response.name == "Ana"
