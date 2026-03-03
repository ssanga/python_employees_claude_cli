from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app import models
from app.database import engine
from app.routers import departments, employees, fiscality, purchases, sales

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Employees API",
    description="REST API for managing employees, departments, sales, purchases, and fiscality",
    version="2.0.0",
)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


app.include_router(employees.router)
app.include_router(departments.router)
app.include_router(sales.router)
app.include_router(purchases.router)
app.include_router(fiscality.router)
