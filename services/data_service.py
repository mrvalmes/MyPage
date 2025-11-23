import pandas as pd
from extensions import db
from models import Transacciones, VentasDetalle, Pagos, Usuarios
import gestiondata

def process_and_save_ventas(file):
    try:
        df = pd.read_excel(file, header=9, usecols="B:BM")
        processed_df = gestiondata.procesar_dataframe_ventas(df)
        
        # The insertion is now handled inside gestiondata.procesar_dataframe_ventas
        return len(processed_df)
    except Exception as e:
        # db.session.rollback() # Rollback is handled inside gestiondata if needed, or here if we want to be safe
        # But since gestiondata commits, we can't rollback here easily unless we pass session.
        # However, gestiondata handles its own transaction block.
        raise e

def process_and_save_pagos(file):
    try:
        df = pd.read_excel(file, header=9, usecols="B:Y")
        
        # Clean column names just in case
        df.columns = df.columns.str.strip()

        # Convert date column to string format
        df["dte"] = pd.to_datetime(
            df["dte"], dayfirst=True, errors="coerce"
        ).dt.strftime("%Y-%m-%d")
        
        # Replace NaN with None for database compatibility
        df = df.where(pd.notnull(df), None)
        
        # Ensure numeric columns are properly typed
        numeric_int_cols = ['id_tipo_compania', 'id_canal', 'id_subcanal', 'transaction_id']
        for col in numeric_int_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
        numeric_float_cols = ['monto', 'fp_efectivo', 'fp_tarjeta', 'fp_cheque', 'fp_otras']
        for col in numeric_float_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0).astype(float)
        
        # Use bulk insert with ON CONFLICT DO NOTHING (equivalent to INSERT OR IGNORE)
        from sqlalchemy.dialects.postgresql import insert
        
        records = df.to_dict('records')
        
        if records:
            stmt = insert(Pagos.__table__).values(records)
            
            # ON CONFLICT: ignore duplicates based on unique constraint
            # UNIQUE(ent_code, transaction_id, custcode, dte, monto)
            stmt = stmt.on_conflict_do_nothing(
                index_elements=['ent_code', 'transaction_id', 'custcode', 'dte', 'monto']
            )
            
            result = db.session.execute(stmt)
            db.session.commit()
            
            print(f"Se procesaron {len(records)} registros de pagos (duplicados ignorados).")
            return len(records)
        else:
            return 0
            
    except Exception as e:
        db.session.rollback()
        raise e

def generar_ventas_sqlalchemy():
    try:
        # 1. Limpiar la tabla VentasDetalle
        db.session.query(VentasDetalle).delete()
        db.session.commit()
        print("Tabla VentasDetalle limpiada.")

        # 2. Leer datos necesarios
        # Transacciones
        transacciones_query = db.session.query(Transacciones).filter(Transacciones.estado_transaccion != 'Cancelada')
        df = pd.read_sql(transacciones_query.statement, db.session.connection())
        
        # Usuarios (Supervisores)
        usuarios_query = db.session.query(Usuarios.codigo, Usuarios.supervisor)
        data_supers = pd.read_sql(usuarios_query.statement, db.session.connection())
        
        # Incentivos
        from models import Incentivos
        incentivos_query = db.session.query(Incentivos)
        data_incentivos = pd.read_sql(incentivos_query.statement, db.session.connection())

        if df.empty:
            return {"status": "warning", "message": "No hay transacciones para procesar."}

        # 3. Procesamiento (Lógica de cn.py)
        # Convertir fecha
        df["fecha_digitacion_orden"] = pd.to_datetime(
            df["fecha_digitacion_orden"], errors="coerce"
        ).dt.normalize()

        df_group = df.copy()
        df_group_Intermet = df.copy()
        df_group_Card = df.copy()

        # Definir grupos de ventas (Regex patterns from cn.py)
        grupos_ventas = {
            "Flex/Max": (
                df_group["razon_servicio"].isin([
                    "1425 - ACTIVACIONES DE LINEAS - SIN EQUIPOS (DEALERS)",
                    "1409 - PORT SIN NUMERO TEMPORERO/SIN EQUIPO (CANAL PRESE)",
                    "1126 - ACTIVACIONES DE LÍNEAS - CON EQUIPOS (EFECTIVO)",
                    "1301 - ACTIVACIONES DE LINEAS - CON EQUIPOS",
                    "1302 - PORT IN CON NUMERO TEMPORERO/CON EQUIPO",
                    "1349 - PORT CON NUMERO TEMPORERO/SIN EQUIPO (CANAL PRESE)",
                    "1402 - ACTIVACIONES LÍNEAS-SIN EQUIPOS (CANAL PRESENCIAL)",
                ]) & df_group["grupo_activacion_orden"].str.contains(
                    r"883 - GRUPO 0|884 - GRUPO 1|885 - GRUPO 2|886 - GRUPO 3|887 - GRUPO 4|"
                    r"888 - GRUPO 5|889 - GRUPO 6|890 - GRUPO 7|891 - GRUPO 8|893 - GRUPO 9|"
                    r"894 - GRUPO 10|895 - GRUPO 11|912 - GRUPO 12",
                    case=False, na=False,
                )
            ),
            "Migraciones": (
                df_group["razon_servicio"].isin([
                    "1468 - AUMENTO DE PRODUCTO CON VENTA DE EQUIPO",                        
                    "1316 - AUMENTO DE PRODUCTO PREPAGO-POSTPAGO",                        
                ]) & df_group["grupo_activacion_orden"].str.contains(
                    r"883 - GRUPO 0|884 - GRUPO 1|885 - GRUPO 2|886 - GRUPO 3|887 - GRUPO 4|"
                    r"888 - GRUPO 5|889 - GRUPO 6|890 - GRUPO 7|891 - GRUPO 8|893 - GRUPO 9|"
                    r"894 - GRUPO 10|895 - GRUPO 11|912 - GRUPO 12",
                    case=False, na=False,
                )
            ),
            "Fidepuntos Pospago": (
                df_group["razon_servicio"].isin(["1378 - USO DE FIDEPUNTOS (CAMBIA TU MOVIL)"])
                & df_group["grupo_activacion_orden"].str.contains(
                    r"883 - GRUPO 0|884 - GRUPO 1|885 - GRUPO 2|886 - GRUPO 3|887 - GRUPO 4|"
                    r"888 - GRUPO 5|889 - GRUPO 6|890 - GRUPO 7|891 - GRUPO 8|893 - GRUPO 9|"
                    r"894 - GRUPO 10|895 - GRUPO 11|912 - GRUPO 12",
                    case=False, na=False,
                )
            ),
            "Fidepuntos Aumento": (
                df_group["razon_servicio"].isin([
                     "5001 - AUMENTO DE PLAN CON VENTA EQUIPO POR FIDE",
                     "5201 - AUMENTO DE PRODUCTO CON VENTA EQUIPO POR FIDE",
                ]) & df_group["grupo_activacion_orden"].str.contains(
                    r"883 - GRUPO 0|884 - GRUPO 1|885 - GRUPO 2|886 - GRUPO 3|887 - GRUPO 4|"
                    r"888 - GRUPO 5|889 - GRUPO 6|890 - GRUPO 7|891 - GRUPO 8|893 - GRUPO 9|"
                    r"894 - GRUPO 10|895 - GRUPO 11|912 - GRUPO 12",
                    case=False, na=False,
                )
            ),
            "Fidepuntos Disminucion": (
                df_group["razon_servicio"].isin(["5031 - DISMINUCIÓN DE PLAN CON VENTA EQUIPO POR FIDE"])
                & df_group["grupo_activacion_orden"].str.contains(
                    r"883 - GRUPO 0|884 - GRUPO 1|885 - GRUPO 2|886 - GRUPO 3|887 - GRUPO 4|"
                    r"888 - GRUPO 5|889 - GRUPO 6|890 - GRUPO 7|891 - GRUPO 8|893 - GRUPO 9|"
                    r"894 - GRUPO 10|895 - GRUPO 11|912 - GRUPO 12",
                    case=False, na=False,
                )
            ),
            "Reemplazo Pospago": (
                df_group["razon_servicio"].isin(["1324 - VENTA DE EQUIPOS/REEMPLAZO"])
                & df_group["grupo_activacion_orden"].str.contains(
                    r"883 - GRUPO 0|884 - GRUPO 1|885 - GRUPO 2|886 - GRUPO 3|887 - GRUPO 4|"
                    r"888 - GRUPO 5|889 - GRUPO 6|890 - GRUPO 7|891 - GRUPO 8|893 - GRUPO 9|"
                    r"894 - GRUPO 10|895 - GRUPO 11|912 - GRUPO 12",
                    case=False, na=False,
                )
            ),
            "Reemplazo Aumento": (
                df_group["razon_servicio"].isin([
                     "5000 - AUMENTO DE PLAN CON VENTA EQUIPO POR REEMPLAZO",
                     "5200 - AUMENTO DE PRODUCTO CON VENTA EQUIPO POR REEMPLAZO",
                ]) & df_group["grupo_activacion_orden"].str.contains(
                    r"883 - GRUPO 0|884 - GRUPO 1|885 - GRUPO 2|886 - GRUPO 3|887 - GRUPO 4|"
                    r"888 - GRUPO 5|889 - GRUPO 6|890 - GRUPO 7|891 - GRUPO 8|893 - GRUPO 9|"
                    r"894 - GRUPO 10|895 - GRUPO 11|912 - GRUPO 12",
                    case=False, na=False,
                )
            ),
            "Reemplazo Disminucion": (
                df_group["razon_servicio"].isin(["5030 - DISMINUCIÓN DE PLAN CON VENTA EQUIPO POR REEMPLAZO"])
                & df_group["grupo_activacion_orden"].str.contains(
                    r"883 - GRUPO 0|884 - GRUPO 1|885 - GRUPO 2|886 - GRUPO 3|887 - GRUPO 4|"
                    r"888 - GRUPO 5|889 - GRUPO 6|890 - GRUPO 7|891 - GRUPO 8|893 - GRUPO 9|"
                    r"894 - GRUPO 10|895 - GRUPO 11|912 - GRUPO 12",
                    case=False, na=False,
                )
            ),
            "Aumentos Pospago": (
                df_group["razon_servicio"].isin([
                    "1322 - AUMENTO DE PLAN / PAQUETE",
                    "1317 - AUMENTO DE PRODUCTO POSTPAGO-POSTPAGO",
                ]) & df_group["grupo_activacion_orden"].str.contains(
                    r"883 - GRUPO 0|884 - GRUPO 1|885 - GRUPO 2|886 - GRUPO 3|887 - GRUPO 4|"
                    r"888 - GRUPO 5|889 - GRUPO 6|890 - GRUPO 7|891 - GRUPO 8|893 - GRUPO 9|"
                    r"894 - GRUPO 10|895 - GRUPO 11|912 - GRUPO 12",
                    case=False, na=False,
                )
            ),
        }

        grupos_ventas_internet = {
            "Internet": (
                df_group_Intermet["razon_servicio"].isin([
                    "1301 - ACTIVACIONES DE LINEAS - CON EQUIPOS",
                    "1402 - ACTIVACIONES LÍNEAS-SIN EQUIPOS (CANAL PRESENCIAL)",
                ]) & df_group_Intermet["grupo_activacion_orden"].str.contains(
                    r"464 - GRUPO NET 1 - 18 MESES|465 - GRUPO NET 2 - 18 MESES|466 - GRUPO NET 3 - 18 MESES|"
                    r"467 - GRUPO NET 4 - 18 MESES|471 - GRUPO NET 5 - 18 MESES|802 - GRUPO NET 6 - 18 MESES|"
                    r"803 - GRUPO NET 7 - 18 MESES|",
                    case=False, na=False,
                )
            ),
            "InternetCard": (
                df_group_Intermet["razon_servicio"].isin([
                    "1301 - ACTIVACIONES DE LINEAS - CON EQUIPOS",
                    "1402 - ACTIVACIONES LÍNEAS-SIN EQUIPOS (CANAL PRESENCIAL)",
                ]) & df_group_Intermet["grupo_activacion_orden"].str.contains(
                    r"482 - GRUPO NET 0 - 12 MESES",
                    case=False, na=False,
                )
            ),
            "Migracion Internet": (
                df_group_Intermet["razon_servicio"].isin([
                    "1468 - AUMENTO DE PRODUCTO CON VENTA DE EQUIPO",
                    "1316 - AUMENTO DE PRODUCTO PREPAGO-POSTPAGO",
                ]) & df_group_Intermet["grupo_activacion_orden"].str.contains(
                    r"464 - GRUPO NET 1 - 18 MESES|465 - GRUPO NET 2 - 18 MESES|466 - GRUPO NET 3 - 18 MESES|"
                    r"467 - GRUPO NET 4 - 18 MESES|471 - GRUPO NET 5 - 18 MESES|802 - GRUPO NET 6 - 18 MESES|"
                    r"803 - GRUPO NET 7 - 18 MESES|",
                    case=False, na=False,
                )
            ),
            "Reemplazo Internet": (
                df_group_Intermet["razon_servicio"].isin(["1324 - VENTA DE EQUIPOS/REEMPLAZO"])
                & df_group_Intermet["grupo_activacion_orden"].str.contains(
                    r"464 - GRUPO NET 1 - 18 MESES|465 - GRUPO NET 2 - 18 MESES|466 - GRUPO NET 3 - 18 MESES|"
                    r"467 - GRUPO NET 4 - 18 MESES|471 - GRUPO NET 5 - 18 MESES|802 - GRUPO NET 6 - 18 MESES|"
                    r"803 - GRUPO NET 7 - 18 MESES|",
                    case=False, na=False,
                )
            ),
            "Reemplazo InternetAum": (
                df_group_Intermet["razon_servicio"].isin(["5000 - AUMENTO DE PLAN CON VENTA EQUIPO POR REEMPLAZO"])
                & df_group_Intermet["grupo_activacion_orden"].str.contains(
                    r"464 - GRUPO NET 1 - 18 MESES|465 - GRUPO NET 2 - 18 MESES|466 - GRUPO NET 3 - 18 MESES|"
                    r"467 - GRUPO NET 4 - 18 MESES|471 - GRUPO NET 5 - 18 MESES|802 - GRUPO NET 6 - 18 MESES|"
                    r"803 - GRUPO NET 7 - 18 MESES|",
                    case=False, na=False,
                )
            ),
            "Reemplazo InternetDism": (
                df_group_Intermet["razon_servicio"].isin(["5030 - DISMINUCIÓN DE PLAN CON VENTA EQUIPO POR REEMPLAZO"])
                & df_group_Intermet["grupo_activacion_orden"].str.contains(
                    r"464 - GRUPO NET 1 - 18 MESES|465 - GRUPO NET 2 - 18 MESES|466 - GRUPO NET 3 - 18 MESES|"
                    r"467 - GRUPO NET 4 - 18 MESES|471 - GRUPO NET 5 - 18 MESES|802 - GRUPO NET 6 - 18 MESES|"
                    r"803 - GRUPO NET 7 - 18 MESES|",
                    case=False, na=False,
                )
            ),
            "Fidepuntos Internet": (
                df_group_Intermet["razon_servicio"].isin(["1378 - USO DE FIDEPUNTOS (CAMBIA TU MOVIL)"])
                & df_group_Intermet["grupo_activacion_orden"].str.contains(
                    r"464 - GRUPO NET 1 - 18 MESES|465 - GRUPO NET 2 - 18 MESES|466 - GRUPO NET 3 - 18 MESES|"
                    r"467 - GRUPO NET 4 - 18 MESES|471 - GRUPO NET 5 - 18 MESES|802 - GRUPO NET 6 - 18 MESES|"
                    r"803 - GRUPO NET 7 - 18 MESES|",
                    case=False, na=False,
                )
            ),
            "Fidepuntos InternetAum": (
                df_group_Intermet["razon_servicio"].isin(["5001 - AUMENTO DE PLAN CON VENTA EQUIPO POR FIDE"])
                & df_group_Intermet["grupo_activacion_orden"].str.contains(
                    r"464 - GR UPO NET 1 - 18 MESES|465 - GRUPO NET 2 - 18 MESES|466 - GRUPO NET 3 - 18 MESES|"
                    r"467 - GRUPO NET 4 - 18 MESES|471 - GRUPO NET 5 - 18 MESES|802 - GRUPO NET 6 - 18 MESES|"
                    r"803 - GRUPO NET 7 - 18 MESES|",
                    case=False, na=False,
                )
            ),
            "Fidepuntos InternetDism": (
                df_group_Intermet["razon_servicio"].isin(["5031 - DISMINUCIÓN DE PLAN CON VENTA EQUIPO POR FIDE"])
                & df_group_Intermet["grupo_activacion_orden"].str.contains(
                    r"464 - GRUPO NET 1 - 18 MESES|465 - GRUPO NET 2 - 18 MESES|466 - GRUPO NET 3 - 18 MESES|"
                    r"467 - GRUPO NET 4 - 18 MESES|471 - GRUPO NET 5 - 18 MESES|802 - GRUPO NET 6 - 18 MESES|"
                    r"803 - GRUPO NET 7 - 18 MESES|",
                    case=False, na=False,
                )
            ),
            "Aumentos Internet": (
                df_group_Intermet["razon_servicio"].isin(["1322 - AUMENTO DE PLAN / PAQUETE"])
                & df_group["grupo_activacion_orden"].str.contains(
                    r"464 - GRUPO NET 1 - 18 MESES|465 - GRUPO NET 2 - 18 MESES|466 - GRUPO NET 3 - 18 MESES|"
                    r"467 - GRUPO NET 4 - 18 MESES|471 - GRUPO NET 5 - 18 MESES|802 - GRUPO NET 6 - 18 MESES|"
                    r"803 - GRUPO NET 7 - 18 MESES|",
                    case=False, na=False,
                )
            ),
        }

        grupos_ventas_card = {
            "Card": (
                df_group_Card["razon_servicio"].isin([
                    "1425 - ACTIVACIONES DE LINEAS - SIN EQUIPOS (DEALERS)",
                    "1409 - PORT SIN NUMERO TEMPORERO/SIN EQUIPO (CANAL PRESE)",                        
                    "1349 - PORT CON NUMERO TEMPORERO/SIN EQUIPO (CANAL PRESE)",
                    "1402 - ACTIVACIONES LÍNEAS-SIN EQUIPOS (CANAL PRESENCIAL)",
                ]) & df_group_Card["grupo_activacion_orden"].str.contains(
                    r"322 - GRUPO CARD SIM ONLY|4 - CARD",
                    case=False, na=False,
                )
            ),
            "CardEquipo": (
                df_group_Card["razon_servicio"].isin([
                    "1126 - ACTIVACIONES DE LÍNEAS - CON EQUIPOS (EFECTIVO)",
                    "1301 - ACTIVACIONES DE LINEAS - CON EQUIPOS",
                    "1302 - PORT IN CON NUMERO TEMPORERO/CON EQUIPO",                        
                ]) & df_group_Card["grupo_activacion_orden"].str.contains(
                    r"322 - GRUPO CARD SIM ONLY|4 - CARD",
                    case=False, na=False,
                )
            ),
        }

        # Aplicar grupos
        df_group_Card["tipo_venta"] = None
        for tipo, condicion in grupos_ventas_card.items():
            df_group_Card.loc[condicion, "tipo_venta"] = tipo

        df_group_Card["Grupo1"] = df_group_Card["grupo_activacion_orden"].str.extract(r"(\d+) - GRUPO CARD SIM ONLY", expand=False)
        df_group_Card["Grupo2"] = df_group_Card["grupo_activacion_orden"].str.extract(r"(\d+) - CARD", expand=False)
        df_group_Card["Grupo"] = df_group_Card["Grupo1"].fillna(df_group_Card["Grupo2"])
        df_group_Card.drop(["Grupo1", "Grupo2"], axis=1, inplace=True)

        df_group["tipo_venta"] = None
        for tipo, condicion in grupos_ventas.items():
            df_group.loc[condicion, "tipo_venta"] = tipo

        df_group["Grupo"] = df_group["grupo_activacion_orden"].str.extract(r"GRUPO (\d+)", expand=True).bfill(axis=1)[0]
        df_group["Grupo_Anterior"] = df_group["grupo_activacion_anterior"].str.extract(r"GRUPO (\d+)", expand=True).bfill(axis=1)[0]

        df_group_Intermet["tipo_venta"] = None
        for tipo, condicion in grupos_ventas_internet.items():
            df_group_Intermet.loc[condicion, "tipo_venta"] = tipo

        df_group_Intermet["Grupo"] = df_group_Intermet["grupo_activacion_orden"].str.extract(r"GRUPO NET (\d+)", expand=True).bfill(axis=1)[0]
        df_group_Intermet["Grupo_Anterior"] = df_group_Intermet["grupo_activacion_anterior"].str.extract(r"GRUPO NET (\d+)", expand=True).bfill(axis=1)[0]
        df_group_Intermet["Grupo_Anterior"] = df_group_Intermet["Grupo_Anterior"].fillna(0)

        df_group["Grupo_Anterior"] = df_group["Grupo_Anterior"].fillna(0)

        # Conteo
        ventas_validas = df_group.dropna(subset=["tipo_venta", "Grupo"], how="any")
        conteo_ventas = ventas_validas.groupby([
            "entity_code", "subcanal", "fecha_digitacion_orden", "usuario_creo_orden", "tipo_venta", "Grupo", "Grupo_Anterior"
        ]).size().reset_index(name="total_ventas")

        ventas_validas_internet = df_group_Intermet.dropna(subset=["tipo_venta", "Grupo"], how="any")
        conteo_ventas_internet = ventas_validas_internet.groupby([
            "entity_code", "subcanal", "fecha_digitacion_orden", "usuario_creo_orden", "tipo_venta", "Grupo", "Grupo_Anterior"
        ]).size().reset_index(name="total_ventas")

        ventas_validas_card = df_group_Card.dropna(subset=["tipo_venta"], how="any")
        conteo_ventas_card = ventas_validas_card.groupby([
            "entity_code", "subcanal", "fecha_digitacion_orden", "usuario_creo_orden", "tipo_venta", "Grupo"
        ]).size().reset_index(name="total_ventas")

        # Concatenar
        resultado = conteo_ventas
        resultado_card = conteo_ventas_card
        resultado_internet = conteo_ventas_internet
        
        resultado_final = pd.concat([resultado, resultado_internet, resultado_card], ignore_index=True)
        resultado_final.rename(columns={"fecha_digitacion_orden": "fecha"}, inplace=True)
        resultado_final["Grupo_Anterior"] = resultado_final["Grupo_Anterior"].fillna(0)

        # Supervisores
        resultado_final["codigo"] = resultado_final["usuario_creo_orden"].str[:7]
        data_supers["codigo"] = data_supers['codigo'].astype(str)
        df_combinado = pd.merge(resultado_final, data_supers, on="codigo", how="left")
        df_combinado = df_combinado.fillna(0)
        
        df_combinado["supervisor"] = pd.to_numeric(df_combinado["supervisor"], errors='coerce').fillna(0).astype(int).astype(str)

        # Grupo Anterior 0 para ciertos tipos
        tipos_venta_grupo_anterior_cero = [
            "Reemplazo InternetAum", "Fidepuntos InternetDism", "Fidepuntos InternetAum",
            "Reemplazo InternetDism", "Reemplazo Disminucion", "Reemplazo Aumento",
            "Fidepuntos Disminucion", "Fidepuntos Aumento", "Migraciones",
        ]
        df_combinado.loc[df_combinado['tipo_venta'].isin(tipos_venta_grupo_anterior_cero), 'Grupo_Anterior'] = 0

        # Merge Incentivos
        df_combinado["Grupo"] = df_combinado["Grupo"].astype(str)
        df_combinado["Grupo_Anterior"] = df_combinado["Grupo_Anterior"].astype(str)
        df_combinado["tipo_venta"] = df_combinado["tipo_venta"].astype(str)
        
        data_incentivos["Grupo"] = data_incentivos["Grupo"].astype(str)
        data_incentivos["Grupo_Anterior"] = data_incentivos["Grupo_Anterior"].astype(str)
        data_incentivos["tipo_venta"] = data_incentivos["tipo_venta"].astype(str)

        df_combinado = pd.merge(df_combinado, data_incentivos, on=["tipo_venta", "Grupo", "Grupo_Anterior"], how="left")

        # Calcular comisiones
        df_combinado["Comision_100"] = pd.to_numeric(df_combinado["Comision_100"], errors='coerce').fillna(0)
        df_combinado["Comision_75"] = pd.to_numeric(df_combinado["Comision_75"], errors='coerce').fillna(0)
        df_combinado["total_ventas"] = pd.to_numeric(df_combinado["total_ventas"], errors="coerce").fillna(0)
        
        df_combinado["Comision_100"] = df_combinado["total_ventas"] * df_combinado["Comision_100"]
        df_combinado["Comision_75"] = df_combinado["total_ventas"] * df_combinado["Comision_75"]

        # Guardar en DB
        ventas_to_add = []
        for _, row in df_combinado.iterrows():
            venta = VentasDetalle(
                entity_code=row.get('entity_code'),
                subcanal=row.get('subcanal'),
                fecha=row.get('fecha'),
                supervisor=row.get('supervisor'),
                usuario_creo_orden=row.get('usuario_creo_orden'),
                tipo_venta=row.get('tipo_venta'),
                Grupo=int(float(row.get('Grupo'))) if row.get('Grupo') else 0,
                Grupo_Anterior=int(float(row.get('Grupo_Anterior'))) if row.get('Grupo_Anterior') else 0,
                total_ventas=row.get('total_ventas'),
                Comision_100=row.get('Comision_100'),
                Comision_75=row.get('Comision_75')
            )
            ventas_to_add.append(venta)
        
        db.session.add_all(ventas_to_add)
        db.session.commit()
        
        return {"status": "success", "message": f"Se generaron {len(ventas_to_add)} registros de ventas."}

    except Exception as e:
        db.session.rollback()
        import traceback
        print(traceback.format_exc())
        return {"status": "error", "message": str(e)}
