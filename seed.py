"""Seed script to populate all tables with sample data."""
import datetime

from app.database import SessionLocal, engine
from app.models import Base, Department, Employee, Fiscality, Purchase, Sale

Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # 1. Departments
    departments = [
        Department(name="Engineering", description="Software & infrastructure", budget=500000.0),
        Department(name="HR", description="Human resources", budget=120000.0),
        Department(name="Finance", description="Accounting & finance", budget=200000.0),
        Department(name="Marketing", description="Sales & marketing", budget=180000.0),
        Department(name="Management", description="Executive management", budget=350000.0),
    ]
    db.add_all(departments)
    db.commit()
    for d in departments:
        db.refresh(d)

    dept = {d.name: d.id for d in departments}

    # 2. Employees
    employees = [
        Employee(name="Alice", surname="Johnson", department_id=dept["Engineering"], salary=72000.0),
        Employee(name="Bob", surname="Smith", department_id=dept["Engineering"], salary=68000.0),
        Employee(name="Carol", surname="Williams", department_id=dept["HR"], salary=48000.0),
        Employee(name="David", surname="Brown", department_id=dept["HR"], salary=45000.0),
        Employee(name="Eva", surname="Martinez", department_id=dept["Finance"], salary=61000.0),
        Employee(name="Frank", surname="Garcia", department_id=dept["Finance"], salary=59000.0),
        Employee(name="Grace", surname="Lee", department_id=dept["Marketing"], salary=53000.0),
        Employee(name="Henry", surname="Wilson", department_id=dept["Marketing"], salary=51000.0),
        Employee(name="Irene", surname="Taylor", department_id=dept["Management"], salary=95000.0),
        Employee(name="James", surname="Anderson", department_id=dept["Management"], salary=91000.0),
    ]
    db.add_all(employees)
    db.commit()
    for e in employees:
        db.refresh(e)

    emp = {e.name: e.id for e in employees}

    # 3. Sales
    sales = [
        Sale(
            employee_id=emp["Alice"],
            department_id=dept["Engineering"],
            amount=15000.0,
            sale_date=datetime.date(2024, 1, 15),
            description="Software license deal",
        ),
        Sale(
            employee_id=emp["Bob"],
            department_id=dept["Engineering"],
            amount=22000.0,
            sale_date=datetime.date(2024, 2, 10),
            description="Cloud migration contract",
        ),
        Sale(
            employee_id=emp["Grace"],
            department_id=dept["Marketing"],
            amount=8500.0,
            sale_date=datetime.date(2024, 3, 5),
            description="Ad campaign package",
        ),
        Sale(
            employee_id=emp["Henry"],
            department_id=dept["Marketing"],
            amount=12000.0,
            sale_date=datetime.date(2024, 3, 20),
            description="Social media campaign",
        ),
        Sale(
            employee_id=emp["Eva"],
            department_id=dept["Finance"],
            amount=5000.0,
            sale_date=datetime.date(2024, 4, 1),
            description="Consulting services",
        ),
    ]
    db.add_all(sales)
    db.commit()

    # 4. Purchases
    purchases = [
        Purchase(
            department_id=dept["Engineering"],
            vendor="AWS",
            amount=9500.0,
            purchase_date=datetime.date(2024, 1, 20),
            description="Cloud infrastructure Q1",
        ),
        Purchase(
            department_id=dept["Engineering"],
            vendor="JetBrains",
            amount=1200.0,
            purchase_date=datetime.date(2024, 2, 1),
            description="IDE licenses",
        ),
        Purchase(
            department_id=dept["HR"],
            vendor="LinkedIn",
            amount=3500.0,
            purchase_date=datetime.date(2024, 1, 10),
            description="Recruiting platform",
        ),
        Purchase(
            department_id=dept["Marketing"],
            vendor="HubSpot",
            amount=4800.0,
            purchase_date=datetime.date(2024, 2, 14),
            description="CRM subscription",
        ),
        Purchase(
            department_id=dept["Finance"],
            vendor="QuickBooks",
            amount=1800.0,
            purchase_date=datetime.date(2024, 3, 1),
            description="Accounting software",
        ),
    ]
    db.add_all(purchases)
    db.commit()

    # 5. Fiscality
    fiscalities = [
        Fiscality(
            department_id=dept["Engineering"],
            tax_year=2023,
            tax_rate=0.21,
            taxable_amount=480000.0,
            tax_paid=100800.0,
            notes="Corporate tax 2023",
        ),
        Fiscality(
            department_id=dept["Finance"],
            tax_year=2023,
            tax_rate=0.21,
            taxable_amount=190000.0,
            tax_paid=39900.0,
            notes="Corporate tax 2023",
        ),
        Fiscality(
            department_id=dept["Marketing"],
            tax_year=2023,
            tax_rate=0.21,
            taxable_amount=165000.0,
            tax_paid=34650.0,
            notes="Corporate tax 2023",
        ),
        Fiscality(
            department_id=dept["HR"],
            tax_year=2023,
            tax_rate=0.21,
            taxable_amount=110000.0,
            tax_paid=23100.0,
            notes="Corporate tax 2023",
        ),
        Fiscality(
            department_id=dept["Management"],
            tax_year=2023,
            tax_rate=0.25,
            taxable_amount=330000.0,
            tax_paid=82500.0,
            notes="Management tier tax 2023",
        ),
    ]
    db.add_all(fiscalities)
    db.commit()

    print("OK: All tables seeded successfully.")
    print(f"  {len(departments)} departments")
    print(f"  {len(employees)} employees")
    print(f"  {len(sales)} sales")
    print(f"  {len(purchases)} purchases")
    print(f"  {len(fiscalities)} fiscality records")
finally:
    db.close()
