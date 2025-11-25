import sqlite3
import pandas as pd

DB_PATH = r"C:\Users\Usuario\Documents\DBHeromovil\VentasHeromovil.db"

try:
    conn = sqlite3.connect(DB_PATH)
    
    # Count rows in empleados
    df_emp = pd.read_sql_query("SELECT * FROM empleados", conn)
    print(f"Rows in 'empleados': {len(df_emp)}")
    if not df_emp.empty:
        print("Sample 'empleados':")
        print(df_emp.head())

    # Count rows in usuarios
    df_usr = pd.read_sql_query("SELECT * FROM usuarios", conn)
    print(f"Rows in 'usuarios': {len(df_usr)}")
    
    # Check overlap
    if not df_emp.empty:
        # Assuming 'id' in empleados matches 'codigo' in usuarios?
        # Let's check columns of empleados first
        pass

    conn.close()
except Exception as e:
    print(f"Error: {e}")
