import sys
from app import create_app, db
# Importa todos los modelos para que SQLAlchemy los conozca
from models import Usuarios, Sesiones, Transacciones, VentasDetalle, Pagos, Objetivos

# Crea una instancia de la aplicación para tener el contexto correcto
app = create_app()

def db_create_all():
    """Crea todas las tablas de la base de datos."""
    # 'app_context' asegura que la aplicación esté configurada correctamente,
    # especialmente la URI de la base de datos.
    with app.app_context():
        print("Creando todas las tablas en la base de datos...")
        try:
            db.create_all()
            print("Tablas creadas exitosamente.")
        except Exception as e:
            print(f"Error al crear las tablas: {e}")

def db_drop_all():
    """Elimina todas las tablas de la base de datos. ¡CUIDADO!"""
    with app.app_context():
        confirm = input("¿Estás seguro de que quieres borrar TODAS las tablas? Esto es irreversible. (s/N): ")
        if confirm.lower() == 's':
            print("Eliminando todas las tablas...")
            try:
                db.drop_all()
                print("Tablas eliminadas exitosamente.")
            except Exception as e:
                print(f"Error al eliminar las tablas: {e}")
        else:
            print("Operación cancelada.")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'db_create_all':
            db_create_all()
        elif command == 'db_drop_all':
            db_drop_all()
        else:
            print(f"Comando desconocido: {command}")
            print("Comandos disponibles: db_create_all, db_drop_all")
    else:
        print("Por favor, proporciona un comando.")
        print("Comandos disponibles: db_create_all, db_drop_all")
