from app import create_app
from extensions import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        # Check if column exists
        with db.engine.connect() as conn:
            # Try to select the column to see if it exists
            try:
                conn.execute(text("SELECT force_password_change FROM usuariosligin LIMIT 1"))
                print("Column 'force_password_change' already exists.")
            except Exception:
                print("Column does not exist. Adding it...")
                # Determine dialect
                dialect = db.engine.dialect.name
                print(f"Database dialect: {dialect}")
                
                if dialect == 'postgresql':
                    conn.execute(text("ALTER TABLE usuariosligin ADD COLUMN force_password_change BOOLEAN DEFAULT FALSE"))
                else:
                    # SQLite or others
                    conn.execute(text("ALTER TABLE usuariosligin ADD COLUMN force_password_change BOOLEAN DEFAULT 0"))
                
                conn.commit()
                print("Column added successfully.")
                
    except Exception as e:
        print(f"An error occurred: {e}")
