from app import create_app
from extensions import db
from models import Transacciones
from datetime import date

app = create_app()

with app.app_context():
    try:
        print("Attempting to insert a test transaction...")
        t = Transacciones(
            id_transaccion="TEST-RANDOM-" + str(date.today()),
            fecha_digitacion_orden=date.today(),
            fecha_termino_orden=date.today(),
            estado_transaccion="Test",
            usuario_creo_orden="Tester",
            entity_code="E123",
            subcanal="322 - GRUPO CARD SIM ONLY", # Testing this
            tipo_actividad="Act",
            razon_servicio="Razon",
            telefono="1234567890",
            imei="123456789012345",
            nom_plan="SMALL 200 MIN / 8GB +27GB BONO",
            grupo_activacion_orden="888 - GRUPO S",
            grupo_activacion_anterior="322 - GRUPO CARD SIM ONLY"
        )
        db.session.add(t)
        db.session.commit()
        print("Insertion successful!")
        
        # Clean up
        db.session.delete(t)
        db.session.commit()
        print("Cleanup successful!")
        
    except Exception as e:
        print("Insertion failed!")
        print(e)
        import traceback
        traceback.print_exc()
