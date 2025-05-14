# Librerias.
import os
import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import sqlite3

# llamar funciones guardar en base de datos
DB_PATH = r"C:\Users\Spectre\Documents\DBHeromovil\VentasHeromovil.db"

def guardar_filtrado_en_db(filtrado, db_path):
    # Conexión
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # OPCIONAL: si quieres borrar todo antes de insertar
    # cur.execute("DELETE FROM transacciones")
    # conn.commit()
    TABLE_NAME = "transacciones"

    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_transaccion TEXT,
        fecha_digitacion_orden DATE,
        estado_transaccion TEXT,
        usuario_creo_orden TEXT,
        tipo_actividad TEXT,
        razon_servicio TEXT,
        telefono TEXT,
        imei TEXT,
        nom_plan TEXT,
        grupo_activacion_orden TEXT,
        grupo_activacion_anterior TEXT
    );
    """
    cur.execute(create_table_query)

    # 2) Crear índice UNIQUE en 5 columnas
    cur.execute(
        """
    CREATE UNIQUE INDEX IF NOT EXISTS idx_transacciones_unicos
    ON transacciones (
        id_transaccion,
        usuario_creo_orden,
        razon_servicio,
        telefono,
        imei
    );
    """
    )

    # Insertar fila a fila, para evitar errores de duplicados
    insert_sql = """
        INSERT OR IGNORE INTO transacciones (
            id_transaccion,
            fecha_digitacion_orden,
            estado_transaccion,
            usuario_creo_orden,
            tipo_actividad,
            razon_servicio,
            telefono,
            imei,
            nom_plan,
            grupo_activacion_orden,
            grupo_activacion_anterior
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

    for _, row in filtrado.iterrows():
        values = (
            row["id_transaccion"],
            str(row["fecha_digitacion_orden"]),  # str() por si viene datetime
            row["estado_transaccion"],
            row["usuario_creo_orden"],
            row["tipo_actividad"],
            row["razon_servicio"],
            str(row["telefono"]),
            str(row["imei"]),
            row["nom_plan"],
            row["grupo_activacion_orden"],
            row["grupo_activacion_anterior"],
        )
        cur.execute(insert_sql, values)

    conn.commit()
    conn.close()


def guardar_ventas_detalle_en_db(df_ventas, db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # OPCIONAL: borrar todo antes de insertar
    cur.execute("DELETE FROM ventas_detalle")
    conn.commit()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS ventas_detalle (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha DATE,
            supervisor TEXT,
            usuario_creo_orden TEXT,
            tipo_venta TEXT,
            Grupo INTEGER,
            Grupo_Anterior INTEGER,
            total_ventas INTEGER           
        );
    """
    )

    insert_sql = """
        INSERT INTO ventas_detalle (
            fecha,
            supervisor,
            usuario_creo_orden,
            tipo_venta,
            Grupo,
            Grupo_Anterior,
            total_ventas            
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """

    for _, row in df_ventas.iterrows():
        values = (
            str(row["fecha"]),  # str() si viene como datetime
            row["supervisor"],
            row["usuario_creo_orden"],
            row["tipo_venta"],
            int(row["Grupo"]),
            int(row["Grupo_Anterior"]),
            int(row["total_ventas"]),
        )
        cur.execute(insert_sql, values)

    conn.commit()
    conn.close()

# Función para seleccionar la carpeta de origen.
def seleccionar_carpeta_origen():
    carpeta_origen = filedialog.askdirectory()
    entrada_carpeta_origen.delete(0, tk.END)
    entrada_carpeta_origen.insert(0, carpeta_origen)

# Función para seleccionar la carpeta de destino.
def seleccionar_carpeta_destino():
    carpeta_destino = filedialog.askdirectory()
    entrada_carpeta_destino.delete(0, tk.END)
    entrada_carpeta_destino.insert(0, carpeta_destino)

# Función para procesar los archivos.
def procesar_archivos():
    try:
        # Obtener las rutas de las carpetas de origen y destino.
        carpeta_origen = entrada_carpeta_origen.get()
        carpeta_destino = entrada_carpeta_destino.get()

        # Validar si se han seleccionado las carpetas
        if not carpeta_origen or not carpeta_destino:
            messagebox.showwarning(
                "Advertencia",
                "Por favor, seleccione ambas carpetas de origen y destino.",
            )
            return

        # Leer valores de mes y año de los dropdowns
        mes_deseado = menu_mes.get()
        anio_deseado = menu_anio.get()

        # Validar los valores de mes y año (convertirlos a números si no están vacíos)
        mes_deseado = int(mes_deseado) if mes_deseado.isdigit() else None
        anio_deseado = int(anio_deseado) if anio_deseado.isdigit() else None

        # Almacenar los DataFrames de cada archivo XLSX
        dfs = []  # correctas
        dfsc = []  # canceladas
        filtrado = []  # dataset nuevo, solo columnas especificas

        # Diccionario para mapear condiciones y sus valores, para ajustar errores en grupos.
        mapeo_condiciones_grupos = {
            "FLEX - APPS 100 MINUTOS/1GB": "884 - GRUPO 1",
            "FLEX - APPS 75 MINUTOS/700MB": "884 - GRUPO 1",
            "FLEX - APPS ESPECIAL DE 200 MIN / 4GB": "886 - GRUPO 3",
            "FLEX - APPS LARGE 200 MIN / 1GB": "887 - GRUPO 4",
            "FLEX - APPS LARGE 200 MIN / 4GB": "886 - GRUPO 3",
            "FLEX - APPS LARGE 250 MIN / 2GB": "888 - GRUPO 5",
            "FLEX - APPS MEDIUM 150 MIN / 2GB": "885 - GRUPO 2",
            "FLEX - APPS MEDIUM 200 MIN / 700MB": "886 - GRUPO 3",
            "FLEX - APPS SMALL 100 MIN / 1GB": "884 - GRUPO 1",
            "FLEX - APPS SMALL 150 MIN / 250MB": "885 - GRUPO 2",
            "FLEX - APPS XLARGE 200 MIN / 5GB": "887 - GRUPO 4",
            "FLEX - APPS XSMALL 100 MIN / 100MB": "884 - GRUPO 1",
            "FLEX - BASICO 300MIN / 1GB": "887 - GRUPO 4",
            "FLEX - BASICO 60MIN / 30MB": "883 - GRUPO 0",
            "FLEX - BASICO150MIN / 100MB": "885 - GRUPO 2",
            "FLEX - BASICO250MIN / 500MB": "886 - GRUPO 3",
            "FLEX - PLAN APPS 100MIN/100MB": "884 - GRUPO 1",
            "FLEX - PLAN APPS 200MIN/100MB": "885 - GRUPO 2",
            "FLEX - PLAN APPS FULL 100MIN/1GB": "887 - GRUPO 4",
            "FLEX - PLAN APPS FULL 200MIN/1GB": "888 - GRUPO 5",
            "FLEX - PLAN APPS PLUS 100MIN/500MB": "886 - GRUPO 3",
            "FLEX - PLAN APPS PLUS 200MIN/500MB": "886 - GRUPO 3",
            "FLEX - PRO ESPECIAL DE 100 MIN / 7GB": "888 - GRUPO 5",
            "FLEX - PRO LARGE 200 MIN / 14GB": "893 - GRUPO 9",
            "FLEX - PRO LARGE 200 MIN / 25GB": "893 - GRUPO 9",
            "FLEX - PRO MEDIUM 150 MIN / 20GB": "890 - GRUPO 7",
            "FLEX - PRO MEDIUM 150 MIN / 7GB": "890 - GRUPO 7",
            "FLEX - PRO MEDIUM 200 MIN / 20GB": "890 - GRUPO 7",
            "FLEX - PRO MEDIUM 200 MIN / 7GB": "890 - GRUPO 7",
            "FLEX - PRO MEDIUM 300 MIN / 20GB": "891 - GRUPO 8",
            "FLEX - PRO MEDIUM 300 MIN / 7GB": "891 - GRUPO 8",
            "FLEX - PRO SMALL 100 MIN / 10GB": "889 - GRUPO 6",
            "FLEX - PRO SMALL 100 MIN / 4GB": "889 - GRUPO 6",
            "FLEX - PRO SMALL 200 MIN / 10GB": "889 - GRUPO 6",
            "FLEX - PRO SMALL 200 MIN / 4GB": "889 - GRUPO 6",
            "FLEX - PRO SMALL 300 MIN / 10GB": "889 - GRUPO 6",
            "FLEX - PRO SMALL 500 MIN / 10GB": "891 - GRUPO 8",
            "FLEX - PRO SMALL 500 MIN / 4GB": "891 - GRUPO 8",
            "FLEX - PRO XSMALL 100 MIN / 2GB": "888 - GRUPO 5",
            "FLEX - PRO XSMALL 100 MIN / 7GB": "888 - GRUPO 5",
            "FLEX ARDILLA - ARDILLA 60 MIN + 60 SMS (FLEX)": "883 - GRUPO 0",
            "FLEX ARDILLA LOS MIOS - ARDILLA 30 MIN + 30 MIN (FLEX)": "883 - GRUPO 0",
            "INTERNET ALTICE-F - 10GB BEST EFFORT": "467 - GRUPO NET 4 - 18 MESES",
            "INTERNET ALTICE-F - 10GB BEST EFFORT ESPECIAL": "467 - GRUPO NET 4 - 18 MESES",
            "INTERNET ALTICE-F - 15GB BEST EFFORT": "471 - GRUPO NET 5 - 18 MESES",
            "INTERNET ALTICE-F - 20GB BEST EFFORT": "802 - GRUPO NET 6 - 18 MESES",
            "INTERNET ALTICE-F - 7GB BEST EFFORT": "466 - GRUPO NET 3 - 18 MESES",
            "INTERNET ALTICE-F REGIONAL - 3GB REGIONAL BEST EFFORT": "464 - GRUPO NET 1 - 18 MESES",
            "INTERNET ALTICE-F REGIONAL - 5GB REGIONAL BEST EFFORT": "465 - GRUPO NET 2 - 18 MESES",
            "INTERNET ALTICE-M - 10GB BEST EFFORT ESPECIAL": "467 - GRUPO NET 4 - 18 MESES",
            "INTERNET ALTICE-M - 15GB BEST EFFORT": "471 - GRUPO NET 5 - 18 MESES",
            "INTERNET ALTICE-M - 20GB BEST EFFORT": "802 - GRUPO NET 6 - 18 MESES",
            "INTERNET ALTICE-M - 7GB BEST EFFORT": "466 - GRUPO NET 3 - 18 MESES",
            "INTERNET ALTICE-M REGIONAL - 3GB REGIONAL BEST EFFORT": "464 - GRUPO NET 1 - 18 MESES",
            "INTERNET ALTICE-M REGIONAL - 5GB REGIONAL BEST EFFORT": "465 - GRUPO NET 2 - 18 MESES",
            "INTERNET MOVIL ALTICE - 3MBPS/1.5MBPS MOVIL": "471 - GRUPO NET 5 - 18 MESES",
            "INTERNET ALTICE-M - 10GB BEST EFFORT": "471 - GRUPO NET 5 - 18 MESES",
            "INTERNET MOVIL ALTICE - 1MBPS/1MBPS MOVIL": "464 - GRUPO NET 1 - 18 MESES",
            "RT - INTERNET ALTICE- F - 2GB BEST EFFORT": "464 - GRUPO NET 1 - 18 MESES",
            "MAX - APPS LARGE 200 MIN / 4GB": "886 - GRUPO 3",
            "MAX - APPS MEDIUM 150 MIN / 2GB": "885 - GRUPO 2",
            "MAX - APPS MEDIUM 200 MIN / 700MB": "886 - GRUPO 3",
            "MAX - PRO SMALL 200 MIN / 4GB": "889 - GRUPO 6",
            "MAX - PRO XSMALL 100 MIN / 7GB": "888 - GRUPO 5",
            "MAX - PRO MEDIUM 500 MIN / 20GB": "891 - GRUPO 8",
            "MAX - PRO MEDIUM 300 MIN / 7GB": "891 - GRUPO 8",
            "MAX - PRO MEDIUM 150 MIN / 20GB": "890 - GRUPO 7",
            "MAX - PRO MEDIUM 200 MIN / 7GB": "890 - GRUPO 7",
            "MAX - PRO SMALL 500 MIN / 10GB": "891 - GRUPO 8",
            "MAX - PRO SMALL 200 MIN / 10GB": "889 - GRUPO 6",
            "MAX - PRO SMALL 100 MIN / 10GB": "889 - GRUPO 6",
            "RT - FLEX BASICO": "883 - GRUPO 0",
            "RT - FLEX BASICO - BASICO 50MIN": "883 - GRUPO 0",
            "RT - FLEX BASICO - BASICO 60MIN / 30MB": "883 - GRUPO 0",
            "RT - FLEX BASICO - APPS SMALL 100 MIN / 1GB": "884 - GRUPO 1",
            "RT - FLEX BASICO - APPS MEDIUM 150 MIN / 2GB": "885 - GRUPO 2",
            "MAX - PRO XSMALL 100 MIN / 2GB": "888 - GRUPO 5",
            "MAX - APPS SMALL 100 MIN / 1GB": "884 - GRUPO 1",
            "ALTICE PREPAGO SIMO": "322 - GRUPO CARD SIM ONLY",
            "ALTICE PREPAGO SIMO - CARD": "322 - GRUPO CARD SIM ONLY",
            "ALTICE CARD": "4 - CARD",
            "ALTICE CARD CANARIO": "4 - CARD",
            "ALTICE PREPAGO": "4 - CARD",
            "ALTICE PREPAGO - CARD": "4 - CARD",
            "ALTICE PREPAGO SIMO - SIMO DATA": "322 - GRUPO CARD SIM ONLY",
            "INTERNET MOVIL PREPAGO - Paquete Internet móvil prepago": "322 - GRUPO CARD SIM ONLY",            
        }
        mapeo_estado_orden = {"Abierta": "Terminada"}

        mapeo_condiciones_ventacosto = {
            "1325 - VENTA DE EQUIPOS AL COSTO": "0",
        }

        # inicio for
        # Leer cada archivo XLSX en la carpeta de origen y agregarlo a la lista
        for archivo in os.listdir(carpeta_origen):
            if archivo.endswith(".xlsx"):
                ruta_completa = os.path.join(carpeta_origen, archivo)
                try:
                    df = pd.read_excel(ruta_completa, header=9)

                    # Convertir la columna 'fecha_digitacion_orden' a datetime y establecer la hora a las 00:00:00
                    df["fecha_digitacion_orden"] = pd.to_datetime(
                        df["fecha_digitacion_orden"], errors="coerce"
                    ).dt.normalize()

                    # Eliminar filas con fechas no válidas
                    df = df.dropna(subset=["fecha_digitacion_orden"])

                    # Aplicar filtro de mes y año si están definidos
                    if mes_deseado or anio_deseado:
                        if mes_deseado:
                            df = df[
                                df["fecha_digitacion_orden"].dt.month == mes_deseado
                            ]
                        if anio_deseado:
                            df = df[
                                df["fecha_digitacion_orden"].dt.year == anio_deseado
                            ]

                    # Rellenar valores nulos
                    df = df.fillna("null")

                    # Función para modificar la columna según la condición, y aplicar el grupo correcto.
                    def modificar_valor(row):
                        return mapeo_condiciones_grupos.get(
                            row["nom_plan_anterior"], row["grupo_activacion_anterior"]
                        )

                    def modificar_ventacosto(row):
                        return mapeo_condiciones_ventacosto.get(
                            row["razon_servicio"], row["grupo_activacion_orden"]
                        )

                    def modificar_estado(row):
                        return mapeo_estado_orden.get(
                            row["estado_transaccion"], row["estado_transaccion"]
                        )

                    # Aplicar la función a las columnas que se desean modificar
                    df["grupo_activacion_anterior"] = df.apply(modificar_valor, axis=1)
                    df["estado_transaccion"] = df.apply(modificar_estado, axis=1)
                    df["grupo_activacion_orden"] = df.apply(
                        modificar_ventacosto, axis=1
                    )

                    # Lista de condiciones para eliminar filas y limpiar datos innecesarios.
                    condiciones_usuario = ["OS - SISTEMA ORDENES(AUTOMATICO)"]
                    condiciones_razon_servicio = [
                        "1159 - MISCELANEOS VIDEO ON DEMAND",
                        "1309 - ACTIVACIONES Y DESACTIVACIÓN SERVICIOS OPCIONALES",
                        "1304 - USO DE FIDEPUNTOS (HABLA MAS / P&S)",
                        "1312 - TRANSFERENCIA FIDEPUNTOS",
                        "1315 - CAMBIO DE NUMERO",
                        "1323 - DISMINUCIÓN DE PLAN / PAQUETE",
                        "1365 - CAMBIO DE NUMERO (PORTABILIDAD)",
                        "1369 - RECONEXION POR ROBO / PÉRDIDA",
                        "1372 - SEPARACION DE CUENTAS",
                        "1400 - TRASPASO DE CONTRATO  PREPAGO",
                        "1376 - UNIFICACION DE CUENTAS",
                        "1318 - DISMINUCION PRODUCTO POSTPAGO-PREPAGO",
                        "1352 - SUSPENSION TEMPORAL (90 DIAS)",
                        "1331 - POR ERROR DE DIGITACIÓN",
                        "1368 - RECONEXIÓN DE SERVICIO",
                        "1327 - A SOLICITUD DEL CLIENTE",
                        "1351 - SUSPENSION TEMPORAL (60 DIAS)",
                        "1329 - SUSPENSIÓN DE SERVICIO POR PÉRDIDA O ROBO",
                        "349 - RETIRO QUITESE",
                        "5020 - TITULAR CON VALIDADOR DE IDENTIDAD",
                    ]

                    condiciones_canceladas = ["Cancelada"]

                    # Seleccionar filas canceladas
                    canceladas = df["estado_transaccion"].isin(condiciones_canceladas)
                    dfsc.append(df[canceladas])

                    # Crear una condición compuesta para eliminar filas y datos innecesarios
                    condicion = (
                        (df["usuario_creo_orden"].isin(condiciones_usuario))
                        | (df["razon_servicio"].isin(condiciones_razon_servicio))
                        | (df["estado_transaccion"].isin(condiciones_canceladas))
                    )

                    # Eliminar las filas que cumplen la condición
                    df.drop(df[condicion].index, inplace=True)

                    # Añadir el DataFrame resultante a la lista
                    dfs.append(df)

                except Exception as e:
                    messagebox.showerror(
                        "Error",
                        f"Ocurrió un error al procesar el archivo {archivo}: {e}",
                    )
            # Fin for

        # Unificar los DataFrames en uno solo
        if dfs:
            try:
                data_set = pd.concat(dfs, ignore_index=True)
                data_set_c = pd.concat(dfsc, ignore_index=True)

                columnas_valida = [
                    "id_transaccion",
                    "fecha_digitacion_orden",
                    "estado_transaccion",
                    "usuario_creo_orden",
                    "tipo_actividad",
                    "razon_servicio",
                    "telefono",
                    "imei",
                    "nom_plan",
                    "grupo_activacion_orden",
                    "grupo_activacion_anterior",
                ]

                # Filtrar las columnas de interés
                # fil = data_set.copy
                filtrado = data_set[columnas_valida]

                # Convertir columnas relevantes a numericas para evitar errores en comparaciones
                columnas_a_convertir = ["id_transaccion", "telefono", "imei"]
                for columna in columnas_a_convertir:
                    if columna in filtrado.columns:
                        filtrado.loc[:, columna] = pd.to_numeric(
                            filtrado[columna], errors="coerce"
                        )
                        # filtrado[columna] = pd.to_numeric(filtrado[columna], errors="coerce")
                    else:
                        messagebox.showwarning(
                            "Advertencia: La columna '{columna}' no está en el DataFrame.",
                        )

                # Eliminar duplicados
                filtrado = filtrado.drop_duplicates(
                    subset=["id_transaccion", "razon_servicio", "telefono", "imei"],
                    keep="last",
                )                
                # Rutas para guardar los archivos
                ruta_resultado = os.path.join(carpeta_destino, "Resultado.xlsx")
                ruta_resultado_c = os.path.join(carpeta_destino, "Canceladas.xlsx")

                # >Este es resultado "Filtrado", es que se inserta en la tabla transacciones, si notas son iguales.
                ruta_resultado_filtrado = os.path.join(carpeta_destino, "Filtrado.xlsx")               

                # Guardar los resultados en archivos Excel
                data_set.to_excel(ruta_resultado, index=False)
                data_set_c.to_excel(ruta_resultado_c, index=False)
                filtrado.to_excel(ruta_resultado_filtrado, index=False)  

                # Guardar en tabla transacciones
                guardar_filtrado_en_db(filtrado, DB_PATH )

                # Mostrar mensaje de confirmación
                mensaje_confirmacion = "Procesamiento completado ✅\n"
                messagebox.showinfo("Finalizado", mensaje_confirmacion)

            except Exception as e:
                messagebox.showerror(
                    "Error", f"Ocurrió un error durante el procesamiento: {e}"
                )
        else:
            messagebox.showwarning(
                "Advertencia", "No se encontraron archivos válidos para procesar."
            )
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {e}")

def generar_ventas():
    """
    Genera un reporte de ventas basado en los datos almacenados en la base de datos.
    Agrupa las ventas por diferentes categorías y guarda el resultado en un archivo Excel.
    """
    carpeta_destino = entrada_carpeta_destino.get()

    # Validar si se ha seleccionado las carpeta
    #if not carpeta_destino:        
    #    messagebox.showwarning(
    #        "Advertencia",
    #        "Por favor, seleccione carpetas donde guardar los datos.",
    #    )
    #    return 

    try:
        conn = sqlite3.connect(DB_PATH)
        query = """
        SELECT *FROM transacciones
        """
        query2 = """
        SELECT codigo, supervisor FROM usuarios
        """
        data = pd.read_sql(query, conn)
        data_supers = pd.read_sql(query2, conn)

        # Leer valores de mes , año y dia de los dropdowns
        dia_deseado = menu_dia.get()
        mes_deseado = menu_mes.get()
        anio_deseado = menu_anio.get()

        # Validar los valores de mes y año (convertirlos a números si no están vacíos)
        dia_deseado = int(dia_deseado) if dia_deseado.isdigit() else None
        mes_deseado = int(mes_deseado) if mes_deseado.isdigit() else None
        anio_deseado = int(anio_deseado) if anio_deseado.isdigit() else None

        # Convertir la columna 'fecha_digitacion_orden' a datetime y establecer la hora a las 00:00:00
        data["fecha_digitacion_orden"] = pd.to_datetime(
            data["fecha_digitacion_orden"], errors="coerce"
        ).dt.normalize()        

        # Aplicar filtro de mes y año si están definidos
        if dia_deseado or mes_deseado or anio_deseado:
            if dia_deseado:
                data = data[
                    data["fecha_digitacion_orden"].dt.day == dia_deseado
                    ]
                if mes_deseado:
                    data = data[
                        data["fecha_digitacion_orden"].dt.month == mes_deseado
                        ]
                    if anio_deseado:
                        data = data[
                            data["fecha_digitacion_orden"].dt.year == anio_deseado
                        ]

        # Convertir los datos en un DataFrame
        df_group = data.copy()
        df_group_Intermet = data.copy()
        df_group_Card = data.copy()

        # Definir los grupos de ventas y sus condiciones
        grupos_ventas = {
            "Flex/Max": (
                df_group["razon_servicio"].isin(
                    [
                        "1425 - ACTIVACIONES DE LINEAS - SIN EQUIPOS (DEALERS)",
                        "1409 - PORT SIN NUMERO TEMPORERO/SIN EQUIPO (CANAL PRESE)",
                        "1126 - ACTIVACIONES DE LÍNEAS - CON EQUIPOS (EFECTIVO)",
                        "1301 - ACTIVACIONES DE LINEAS - CON EQUIPOS",
                        "1302 - PORT IN CON NUMERO TEMPORERO/CON EQUIPO",
                        "1349 - PORT CON NUMERO TEMPORERO/SIN EQUIPO (CANAL PRESE)",
                        "1402 - ACTIVACIONES LÍNEAS-SIN EQUIPOS (CANAL PRESENCIAL)",
                    ]
                )
                & df_group["grupo_activacion_orden"].str.contains(
                    r"883 - GRUPO 0|884 - GRUPO 1|885 - GRUPO 2|886 - GRUPO 3|887 - GRUPO 4|"
                    r"888 - GRUPO 5|889 - GRUPO 6|890 - GRUPO 7|891 - GRUPO 8|893 - GRUPO 9|"
                    r"894 - GRUPO 10|895 - GRUPO 11|912 - GRUPO 12",
                    case=False,
                    na=False,
                )
            ),
            "Migraciones": (
                df_group["razon_servicio"].isin(
                    [
                        "1468 - AUMENTO DE PRODUCTO CON VENTA DE EQUIPO",                        
                        "1316 - AUMENTO DE PRODUCTO PREPAGO-POSTPAGO",
                    ]
                )
                & df_group["grupo_activacion_orden"].str.contains(
                    r"883 - GRUPO 0|884 - GRUPO 1|885 - GRUPO 2|886 - GRUPO 3|887 - GRUPO 4|"
                    r"888 - GRUPO 5|889 - GRUPO 6|890 - GRUPO 7|891 - GRUPO 8|893 - GRUPO 9|"
                    r"894 - GRUPO 10|895 - GRUPO 11|912 - GRUPO 12",
                    case=False,
                    na=False,
                )
            ),
            "Fidepuntos Pospago": (
                df_group["razon_servicio"].isin(
                    ["1378 - USO DE FIDEPUNTOS (CAMBIA TU MOVIL)"]
                )
                & df_group["grupo_activacion_orden"].str.contains(
                    r"883 - GRUPO 0|884 - GRUPO 1|885 - GRUPO 2|886 - GRUPO 3|887 - GRUPO 4|"
                    r"888 - GRUPO 5|889 - GRUPO 6|890 - GRUPO 7|891 - GRUPO 8|893 - GRUPO 9|"
                    r"894 - GRUPO 10|895 - GRUPO 11|912 - GRUPO 12",
                    case=False,
                    na=False,
                )
            ),
            "Fidepuntos Aumento": (
                df_group["razon_servicio"].isin(
                    ["5001 - AUMENTO DE PLAN CON VENTA EQUIPO POR FIDE"]
                )
                & df_group["grupo_activacion_orden"].str.contains(
                    r"883 - GRUPO 0|884 - GRUPO 1|885 - GRUPO 2|886 - GRUPO 3|887 - GRUPO 4|"
                    r"888 - GRUPO 5|889 - GRUPO 6|890 - GRUPO 7|891 - GRUPO 8|893 - GRUPO 9|"
                    r"894 - GRUPO 10|895 - GRUPO 11|912 - GRUPO 12",
                    case=False,
                    na=False,
                )
            ),
            "Fidepuntos Disminucion": (
                df_group["razon_servicio"].isin(
                    ["5031 - DISMINUCIÓN DE PLAN CON VENTA EQUIPO POR FIDE"]
                )
                & df_group["grupo_activacion_orden"].str.contains(
                    r"883 - GRUPO 0|884 - GRUPO 1|885 - GRUPO 2|886 - GRUPO 3|887 - GRUPO 4|"
                    r"888 - GRUPO 5|889 - GRUPO 6|890 - GRUPO 7|891 - GRUPO 8|893 - GRUPO 9|"
                    r"894 - GRUPO 10|895 - GRUPO 11|912 - GRUPO 12",
                    case=False,
                    na=False,
                )
            ),
            "Reemplazo Pospago": (
                df_group["razon_servicio"].isin(["1324 - VENTA DE EQUIPOS/REEMPLAZO"])
                & df_group["grupo_activacion_orden"].str.contains(
                    r"883 - GRUPO 0|884 - GRUPO 1|885 - GRUPO 2|886 - GRUPO 3|887 - GRUPO 4|"
                    r"888 - GRUPO 5|889 - GRUPO 6|890 - GRUPO 7|891 - GRUPO 8|893 - GRUPO 9|"
                    r"894 - GRUPO 10|895 - GRUPO 11|912 - GRUPO 12",
                    case=False,
                    na=False,
                )
            ),
            "Reemplazo Aumento": (
                df_group["razon_servicio"].isin(
                    ["5000 - AUMENTO DE PLAN CON VENTA EQUIPO POR REEMPLAZO"]
                )
                & df_group["grupo_activacion_orden"].str.contains(
                    r"883 - GRUPO 0|884 - GRUPO 1|885 - GRUPO 2|886 - GRUPO 3|887 - GRUPO 4|"
                    r"888 - GRUPO 5|889 - GRUPO 6|890 - GRUPO 7|891 - GRUPO 8|893 - GRUPO 9|"
                    r"894 - GRUPO 10|895 - GRUPO 11|912 - GRUPO 12",
                    case=False,
                    na=False,
                )
            ),
            "Reemplazo Disminucion": (
                df_group["razon_servicio"].isin(
                    ["5030 - DISMINUCIÓN DE PLAN CON VENTA EQUIPO POR REEMPLAZO"]
                )
                & df_group["grupo_activacion_orden"].str.contains(
                    r"883 - GRUPO 0|884 - GRUPO 1|885 - GRUPO 2|886 - GRUPO 3|887 - GRUPO 4|"
                    r"888 - GRUPO 5|889 - GRUPO 6|890 - GRUPO 7|891 - GRUPO 8|893 - GRUPO 9|"
                    r"894 - GRUPO 10|895 - GRUPO 11|912 - GRUPO 12",
                    case=False,
                    na=False,
                )
            ),
            "Aumentos Pospago": (
                df_group["razon_servicio"].isin(["1322 - AUMENTO DE PLAN / PAQUETE"])
                & df_group["grupo_activacion_orden"].str.contains(
                    r"883 - GRUPO 0|884 - GRUPO 1|885 - GRUPO 2|886 - GRUPO 3|887 - GRUPO 4|"
                    r"888 - GRUPO 5|889 - GRUPO 6|890 - GRUPO 7|891 - GRUPO 8|893 - GRUPO 9|"
                    r"894 - GRUPO 10|895 - GRUPO 11|912 - GRUPO 12",
                    case=False,
                    na=False,
                )
            ),
        }

        grupos_ventas_internet = {
            "Internet": (
                df_group_Intermet["razon_servicio"].isin(
                    [
                        "1301 - ACTIVACIONES DE LINEAS - CON EQUIPOS",
                        "1402 - ACTIVACIONES LÍNEAS-SIN EQUIPOS (CANAL PRESENCIAL)",
                    ]
                )
                & df_group_Intermet["grupo_activacion_orden"].str.contains(
                    r"464 - GRUPO NET 1 - 18 MESES|465 - GRUPO NET 2 - 18 MESES|466 - GRUPO NET 3 - 18 MESES|"
                    r"467 - GRUPO NET 4 - 18 MESES|471 - GRUPO NET 5 - 18 MESES|802 - GRUPO NET 6 - 18 MESES|"
                    r"803 - GRUPO NET 7 - 18 MESES|",
                    case=False,
                    na=False,
                )
            ),
            "InternetCard": (
                df_group_Intermet["razon_servicio"].isin(
                    [
                        "1301 - ACTIVACIONES DE LINEAS - CON EQUIPOS",
                        "1402 - ACTIVACIONES LÍNEAS-SIN EQUIPOS (CANAL PRESENCIAL)",
                    ]
                )
                & df_group_Intermet["grupo_activacion_orden"].str.contains(
                    r"482 - GRUPO NET 0 - 12 MESES",
                    case=False,
                    na=False,
                )
            ),
            "Migracion Internet": (
                df_group_Intermet["razon_servicio"].isin(
                    [
                        "1468 - AUMENTO DE PRODUCTO CON VENTA DE EQUIPO",
                        "1316 - AUMENTO DE PRODUCTO PREPAGO-POSTPAGO",
                    ]
                )
                & df_group_Intermet["grupo_activacion_orden"].str.contains(
                    r"464 - GRUPO NET 1 - 18 MESES|465 - GRUPO NET 2 - 18 MESES|466 - GRUPO NET 3 - 18 MESES|"
                    r"467 - GRUPO NET 4 - 18 MESES|471 - GRUPO NET 5 - 18 MESES|802 - GRUPO NET 6 - 18 MESES|"
                    r"803 - GRUPO NET 7 - 18 MESES|",
                    case=False,
                    na=False,
                )
            ),
            "Reemplazo Internet": (
                df_group_Intermet["razon_servicio"].isin(
                    ["1324 - VENTA DE EQUIPOS/REEMPLAZO"]
                )
                & df_group_Intermet["grupo_activacion_orden"].str.contains(
                    r"464 - GRUPO NET 1 - 18 MESES|465 - GRUPO NET 2 - 18 MESES|466 - GRUPO NET 3 - 18 MESES|"
                    r"467 - GRUPO NET 4 - 18 MESES|471 - GRUPO NET 5 - 18 MESES|802 - GRUPO NET 6 - 18 MESES|"
                    r"803 - GRUPO NET 7 - 18 MESES|",
                    case=False,
                    na=False,
                )
            ),
            "Reemplazo InternetAum": (
                df_group_Intermet["razon_servicio"].isin(
                    ["5000 - AUMENTO DE PLAN CON VENTA EQUIPO POR REEMPLAZO"]
                )
                & df_group_Intermet["grupo_activacion_orden"].str.contains(
                    r"464 - GRUPO NET 1 - 18 MESES|465 - GRUPO NET 2 - 18 MESES|466 - GRUPO NET 3 - 18 MESES|"
                    r"467 - GRUPO NET 4 - 18 MESES|471 - GRUPO NET 5 - 18 MESES|802 - GRUPO NET 6 - 18 MESES|"
                    r"803 - GRUPO NET 7 - 18 MESES|",
                    case=False,
                    na=False,
                )
            ),
            "Reemplazo InternetDism": (
                df_group_Intermet["razon_servicio"].isin(
                    ["5030 - DISMINUCIÓN DE PLAN CON VENTA EQUIPO POR REEMPLAZO"]
                )
                & df_group_Intermet["grupo_activacion_orden"].str.contains(
                    r"464 - GRUPO NET 1 - 18 MESES|465 - GRUPO NET 2 - 18 MESES|466 - GRUPO NET 3 - 18 MESES|"
                    r"467 - GRUPO NET 4 - 18 MESES|471 - GRUPO NET 5 - 18 MESES|802 - GRUPO NET 6 - 18 MESES|"
                    r"803 - GRUPO NET 7 - 18 MESES|",
                    case=False,
                    na=False,
                )
            ),
            "Fidepuntos Internet": (
                df_group_Intermet["razon_servicio"].isin(
                    ["1378 - USO DE FIDEPUNTOS (CAMBIA TU MOVIL)"]
                )
                & df_group_Intermet["grupo_activacion_orden"].str.contains(
                    r"464 - GRUPO NET 1 - 18 MESES|465 - GRUPO NET 2 - 18 MESES|466 - GRUPO NET 3 - 18 MESES|"
                    r"467 - GRUPO NET 4 - 18 MESES|471 - GRUPO NET 5 - 18 MESES|802 - GRUPO NET 6 - 18 MESES|"
                    r"803 - GRUPO NET 7 - 18 MESES|",
                    case=False,
                    na=False,
                )
            ),
            "Fidepuntos InternetAum": (
                df_group_Intermet["razon_servicio"].isin(
                    ["5001 - AUMENTO DE PLAN CON VENTA EQUIPO POR FIDE"]
                )
                & df_group_Intermet["grupo_activacion_orden"].str.contains(
                    r"464 - GR UPO NET 1 - 18 MESES|465 - GRUPO NET 2 - 18 MESES|466 - GRUPO NET 3 - 18 MESES|"
                    r"467 - GRUPO NET 4 - 18 MESES|471 - GRUPO NET 5 - 18 MESES|802 - GRUPO NET 6 - 18 MESES|"
                    r"803 - GRUPO NET 7 - 18 MESES|",
                    case=False,
                    na=False,
                )
            ),
            "Fidepuntos InternetDism": (
                df_group_Intermet["razon_servicio"].isin(
                    ["5031 - DISMINUCIÓN DE PLAN CON VENTA EQUIPO POR FIDE"]
                )
                & df_group_Intermet["grupo_activacion_orden"].str.contains(
                    r"464 - GRUPO NET 1 - 18 MESES|465 - GRUPO NET 2 - 18 MESES|466 - GRUPO NET 3 - 18 MESES|"
                    r"467 - GRUPO NET 4 - 18 MESES|471 - GRUPO NET 5 - 18 MESES|802 - GRUPO NET 6 - 18 MESES|"
                    r"803 - GRUPO NET 7 - 18 MESES|",
                    case=False,
                    na=False,
                )
            ),
            "Aumentos Internet": (
                df_group_Intermet["razon_servicio"].isin(
                    ["1322 - AUMENTO DE PLAN / PAQUETE"]
                )
                & df_group["grupo_activacion_orden"].str.contains(
                    r"464 - GRUPO NET 1 - 18 MESES|465 - GRUPO NET 2 - 18 MESES|466 - GRUPO NET 3 - 18 MESES|"
                    r"467 - GRUPO NET 4 - 18 MESES|471 - GRUPO NET 5 - 18 MESES|802 - GRUPO NET 6 - 18 MESES|"
                    r"803 - GRUPO NET 7 - 18 MESES|",
                    case=False,
                    na=False,
                )
            ),
        }

        grupos_ventas_card = {
            "Card": (
                df_group_Card["razon_servicio"].isin(
                    [
                        "1425 - ACTIVACIONES DE LINEAS - SIN EQUIPOS (DEALERS)",
                        "1409 - PORT SIN NUMERO TEMPORERO/SIN EQUIPO (CANAL PRESE)",
                        "1126 - ACTIVACIONES DE LÍNEAS - CON EQUIPOS (EFECTIVO)",
                        "1301 - ACTIVACIONES DE LINEAS - CON EQUIPOS",
                        "1302 - PORT IN CON NUMERO TEMPORERO/CON EQUIPO",
                        "1349 - PORT CON NUMERO TEMPORERO/SIN EQUIPO (CANAL PRESE)",
                        "1402 - ACTIVACIONES LÍNEAS-SIN EQUIPOS (CANAL PRESENCIAL)",
                    ]
                )
                & df_group_Card["grupo_activacion_orden"].str.contains(
                    r"322 - GRUPO CARD SIM ONLY|4 - CARD",
                    case=False,
                    na=False,
                )
            ),
        }

        # Agrupación card
        df_group_Card["tipo_venta"] = None
        for tipo, condicion in grupos_ventas_card.items():
            df_group_Card.loc[condicion, "tipo_venta"] = tipo

        # 2) Extraemos Grupo a partir de dos patrones
        df_group_Card["Grupo1"] = df_group_Card["grupo_activacion_orden"].str.extract(
            r"(\d+) - GRUPO CARD SIM ONLY", expand=False
        )
        df_group_Card["Grupo2"] = df_group_Card["grupo_activacion_orden"].str.extract(
            r"(\d+) - CARD", expand=False
        )

        df_group_Card["Grupo"] = df_group_Card["Grupo1"].fillna(df_group_Card["Grupo2"])
        df_group_Card.drop(["Grupo1", "Grupo2"], axis=1, inplace=True)

        # fin card

        # Agrupación Flex/Max
        df_group["tipo_venta"] = None
        for tipo, condicion in grupos_ventas.items():
            df_group.loc[condicion, "tipo_venta"] = tipo

        # Extraer el número del grupo para agruparlo
        df_group["Grupo"] = (
            df_group["grupo_activacion_orden"]
            .str.extract(r"GRUPO (\d+)", expand=True)
            .bfill(axis=1)[0]
        )

        # Extraer el número del grupo anterior para agruparlo
        df_group["Grupo_Anterior"] = (
            df_group["grupo_activacion_anterior"]
            .str.extract(r"GRUPO (\d+)", expand=True)
            .bfill(axis=1)[0]
        )
        # fin flex/mas

        # Agrupación Internet
        df_group_Intermet["tipo_venta"] = None
        for tipo, condicion in grupos_ventas_internet.items():
            df_group_Intermet.loc[condicion, "tipo_venta"] = tipo

        # Extraer el número del grupo para agruparlo
        df_group_Intermet["Grupo"] = (
            df_group_Intermet["grupo_activacion_orden"]
            .str.extract(r"GRUPO NET (\d+)", expand=True)
            .bfill(axis=1)[0]
        )

        # Extraer el número del grupo anterior para agruparlo
        df_group_Intermet["Grupo_Anterior"] = (
            df_group_Intermet["grupo_activacion_anterior"]
            .str.extract(r"GRUPO NET (\d+)", expand=True)
            .bfill(axis=1)[0]
        )

        # Internet
        df_group_Intermet["Grupo_Anterior"] = df_group_Intermet["Grupo_Anterior"].fillna(0)

        # Fin Agrupacion Internet

        # Rellenar NaN en "Grupo Anterior" con 0
        df_group["Grupo_Anterior"] = df_group["Grupo_Anterior"].fillna(0)

        # Generar conteo
        ventas_validas = df_group.dropna(subset=["tipo_venta", "Grupo"], how="any")
        conteo_ventas = (
            ventas_validas.groupby(
                [
                    "fecha_digitacion_orden",
                    "usuario_creo_orden",                    
                    "tipo_venta",
                    "Grupo",
                    "Grupo_Anterior",
                ]
            )
            .size()
            .reset_index()
        )

        # Internet
        ventas_validas_internet = df_group_Intermet.dropna(
            subset=["tipo_venta", "Grupo"], how="any"
        )
        conteo_ventas_internet = (
            ventas_validas_internet.groupby(
                [
                    "fecha_digitacion_orden",                    
                    "usuario_creo_orden",
                    "tipo_venta",
                    "Grupo",
                    "Grupo_Anterior",
                ]
            )
            .size()
            .reset_index()
        )

        # card
        ventas_validas_card = df_group_Card.dropna(subset=["tipo_venta"], how="any")
        conteo_ventas_card = (
            ventas_validas_card.groupby(
                [
                    "fecha_digitacion_orden",                    
                    "usuario_creo_orden",
                    "tipo_venta",
                    "Grupo",
                ]
            )
            .size()
            .reset_index()
        )

        # Renombrar la columna de conteo
        conteo_ventas.rename(columns={0: "total_ventas"}, inplace=True)
        conteo_ventas_internet.rename(columns={0: "total_ventas"}, inplace=True)
        conteo_ventas_card.rename(columns={0: "total_ventas"}, inplace=True)

        if conteo_ventas.empty:
            raise ValueError("No se encontraron ventas válidas.")

        if conteo_ventas_internet.empty:
            raise ValueError("No se encontraron ventas válidas.")

        if conteo_ventas_card.empty:
            raise ValueError("No se encontraron ventas válidas.")

        resultado = conteo_ventas.reset_index()
        resultado.rename(columns={0: "total_ventas"}, inplace=True)

        # card
        resultado_card = conteo_ventas_card.reset_index()
        resultado_card.rename(columns={0: "total_ventas"}, inplace=True)

        # Internet
        resultado_internet = conteo_ventas_internet.reset_index()
        resultado_internet.rename(columns={0: "total_ventas"}, inplace=True)

        reultado_final = pd.concat(
            [resultado, resultado_internet, resultado_card], ignore_index=True
        )
        reultado_final.rename(columns={"fecha_digitacion_orden": "fecha"}, inplace=True)

        reultado_final["Grupo_Anterior"] = reultado_final["Grupo_Anterior"].fillna(0)

        # asignar los supervisores
        reultado_final["codigo"] = reultado_final["usuario_creo_orden"].str[:7]
        data_supers["codigo"] = data_supers['codigo'].astype(str)        

        df_combinado = pd.merge(reultado_final, data_supers, on="codigo", how="left")
        df_combinado.rename(columns={"supervisor": "supervisor"}, inplace=True)    
        df_combinado = df_combinado.fillna("0")
        # Convierte a entero (int) y luego a string
        df_combinado["supervisor"] = (
            df_combinado["supervisor"]
            .astype(float)  # Asegura que sea float para evitar errores
            .astype(int)  # Conviertes a int (ej. 1025113.0 -> 1025113)
            .astype(str)  # Finalmente, a string ("1025113")
        )
        # Obtener la lista de columnas
        columnas = df_combinado.columns.tolist()

        # Mover "supervisor" antes de "usuario_creo_orden"
        columnas.insert(
            columnas.index("usuario_creo_orden"),
            columnas.pop(columnas.index("supervisor")),
        )
        
        # Reasignar el orden de las columnas
        df_combinado = df_combinado[columnas]

        df_combinado.drop("codigo", axis=1, inplace=True)

        carpeta_destino = entrada_carpeta_destino.get()

        # Define the path for the output file
        resultado_ventas_conjunto = os.path.join(carpeta_destino, "Ventas_Detalle.xlsx")
        df_combinado.to_excel(resultado_ventas_conjunto, index=False)

        # >Este "Ventas conjunto" es el que debe ir en la tabla ventas_detalle, solo le falta incluir la decha
        resultado_ventas_conjunto = os.path.join(
            carpeta_destino, "Ventas_Detalle.xlsx"
        )

        # Guardar en tabla ventas_detalle
        guardar_ventas_detalle_en_db(
            df_combinado, DB_PATH
            )  
        messagebox.showinfo("Listo", "Archivo Guardado Correctamente.⚡")

        # Fin agugacion ventas
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {e}")

# Fin Creacion Venta_Detalles.

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Gestion Data")

# Etiqueta y entrada para la carpeta de origen
etiqueta_carpeta_origen = tk.Label(ventana, text="Carpeta de Origen:")
etiqueta_carpeta_origen.grid(row=0, column=0)

entrada_carpeta_origen = tk.Entry(ventana, width=60)
entrada_carpeta_origen.grid(row=0, column=1)

btn_seleccionar_carpeta_origen = tk.Button(
    ventana, text="Seleccionar Carpeta", command=seleccionar_carpeta_origen, fg="blue"
)
btn_seleccionar_carpeta_origen.grid(row=0, column=2)

# Etiqueta y entrada para la carpeta de destino
etiqueta_carpeta_destino = tk.Label(ventana, text="Carpeta de Destino:")
etiqueta_carpeta_destino.grid(row=1, column=0)

entrada_carpeta_destino = tk.Entry(ventana, width=60)
entrada_carpeta_destino.grid(row=1, column=1)

btn_seleccionar_carpeta_destino = tk.Button(
    ventana, text="Seleccionar Carpeta", command=seleccionar_carpeta_destino, fg="blue"
)
btn_seleccionar_carpeta_destino.grid(row=1, column=2)

# Dropdown para seleccionar dia
etiqueta_dia = tk.Label(ventana, text="Dia:")
etiqueta_dia.grid(row=2, column=0)

menu_dia = ttk.Combobox(ventana, values=[str(i) for i in range(1, 32)], width=10)
menu_dia.grid(row=2, column=1)

# Dropdown para seleccionar mes
etiqueta_mes = tk.Label(ventana, text="Mes:")
etiqueta_mes.grid(row=3, column=0)

menu_mes = ttk.Combobox(ventana, values=[str(i) for i in range(1, 13)], width=10)
menu_mes.grid(row=3, column=1)

# Dropdown para seleccionar año
etiqueta_anio = tk.Label(ventana, text="Año:")
etiqueta_anio.grid(row=4, column=0)

menu_anio = ttk.Combobox(ventana, values=[str(i) for i in range(2019, 2101)], width=10)
menu_anio.grid(row=4, column=1)

# Label mensaje uso de fechas
etiqueta_msj = tk.Label(
    ventana,
    text=(
        "Al seleccionar un mes y año, se generará un archivo solo con los datos de la fecha seleccionada.\n"
        "Si los deja vacío, mostrará todos los datos en cualquier fecha que contenga sin filtrar."
    ),
    fg="red",
    wraplength=300,  # Ancho máximo en píxeles antes de hacer salto de línea
    justify="center",  # Alinear el texto al centro
)
etiqueta_msj.grid(row=5, column=1, padx=8, pady=8)

# Botón para procesar los archivos
btn_procesar = tk.Button(
    ventana, text="Procesar Archivos", command=procesar_archivos, fg="blue"
)
btn_generar_ventas = tk.Button(
    ventana, text="Generar Ventas", command=generar_ventas, fg="red"
)
btn_procesar.grid(row=7, column=1)

btn_generar_ventas.grid(row=10, column=1)

# Ejecutar la ventana
ventana.mainloop()
