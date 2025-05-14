# chart_utils.py
import sqlite3


def get_chart_data(db_path, anio="2025", empleado_id=None, supervisor_id=None):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

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
        query += " AND usuario_creo_orden LIKE ?"
        params.append(empleado_id + " - %")

    if supervisor_id:
        query += " AND supervisor = ?"
        params.append(supervisor_id)

    query += """
    GROUP BY tipo_venta, mes
    ORDER BY tipo_venta, mes
    """

    print(query)
    print(params)

    cur.execute(query, tuple(params))
    rows = cur.fetchall()
    conn.close()

    # data_dict original: { tipo_venta: [0..11], ... }
    data_dict = {}
    for tipo_venta, mes, total in rows:
        if tipo_venta not in data_dict:
            data_dict[tipo_venta] = [0] * 12
        data_dict[tipo_venta][mes - 1] = total

    # Definir agrupaciones
    groups_map = {
        "Card": ["Card"],
        "Flex/Max": ["Flex/Max"],
        "Internet": ["Internet"],
        "Migraciones": ["Migraciones", "Migraciones Net"],
        "Fidepuntos Pos": ["Fidepuntos Pospago", "Fidepuntos Disminucion"],
        "Fidepuntos Up": ["Fidepuntos Aumento"],
        "Reemplazo Pos": ["Reemplazo Pospago", "Reemplazo Disminucion"],
        "Reemplazo Up": ["Reemplazo Aumento"],
        "Fide Reemp Internet Up": [
            "Reemplazo Internet",
            "Fidepuntos Internet",
            "Fidepuntos InternetAum",
            "Fidepuntos InternetDism",
            "Reemplazo InternetAum",
            "Reemplazo InternetDism",
        ],
        "Aumentos": ["Aumentos Pospago", "Aumentos Internet"],
    }

    # Crear un diccionario nuevo con las categorías finales
    # Inicializamos en 0
    agrupado_dict = {}
    for categoria in groups_map:
        agrupado_dict[categoria] = [0] * 12

    # Rellenar agrupado_dict sumando los arrays de data_dict
    for categoria, lista_tipos in groups_map.items():
        for tv in lista_tipos:
            if tv in data_dict:
                # Sumar cada mes
                for i in range(12):
                    agrupado_dict[categoria][i] += data_dict[tv][i]

    # Construir labels
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

    # Colores para las nuevas categorías (no para los tipos originales)
    color_map = {
        "Card": "rgba(255, 255, 0, 1)",
        "Flex/Max": "rgba(1, 126, 250, 1)",
        "Internet": "rgba(0, 255, 0, 1)",
        "Migraciones": "rgba(155, 89, 182, 1)",
        "Fidepuntos Pos": "rgba(46, 204, 113, 1)",
        "Fidepuntos Up": "rgba(243, 156, 18, 1)",
        "Reemplazo Pos": "rgba(52, 152, 219, 1)",
        "Reemplazo Up": "rgba(26, 188, 156, 1)",
        "Fide Reemp Internet Up": "rgba(231, 76, 60, 1)",
        "Aumentos": "rgba(128, 128, 128, 0.5)",
    }

    # Crear datasets
    datasets = []
    for cat, values in agrupado_dict.items():
        datasets.append(
            {
                "label": cat,
                "data": values,
                "backgroundColor": color_map.get(cat, "rgba(0,0,0,0.5)"),
                "borderColor": color_map.get(cat, "rgba(0,0,0,1)"),
                "borderWidth": 2,
            }
        )

    return {"labels": labels, "datasets": datasets}


# chart con logro, se agrega el objetivo
def get_chart_data_logro(db_path, anio="2025", empleado_id=None, supervisor_id=None):
    """
    Devuelve un dict con {labels, datasets}, filtrando por año/empleado/supervisor.
    Cada categoría es la suma de varios tipo_venta (groups_map).
    Calcula el porcentaje de logro = sum(ventas) / sum(objetivos) * 100
    para cada mes (1..12).
    """
    print("Supervisor:", supervisor_id)
    print("Empleado:", empleado_id)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    if empleado_id and empleado_id.lower() != "none":
        # Consulta base
        query = """
        SELECT
            vd.tipo_venta,
            CAST(strftime('%m', vd.fecha) AS INTEGER) AS mes,
            SUM(vd.total_ventas) AS total_ventas,
            -- Objetivos (uno por mes, supuestamente)
            o.sim_card_prepago,
            o.flex_max,
            o.internet_pospago,
            o.migraciones_pospago_net,
            o.fidepuntos_pospago,
            o.fidepuntos_up,
            o.reemplazo_pospago,
            o.reemplazo_up,
            o.fide_reemp_internet_up,
            o.aumentos_plan_pos_net
        FROM ventas_detalle vd
        LEFT JOIN objetivos o 
            ON vd.usuario_creo_orden LIKE o.id_empleado || ' - %'
            AND strftime('%Y', o.fecha) = ?
            AND strftime('%m', o.fecha) = strftime('%m', vd.fecha)
        WHERE strftime('%Y', vd.fecha) = ?
        """
        params = [anio, anio]
        query += " AND vd.usuario_creo_orden LIKE ?"
        params.append(empleado_id + " - %") 
        query += """
        GROUP BY vd.tipo_venta, mes,
                o.sim_card_prepago,
                o.flex_max, o.internet_pospago, 
                o.migraciones_pospago_net, o.fidepuntos_pospago, 
                o.fidepuntos_up, o.reemplazo_pospago, o.reemplazo_up,
                o.fide_reemp_internet_up, o.aumentos_plan_pos_net
        ORDER BY vd.tipo_venta, mes
        """        

    if supervisor_id and supervisor_id.lower() != "none":
        # Consulta base
        query = """
        SELECT
            vd.tipo_venta,
            CAST(strftime('%m', vd.fecha) AS INTEGER) AS mes,
            SUM(vd.total_ventas) AS total_ventas,
            -- Objetivos (uno por mes, supuestamente)
            o.sim_card_prepago,
            o.flex_max,
            o.internet_pospago,
            o.migraciones_pospago_net,
            o.fidepuntos_pospago,
            o.fidepuntos_up,
            o.reemplazo_pospago,
            o.reemplazo_up,
            o.fide_reemp_internet_up,
            o.aumentos_plan_pos_net
        FROM ventas_detalle vd
        LEFT JOIN objetivos o 
            ON vd.supervisor = o.id_empleado
            AND strftime('%Y', o.fecha) = ?
            AND strftime('%m', o.fecha) = strftime('%m', vd.fecha)
        WHERE strftime('%Y', vd.fecha) = ?
        """
        params = [anio, anio]
        query += " AND vd.supervisor = ?"
        params.append(supervisor_id)    
        query += """
        GROUP BY vd.tipo_venta, mes,
                o.sim_card_prepago,
                o.flex_max, o.internet_pospago, 
                o.migraciones_pospago_net, o.fidepuntos_pospago, 
                o.fidepuntos_up, o.reemplazo_pospago, o.reemplazo_up,
                o.fide_reemp_internet_up, o.aumentos_plan_pos_net
        ORDER BY vd.tipo_venta, mes
        """    
        
    cur.execute(query, tuple(params))
    rows = cur.fetchall()
    conn.close()
    print(query)

    # 2) Estructuras "raw": guardan los valores
    #    sin agrupar en categorías todavía.
    #    raw_ventas[tv] => array de 12
    #    raw_obj[tv]    => array de 12
    raw_ventas = {}
    raw_obj = {}

    # Llenar con 0..12 para cada "tipo_venta" que aparezca
    # (O incluso si no aparece, lo forzamos luego)
    # Recorremos las filas:
    for (
        tipo_venta,
        mes,
        total_ventas,
        sim_card_prepago,
        flex_max,
        internet_pospago,
        migraciones_pospago_net,
        fidepuntos_pospago,
        fidepuntos_up,
        reemplazo_pospago,
        reemplazo_up,
        fide_reemp_internet_up,
        aumentos_plan_pos_net,
    ) in rows:
        # Asegurar array de 12        
        if tipo_venta not in raw_ventas:
            raw_ventas[tipo_venta] = [0] * 12
            raw_obj[tipo_venta] = [0] * 12

        # Sumar las ventas
        raw_ventas[tipo_venta][mes - 1] += total_ventas

        # Determinar objetivo "por tipo_venta"
        # Ajusta si tienes un grouping map aquí,
        # pero en este paso interpretamos 1:1
        # (ej. "Flex/Max" => flex_max).
        objetivo_val = 0
        if tipo_venta == "Card":
            objetivo_val = sim_card_prepago or 0
        elif tipo_venta == "Flex/Max":
            objetivo_val = flex_max or 0
        elif tipo_venta == "Internet":
            objetivo_val = internet_pospago or 0
        elif tipo_venta == "Migraciones":
            objetivo_val = migraciones_pospago_net or 0
        elif tipo_venta in ("Fidepuntos Pospago", "Fidepuntos Disminucion"):
            objetivo_val = fidepuntos_pospago or 0
        elif tipo_venta == "Fidepuntos Aumento":
            objetivo_val = fidepuntos_up or 0
        elif tipo_venta in ("Reemplazo Pospago", "Reemplazo Disminucion"):
            objetivo_val = reemplazo_pospago or 0
        elif tipo_venta == "Reemplazo Aumento":
            objetivo_val = reemplazo_up or 0
        elif tipo_venta == "Fide Reemp Internet Up":
            objetivo_val = fide_reemp_internet_up or 0
        elif tipo_venta in ("Aumentos Pospago", "Aumentos Internet"):
            objetivo_val = aumentos_plan_pos_net or 0
        # agregar mas condiciones, cuando sean necesarias

        raw_obj[tipo_venta][mes - 1] += objetivo_val

    # 3) groups_map => agrupar varios "tipo_venta" en una categoría final
    groups_map = {
        "Card": ["Card"],
        "Flex/Max": ["Flex/Max"],
        "Internet": ["Internet"],
        "Migraciones": ["Migraciones", "Migraciones Net"],
        "Fidepuntos Pos": ["Fidepuntos Pospago", "Fidepuntos Disminucion"],
        "Fidepuntos Up": ["Fidepuntos Aumento"],
        "Reemplazo Pos": ["Reemplazo Pospago", "Reemplazo Disminucion"],
        "Reemplazo Up": ["Reemplazo Aumento"],
        "Fide Reemp Internet Up": [
            "Reemplazo Internet",
            "Fidepuntos Internet",
            "Fidepuntos InternetAum",
            "Fidepuntos InternetDism",
            "Reemplazo InternetAum",
            "Reemplazo InternetDism",
        ],
        "Aumentos": ["Aumentos Pospago", "Aumentos Internet"],
    }

    # Para asegurar que incluso categorías no aparecidas queden con 0
    # creamos un diccionario final_ventas, final_obj
    # con 12 ceros para cada categoría.
    final_ventas = {}
    final_obj = {}
    for cat in groups_map.keys():
        final_ventas[cat] = [0] * 12
        final_obj[cat] = [0] * 12

    # Sumar sub-tipos en la categoría
    # Ej: "Aumentos" => "Aumentos Pospago", "Aumentos Internet"
    # si raw_ventas["Aumentos Pospago"] existe, la sumo, etc.
    for cat, lista_tipos in groups_map.items():
        for tv in lista_tipos:
            # Sumar arrays si existen
            if tv in raw_ventas:
                for i in range(12):
                    final_ventas[cat][i] += raw_ventas[tv][i]
                    final_obj[cat][i] += raw_obj[tv][i]

    # 4) Calcular el % de logro = final_ventas / final_obj
    #    si final_obj es 0 => 0%
    logro_dict = {}
    for cat in groups_map.keys():
        logro_dict[cat] = [0] * 12
        # print("Logro:",logro_dict)
        for i in range(12):
            obj_val = final_obj[cat][i]
            # print("obj_val:", obj_val)
            ven_val = final_ventas[cat][i]
            # print("ven_val:", ven_val)
            if obj_val > 0:
                logro_dict[cat][i] = round((ven_val / obj_val) * 100, 2)
            else:
                logro_dict[cat][i] = 0  # o 0.0

    # 5) labels (meses)
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

    # 6) Construir datasets => usando logro_dict
    color_map = {
        "Card": "rgba(255, 255, 0, 1)",
        "Flex/Max": "rgba(1, 126, 250, 1)",
        "Internet": "rgba(0, 255, 0, 1)",
        "Migraciones": "rgba(155, 89, 182, 1)",
        "Fidepuntos Pos": "rgba(46, 204, 113, 1)",
        "Fidepuntos Up": "rgba(243, 156, 18, 1)",
        "Reemplazo Pos": "rgba(52, 152, 219, 1)",
        "Reemplazo Up": "rgba(26, 188, 156, 1)",
        "Fide Reemp Internet Up": "rgba(231, 76, 60, 1)",
        "Aumentos": "rgba(128, 128, 128, 0.5)",
    }

    datasets = []
    for cat in groups_map.keys():
        datasets.append(
            {
                "label": cat,
                "data": logro_dict[cat],
                "backgroundColor": color_map.get(cat, "rgba(0,0,0,0.5)"),
                "borderColor": color_map.get(cat, "rgba(0,0,0,1)"),
                "borderWidth": 2,
            }
        )

    return {"labels": labels, "datasets": datasets}
