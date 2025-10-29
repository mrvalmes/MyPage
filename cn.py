import sqlite3

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
    print(f"Consulta ejecutada: {query}")  # Debugging line
    print(f"Resultado de la consulta: {resultado}")  # Debugging line

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
	AND entity_code = '44066'
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

def get_rank_pav():
    """
    Retorna los top 10 usuarios (usuario_creo_orden) y su suma de ventas
    para el mes/año actual, excluyendo 'Card'.
    """
    conn = sqlite3.connect(conect())
    cur = conn.cursor()

    query = """
    SELECT usuario_creo_orden,
        SUM(total_ventas) AS total_ventas
    FROM ventas_detalle
    WHERE tipo_venta != 'Card'
    AND tipo_venta != 'CardEquipo'
    AND tipo_venta != 'InternetCard'
    AND entity_code  != 'EX332'
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
