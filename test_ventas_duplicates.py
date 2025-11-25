from extensions import db
from models import Transacciones
from app import create_app
import pandas as pd
import gestiondata

app = create_app()

with app.app_context():
    print("=== Prueba de Duplicados en Carga de Ventas ===\n")
    
    # Contar registros iniciales
    count_before = db.session.query(Transacciones).count()
    print(f"Registros iniciales en transacciones: {count_before}")
    
    # Crear DataFrame de prueba con datos únicos
    test_data = {
        'id_transaccion': ['TEST_DUP_001', 'TEST_DUP_002', 'TEST_DUP_003'],
        'fecha_digitacion_orden': [pd.Timestamp('2025-11-22'), pd.Timestamp('2025-11-22'), pd.Timestamp('2025-11-22')],
        'fecha_termino_orden': [pd.NaT, pd.NaT, pd.NaT],
        'estado_transaccion': ['Abierta', 'Abierta', 'Abierta'],
        'usuario_creo_orden': ['1004203 - TEST USER', '1004208 - TEST USER 2', '1004209 - TEST USER 3'],
        'entity_code': ['TEST', 'TEST', 'TEST'],
        'subcanal': [pd.NA, pd.NA, pd.NA],
        'tipo_actividad': ['Activacion', 'Activacion', 'Activacion'],
        'razon_servicio': ['1301 - TEST', '1302 - TEST', '1303 - TEST'],
        'telefono': ['8091111111', '8092222222', '8093333333'],
        'imei': ['111111111111111', '222222222222222', '333333333333333'],
        'nom_plan': ['TEST PLAN 1', 'TEST PLAN 2', 'TEST PLAN 3'],
        'grupo_activacion_orden': ['888 - GRUPO 5', '889 - GRUPO 6', '890 - GRUPO 7'],
        'grupo_activacion_anterior': ['322 - GRUPO CARD SIM ONLY', '4 - CARD', '5 - CARD']
    }
    
    df = pd.DataFrame(test_data)
    
    print("\n--- Primera Carga (Inserción) ---")
    try:
        gestiondata.guardar_transacciones_db(df.copy())
        count_after_first = db.session.query(Transacciones).count()
        inserted = count_after_first - count_before
        print(f"✓ Primera carga exitosa")
        print(f"Registros después de primera carga: {count_after_first}")
        print(f"Registros insertados: {inserted}")
    except Exception as e:
        print(f"✗ Error en primera carga: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n--- Segunda Carga (Duplicados - NO debe insertar) ---")
    try:
        gestiondata.guardar_transacciones_db(df.copy())
        count_after_second = db.session.query(Transacciones).count()
        inserted_second = count_after_second - count_after_first
        print(f"✓ Segunda carga exitosa")
        print(f"Registros después de segunda carga: {count_after_second}")
        print(f"Registros insertados: {inserted_second}")
        
        if inserted_second == 0:
            print("✓✓✓ CORRECTO: No se insertaron duplicados")
        else:
            print(f"✗✗✗ ERROR: Se insertaron {inserted_second} duplicados")
    except Exception as e:
        print(f"✗ Error en segunda carga: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n--- Tercera Carga (Actualización de estado) ---")
    # Cambiar estado a Terminada
    df['estado_transaccion'] = 'Terminada'
    df['fecha_termino_orden'] = pd.Timestamp('2025-11-23')
    
    try:
        gestiondata.guardar_transacciones_db(df.copy())
        count_after_third = db.session.query(Transacciones).count()
        inserted_third = count_after_third - count_after_second
        print(f"✓ Tercera carga exitosa")
        print(f"Registros después de tercera carga: {count_after_third}")
        print(f"Registros insertados: {inserted_third}")
        
        if inserted_third == 0:
            print("✓✓✓ CORRECTO: No se insertaron duplicados, solo se actualizaron")
        else:
            print(f"✗✗✗ ERROR: Se insertaron {inserted_third} registros en lugar de actualizar")
        
        # Verificar que se actualizaron los estados
        updated_records = Transacciones.query.filter(
            Transacciones.id_transaccion.in_(['TEST_DUP_001', 'TEST_DUP_002', 'TEST_DUP_003'])
        ).all()
        
        print("\nEstados actualizados:")
        for r in updated_records:
            print(f"  - {r.id_transaccion}: estado={r.estado_transaccion}, fecha_termino={r.fecha_termino_orden}")
        
    except Exception as e:
        print(f"✗ Error en tercera carga: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n--- Limpieza ---")
    # Eliminar registros de prueba
    Transacciones.query.filter(
        Transacciones.id_transaccion.in_(['TEST_DUP_001', 'TEST_DUP_002', 'TEST_DUP_003'])
    ).delete()
    db.session.commit()
    
    count_final = db.session.query(Transacciones).count()
    print(f"Registros finales: {count_final}")
    print(f"✓ Limpieza completada")
