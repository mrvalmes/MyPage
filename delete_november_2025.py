from extensions import db
from models import Pagos
from app import create_app
from sqlalchemy import extract

app = create_app()

with app.app_context():
    print("=== Eliminando PAGOS de Noviembre 2025 ===\n")
    
    # 1. Contar registros antes de eliminar
    print("Contando registros antes de eliminar...")
    pagos_count = db.session.query(Pagos).filter(
        extract('year', db.func.cast(Pagos.dte, db.Date)) == 2025,
        extract('month', db.func.cast(Pagos.dte, db.Date)) == 11
    ).count()
    
    print(f"Pagos (noviembre 2025): {pagos_count}")
    
    # 2. Confirmar antes de eliminar
    if pagos_count == 0:
        print("\n✓ No hay registros de pagos para eliminar.")
    else:
        respuesta = input(f"\n¿Desea eliminar {pagos_count} registros de pagos? (escriba 'SI' para confirmar): ")
        
        if respuesta.strip().upper() == 'SI':
            print("\nEliminando registros de pagos...")
            
            deleted = db.session.query(Pagos).filter(
                extract('year', db.func.cast(Pagos.dte, db.Date)) == 2025,
                extract('month', db.func.cast(Pagos.dte, db.Date)) == 11
            ).delete(synchronize_session=False)
            
            # Commit
            db.session.commit()
            print(f"✓ Eliminados {deleted} registros de pagos")
            print("\n✓✓✓ Eliminación completada exitosamente")
            
            # Verificar
            print("\nVerificando...")
            pagos_after = db.session.query(Pagos).filter(
                extract('year', db.func.cast(Pagos.dte, db.Date)) == 2025,
                extract('month', db.func.cast(Pagos.dte, db.Date)) == 11
            ).count()
            print(f"Pagos restantes (noviembre 2025): {pagos_after}")
            
        else:
            print("\n✗ Eliminación cancelada por el usuario")

