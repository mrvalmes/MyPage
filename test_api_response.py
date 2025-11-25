from extensions import db
from app import create_app
from blueprints.api import api_bp
from flask import Flask
import json

app = create_app()

with app.app_context():
    print("=== Probando endpoint /api/top_ventas_cc ===\n")
    
    # Simular la llamada al endpoint
    with app.test_client() as client:
        # Necesitamos autenticarnos primero
        # Por ahora, vamos a probar directamente la función
        from services.report_service import get_rank_pav_cc
        
        results = get_rank_pav_cc()
        
        # Simular el formato que devuelve el endpoint
        formatted_data = [{"nombre": row.usuario_creo_orden, "total_pav": row.total_ventas} for row in results]
        
        print("Formato JSON que devuelve el endpoint:")
        print(json.dumps(formatted_data, indent=2, ensure_ascii=False))
        
        print(f"\nTotal de registros: {len(formatted_data)}")
        
        if formatted_data:
            print("\nPrimer registro:")
            print(f"  nombre: {formatted_data[0]['nombre']}")
            print(f"  total_pav: {formatted_data[0]['total_pav']}")
            print(f"  tipo de total_pav: {type(formatted_data[0]['total_pav'])}")
