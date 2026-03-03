# Employees API

[![CI](https://github.com/ssanga/python_employees_claude_cli/actions/workflows/ci.yml/badge.svg)](https://github.com/ssanga/python_employees_claude_cli/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/ssanga/python_employees_claude_cli/branch/main/graph/badge.svg)](https://codecov.io/gh/ssanga/python_employees_claude_cli)
[![Python](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-brightgreen.svg)](https://fastapi.tiangolo.com)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red.svg)](https://docs.sqlalchemy.org/)

REST API para gestión de empleados, departamentos, ventas, compras y fiscalidad construida con **FastAPI**, **SQLAlchemy** y **SQLite**.

## Tecnologías

| Tecnología | Versión | Uso |
|---|---|---|
| Python | 3.13 | Lenguaje |
| FastAPI | ≥ 0.115 | Framework REST API |
| SQLAlchemy | ≥ 2.0 | ORM |
| SQLite | — | Base de datos |
| Pydantic | ≥ 2.0 | Validación y schemas |
| Uvicorn | ≥ 0.32 | Servidor ASGI |
| pytest | ≥ 8.0 | Tests |
| pytest-cov | ≥ 5.0 | Cobertura de código |

---

## Estructura del proyecto

```
python_employees_claude_cli/
├── app/
│   ├── __init__.py
│   ├── database.py          # Engine SQLite, sesión y Base declarativa
│   ├── models.py            # Modelos ORM: Department, Employee, Sale, Purchase, Fiscality
│   ├── schemas.py           # Schemas Pydantic (Create / Update / Response) para cada entidad
│   ├── crud.py              # Operaciones CRUD para todas las entidades
│   ├── main.py              # Aplicación FastAPI, registra los routers
│   └── routers/
│       ├── __init__.py
│       ├── employees.py     # Endpoints /employees
│       ├── departments.py   # Endpoints /departments
│       ├── sales.py         # Endpoints /sales
│       ├── purchases.py     # Endpoints /purchases
│       └── fiscality.py     # Endpoints /fiscality
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Fixtures compartidos (BD en memoria + TestClient)
│   ├── test_unit.py         # Tests unitarios de CRUD y schemas
│   └── test_integration.py  # Tests de integración de endpoints HTTP
├── .github/
│   └── workflows/
│       └── ci.yml           # Pipeline CI: tests + cobertura + lint
├── .vscode/
│   └── launch.json          # Configuración F5: arranca uvicorn y abre Swagger
├── seed.py                  # Pobla la BD con datos de ejemplo (5 tablas)
├── pyproject.toml
├── requirements.txt
└── .gitignore
```

---

## Instalación

### Requisitos previos

- Python 3.13+
- pip

### Pasos

```bash
# 1. Clonar el repositorio
git clone <url-del-repositorio>
cd python_employees_claude_cli

# 2. Crear entorno virtual (recomendado)
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
.venv\Scripts\activate           # Windows

# 3. Instalar dependencias
pip install -r requirements.txt
```

---

## Ejecución

### Opción A — VSCode (recomendado)

Pulsa **F5** en VSCode. El servidor arranca automáticamente y abre el navegador en Swagger UI.

### Opción B — Línea de comandos

```bash
uvicorn app.main:app --reload
```

El servidor arranca en `http://localhost:8000`.

| URL | Descripción |
|---|---|
| http://localhost:8000 | Redirige a Swagger |
| http://localhost:8000/docs | Swagger UI (interactivo) |
| http://localhost:8000/redoc | ReDoc (documentación alternativa) |
| http://localhost:8000/openapi.json | Esquema OpenAPI en JSON |

### Poblar la base de datos con datos de ejemplo

```bash
python seed.py
```

Inserta datos en todas las tablas en orden de dependencia:

| Tabla | Registros |
|---|---|
| departments | 5 |
| employees | 10 |
| sales | 5 |
| purchases | 5 |
| fiscality | 5 |

---

## Modelo de datos

### Relaciones entre tablas

```
Department (1) ──< Employee (N)
Department (1) ──< Sale (N)
Department (1) ──< Purchase (N)
Department (1) ──< Fiscality (N)
Employee   (1) ──< Sale (N)
```

### Esquema SQL

```sql
CREATE TABLE departments (
    id          INTEGER PRIMARY KEY,
    name        VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(500),
    budget      FLOAT NOT NULL
);

CREATE TABLE employees (
    id            INTEGER PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    surname       VARCHAR(100) NOT NULL,
    department_id INTEGER NOT NULL REFERENCES departments(id),
    salary        FLOAT NOT NULL
);

CREATE TABLE sales (
    id            INTEGER PRIMARY KEY,
    employee_id   INTEGER NOT NULL REFERENCES employees(id),
    department_id INTEGER NOT NULL REFERENCES departments(id),
    amount        FLOAT NOT NULL,
    sale_date     DATE NOT NULL,
    description   VARCHAR(500)
);

CREATE TABLE purchases (
    id            INTEGER PRIMARY KEY,
    department_id INTEGER NOT NULL REFERENCES departments(id),
    vendor        VARCHAR(200) NOT NULL,
    amount        FLOAT NOT NULL,
    purchase_date DATE NOT NULL,
    description   VARCHAR(500)
);

CREATE TABLE fiscality (
    id             INTEGER PRIMARY KEY,
    department_id  INTEGER NOT NULL REFERENCES departments(id),
    tax_year       INTEGER NOT NULL,
    tax_rate       FLOAT NOT NULL,
    taxable_amount FLOAT NOT NULL,
    tax_paid       FLOAT NOT NULL,
    notes          VARCHAR(500)
);
```

---

## API Reference

Todos los recursos siguen el mismo patrón REST con paginación `?skip=0&limit=100`.

### Employees — `/employees`

**Modelo de respuesta**
```json
{
  "id": 1,
  "name": "Alice",
  "surname": "Johnson",
  "department_id": 1,
  "salary": 72000.0
}
```

**Validaciones**
- `name`, `surname`: requeridos, 1–100 caracteres
- `department_id`: requerido, entero > 0 (FK a departments)
- `salary`: requerido, valor > 0

| Método | Ruta | Descripción | Respuesta |
|---|---|---|---|
| GET | `/employees` | Lista empleados (paginado) | 200 |
| GET | `/employees/{id}` | Obtiene empleado por ID | 200 / 404 |
| POST | `/employees` | Crea empleado | 201 / 422 |
| PUT | `/employees/{id}` | Actualización parcial | 200 / 404 |
| DELETE | `/employees/{id}` | Elimina empleado | 204 / 404 |

---

### Departments — `/departments`

**Modelo de respuesta**
```json
{
  "id": 1,
  "name": "Engineering",
  "description": "Software & infrastructure",
  "budget": 500000.0
}
```

**Validaciones**
- `name`: requerido, 1–100 caracteres
- `budget`: requerido, valor ≥ 0

| Método | Ruta | Descripción | Respuesta |
|---|---|---|---|
| GET | `/departments` | Lista departamentos | 200 |
| GET | `/departments/{id}` | Obtiene departamento por ID | 200 / 404 |
| POST | `/departments` | Crea departamento | 201 / 422 |
| PUT | `/departments/{id}` | Actualización parcial | 200 / 404 |
| DELETE | `/departments/{id}` | Elimina departamento | 204 / 404 |

---

### Sales — `/sales`

**Modelo de respuesta**
```json
{
  "id": 1,
  "employee_id": 1,
  "department_id": 1,
  "amount": 15000.0,
  "sale_date": "2024-01-15",
  "description": "Software license deal"
}
```

**Validaciones**
- `employee_id`, `department_id`: requeridos, enteros > 0
- `amount`: requerido, valor > 0
- `sale_date`: requerido, formato `YYYY-MM-DD`

| Método | Ruta | Descripción | Respuesta |
|---|---|---|---|
| GET | `/sales` | Lista ventas | 200 |
| GET | `/sales/{id}` | Obtiene venta por ID | 200 / 404 |
| POST | `/sales` | Crea venta | 201 / 422 |
| PUT | `/sales/{id}` | Actualización parcial | 200 / 404 |
| DELETE | `/sales/{id}` | Elimina venta | 204 / 404 |

---

### Purchases — `/purchases`

**Modelo de respuesta**
```json
{
  "id": 1,
  "department_id": 1,
  "vendor": "AWS",
  "amount": 9500.0,
  "purchase_date": "2024-01-20",
  "description": "Cloud infrastructure Q1"
}
```

**Validaciones**
- `department_id`: requerido, entero > 0
- `vendor`: requerido, 1–200 caracteres
- `amount`: requerido, valor > 0
- `purchase_date`: requerido, formato `YYYY-MM-DD`

| Método | Ruta | Descripción | Respuesta |
|---|---|---|---|
| GET | `/purchases` | Lista compras | 200 |
| GET | `/purchases/{id}` | Obtiene compra por ID | 200 / 404 |
| POST | `/purchases` | Crea compra | 201 / 422 |
| PUT | `/purchases/{id}` | Actualización parcial | 200 / 404 |
| DELETE | `/purchases/{id}` | Elimina compra | 204 / 404 |

---

### Fiscality — `/fiscality`

**Modelo de respuesta**
```json
{
  "id": 1,
  "department_id": 1,
  "tax_year": 2023,
  "tax_rate": 0.21,
  "taxable_amount": 480000.0,
  "tax_paid": 100800.0,
  "notes": "Corporate tax 2023"
}
```

**Validaciones**
- `department_id`: requerido, entero > 0
- `tax_year`: requerido, entre 2000 y 2100
- `tax_rate`: requerido, entre 0.0 y 1.0 (porcentaje decimal)
- `taxable_amount`, `tax_paid`: requeridos, valor ≥ 0

| Método | Ruta | Descripción | Respuesta |
|---|---|---|---|
| GET | `/fiscality` | Lista registros fiscales | 200 |
| GET | `/fiscality/{id}` | Obtiene registro fiscal por ID | 200 / 404 |
| POST | `/fiscality` | Crea registro fiscal | 201 / 422 |
| PUT | `/fiscality/{id}` | Actualización parcial | 200 / 404 |
| DELETE | `/fiscality/{id}` | Elimina registro fiscal | 204 / 404 |

---

## Tests

### Ejecutar todos los tests con cobertura

```bash
pytest -v
```

### Solo tests unitarios

```bash
pytest tests/test_unit.py -v
```

### Solo tests de integración

```bash
pytest tests/test_integration.py -v
```

### Ver informe de cobertura en HTML

```bash
pytest --cov=app --cov-report=html
# Abre htmlcov/index.html en el navegador
```

### Resultado esperado

```
150 passed in ~5s   |   Cobertura total: 99%
```

### Descripción de los tests

**Tests unitarios** (`test_unit.py`) — prueban la capa CRUD y los schemas de forma aislada:

| Entidad | Clases de test |
|---|---|
| Employee | `TestCrudCreateEmployee`, `TestCrudGetEmployee`, `TestCrudGetEmployees`, `TestCrudUpdateEmployee`, `TestCrudDeleteEmployee`, `TestEmployeeSchemas` |
| Department | `TestCrudCreateDepartment`, `TestCrudGetDepartment`, `TestCrudGetDepartments`, `TestCrudUpdateDepartment`, `TestCrudDeleteDepartment`, `TestDepartmentSchemas` |
| Sale | `TestCrudCreateSale`, `TestCrudGetSale`, `TestCrudGetSales`, `TestCrudUpdateSale`, `TestCrudDeleteSale`, `TestSaleSchemas` |
| Purchase | `TestCrudCreatePurchase`, `TestCrudGetPurchase`, `TestCrudGetPurchases`, `TestCrudUpdatePurchase`, `TestCrudDeletePurchase`, `TestPurchaseSchemas` |
| Fiscality | `TestCrudCreateFiscality`, `TestCrudGetFiscality`, `TestCrudGetFiscalities`, `TestCrudUpdateFiscality`, `TestCrudDeleteFiscality`, `TestFiscalitySchemas` |

**Tests de integración** (`test_integration.py`) — prueban los endpoints HTTP completos:

| Entidad | Clases de test |
|---|---|
| — | `TestRootRedirect` |
| Employee | `TestListEmployees`, `TestGetEmployee`, `TestCreateEmployee`, `TestUpdateEmployee`, `TestDeleteEmployee` |
| Department | `TestListDepartments`, `TestGetDepartment`, `TestCreateDepartment`, `TestUpdateDepartment`, `TestDeleteDepartment` |
| Sale | `TestListSales`, `TestGetSale`, `TestCreateSale`, `TestUpdateSale`, `TestDeleteSale` |
| Purchase | `TestListPurchases`, `TestGetPurchase`, `TestCreatePurchase`, `TestUpdatePurchase`, `TestDeletePurchase` |
| Fiscality | `TestListFiscalities`, `TestGetFiscality`, `TestCreateFiscality`, `TestUpdateFiscality`, `TestDeleteFiscality` |

---

## Pipeline CI/CD

El fichero [`.github/workflows/ci.yml`](.github/workflows/ci.yml) se ejecuta en cada push y pull request a `main` y `develop`.

### Job `test`

```
checkout → setup Python 3.13 → pip install → pytest --cov
```

- Genera `coverage.xml` y `htmlcov/`
- Sube el informe a **Codecov** (requiere secret `CODECOV_TOKEN`)
- Publica el HTML como artefacto de la acción (retención 7 días)
- Umbral mínimo de cobertura: **80%**

---

## Base de datos

La base de datos SQLite se crea automáticamente en `employees.db` al arrancar el servidor.

Los tests usan una base de datos **SQLite en memoria** con `StaticPool` para garantizar aislamiento total entre tests.
