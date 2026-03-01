# Employees API

REST API para gestión de empleados construida con **FastAPI**, **SQLAlchemy** y **SQLite**.

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
│   ├── models.py            # Modelo ORM Employee
│   ├── schemas.py           # Schemas Pydantic (Create / Update / Response)
│   ├── crud.py              # Operaciones CRUD
│   └── main.py              # Aplicación FastAPI y endpoints
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Fixtures compartidos (BD en memoria + TestClient)
│   ├── test_unit.py         # Tests unitarios de CRUD y schemas
│   └── test_integration.py  # Tests de integración de endpoints HTTP
├── .github/
│   └── workflows/
│       └── ci.yml           # Pipeline CI: tests + cobertura + lint
├── seed.py                  # Script para poblar la BD con datos de ejemplo
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

### Arrancar el servidor

```bash
uvicorn app.main:app --reload
```

El servidor arranca en `http://localhost:8000`.
La ruta raíz `/` redirige automáticamente al **Swagger UI** en `/docs`.

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

Inserta 10 empleados de ejemplo en distintos departamentos.

---

## API Reference

### Modelo de datos

```json
{
  "id":         1,
  "name":       "Alice",
  "surname":    "Johnson",
  "department": "Engineering",
  "salary":     72000.0
}
```

### Endpoints

#### `GET /employees`

Lista todos los empleados. Soporta paginación.

**Query params**

| Parámetro | Tipo | Default | Descripción |
|---|---|---|---|
| `skip` | int | 0 | Registros a saltar |
| `limit` | int | 100 | Máximo de registros devueltos |

**Respuesta `200 OK`**
```json
[
  { "id": 1, "name": "Alice", "surname": "Johnson", "department": "Engineering", "salary": 72000.0 },
  { "id": 2, "name": "Bob",   "surname": "Smith",   "department": "Engineering", "salary": 68000.0 }
]
```

---

#### `GET /employees/{id}`

Obtiene un empleado por su ID.

**Respuesta `200 OK`**
```json
{ "id": 1, "name": "Alice", "surname": "Johnson", "department": "Engineering", "salary": 72000.0 }
```

**Respuesta `404 Not Found`**
```json
{ "detail": "Employee not found" }
```

---

#### `POST /employees`

Crea un nuevo empleado.

**Body**
```json
{
  "name":       "Laura",
  "surname":    "Perez",
  "department": "Engineering",
  "salary":     65000.0
}
```

**Validaciones**
- `name`, `surname`, `department`: requeridos, entre 1 y 100 caracteres
- `salary`: requerido, valor mayor que 0

**Respuesta `201 Created`**
```json
{ "id": 11, "name": "Laura", "surname": "Perez", "department": "Engineering", "salary": 65000.0 }
```

---

#### `PUT /employees/{id}`

Actualiza un empleado existente. Todos los campos son opcionales (actualización parcial).

**Body** (cualquier combinación de campos)
```json
{
  "salary":     70000.0,
  "department": "Management"
}
```

**Respuesta `200 OK`**
```json
{ "id": 11, "name": "Laura", "surname": "Perez", "department": "Management", "salary": 70000.0 }
```

**Respuesta `404 Not Found`**
```json
{ "detail": "Employee not found" }
```

---

#### `DELETE /employees/{id}`

Elimina un empleado por su ID.

**Respuesta `204 No Content`** — sin cuerpo

**Respuesta `404 Not Found`**
```json
{ "detail": "Employee not found" }
```

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
33 passed in ~1s   |   Cobertura total: 96%
```

#### Descripción de los tests

**Tests unitarios** (`test_unit.py`) — prueban la capa de datos de forma aislada:

| Clase | Tests |
|---|---|
| `TestCrudCreateEmployee` | Creación con campos correctos, IDs únicos |
| `TestCrudGetEmployee` | Obtener por ID existente y no existente |
| `TestCrudGetEmployees` | Listar todos, lista vacía, paginación |
| `TestCrudUpdateEmployee` | Actualización parcial y total, ID no existente |
| `TestCrudDeleteEmployee` | Borrado exitoso, ID no existente |
| `TestSchemas` | Validaciones de Pydantic (campos vacíos, salario negativo) |

**Tests de integración** (`test_integration.py`) — prueban los endpoints HTTP completos:

| Clase | Tests |
|---|---|
| `TestRootRedirect` | Redirección `/` → `/docs` |
| `TestListEmployees` | Lista vacía, con datos, paginación |
| `TestGetEmployee` | Por ID, 404 |
| `TestCreateEmployee` | Creación exitosa, 422 por campos inválidos |
| `TestUpdateEmployee` | Actualización parcial, 404 |
| `TestDeleteEmployee` | Borrado, verificación posterior, 404 |

---

## Pipeline CI/CD

El fichero [`.github/workflows/ci.yml`](.github/workflows/ci.yml) define dos jobs que se ejecutan en cada push y pull request a `main` y `develop`.

### Job `test`

```
checkout → setup Python 3.13 → pip install → pytest --cov
```

- Genera `coverage.xml` y `htmlcov/`
- Sube el informe a **Codecov** (requiere secret `CODECOV_TOKEN`)
- Publica el HTML como artefacto de la acción (retención 7 días)
- Umbral mínimo de cobertura: **80%**

### Job `lint`

```
checkout → setup Python 3.13 → pip install ruff → ruff check + ruff format --check
```

- Comprueba estilo y formato con **ruff**

### Añadir badge de cobertura

Una vez configurado Codecov, añade al README:

```markdown
[![Coverage](https://codecov.io/gh/<usuario>/<repo>/branch/main/graph/badge.svg)](https://codecov.io/gh/<usuario>/<repo>)
```

---

## Base de datos

La base de datos SQLite se crea automáticamente en `employees.db` al arrancar el servidor.

### Esquema

```sql
CREATE TABLE employees (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       VARCHAR(100) NOT NULL,
    surname    VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    salary     FLOAT        NOT NULL
);
```

### Estrategia de tests

Los tests usan una base de datos **SQLite en memoria** con `StaticPool` para garantizar que todas las conexiones comparten el mismo estado. La BD se crea antes de cada test y se elimina al terminar, asegurando aislamiento total entre tests.
