import sqlite3
import pandas as pd
from app import create_app, db
from models import (
    UsuariosLogin, Sesiones, Usuarios, Transacciones, 
    VentasDetalle, Pagos, Objetivos, Incentivos, Localidades, 
    TiposVenta
)
from sqlalchemy.exc import IntegrityError

# --- Configuración ---
SQLITE_DB_PATH = r"C:\Users\Usuario\Documents\DBHeromovil\VentasHeromovil.db"
app = create_app()

def migrate_table(sqlite_conn, table_name, model, column_mapping=None, pre_process_df=None):
    """
    Función genérica para migrar una tabla de SQLite a PostgreSQL.
    """
    print(f"--- Iniciando migración de la tabla '{table_name}' ---")
    try:
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", sqlite_conn)
        print(f"Se encontraron {len(df)} registros en la tabla '{table_name}' de SQLite.")

        if df.empty:
            print("La tabla está vacía, no hay nada que migrar.")
            return
            
        if pre_process_df:
            df = pre_process_df(df)

        if column_mapping:
            df.rename(columns=column_mapping, inplace=True)

        model_columns = [c.key for c in model.__table__.columns]
        df_columns = df.columns.tolist()
        
        df_filtered = df[[col for col in df_columns if col in model_columns]]

        registros = df_filtered.to_dict(orient='records')

        if registros:
            db.session.bulk_insert_mappings(model, registros)
            db.session.commit()
            print(f"¡Éxito! Se migraron {len(registros)} registros a la tabla '{model.__tablename__}'.")
        else:
            print("No hay registros para migrar después del filtrado.")

    except IntegrityError as e:
        db.session.rollback()
        print(f"Error de integridad en tabla '{table_name}': Es posible que los datos ya existan o haya una clave foránea incorrecta. {e}")
    except Exception as e:
        db.session.rollback()
        print(f"Ocurrió un error inesperado al migrar la tabla '{table_name}': {e}")


def run_migration():
    """
    Orquesta la migración completa.
    """
    try:
        sqlite_conn = sqlite3.connect(SQLITE_DB_PATH)
        print(f"Conexión a SQLite en '{SQLITE_DB_PATH}' exitosa.")
    except Exception as e:
        print(f"No se pudo conectar a la base de datos SQLite. Verifica la ruta. Error: {e}")
        return

    with app.app_context():
        print("\nADVERTENCIA: Se borrarán y recrearán todas las tablas en PostgreSQL.")
        confirm = input("¿Estás seguro de que quieres continuar? Esta acción es irreversible. (s/N): ")
        if confirm.lower() != 's':
            print("Migración cancelada por el usuario.")
            sqlite_conn.close()
            return
            
        try:
            print("Recreando esquema de base de datos (DROP ALL / CREATE ALL)...")
            db.drop_all()
            db.create_all()
            print("Tablas recreadas correctamente.")
        except Exception as e:
            db.session.rollback()
            print(f"Error al recrear las tablas: {e}")
            sqlite_conn.close()
            return

        # --- Ejecución de la migración tabla por tabla ---
        # 1. UsuariosLogin (Autenticación)
        migrate_table(sqlite_conn, 'usuariosligin', UsuariosLogin)
        
        # 2. Usuarios (Información de Empleados)
        # Aseguramos que el código sea string
        def process_usuarios(df):
            df['codigo'] = df['codigo'].astype(str)
            return df
        migrate_table(sqlite_conn, 'usuarios', Usuarios, pre_process_df=process_usuarios)

        # 3. Tablas auxiliares
        migrate_table(sqlite_conn, 'localidades', Localidades)
        migrate_table(sqlite_conn, 'tipos_venta', TiposVenta)
        
        # 4. Tablas transaccionales
        migrate_table(sqlite_conn, 'transacciones', Transacciones)
        migrate_table(sqlite_conn, 'pagos', Pagos)
        
        # 5. Objetivos (Cuidado con FK a usuarios.codigo)
        def process_objetivos(df):
            df['id_empleado'] = df['id_empleado'].astype(str)
            return df
        migrate_table(sqlite_conn, 'objetivos', Objetivos, pre_process_df=process_objetivos)
        
        migrate_table(sqlite_conn, 'incentivosEmpleados', Incentivos)
        migrate_table(sqlite_conn, 'ventas_detalle', VentasDetalle)

        db.session.commit()
        print("\n--- MIGRACIÓN DE DATOS FINALIZADA ---")

    sqlite_conn.close()

if __name__ == '__main__':
    run_migration()