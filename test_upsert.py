from extensions import db
from app import create_app
import pandas as pd
import gestiondata

app = create_app()

with app.app_context():
    print("=== Testing guardar_transacciones_db with nom_plan_anterior ===\n")
    
    # Create test DataFrame with nom_plan_anterior (como viene de procesar_dataframe_ventas)
    test_data = {
        'id_transaccion': ['TEST_UPSERT_001', 'TEST_UPSERT_002'],
        'fecha_digitacion_orden': [pd.Timestamp('2025-11-22'), pd.Timestamp('2025-11-22')],
        'fecha_termino_orden': [pd.NaT, pd.NaT],
        'estado_transaccion': ['Abierta', 'Abierta'],
        'usuario_creo_orden': ['1004203 - TEST USER', '1004208 - TEST USER 2'],
        'entity_code': ['TEST', 'TEST'],
        'subcanal': [pd.NA, pd.NA],
        'tipo_actividad': ['Activacion', 'Activacion'],
        'razon_servicio': ['1301 - TEST', '1302 - TEST'],
        'telefono': ['8091111111', '8092222222'],
        'imei': ['111111111111111', '222222222222222'],
        'nom_plan': ['TEST PLAN 1', 'TEST PLAN 2'],
        'nom_plan_anterior': ['OLD PLAN 1', 'OLD PLAN 2'],  # Esta columna debe ser eliminada
        'grupo_activacion_orden': ['888 - GRUPO 5', '889 - GRUPO 6'],
        'grupo_activacion_anterior': ['322 - GRUPO CARD SIM ONLY', '4 - CARD']
    }
    
    df = pd.DataFrame(test_data)
    
    print("DataFrame columns BEFORE guardar_transacciones_db:")
    print(df.columns.tolist())
    print(f"\nnom_plan_anterior present: {'nom_plan_anterior' in df.columns}")
    
    try:
        # Call the function
        gestiondata.guardar_transacciones_db(df)
        print("\n✓ SUCCESS! Data inserted/updated")
        
        # Verify the data was inserted
        from models import Transacciones
        result = Transacciones.query.filter(
            Transacciones.id_transaccion.in_(['TEST_UPSERT_001', 'TEST_UPSERT_002'])
        ).all()
        
        print(f"\nVerification: Found {len(result)} records in database")
        for r in result:
            print(f"  - {r.id_transaccion}: estado={r.estado_transaccion}, subcanal={r.subcanal}")
        
        # Cleanup
        for r in result:
            db.session.delete(r)
        db.session.commit()
        print("\n✓ Cleanup completed")
        
    except Exception as e:
        print(f"\n✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
