from app import create_app
from extensions import db
from sqlalchemy import inspect

app = create_app()

with app.app_context():
    print("All columns in 'transacciones' from information_schema:")
    result = db.session.execute(db.text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'transacciones'"))
    for row in result:
        print(f"- {row[0]}: {row[1]}")
