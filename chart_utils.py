# chart_utils.py
import sqlite3


def get_chart_data(db_path, anio="2025", empleado=None):
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

    # Si el empleado no es None, agregamos una condición en el WHERE
    if empleado:
        query += " AND usuario_creo_orden = ?"
        params.append(empleado)

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
