# chart_utils.py
import sqlite3

# funcion para obtener los datos de ventas totales
def get_chart_data(db_path, anio="2025", empleado_id=None):
    """
    Devuelve un dict con { labels, datasets }, filtrando por:
    - El año (anio)
    - El empleado (opcional).
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Construir la consulta base
    query = """
    SELECT
      tipo_venta,
      CAST(strftime('%m', fecha) AS INTEGER) AS mes,
      SUM(total_ventas) AS total
    FROM ventas_detalle
    WHERE strftime('%Y', fecha) = ?
    """
    params = [anio]

    if empleado_id:
        # Solo si empleado_id no es None ni está vacío
        query += " AND usuario_creo_orden LIKE ?"
        params.append(empleado_id + " - %")  # '1016312 - %'
    # si empleado_id es None, no añadimos la condición

    query += """
    GROUP BY tipo_venta, mes
    ORDER BY tipo_venta, mes
    """

    cur.execute(query, tuple(params))
    rows = cur.fetchall()
    conn.close()

    # Construir el diccionario data_dict...
    # (igual que antes)
    data_dict = {}
    for tipo_venta, mes, total in rows:
        if tipo_venta not in data_dict:
            data_dict[tipo_venta] = [0]*12
        data_dict[tipo_venta][mes-1] = total

    # labels (meses)
    labels = [
        "Enero",
        "Febrero",
        "Marzo",
        "Abril",
        "Mayo",
        "Junio",
        "Julio",
        "Agosto",
        "Septiembre",
        "Octubre",
        "Noviembre",
        "Diciembre",
    ]

    # mapa de colores, ajusta a tus tipos de venta
    color_map = {
        "Flex/Max": "rgba(231, 76, 60, 1)",  # Rojo
        "Internet": "rgba(22, 160, 133, 1)",  # Verde azulado
        "Migraciones": "rgba(155, 89, 182, 1)",  # Morado
        "Aumentos Pospago": "rgba(255, 87, 51, 1)",  # Naranja
        "Aumentos Internet": "rgba(142, 68, 173, 1)",  # Morado oscuro
        "Reemplazo Pospago": "rgba(52, 152, 219, 1)",  # Azul
        "Reemplazo Aumento": "rgba(26, 188, 156, 1)",  # Turquesa
        "Reemplazo Disminucion": "rgba(241, 196, 15, 1)",  # Amarillo claro
        "Fidepuntos Pospago": "rgba(46, 204, 113, 1)",  # Verde
        "Fidepuntos Aumento": "rgba(243, 156, 18, 1)",  # Amarillo
        "Fidepuntos Disminucion": "rgba(52, 73, 94, 1)",  # Gris oscuro
        "Reemplazo Internet": "rgba(211, 84, 0, 1)",  # Naranja oscuro
        "Fidepuntos Internet": "rgba(41, 128, 185, 1)",  # Azul oscuro
        "Fidepuntos InternetAum": "rgba(230, 126, 34, 1)",  # Naranja claro
        "Fidepuntos InternetDism": "rgba(189, 195, 199, 1)",  # Gris claro
        "Reemplazo InternetAum": "rgba(192, 57, 43, 1)",  # Rojo oscuro
        "Reemplazo InternetDism": "rgba(127, 140, 141, 1)",  # Gris claro
    }

    datasets = []
    for tipo, values in data_dict.items():
        datasets.append(
            {
                "label": tipo,
                "data": values,
                "backgroundColor": color_map.get(tipo, "rgba(0,0,0,0.5)"),
                "borderColor": color_map.get(tipo, "rgba(0,0,0,1)"),
                "borderWidth": 2,
            }
        )

    return {"labels": labels, "datasets": datasets}

# funcion para retornar el resultado de los logros
def get_chart_data_logro(db_path, anio="2025", empleado_id=None):
    """
    Devuelve un dict con { labels, datasets }, filtrando por:
    - El año (anio)
    - El empleado (opcional).
    Calcula el logro en porcentaje para cada tipo de venta.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Construir la consulta base
    query = """
    SELECT
        vd.tipo_venta,
        CAST(strftime('%m', vd.fecha) AS INTEGER) AS mes,
        SUM(vd.total_ventas) AS total_ventas,
        o.sim_card_prepago,
        o.flex_max,        
        o.internet_pospago,
        o.migraciones_pospago_net,
        o.fidepuntos_pospago,
        o.fidepuntos_up,
        o.reemplazo_pospago,
        o.reemplazo_up,
        o.fide_reemp_internet_up,
        o.aumentos_plan_pos_net,
        o.recargas
    FROM ventas_detalle vd
    INNER JOIN objetivos o ON vd.usuario_creo_orden LIKE o.id_empleado || ' - %' AND strftime('%Y', o.fecha) = ?
    WHERE strftime('%Y', vd.fecha) = ?    
    """
    params = [anio, anio]

    if empleado_id:
        # Solo si empleado_id no es None ni está vacío
        query += " AND vd.usuario_creo_orden LIKE ?"
        params.append(empleado_id + " - %")  # '1016312 - %'
    # si empleado_id es None, no añadimos la condición

    query += """
    GROUP BY vd.tipo_venta, mes, o.flex_max, o.fijos_hfc_dth, o.internet_pospago, 
    o.migraciones_pospago_net, o.fidepuntos_pospago, o.fidepuntos_up, o.reemplazo_pospago, o.reemplazo_up,
    o.fide_reemp_internet_up, o.aumentos_plan_pos_net
    ORDER BY vd.tipo_venta, mes
    """

    cur.execute(query, tuple(params))
    rows = cur.fetchall()
    conn.close()

    # Construir el diccionario data_dict...
    data_dict = {}
    for (
        tipo_venta,
        mes,
        total_ventas,        
        flex_max,        
        internet_pospago,
        migraciones_pospago_net,
        fidepuntos_pospago,
        fidepuntos_up,
        reemplazo_pospago,
        reemplazo_up,
        fide_reemp_internet_up,
        aumentos_plan_pos_net,
        recargas,
    ) in rows:

        objetivo = None
        if tipo_venta == "Flex/Max":
            objetivo = flex_max
        elif tipo_venta == "Internet":
            objetivo = internet_pospago
        elif tipo_venta == "Migraciones":
            objetivo = migraciones_pospago_net
        elif tipo_venta == "Fidepuntos Pospago":
            objetivo = fidepuntos_pospago
        elif tipo_venta == "Fidepuntos Aumento":
            objetivo = fidepuntos_up
        elif tipo_venta == "Reemplazo Pospago":
            objetivo = reemplazo_pospago
        elif tipo_venta == "Reemplazo Aumento":
            objetivo = reemplazo_up
        elif tipo_venta == "Fide Reemp Internet Up":
            objetivo = fide_reemp_internet_up
        elif tipo_venta == "Aumentos Plan Pos Net":
            objetivo = aumentos_plan_pos_net       

        if objetivo is not None:
            logro_porcentaje = (total_ventas * 100.0) / objetivo
            if tipo_venta not in data_dict:
                data_dict[tipo_venta] = [0] * 12
            data_dict[tipo_venta][mes - 1] = logro_porcentaje

            datasets = []

    # labels (meses)
    labels = [
        "Enero",
        "Febrero",
        "Marzo",
        "Abril",
        "Mayo",
        "Junio",
        "Julio",
        "Agosto",
        "Septiembre",
        "Octubre",
        "Noviembre",
        "Diciembre",
    ]

    # mapa de colores, ajusta a tus tipos de venta
    color_map = {
        "Flex/Max": "rgba(231, 76, 60, 1)",  # Rojo
        "Internet": "rgba(22, 160, 133, 1)",  # Verde azulado
        "Migraciones": "rgba(155, 89, 182, 1)",  # Morado
        "Aumentos Pospago": "rgba(255, 87, 51, 1)",  # Naranja
        "Aumentos Internet": "rgba(142, 68, 173, 1)",  # Morado oscuro
        "Reemplazo Pospago": "rgba(52, 152, 219, 1)",  # Azul
        "Reemplazo Aumento": "rgba(26, 188, 156, 1)",  # Turquesa
        "Reemplazo Disminucion": "rgba(241, 196, 15, 1)",  # Amarillo claro
        "Fidepuntos Pospago": "rgba(46, 204, 113, 1)",  # Verde
        "Fidepuntos Aumento": "rgba(243, 156, 18, 1)",  # Amarillo
        "Fidepuntos Disminucion": "rgba(52, 73, 94, 1)",  # Gris oscuro
        "Reemplazo Internet": "rgba(211, 84, 0, 1)",  # Naranja oscuro
        "Fidepuntos Internet": "rgba(41, 128, 185, 1)",  # Azul oscuro
        "Fidepuntos InternetAum": "rgba(230, 126, 34, 1)",  # Naranja claro
        "Fidepuntos InternetDism": "rgba(189, 195, 199, 1)",  # Gris claro
        "Reemplazo InternetAum": "rgba(192, 57, 43, 1)",  # Rojo oscuro
        "Reemplazo InternetDism": "rgba(127, 140, 141, 1)",  # Gris claro
    }

    for tipo, values in data_dict.items():
        datasets.append(
            {
                "label": tipo,
                "data": values,
                "backgroundColor": color_map.get(tipo, "rgba(0,0,0,0.5)"),
                "borderColor": color_map.get(tipo, "rgba(0,0,0,1)"),
                "borderWidth": 2,
            }
        )

        return {"labels": labels, "datasets": datasets}
