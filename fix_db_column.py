from app import create_app
from extensions import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        # Intentar agregar la columna
        with db.engine.connect() as conn:
            # Determinar el dialecto
            dialect = db.engine.dialect.name
            print(f"Dialecto de base de datos: {dialect}")
            
            if dialect == 'postgresql':
                conn.execute(text("ALTER TABLE usuariosligin ADD COLUMN IF NOT EXISTS force_password_change BOOLEAN DEFAULT FALSE NOT NULL"))
                conn.commit()
                print("Columna agregada exitosamente (PostgreSQL).")
            else:
                # SQLite
                # Primero verificar si la columna ya existe
                result = conn.execute(text("PRAGMA table_info(usuariosligin)"))
                columns = [row[1] for row in result]
                
                if 'force_password_change' not in columns:
                    conn.execute(text("ALTER TABLE usuariosligin ADD COLUMN force_password_change INTEGER DEFAULT 0 NOT NULL"))
                    conn.commit()
                    print("Columna agregada exitosamente (SQLite).")
                else:
                    print("La columna ya existe.")
                
    except Exception as e:
        print(f"Error: {e}")
