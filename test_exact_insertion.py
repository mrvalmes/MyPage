from extensions import db
from models import Transacciones
from app import create_app
import pandas as pd

app = create_app()

with app.app_context():
    print("=== Testing insertion with problematic values ===\n")
    
    # Create a test dataframe similar to what gestiondata.py would produce
    test_data = {
        'id_transaccion': ['TEST_001'],
        'fecha_digitacion_orden': [pd.NaT],
        'fecha_termino_orden': [pd.NaT],
        'estado_transaccion': ['Abierta'],
        'usuario_creo_orden': ['1004203 - TEST USER'],
        'entity_code': ['TEST'],
        'subcanal': [pd.NA],  # This should become None
        'tipo_actividad': ['Activacion'],
        'razon_servicio': ['1301 - ACTIVACIONES DE LINEAS'],
        'telefono': ['8091234567'],
        'imei': ['123456789012345'],
        'nom_plan': ['APPS SMALL 200 MIN / 8GB +27GB BONO'],
        'grupo_activacion_orden': ['888 - GRUPO 5'],
        'grupo_activacion_anterior': ['322 - GRUPO CARD SIM ONLY']
    }
    
    df = pd.DataFrame(test_data)
    
    print("DataFrame created:")
    print(df)
    print(f"\nsubcanal type: {df['subcanal'].dtype}")
    print(f"subcanal value: {df['subcanal'].iloc[0]}")
    
    # Apply the same transformations as in guardar_transacciones_db
    df['fecha_digitacion_orden'] = df['fecha_digitacion_orden'].replace({pd.NaT: None})
    df['fecha_termino_orden'] = df['fecha_termino_orden'].replace({pd.NaT: None})
    
    if 'subcanal' in df.columns:
        df['subcanal'] = df['subcanal'].astype(object).where(pd.notnull(df['subcanal']), None)
    
    print(f"\nAfter transformation:")
    print(f"subcanal type: {type(df['subcanal'].iloc[0])}")
    print(f"subcanal value: {df['subcanal'].iloc[0]}")
    
    # Try to insert
    try:
        for index, row in df.iterrows():
            print(f"\nInserting row {index}...")
            print(f"  subcanal: {row['subcanal']} (type: {type(row['subcanal'])})")
            
            t = Transacciones(
                id_transaccion=row['id_transaccion'],
                fecha_digitacion_orden=row['fecha_digitacion_orden'],
                fecha_termino_orden=row['fecha_termino_orden'],
                estado_transaccion=row['estado_transaccion'],
                usuario_creo_orden=row['usuario_creo_orden'],
                entity_code=row['entity_code'],
                subcanal=row['subcanal'],
                tipo_actividad=row['tipo_actividad'],
                razon_servicio=row['razon_servicio'],
                telefono=row['telefono'],
                imei=row['imei'],
                nom_plan=row['nom_plan'],
                grupo_activacion_orden=row['grupo_activacion_orden'],
                grupo_activacion_anterior=row['grupo_activacion_anterior']
            )
            
            db.session.add(t)
            db.session.commit()
            print("  ✓ SUCCESS!")
            
            # Cleanup
            db.session.delete(t)
            db.session.commit()
            
    except Exception as e:
        db.session.rollback()
        print(f"  ✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
