from extensions import db
from app import create_app
from services.report_service import get_rank_pav_cc

app = create_app()

with app.app_context():
    print("=== Probando get_rank_pav_cc ===\n")
    
    try:
        results = get_rank_pav_cc()
        
        print(f"Total de resultados: {len(results)}")
        print("\nResultados:")
        
        if results:
            for i, row in enumerate(results, 1):
                print(f"{i}. Usuario: {row.usuario_creo_orden}, Total Ventas: {row.total_ventas}")
        else:
            print("No se encontraron resultados.")
            
        # Verificar si hay datos en ventas_detalle para noviembre 2025
        from models import VentasDetalle
        from sqlalchemy import extract, func
        from datetime import datetime
        
        now = datetime.now()
        
        print(f"\n=== Verificando datos en ventas_detalle ===")
        print(f"Mes actual: {now.month}/{now.year}")
        
        # Total de registros en noviembre 2025
        total_count = db.session.query(VentasDetalle).filter(
            extract('year', VentasDetalle.fecha) == now.year,
            extract('month', VentasDetalle.fecha) == now.month
        ).count()
        print(f"Total registros en ventas_detalle (nov 2025): {total_count}")
        
        # Registros excluyendo Card
        no_card_count = db.session.query(VentasDetalle).filter(
            VentasDetalle.tipo_venta != 'Card',
            extract('year', VentasDetalle.fecha) == now.year,
            extract('month', VentasDetalle.fecha) == now.month
        ).count()
        print(f"Registros sin 'Card': {no_card_count}")
        
        # Registros excluyendo entity_code 44066
        no_44066_count = db.session.query(VentasDetalle).filter(
            VentasDetalle.tipo_venta != 'Card',
            VentasDetalle.entity_code != '44066',
            extract('year', VentasDetalle.fecha) == now.year,
            extract('month', VentasDetalle.fecha) == now.month
        ).count()
        print(f"Registros sin entity_code '44066': {no_44066_count}")
        
        # Ver algunos entity_code únicos
        entity_codes = db.session.query(VentasDetalle.entity_code).filter(
            extract('year', VentasDetalle.fecha) == now.year,
            extract('month', VentasDetalle.fecha) == now.month
        ).distinct().limit(10).all()
        print(f"\nAlgunos entity_code únicos: {[e[0] for e in entity_codes]}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
