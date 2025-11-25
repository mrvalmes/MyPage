import sqlite3
import pandas as pd

DB_PATH = r"C:\Users\Usuario\Documents\DBHeromovil\VentasHeromovil.db"

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # List all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables in SQLite DB:")
    for t in tables:
        print(f"- {t[0]}")
        
    # Check columns for 'usuarios'
    print("\nColumns in 'usuarios':")
    cursor.execute("PRAGMA table_info(usuarios)")
    columns = cursor.fetchall()
    for c in columns:
        print(c)

    conn.close()
except Exception as e:
    print(f"Error: {e}")
