"""Seed script to populate the employees table with sample data."""
from app.database import SessionLocal, engine
from app.models import Base, Employee

Base.metadata.create_all(bind=engine)

EMPLOYEES = [
    Employee(name="Alice",   surname="Johnson",   department="Engineering",  salary=72000.0),
    Employee(name="Bob",     surname="Smith",     department="Engineering",  salary=68000.0),
    Employee(name="Carol",   surname="Williams",  department="HR",           salary=48000.0),
    Employee(name="David",   surname="Brown",     department="HR",           salary=45000.0),
    Employee(name="Eva",     surname="Martinez",  department="Finance",      salary=61000.0),
    Employee(name="Frank",   surname="Garcia",    department="Finance",      salary=59000.0),
    Employee(name="Grace",   surname="Lee",       department="Marketing",    salary=53000.0),
    Employee(name="Henry",   surname="Wilson",    department="Marketing",    salary=51000.0),
    Employee(name="Irene",   surname="Taylor",    department="Management",   salary=95000.0),
    Employee(name="James",   surname="Anderson",  department="Management",   salary=91000.0),
]

db = SessionLocal()
try:
    db.add_all(EMPLOYEES)
    db.commit()
    print(f"OK: {len(EMPLOYEES)} employees inserted successfully.")
finally:
    db.close()
