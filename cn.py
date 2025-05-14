import sqlite3

def conect():
    DB_PATH = r"C:\Users\Spectre\Documents\DBHeromovil\VentasHeromovil.db"
    
    return DB_PATH

def empleados():
    DB_PATH = conect()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT codigo, nombre FROM usuarios WHERE status = 1")
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

def pagos(userlogin):    
    """
    Retorna la cantidad (conteo) de registros de la tabla 'pagos'
    que tengan el campo 'userlogin' igual al valor proporcionado.
    """    
    conn = sqlite3.connect(conect())
    cur = conn.cursor()

    if userlogin and userlogin.lower() != "none":
        # query = "SELECT COUNT(*) FROM pagos WHERE SUBSTR(userlogin, 1, 7) = ?"
        query = """
        SELECT COUNT(*)
        FROM pagos
        WHERE SUBSTR(userlogin, 1, 7) = ?
        AND SUBSTR(dte,4,2) = strftime('%m','now', 'localtime')
        AND SUBSTR(dte,7,4) = strftime('%Y','now', 'localtime')
        """
        cur.execute(query, (userlogin,))
    else:
        query = """
        SELECT COUNT(*)
        FROM pagos
        WHERE SUBSTR(dte,4,2) = strftime('%m','now', 'localtime')
        AND SUBSTR(dte,7,4) = strftime('%Y','now', 'localtime')
        """
        cur.execute(query)

    resultado = cur.fetchone()

    conn.close()

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
    AND usuario_creo_orden  != '1013843 - JUAN CARLOS GRULLON GARCIA'
    AND usuario_creo_orden  != '1013437 - ANABEL MARTE'
    AND usuario_creo_orden  != '1018784 - KANDY PENELOPE JIMENEZ JIMENEZ'
    AND usuario_creo_orden  != '1018294 - MARIA VANESSA MOSQUEA ABAD'
    AND usuario_creo_orden  != '1018940 - ADAMARYS RODRIGUEZ BATISTA'
    AND usuario_creo_orden  != '2025551 - ANGEL NOEL CAMPOS LORA'
    AND usuario_creo_orden  != '1003794 - CARINA DE LA CRUZ CASTILLO' 
    AND usuario_creo_orden  != '2025552 - ARLYN ROSARIO LOPEZ'  
    AND usuario_creo_orden  != '1025332 - EDWIN GRULLON ROSARIO'
    AND usuario_creo_orden  != '1025727 - FLORANGEL ISABEL ALMONTE TOLENTINO'
    AND usuario_creo_orden  != '1025456 - ANDISON LIMA MATIAS'
    AND usuario_creo_orden  != '1025677 - MAURIFE MATEO PEÑA'
    AND usuario_creo_orden  != '1025674 - ROLANDO PICHARDO DISLA'
    AND usuario_creo_orden  != '1025676 - MARIA LUISA DELGADO DE LA CRUZ'
    AND usuario_creo_orden  != '1025679 - YISELLE ESPINAL VARGAS'
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
