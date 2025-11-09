import sqlite3
import openpyxl
import pandas as pd

def conect():
    DB_PATH = r"C:\Users\Usuario\Documents\DBHeromovil\VentasHeromovil.db"
    
    return DB_PATH

def empleados():
    DB_PATH = conect()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""SELECT codigo, nombre
                        FROM usuarios
                        WHERE status = 1
                        AND puesto IN ('Ventas', 'Supervisor')
                        AND codigo NOT IN ('1003779', '1016312', '1020462')
                        ORDER BY nombre ASC;""")
    rows = cursor.fetchall()
    conn.close()

    return rows

def supervisor():
    DB_PATH = conect()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = """
        SELECT codigo, nombre      
            FROM usuarios
            WHERE puesto = 'Supervisor'
			AND status = 1
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    return rows

def pagos(empleado_id):
    """
    Retorna la cantidad (conteo) de registros de la tabla 'pagos'
    que tengan el campo 'userlogin' igual al valor proporcionado.
    """    
    print(f"Empleado ID recibido: {empleado_id}")  # Debugging line
    conn = sqlite3.connect(conect())
    cur = conn.cursor()

    if empleado_id and empleado_id.lower() != "none":
        query = """
        SELECT COUNT(*)
        FROM pagos
        WHERE SUBSTR(userlogin, 1, 7) = ?
        AND strftime('%Y-%m', dte) = strftime('%Y-%m', 'now', 'localtime');        
        """
        cur.execute(query, (empleado_id,))
    else:
        query = """
        SELECT COUNT(*)
        FROM pagos
        WHERE strftime('%Y-%m', dte) = strftime('%Y-%m', 'now', 'localtime');
        """
        cur.execute(query)

    resultado = cur.fetchone()
    conn.close()
    #Debugging lines
    """
    print(f"Consulta ejecutada: {query}")  # Debugging line
    print(f"Resultado de la consulta: {resultado}")  # Debugging line
    """

    if resultado is not None:
        return resultado[0]  # El primer (y único) valor es el conteo
    else:
        return 0

def get_ventas():
    """
    Retorna la cantidad (conteo) de registros de la tabla 'Venta_detalle'
    """    
    conn = sqlite3.connect(conect())
    cur = conn.cursor()

    query = """
    SELECT SUM(total_ventas) AS total_pav
	FROM ventas_detalle
	WHERE tipo_venta != 'Card'
	AND entity_code != 'EX332'	
	AND strftime('%Y-%m', fecha) = strftime('%Y-%m', 'now', 'localtime')
	AND strftime('%Y-%m', fecha) = strftime('%Y-%m', 'now', 'localtime')
    """
    cur.execute(query)   

    resultado = cur.fetchone()

    conn.close()

    if resultado is not None:
        return resultado[0]  # El primer (y único) valor es el conteo
    else:
        return 0

def get_rank_pav(start_date=None, end_date=None):
    """
    Retorna los top 10 usuarios (usuario_creo_orden) y su suma de ventas
    para un rango de fechas o para el mes actual, excluyendo 'Card'.
    """
    conn = sqlite3.connect(conect())
    cur = conn.cursor()

    params = []
    date_filter = ""

    if start_date and end_date:
        date_filter = "fecha BETWEEN ? AND ?"
        params.extend([start_date, end_date])
    elif start_date:
        date_filter = "fecha = ?"
        params.append(start_date)
    elif end_date:
        date_filter = "fecha = ?"
        params.append(end_date)
    else:
        # Filtro por mes y año actual si no se proporcionan fechas
        date_filter = "strftime('%Y-%m', fecha) = strftime('%Y-%m', 'now', 'localtime')"

    query = f"""
    SELECT usuario_creo_orden,
        SUM(total_ventas) AS total_ventas
    FROM ventas_detalle
    WHERE tipo_venta != 'Card'
    AND tipo_venta != 'CardEquipo'
    AND tipo_venta != 'InternetCard'
    AND entity_code  != 'EX332'
    AND {date_filter}
    GROUP BY usuario_creo_orden
    ORDER BY total_ventas DESC
    LIMIT 10;
    """
    cur.execute(query, tuple(params))
    filas = cur.fetchall()

    conn.close()

    return filas

def get_rank_pav_cc():
    """
    Retorna los top 10 usuarios (usuario_creo_orden) y su suma de ventas
    para el mes/año actual, excluyendo 'entidad 44066'.
    """
    conn = sqlite3.connect(conect())
    cur = conn.cursor()

    query = """
    SELECT usuario_creo_orden,
        SUM(total_ventas) AS total_ventas
    FROM ventas_detalle
    WHERE tipo_venta != 'Card'
    AND entity_code  != '44066'
    AND strftime('%Y-%m', fecha) = strftime('%Y-%m', 'now', 'localtime')
    AND strftime('%Y-%m', fecha) = strftime('%Y-%m', 'now', 'localtime')
    GROUP BY usuario_creo_orden
    ORDER BY total_ventas DESC
    LIMIT 10;
    """
    cur.execute(query)
    # fetchall para todas las filas
    filas = cur.fetchall()

    conn.close()

    # 'filas' será una lista de tuplas: [(usuario_creo_orden, total_ventas), ...]
    return filas

def get_recent_activity():
    """
    Obtiene los 3 tipos de venta con más volumen, funcion modificada poara mostrar el dia, y excluir 'Card'.
    1. Si hoy es domingo, obtiene los datos del sábado.
    2. Si no, obtiene los datos de hoy.
    mantener este formato para la compatibilidad con el front-end.
    """
    conn = sqlite3.connect(conect())
    cur = conn.cursor()

    try:        
        query = """
        SELECT usuario_creo_orden, tipo_venta, SUM(total_ventas) AS cantidad
        FROM ventas_detalle
        WHERE date(fecha) = CASE		
            WHEN strftime('%w', 'now', 'localtime') = '0' 
                THEN date('now', '-1 day', 'localtime')   -- si es domingo, usar el sábado
            ELSE date('now', 'localtime')                  -- si no, usar hoy
        END
        AND tipo_venta != 'Card'
        AND entity_code != 'EX332'
        GROUP BY usuario_creo_orden, tipo_venta
        ORDER BY cantidad DESC
        LIMIT 7;
        """
        cur.execute(query)
        
        data = cur.fetchall()

        cur.close()

        return data
    except Exception as e:
        print(f"Error en get_recent_activity: {e}")
        return []

def get_sales_overview():
    """
    Obtiene los 5 tipos de venta más importantes (excluyendo 'Card') del mes actual
    y calcula su porcentaje respecto al total (sin 'Card').
    """
    conn = sqlite3.connect(conect())
    cur = conn.cursor()
    try:
        # Obtener el total de ventas excluyendo 'Card' para el mes actual
        query_total = """
        SELECT SUM(total_ventas) as total
        FROM ventas_detalle
        WHERE tipo_venta != 'Card' 
        AND entity_code != 'EX332'
        AND strftime('%Y-%m', fecha) = strftime('%Y-%m', 'now', 'localtime');
        """
        cur.execute(query_total)
        total_sales_result = cur.fetchone()
        total_sales = total_sales_result[0] if total_sales_result else 0

        if total_sales is None or total_sales == 0:
            cur.close()
            conn.close()
            return {"labels": [], "data": []}

        # Obtener el top 5 de ventas (sin 'Card') para el mes actual
        query_top5 = """
        SELECT tipo_venta, SUM(total_ventas) AS total
            FROM ventas_detalle
            WHERE tipo_venta IN (
                'Flex/Max',
                'Migraciones',
                'Internet',
                'Reemplazo Aumento',
                'Aumentos Pospago',
                'Aumentos Internet'
            )
            AND entity_code != 'EX332'
            AND strftime('%Y-%m', fecha) = strftime('%Y-%m', 'now', 'localtime')
            GROUP BY tipo_venta
            ORDER BY total DESC;
        """
        cur.execute(query_top5)
        top5_sales = cur.fetchall()
        cur.close()
        conn.close()

        labels = []
        data = []
        for row in top5_sales:
            labels.append(row[0])
            percentage = (row[1] / total_sales) * 100
            data.append(round(percentage, 2))

        return {"labels": labels, "data": data}
    except Exception as e:
        print(f"Error en get_sales_overview: {e}")
        # Asegurarse de cerrar la conexión si hay un error
        if 'cur' in locals() and cur:
            cur.close()
        if 'conn' in locals() and conn:
            conn.close()
        return {"labels": [], "data": []}

# Guarda el DataFrame 'filtrado' en la base de datos SQLite en tabla transacciones
def guardar_filtrado_en_db(filtrado):
    # Reemplaza NaN por None
    filtrado = filtrado.where(pd.notnull(filtrado), None)

    # Conexión
    conn = sqlite3.connect(conect())
    cur = conn.cursor()

    TABLE_NAME = "transacciones"

    # 1️ Crear tabla con restricción UNIQUE
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_transaccion TEXT NOT NULL,
        fecha_digitacion_orden DATE,
        fecha_termino_orden DATE,
        estado_transaccion TEXT,
        usuario_creo_orden TEXT NOT NULL,
        entity_code TEXT,
        subcanal INTEGER,
        tipo_actividad TEXT,
        razon_servicio TEXT NOT NULL,
        telefono TEXT NOT NULL,
        imei TEXT NOT NULL,
        nom_plan TEXT,
        grupo_activacion_orden TEXT,
        grupo_activacion_anterior TEXT,
        UNIQUE (id_transaccion, usuario_creo_orden, razon_servicio, telefono, imei)
    );
    """
    cur.execute(create_table_query)

    # 2️ Insertar o actualizar con ON CONFLICT
    insert_query = f"""
    INSERT INTO {TABLE_NAME} (
        id_transaccion, fecha_digitacion_orden, fecha_termino_orden,
        estado_transaccion, usuario_creo_orden, entity_code, subcanal, tipo_actividad,
        razon_servicio, telefono, imei, nom_plan, grupo_activacion_orden, grupo_activacion_anterior
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(id_transaccion, usuario_creo_orden, razon_servicio, telefono, imei)
    DO UPDATE SET
        estado_transaccion = excluded.estado_transaccion
    WHERE transacciones.estado_transaccion != excluded.estado_transaccion;
    """

    # 3️ Ejecutar en bloque
    data = [
        (
            row["id_transaccion"],
            str(row["fecha_digitacion_orden"]),
            str(row["fecha_termino_orden"]),
            row["estado_transaccion"],
            row["usuario_creo_orden"],
            row["entity_code"],
            row["subcanal"],
            row["tipo_actividad"],
            row["razon_servicio"],
            str(row["telefono"]),
            str(row["imei"]),
            row["nom_plan"],
            row["grupo_activacion_orden"],
            row["grupo_activacion_anterior"],
        )
        for _, row in filtrado.iterrows()
    ]

    cur.executemany(insert_query, data)

    conn.commit()
    conn.close()

# Guarda el los datos procedados en la base de datos SQLite ventas_detalle
def guardar_ventas_detalle_en_db(df_ventas):

    conn = sqlite3.connect(conect())
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS ventas_detalle (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_code TEXT,
            subcanal INTEGER,
            fecha DATE,
            supervisor TEXT,
            usuario_creo_orden TEXT,
            tipo_venta TEXT,
            Grupo INTEGER,
            Grupo_Anterior INTEGER,
            total_ventas INTEGER,  
            Comision_100 INTEGER,
            Comision_75 INTEGER        
        );
    """
    )

    # OPCIONAL: borrar todo antes de insertar
    cur.execute("DELETE FROM ventas_detalle")
    conn.commit()

    insert_sql = """
        INSERT INTO ventas_detalle (
            entity_code,
            subcanal,
            fecha,
            supervisor,
            usuario_creo_orden,
            tipo_venta,
            Grupo,
            Grupo_Anterior,
            total_ventas,
            Comision_100,
            Comision_75            
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) """

    for _, row in df_ventas.iterrows():
        values = (
            row["entity_code"],
            row["subcanal"],
            str(row["fecha"]),  # str() si viene como datetime
            row["supervisor"],
            row["usuario_creo_orden"],
            row["tipo_venta"],
            int(row["Grupo"]),
            int(row["Grupo_Anterior"]),
            int(row["total_ventas"]),
            int(row["Comision_100"]),
            int(row["Comision_75"]),
        )
        cur.execute(insert_sql, values)

    conn.commit()
    conn.close()

# Guarda los pagos desde un archivo Excel a la tabla 'pagos'
def insertar_pagos(df_pagos):
    try:
        # Conectar a la base de datos SQLite
        conn = sqlite3.connect(conect())
        cursor = conn.cursor()

        # 1️ Crear tabla si no existe
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pagos (
            id_tipo_compania INTEGER,
            compania TEXT,
            ent_code TEXT,
            estado TEXT,
            entity_name	TEXT,
            id_canal INTEGER,
            id_subcanal	INTEGER,
            dte	TEXT,
            monto REAL,
            custcode TEXT,
            id_cuenta TEXT,
            cn TEXT,
            fn TEXT,
            cachknum TEXT,
            userlogin TEXT,
            caja TEXT,
            concepto_pago TEXT,
            transaction_id INTEGER,
            fp_efectivo REAL,
            fp_tarjeta REAL,
            fp_cheque REAL,
            fp_otras REAL,
            tel_contacto TEXT,
            tel_contacto2 TEXT,
            UNIQUE(ent_code, transaction_id, custcode, dte, monto)
        );
        """)

        # 2️ Leer el archivo Excel
        wb = openpyxl.load_workbook(df_pagos, data_only=True)
        hoja = wb.active

        # 3️ Preparar datos
        datos_a_insertar = []   # ignora encabezados
        for fila in hoja.iter_rows(min_row=2, values_only=True):  # type: ignore
            if any(fila):  # evita filas vacías
                datos_a_insertar.append(fila)

        # 4️ Insertar datos (evita duplicados con INSERT OR IGNORE)
        cursor.executemany("""
            INSERT OR IGNORE INTO pagos VALUES (
                ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?
            )
        """, datos_a_insertar)

        # 5️ Guardar cambios
        conn.commit()
        conn.close()
        print(f"{len(datos_a_insertar)} registros procesados correctamente (sin duplicados).")       

    except Exception as e:
        print(f"Hubo un problema al insertar los datos: {e}")
       
#Guarda los objetivos desde un archivo Excel a la tabla 'objetivos'
def insertar_objetivos(df_objetivos):

    try:
        # Conectar a la base de datos SQLite
        conn = sqlite3.connect(conect())
        cursor = conn.cursor()

        # Leer el archivo Excel
        wb = openpyxl.load_workbook(df_objetivos)
        if wb.sheetnames:
            hoja = wb.active
        else:
            raise ValueError("El archivo Excel no contiene hojas.")

        # Iterar sobre las filas del archivo Excel e insertar en la tabla
        for fila in hoja.iter_rows(min_row=2, values_only=True): # type: ignore
            cursor.execute("""
                INSERT INTO objetivos (id_empleado, fecha, sim_card_prepago, flex_max, fijos_hfc_dth, internet_pospago,
                                    migraciones_pospago_net, fidepuntos_pospago, fidepuntos_up, reemplazo_pospago,
                                    reemplazo_up, fide_reemp_internet_up, aumentos_plan_pos_net, recargas)
                VALUES (?, ?,?,?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, fila)

        # Confirmar la transacción y cerrar la conexión
        conn.commit()
        conn.close()
        print("Objetivos insertados correctamente")

    except Exception as e:
        print(f"Hubo un problema al insertar los objetivos: {e}")