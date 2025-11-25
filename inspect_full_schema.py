from extensions import db
from app import create_app
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("--- Columns in 'transacciones' ---")
    result = db.session.execute(db.text("""
        SELECT column_name, data_type, udt_name 
        FROM information_schema.columns 
        WHERE table_name = 'transacciones'
    """))
    for row in result:
        print(f"{row[0]}: {row[1]} ({row[2]})")

    print("\n--- Triggers on 'transacciones' ---")
    result = db.session.execute(db.text("""
        SELECT tgname, tgtype, proname 
        FROM pg_trigger t
        JOIN pg_proc p ON t.tgfoid = p.oid
        WHERE tgrelid = 'transacciones'::regclass
    """))
    for row in result:
        print(f"Trigger: {row[0]}, Function: {row[2]}")

    print("\n--- Rules on 'transacciones' ---")
    result = db.session.execute(db.text("SELECT * FROM pg_rules WHERE tablename = 'transacciones'"))
    for row in result:
        print(row)

    print(f"\nDB URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
