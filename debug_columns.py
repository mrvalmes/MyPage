import os
from extensions import db
from models import Transacciones
from app import create_app
from sqlalchemy import text

app = create_app()

def test_insert_column(column_name, value):
    print(f"Testing insertion of '{value}' into column '{column_name}'...")
    try:
        # Create a dummy transaction with valid defaults
        t = Transacciones(
            id_transaccion="TEST_DEBUG",
            fecha_digitacion_orden=None,
            fecha_termino_orden=None,
            estado_transaccion="TEST",
            usuario_creo_orden="TEST",
            entity_code="TEST",
            subcanal=None,
            tipo_actividad="TEST",
            razon_servicio="TEST",
            telefono="8090000000",
            imei="000000000000000",
            nom_plan="TEST",
            grupo_activacion_orden="TEST",
            grupo_activacion_anterior="TEST"
        )
        
        # Set the target column to the test value
        setattr(t, column_name, value)
        
        db.session.add(t)
        db.session.commit()
        print(f"SUCCESS: Inserted into {column_name}")
        
        # Cleanup
        db.session.delete(t)
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        print(f"FAILED: {e}")
        # Check if error message matches
        if "double precision" in str(e):
            print(f"!!! FOUND IT: Column '{column_name}' caused the 'double precision' error !!!")

with app.app_context():
    columns = [
        'id_transaccion', 'fecha_digitacion_orden', 'fecha_termino_orden',
        'estado_transaccion', 'usuario_creo_orden', 'entity_code',
        'subcanal', 'tipo_actividad', 'razon_servicio', 'telefono',
        'imei', 'nom_plan', 'grupo_activacion_orden', 'grupo_activacion_anterior'
    ]
    
    test_value = "322 - GRUPO CARD SIM ONLY"
    
    for col in columns:
        test_insert_column(col, test_value)
