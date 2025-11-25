from extensions import db
from models import Pagos
from app import create_app

app = create_app()

with app.app_context():
    print("Checking userlogin format in pagos table...")
    sample_pagos = Pagos.query.limit(10).all()
    
    if sample_pagos:
        print(f"\nFound {len(sample_pagos)} sample records:")
        for pago in sample_pagos:
            print(f"userlogin: '{pago.userlogin}' (length: {len(pago.userlogin) if pago.userlogin else 0})")
    else:
        print("No pagos found in database")
