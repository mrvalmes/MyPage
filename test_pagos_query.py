from extensions import db
from models import Pagos
from app import create_app
from sqlalchemy import func, extract, cast
from datetime import datetime

app = create_app()

with app.app_context():
    empleado_id = "1004203"  # Sample employee ID from the data
    now = datetime.now()
    
    print(f"Testing query for empleado_id: {empleado_id}")
    print(f"Current month/year: {now.month}/{now.year}\n")
    
    # Test the query used in get_total_pagos
    query = db.session.query(func.count(Pagos.id)).filter(
        extract('year', cast(Pagos.dte, db.Date)) == now.year,
        extract('month', cast(Pagos.dte, db.Date)) == now.month,
        func.substr(Pagos.userlogin, 1, 7) == empleado_id
    )
    
    result = query.scalar()
    print(f"Result with substr filter: {result}")
    
    # Also test without the employee filter to see total
    query_total = db.session.query(func.count(Pagos.id)).filter(
        extract('year', cast(Pagos.dte, db.Date)) == now.year,
        extract('month', cast(Pagos.dte, db.Date)) == now.month
    )
    
    result_total = query_total.scalar()
    print(f"Total pagos this month: {result_total}")
    
    # Check if there are any pagos with this userlogin prefix
    sample_query = db.session.query(Pagos).filter(
        func.substr(Pagos.userlogin, 1, 7) == empleado_id
    ).limit(5)
    
    samples = sample_query.all()
    print(f"\nSample pagos for {empleado_id}:")
    for pago in samples:
        print(f"  - userlogin: {pago.userlogin}, dte: {pago.dte}")
