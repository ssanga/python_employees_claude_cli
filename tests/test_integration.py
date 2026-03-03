"""Integration tests for the FastAPI REST endpoints."""


class TestRootRedirect:
    def test_root_redirects_to_docs(self, client):
        response = client.get("/", follow_redirects=False)

        assert response.status_code == 307
        assert response.headers["location"] == "/docs"


# ─── Employees ────────────────────────────────────────────────────────────────


class TestListEmployees:
    def test_returns_empty_list_initially(self, client):
        response = client.get("/employees")

        assert response.status_code == 200
        assert response.json() == []

    def test_returns_created_employees(self, client, sample_department):
        client.post(
            "/employees",
            json={"name": "Alice", "surname": "Smith", "department_id": sample_department.id, "salary": 45000},
        )
        client.post(
            "/employees",
            json={"name": "Bob", "surname": "Jones", "department_id": sample_department.id, "salary": 55000},
        )

        response = client.get("/employees")

        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_skip_and_limit_query_params(self, client, sample_department):
        for i in range(5):
            client.post(
                "/employees",
                json={"name": f"Emp{i}", "surname": "Test", "department_id": sample_department.id, "salary": 1000},
            )

        response = client.get("/employees?skip=1&limit=2")

        assert response.status_code == 200
        assert len(response.json()) == 2


class TestGetEmployee:
    def test_returns_employee_by_id(self, client, sample_department):
        created = client.post(
            "/employees",
            json={"name": "Alice", "surname": "Smith", "department_id": sample_department.id, "salary": 45000},
        ).json()

        response = client.get(f"/employees/{created['id']}")

        assert response.status_code == 200
        assert response.json()["name"] == "Alice"

    def test_returns_404_for_missing_id(self, client):
        response = client.get("/employees/9999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Employee not found"


class TestCreateEmployee:
    def test_creates_employee_successfully(self, client, sample_department):
        payload = {
            "name": "John",
            "surname": "Doe",
            "department_id": sample_department.id,
            "salary": 60000,
        }

        response = client.post("/employees", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["id"] is not None
        assert data["name"] == "John"
        assert data["surname"] == "Doe"
        assert data["department_id"] == sample_department.id
        assert data["salary"] == 60000

    def test_returns_422_for_missing_fields(self, client):
        response = client.post("/employees", json={"name": "John"})

        assert response.status_code == 422

    def test_returns_422_for_negative_salary(self, client, sample_department):
        payload = {
            "name": "John",
            "surname": "Doe",
            "department_id": sample_department.id,
            "salary": -100,
        }

        response = client.post("/employees", json=payload)

        assert response.status_code == 422

    def test_returns_422_for_empty_name(self, client, sample_department):
        payload = {
            "name": "",
            "surname": "Doe",
            "department_id": sample_department.id,
            "salary": 50000,
        }

        response = client.post("/employees", json=payload)

        assert response.status_code == 422


class TestUpdateEmployee:
    def test_updates_employee_fields(self, client, sample_department):
        created = client.post(
            "/employees",
            json={"name": "John", "surname": "Doe", "department_id": sample_department.id, "salary": 60000},
        ).json()

        response = client.put(
            f"/employees/{created['id']}",
            json={"salary": 80000, "department_id": sample_department.id},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["salary"] == 80000
        assert data["department_id"] == sample_department.id
        assert data["name"] == "John"

    def test_returns_404_for_missing_id(self, client):
        response = client.put("/employees/9999", json={"salary": 80000})

        assert response.status_code == 404

    def test_partial_update_preserves_other_fields(self, client, sample_department):
        created = client.post(
            "/employees",
            json={"name": "John", "surname": "Doe", "department_id": sample_department.id, "salary": 60000},
        ).json()

        response = client.put(f"/employees/{created['id']}", json={"name": "Jane"})

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Jane"
        assert data["surname"] == "Doe"
        assert data["salary"] == 60000


class TestDeleteEmployee:
    def test_deletes_employee_successfully(self, client, sample_department):
        created = client.post(
            "/employees",
            json={"name": "John", "surname": "Doe", "department_id": sample_department.id, "salary": 60000},
        ).json()

        response = client.delete(f"/employees/{created['id']}")

        assert response.status_code == 204

    def test_deleted_employee_no_longer_accessible(self, client, sample_department):
        created = client.post(
            "/employees",
            json={"name": "John", "surname": "Doe", "department_id": sample_department.id, "salary": 60000},
        ).json()
        client.delete(f"/employees/{created['id']}")

        response = client.get(f"/employees/{created['id']}")

        assert response.status_code == 404

    def test_returns_404_for_missing_id(self, client):
        response = client.delete("/employees/9999")

        assert response.status_code == 404


# ─── Departments ──────────────────────────────────────────────────────────────


class TestListDepartments:
    def test_returns_empty_list_initially(self, client):
        response = client.get("/departments")

        assert response.status_code == 200
        assert response.json() == []

    def test_returns_created_departments(self, client):
        client.post("/departments", json={"name": "Eng", "budget": 100000})
        client.post("/departments", json={"name": "HR", "budget": 50000})

        response = client.get("/departments")

        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_skip_and_limit_query_params(self, client):
        for i in range(5):
            client.post("/departments", json={"name": f"D{i}", "budget": 1000})

        response = client.get("/departments?skip=1&limit=2")

        assert response.status_code == 200
        assert len(response.json()) == 2


class TestGetDepartment:
    def test_returns_department_by_id(self, client):
        created = client.post("/departments", json={"name": "Finance", "budget": 200000}).json()

        response = client.get(f"/departments/{created['id']}")

        assert response.status_code == 200
        assert response.json()["name"] == "Finance"

    def test_returns_404_for_missing_id(self, client):
        response = client.get("/departments/9999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Department not found"


class TestCreateDepartment:
    def test_creates_department_successfully(self, client):
        payload = {"name": "Marketing", "description": "Marketing team", "budget": 180000}

        response = client.post("/departments", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["id"] is not None
        assert data["name"] == "Marketing"
        assert data["budget"] == 180000

    def test_returns_422_for_missing_fields(self, client):
        response = client.post("/departments", json={"name": "Ops"})

        assert response.status_code == 422

    def test_returns_422_for_empty_name(self, client):
        response = client.post("/departments", json={"name": "", "budget": 1000})

        assert response.status_code == 422

    def test_returns_422_for_negative_budget(self, client):
        response = client.post("/departments", json={"name": "Ops", "budget": -1})

        assert response.status_code == 422


class TestUpdateDepartment:
    def test_updates_department_fields(self, client):
        created = client.post("/departments", json={"name": "OldName", "budget": 1000}).json()

        response = client.put(f"/departments/{created['id']}", json={"budget": 99999})

        assert response.status_code == 200
        assert response.json()["budget"] == 99999
        assert response.json()["name"] == "OldName"

    def test_returns_404_for_missing_id(self, client):
        response = client.put("/departments/9999", json={"budget": 1000})

        assert response.status_code == 404

    def test_partial_update_preserves_other_fields(self, client):
        created = client.post("/departments", json={"name": "Dev", "budget": 5000}).json()

        response = client.put(f"/departments/{created['id']}", json={"name": "DevOps"})

        assert response.status_code == 200
        assert response.json()["name"] == "DevOps"
        assert response.json()["budget"] == 5000


class TestDeleteDepartment:
    def test_deletes_department_successfully(self, client):
        created = client.post("/departments", json={"name": "Temp", "budget": 1000}).json()

        response = client.delete(f"/departments/{created['id']}")

        assert response.status_code == 204

    def test_deleted_department_no_longer_accessible(self, client):
        created = client.post("/departments", json={"name": "Temp", "budget": 1000}).json()
        client.delete(f"/departments/{created['id']}")

        response = client.get(f"/departments/{created['id']}")

        assert response.status_code == 404

    def test_returns_404_for_missing_id(self, client):
        response = client.delete("/departments/9999")

        assert response.status_code == 404


# ─── Sales ────────────────────────────────────────────────────────────────────


class TestListSales:
    def test_returns_empty_list_initially(self, client):
        response = client.get("/sales")

        assert response.status_code == 200
        assert response.json() == []

    def test_returns_created_sales(self, client, sample_department):
        emp = client.post(
            "/employees",
            json={"name": "Seller", "surname": "A", "department_id": sample_department.id, "salary": 50000},
        ).json()
        for i in range(2):
            client.post(
                "/sales",
                json={
                    "employee_id": emp["id"],
                    "department_id": sample_department.id,
                    "amount": 1000 * (i + 1),
                    "sale_date": f"2024-0{i + 1}-01",
                },
            )

        response = client.get("/sales")

        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_skip_and_limit_query_params(self, client, sample_department):
        emp = client.post(
            "/employees",
            json={"name": "Seller", "surname": "B", "department_id": sample_department.id, "salary": 50000},
        ).json()
        for i in range(5):
            client.post(
                "/sales",
                json={
                    "employee_id": emp["id"],
                    "department_id": sample_department.id,
                    "amount": 1000,
                    "sale_date": f"2024-01-{i + 1:02d}",
                },
            )

        response = client.get("/sales?skip=1&limit=2")

        assert response.status_code == 200
        assert len(response.json()) == 2


class TestGetSale:
    def test_returns_sale_by_id(self, client, sample_department):
        emp = client.post(
            "/employees",
            json={"name": "S", "surname": "T", "department_id": sample_department.id, "salary": 50000},
        ).json()
        created = client.post(
            "/sales",
            json={
                "employee_id": emp["id"],
                "department_id": sample_department.id,
                "amount": 7500,
                "sale_date": "2024-06-15",
            },
        ).json()

        response = client.get(f"/sales/{created['id']}")

        assert response.status_code == 200
        assert response.json()["amount"] == 7500

    def test_returns_404_for_missing_id(self, client):
        response = client.get("/sales/9999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Sale not found"


class TestCreateSale:
    def test_creates_sale_successfully(self, client, sample_department):
        emp = client.post(
            "/employees",
            json={"name": "John", "surname": "Doe", "department_id": sample_department.id, "salary": 60000},
        ).json()
        payload = {
            "employee_id": emp["id"],
            "department_id": sample_department.id,
            "amount": 5000,
            "sale_date": "2024-01-15",
            "description": "Big deal",
        }

        response = client.post("/sales", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["id"] is not None
        assert data["amount"] == 5000
        assert data["employee_id"] == emp["id"]

    def test_returns_422_for_missing_fields(self, client):
        response = client.post("/sales", json={"amount": 1000})

        assert response.status_code == 422

    def test_returns_422_for_zero_amount(self, client, sample_department):
        emp = client.post(
            "/employees",
            json={"name": "E", "surname": "F", "department_id": sample_department.id, "salary": 50000},
        ).json()
        response = client.post(
            "/sales",
            json={
                "employee_id": emp["id"],
                "department_id": sample_department.id,
                "amount": 0,
                "sale_date": "2024-01-01",
            },
        )

        assert response.status_code == 422


class TestUpdateSale:
    def test_updates_sale_fields(self, client, sample_department):
        emp = client.post(
            "/employees",
            json={"name": "S", "surname": "T", "department_id": sample_department.id, "salary": 50000},
        ).json()
        created = client.post(
            "/sales",
            json={
                "employee_id": emp["id"],
                "department_id": sample_department.id,
                "amount": 1000,
                "sale_date": "2024-01-01",
            },
        ).json()

        response = client.put(f"/sales/{created['id']}", json={"amount": 9999})

        assert response.status_code == 200
        assert response.json()["amount"] == 9999

    def test_returns_404_for_missing_id(self, client):
        response = client.put("/sales/9999", json={"amount": 1000})

        assert response.status_code == 404


class TestDeleteSale:
    def test_deletes_sale_successfully(self, client, sample_department):
        emp = client.post(
            "/employees",
            json={"name": "S", "surname": "T", "department_id": sample_department.id, "salary": 50000},
        ).json()
        created = client.post(
            "/sales",
            json={
                "employee_id": emp["id"],
                "department_id": sample_department.id,
                "amount": 1000,
                "sale_date": "2024-01-01",
            },
        ).json()

        response = client.delete(f"/sales/{created['id']}")

        assert response.status_code == 204

    def test_deleted_sale_no_longer_accessible(self, client, sample_department):
        emp = client.post(
            "/employees",
            json={"name": "S", "surname": "T", "department_id": sample_department.id, "salary": 50000},
        ).json()
        created = client.post(
            "/sales",
            json={
                "employee_id": emp["id"],
                "department_id": sample_department.id,
                "amount": 1000,
                "sale_date": "2024-01-01",
            },
        ).json()
        client.delete(f"/sales/{created['id']}")

        response = client.get(f"/sales/{created['id']}")

        assert response.status_code == 404

    def test_returns_404_for_missing_id(self, client):
        response = client.delete("/sales/9999")

        assert response.status_code == 404


# ─── Purchases ────────────────────────────────────────────────────────────────


class TestListPurchases:
    def test_returns_empty_list_initially(self, client):
        response = client.get("/purchases")

        assert response.status_code == 200
        assert response.json() == []

    def test_returns_created_purchases(self, client, sample_department):
        for vendor in ["AWS", "Azure"]:
            client.post(
                "/purchases",
                json={
                    "department_id": sample_department.id,
                    "vendor": vendor,
                    "amount": 1000,
                    "purchase_date": "2024-01-01",
                },
            )

        response = client.get("/purchases")

        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_skip_and_limit_query_params(self, client, sample_department):
        for i in range(5):
            client.post(
                "/purchases",
                json={
                    "department_id": sample_department.id,
                    "vendor": f"V{i}",
                    "amount": 1000,
                    "purchase_date": f"2024-01-{i + 1:02d}",
                },
            )

        response = client.get("/purchases?skip=1&limit=2")

        assert response.status_code == 200
        assert len(response.json()) == 2


class TestGetPurchase:
    def test_returns_purchase_by_id(self, client, sample_department):
        created = client.post(
            "/purchases",
            json={
                "department_id": sample_department.id,
                "vendor": "Microsoft",
                "amount": 3000,
                "purchase_date": "2024-03-01",
            },
        ).json()

        response = client.get(f"/purchases/{created['id']}")

        assert response.status_code == 200
        assert response.json()["vendor"] == "Microsoft"

    def test_returns_404_for_missing_id(self, client):
        response = client.get("/purchases/9999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Purchase not found"


class TestCreatePurchase:
    def test_creates_purchase_successfully(self, client, sample_department):
        payload = {
            "department_id": sample_department.id,
            "vendor": "AWS",
            "amount": 9500,
            "purchase_date": "2024-01-20",
            "description": "Cloud Q1",
        }

        response = client.post("/purchases", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["id"] is not None
        assert data["vendor"] == "AWS"
        assert data["amount"] == 9500

    def test_returns_422_for_missing_fields(self, client):
        response = client.post("/purchases", json={"vendor": "AWS"})

        assert response.status_code == 422

    def test_returns_422_for_empty_vendor(self, client, sample_department):
        response = client.post(
            "/purchases",
            json={
                "department_id": sample_department.id,
                "vendor": "",
                "amount": 1000,
                "purchase_date": "2024-01-01",
            },
        )

        assert response.status_code == 422


class TestUpdatePurchase:
    def test_updates_purchase_fields(self, client, sample_department):
        created = client.post(
            "/purchases",
            json={
                "department_id": sample_department.id,
                "vendor": "OldVendor",
                "amount": 1000,
                "purchase_date": "2024-01-01",
            },
        ).json()

        response = client.put(f"/purchases/{created['id']}", json={"vendor": "NewVendor"})

        assert response.status_code == 200
        assert response.json()["vendor"] == "NewVendor"
        assert response.json()["amount"] == 1000

    def test_returns_404_for_missing_id(self, client):
        response = client.put("/purchases/9999", json={"amount": 1000})

        assert response.status_code == 404


class TestDeletePurchase:
    def test_deletes_purchase_successfully(self, client, sample_department):
        created = client.post(
            "/purchases",
            json={
                "department_id": sample_department.id,
                "vendor": "TempVendor",
                "amount": 500,
                "purchase_date": "2024-01-01",
            },
        ).json()

        response = client.delete(f"/purchases/{created['id']}")

        assert response.status_code == 204

    def test_deleted_purchase_no_longer_accessible(self, client, sample_department):
        created = client.post(
            "/purchases",
            json={
                "department_id": sample_department.id,
                "vendor": "TempVendor",
                "amount": 500,
                "purchase_date": "2024-01-01",
            },
        ).json()
        client.delete(f"/purchases/{created['id']}")

        response = client.get(f"/purchases/{created['id']}")

        assert response.status_code == 404

    def test_returns_404_for_missing_id(self, client):
        response = client.delete("/purchases/9999")

        assert response.status_code == 404


# ─── Fiscality ────────────────────────────────────────────────────────────────


class TestListFiscalities:
    def test_returns_empty_list_initially(self, client):
        response = client.get("/fiscality")

        assert response.status_code == 200
        assert response.json() == []

    def test_returns_created_fiscalities(self, client, sample_department):
        for year in [2022, 2023]:
            client.post(
                "/fiscality",
                json={
                    "department_id": sample_department.id,
                    "tax_year": year,
                    "tax_rate": 0.21,
                    "taxable_amount": 100000,
                    "tax_paid": 21000,
                },
            )

        response = client.get("/fiscality")

        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_skip_and_limit_query_params(self, client, sample_department):
        for year in range(2018, 2023):
            client.post(
                "/fiscality",
                json={
                    "department_id": sample_department.id,
                    "tax_year": year,
                    "tax_rate": 0.21,
                    "taxable_amount": 100000,
                    "tax_paid": 21000,
                },
            )

        response = client.get("/fiscality?skip=1&limit=2")

        assert response.status_code == 200
        assert len(response.json()) == 2


class TestGetFiscality:
    def test_returns_fiscality_by_id(self, client, sample_department):
        created = client.post(
            "/fiscality",
            json={
                "department_id": sample_department.id,
                "tax_year": 2023,
                "tax_rate": 0.21,
                "taxable_amount": 100000,
                "tax_paid": 21000,
            },
        ).json()

        response = client.get(f"/fiscality/{created['id']}")

        assert response.status_code == 200
        assert response.json()["tax_year"] == 2023

    def test_returns_404_for_missing_id(self, client):
        response = client.get("/fiscality/9999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Fiscality not found"


class TestCreateFiscality:
    def test_creates_fiscality_successfully(self, client, sample_department):
        payload = {
            "department_id": sample_department.id,
            "tax_year": 2023,
            "tax_rate": 0.21,
            "taxable_amount": 200000,
            "tax_paid": 42000,
            "notes": "Annual tax",
        }

        response = client.post("/fiscality", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["id"] is not None
        assert data["tax_year"] == 2023
        assert data["tax_rate"] == 0.21

    def test_returns_422_for_missing_fields(self, client):
        response = client.post("/fiscality", json={"tax_year": 2023})

        assert response.status_code == 422

    def test_returns_422_for_invalid_tax_year(self, client, sample_department):
        response = client.post(
            "/fiscality",
            json={
                "department_id": sample_department.id,
                "tax_year": 1999,
                "tax_rate": 0.21,
                "taxable_amount": 100000,
                "tax_paid": 21000,
            },
        )

        assert response.status_code == 422

    def test_returns_422_for_tax_rate_above_one(self, client, sample_department):
        response = client.post(
            "/fiscality",
            json={
                "department_id": sample_department.id,
                "tax_year": 2023,
                "tax_rate": 1.5,
                "taxable_amount": 100000,
                "tax_paid": 21000,
            },
        )

        assert response.status_code == 422


class TestUpdateFiscality:
    def test_updates_fiscality_fields(self, client, sample_department):
        created = client.post(
            "/fiscality",
            json={
                "department_id": sample_department.id,
                "tax_year": 2023,
                "tax_rate": 0.21,
                "taxable_amount": 100000,
                "tax_paid": 21000,
            },
        ).json()

        response = client.put(f"/fiscality/{created['id']}", json={"tax_paid": 99999})

        assert response.status_code == 200
        assert response.json()["tax_paid"] == 99999
        assert response.json()["tax_year"] == 2023

    def test_returns_404_for_missing_id(self, client):
        response = client.put("/fiscality/9999", json={"tax_paid": 1000})

        assert response.status_code == 404


class TestDeleteFiscality:
    def test_deletes_fiscality_successfully(self, client, sample_department):
        created = client.post(
            "/fiscality",
            json={
                "department_id": sample_department.id,
                "tax_year": 2023,
                "tax_rate": 0.21,
                "taxable_amount": 100000,
                "tax_paid": 21000,
            },
        ).json()

        response = client.delete(f"/fiscality/{created['id']}")

        assert response.status_code == 204

    def test_deleted_fiscality_no_longer_accessible(self, client, sample_department):
        created = client.post(
            "/fiscality",
            json={
                "department_id": sample_department.id,
                "tax_year": 2023,
                "tax_rate": 0.21,
                "taxable_amount": 100000,
                "tax_paid": 21000,
            },
        ).json()
        client.delete(f"/fiscality/{created['id']}")

        response = client.get(f"/fiscality/{created['id']}")

        assert response.status_code == 404

    def test_returns_404_for_missing_id(self, client):
        response = client.delete("/fiscality/9999")

        assert response.status_code == 404
