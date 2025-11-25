from extensions import db
from models import Transacciones
from app import create_app
import pandas as pd

app = create_app()

with app.app_context():
    print("Attempting to insert the failing row...")
    try:
        t = Transacciones(
            id_transaccion="DEBUG_FAIL_ROW",
            fecha_digitacion_orden=None,
            fecha_termino_orden=None,
            estado_transaccion="Abierta",
            usuario_creo_orden="TEST_USER",
            entity_code="TEST_ENTITY",
            subcanal=None, # We expect this to be None after cleaning
            tipo_actividad="Activacion",
            razon_servicio="1301 - ACTIVACIONES DE LINEAS",
            telefono="8091234567",
            imei="123456789012345",
            nom_plan="APPS SMALL 200 MIN / 8GB +27GB BONO",
            grupo_activacion_orden="888 - GRUPO 5",
            grupo_activacion_anterior="322 - GRUPO CARD SIM ONLY"
        )
        
        db.session.add(t)
        db.session.commit()
        print("SUCCESS: Inserted failing row!")
        
        # Cleanup
        db.session.delete(t)
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        print(f"FAILED: {e}")

    print("\nAttempting to insert with subcanal='322 - GRUPO CARD SIM ONLY' (Should fail with integer error)...")
    try:
        t = Transacciones(
            id_transaccion="DEBUG_FAIL_ROW_2",
            fecha_digitacion_orden=None,
            fecha_termino_orden=None,
            estado_transaccion="Abierta",
            usuario_creo_orden="TEST_USER",
            entity_code="TEST_ENTITY",
            subcanal="322 - GRUPO CARD SIM ONLY", # This should trigger integer error
            tipo_actividad="Activacion",
            razon_servicio="1301 - ACTIVACIONES DE LINEAS",
            telefono="8091234567",
            imei="123456789012345",
            nom_plan="APPS SMALL 200 MIN / 8GB +27GB BONO",
            grupo_activacion_orden="888 - GRUPO 5",
            grupo_activacion_anterior="322 - GRUPO CARD SIM ONLY"
        )
        
        db.session.add(t)
        db.session.commit()
        print("SUCCESS: Inserted row with string subcanal (Unexpected!)")
        
        # Cleanup
        db.session.delete(t)
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        print(f"FAILED: {e}")
