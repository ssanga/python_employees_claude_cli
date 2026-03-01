"""Integration tests for the FastAPI REST endpoints."""


class TestRootRedirect:
    def test_root_redirects_to_docs(self, client):
        response = client.get("/", follow_redirects=False)

        assert response.status_code == 307
        assert response.headers["location"] == "/docs"


class TestListEmployees:
    def test_returns_empty_list_initially(self, client):
        response = client.get("/employees")

        assert response.status_code == 200
        assert response.json() == []

    def test_returns_created_employees(self, client):
        client.post("/employees", json={"name": "Alice", "surname": "Smith", "department": "HR", "salary": 45000})
        client.post("/employees", json={"name": "Bob", "surname": "Jones", "department": "IT", "salary": 55000})

        response = client.get("/employees")

        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_skip_and_limit_query_params(self, client):
        for i in range(5):
            client.post("/employees", json={"name": f"Emp{i}", "surname": "Test", "department": "Dept", "salary": 1000})

        response = client.get("/employees?skip=1&limit=2")

        assert response.status_code == 200
        assert len(response.json()) == 2


class TestGetEmployee:
    def test_returns_employee_by_id(self, client):
        created = client.post("/employees", json={"name": "Alice", "surname": "Smith", "department": "HR", "salary": 45000}).json()

        response = client.get(f"/employees/{created['id']}")

        assert response.status_code == 200
        assert response.json()["name"] == "Alice"

    def test_returns_404_for_missing_id(self, client):
        response = client.get("/employees/9999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Employee not found"


class TestCreateEmployee:
    def test_creates_employee_successfully(self, client):
        payload = {"name": "John", "surname": "Doe", "department": "Engineering", "salary": 60000}

        response = client.post("/employees", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["id"] is not None
        assert data["name"] == "John"
        assert data["surname"] == "Doe"
        assert data["department"] == "Engineering"
        assert data["salary"] == 60000

    def test_returns_422_for_missing_fields(self, client):
        response = client.post("/employees", json={"name": "John"})

        assert response.status_code == 422

    def test_returns_422_for_negative_salary(self, client):
        payload = {"name": "John", "surname": "Doe", "department": "Engineering", "salary": -100}

        response = client.post("/employees", json=payload)

        assert response.status_code == 422

    def test_returns_422_for_empty_name(self, client):
        payload = {"name": "", "surname": "Doe", "department": "Engineering", "salary": 50000}

        response = client.post("/employees", json=payload)

        assert response.status_code == 422


class TestUpdateEmployee:
    def test_updates_employee_fields(self, client):
        created = client.post("/employees", json={"name": "John", "surname": "Doe", "department": "Engineering", "salary": 60000}).json()

        response = client.put(f"/employees/{created['id']}", json={"salary": 80000, "department": "Management"})

        assert response.status_code == 200
        data = response.json()
        assert data["salary"] == 80000
        assert data["department"] == "Management"
        assert data["name"] == "John"

    def test_returns_404_for_missing_id(self, client):
        response = client.put("/employees/9999", json={"salary": 80000})

        assert response.status_code == 404

    def test_partial_update_preserves_other_fields(self, client):
        created = client.post("/employees", json={"name": "John", "surname": "Doe", "department": "Engineering", "salary": 60000}).json()

        response = client.put(f"/employees/{created['id']}", json={"name": "Jane"})

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Jane"
        assert data["surname"] == "Doe"
        assert data["salary"] == 60000


class TestDeleteEmployee:
    def test_deletes_employee_successfully(self, client):
        created = client.post("/employees", json={"name": "John", "surname": "Doe", "department": "Engineering", "salary": 60000}).json()

        response = client.delete(f"/employees/{created['id']}")

        assert response.status_code == 204

    def test_deleted_employee_no_longer_accessible(self, client):
        created = client.post("/employees", json={"name": "John", "surname": "Doe", "department": "Engineering", "salary": 60000}).json()
        client.delete(f"/employees/{created['id']}")

        response = client.get(f"/employees/{created['id']}")

        assert response.status_code == 404

    def test_returns_404_for_missing_id(self, client):
        response = client.delete("/employees/9999")

        assert response.status_code == 404
