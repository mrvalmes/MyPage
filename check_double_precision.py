from extensions import db
from app import create_app
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("=== Checking for DOUBLE PRECISION columns in transacciones ===\n")
    
    result = db.session.execute(db.text("""
        SELECT column_name, data_type, udt_name 
        FROM information_schema.columns 
        WHERE table_name = 'transacciones' 
        AND data_type = 'double precision'
    """))
    
    double_cols = result.fetchall()
    
    if double_cols:
        print("Found DOUBLE PRECISION columns:")
        for row in double_cols:
            print(f"  - {row[0]}: {row[1]} ({row[2]})")
    else:
        print("No DOUBLE PRECISION columns found in transacciones table")
    
    print("\n=== All numeric-type columns ===\n")
    result2 = db.session.execute(db.text("""
        SELECT column_name, data_type, udt_name 
        FROM information_schema.columns 
        WHERE table_name = 'transacciones' 
        AND data_type IN ('integer', 'bigint', 'smallint', 'numeric', 'real', 'double precision')
    """))
    
    for row in result2:
        print(f"  - {row[0]}: {row[1]} ({row[2]})")
