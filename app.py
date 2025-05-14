from flask import Flask, render_template, jsonify, request
from chart_utils import get_chart_data, get_chart_data_logro
from cn import conect, empleados, supervisor, pagos, get_ventas, get_rank_pav
import sqlite3

app = Flask(__name__)

@app.route("/")
def index():
    # Renderiza tu archivo index.html
    return render_template("login.html")

@app.route("/home")
def home():
    # Renderiza reportes.html
    return render_template("Home.html")

@app.route("/dashboard")
def dashboard():
    # Renderiza dashboard.html
    return render_template("dashboard.html")

@app.route("/Mantenimientos")
def Mantenimientos():
    # Renderiza dashboard.html
    return render_template("Mantenimientos.html")

@app.route("/Comisiones")
def Comisiones():
    # Renderiza dashboard.html
    return render_template("Comisiones.html")

@app.route("/chart-data")
def chart_data():
    anio = request.args.get("anio", "2025")
    empleado_id = request.args.get("empleado")  # None si no viene
    supervisor_id = request.args.get("supervisor")  # None si no viene
    modo = request.args.get("modo")

    # Si 'empleado_id' es "None" (cadena) o está vacío, conviértelo a None real:
    if not empleado_id or empleado_id.lower() == "none":
        empleado_id = None

    if not supervisor_id or supervisor_id.lower() == "none":
        supervisor_id = None

    if not modo or modo.lower() == "none":
        modo = "resultados"

    if modo == "logro":
        data = get_chart_data_logro(conect(), anio, empleado_id, supervisor_id)

    elif modo == "resultados":
        data = get_chart_data(conect(), anio, empleado_id, supervisor_id)

    return jsonify(data)

# falta crear la validacion, del tipo de reporte a solicitar/crear
@app.route("/api/empleados")
def api_empleados():
    rows = empleados()

    # rows es como [(1016312, 'JENS PYDDE'), (1013794, 'CARINA...'), ...]
    empleado_id = []
    for r in rows:
        empleado_id.append({"id": r[0], "nombre": r[1]})

    return jsonify(empleado_id)

@app.route("/api/supervisor")
def api_supervisor():
    rows = supervisor()

    # rows es como [(1016312, 'JENS PYDDE'), (1013794, 'CARINA...'), ...]
    super_id = []
    for r in rows:
        super_id.append({"id": r[0], "nombre": r[1]})

    return jsonify(super_id)

@app.route("/api/pagos")
def api_pagos():
    empleado_id = request.args.get("empleado_id")  # p.ej. "1016312"
    pagos_total = pagos(empleado_id)

    return jsonify({"pagos": pagos_total})

@app.route("/api/pav")
def api_pav():
    pav_total = get_ventas()

    return jsonify({"pav": pav_total})

@app.route("/api/top_ventas")
def api_topventas():
    top = get_rank_pav()

    return jsonify(top)

@app.route("/api/incentivos")
def incentivos():
    try:
        empleado_id = request.args.get("empleado_id")

        if not empleado_id:
            return jsonify({"error": "Falta empleado_id"}), 400

        conn = sqlite3.connect(conect())
        cur = conn.cursor()

        # Consulta de OBJETIVOS
        sql_objetivos = """
        SELECT id_empleado, fecha,
               sim_card_prepago, flex_max, internet_pospago,
               migraciones_pospago_net, fidepuntos_pospago, fidepuntos_up,
               reemplazo_pospago, reemplazo_up, fide_reemp_internet_up,
               aumentos_plan_pos_net
        FROM objetivos
        WHERE id_empleado = ?
          AND strftime('%Y-%m', fecha) = strftime('%Y-%m', 'now', 'localtime')
        ORDER BY fecha DESC
        LIMIT 1
        """
        cur.execute(sql_objetivos, (empleado_id,))
        row_obj = cur.fetchone()

        objetivos = {}
        if row_obj:
            objetivos = {
                "id_empleado": row_obj[0],
                "fecha": row_obj[1],
                "sim_card_prepago": row_obj[2],
                "flex_max": row_obj[3],
                "internet_pospago": row_obj[4],
                "migraciones_pospago_net": row_obj[5],
                "fidepuntos_pospago": row_obj[6],
                "fidepuntos_up": row_obj[7],
                "reemplazo_pospago": row_obj[8],
                "reemplazo_up": row_obj[9],
                "fide_reemp_internet_up": row_obj[10],
                "aumentos_plan_pos_net": row_obj[11],
            }

        # Consulta de RESULTADOS y COMISIONES
        like_pattern = empleado_id + " - %"
        sql_resultados_comisiones = """
        SELECT tipo_venta, SUM(total_ventas) AS suma_ventas,
            COALESCE(SUM(Comision_75), 0) as comision_75_total,
            COALESCE(SUM(Comision_100), 0) as comision_100_total
        FROM ventas_detalle
        WHERE strftime('%Y-%m', fecha) = strftime('%Y-%m', 'now', 'localtime')
        AND (usuario_creo_orden LIKE ? OR supervisor = ?)
        GROUP BY tipo_venta;
        """
        cur.execute(sql_resultados_comisiones, (like_pattern, empleado_id))
        rows_res_com = cur.fetchall()
        conn.close()

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

        objetivos_map = {
            "Card": "sim_card_prepago",
            "Flex/Max": "flex_max",
            "Internet": "internet_pospago",
            "Migraciones": "migraciones_pospago_net",
            "Fidepuntos Pos": "fidepuntos_pospago",
            "Fidepuntos Up": "fidepuntos_up",
            "Reemplazo Pos": "reemplazo_pospago",
            "Reemplazo Up": "reemplazo_up",
            "Fide Reemp Internet Up": "fide_reemp_internet_up",
            "Aumentos": "aumentos_plan_pos_net",
        }

        resultados = {key: 0 for key in groups_map}
        comisiones = {key: 0 for key in groups_map}

        for tv, suma_ventas, comision_75, comision_100 in rows_res_com:
            print(f"Procesando {tv}: ventas={suma_ventas}, com75={comision_75}, com100={comision_100}")
            for cat, lista_tv in groups_map.items():
                if tv in lista_tv:
                    resultados[cat] += suma_ventas
                    # cat_obj_key = cat.lower().replace("/", "_").replace(" ", "_")
                    cat_obj_key = objetivos_map.get(cat)

                    # Debug
                    print(f"Categoría: {cat}, clave objetivo: {cat_obj_key}")
                    if cat_obj_key in objetivos:
                        print(f"Objetivo para {cat}: {objetivos[cat_obj_key]}")
                    else:
                        print(f"No hay objetivo para {cat}")

                    # Verificar si el objetivo existe y es mayor que 0
                    if cat_obj_key in objetivos and objetivos[cat_obj_key] > 0:
                        objetivo_valor = objetivos[cat_obj_key]

                        # Calcular el logro porcentual
                        logro_porcentaje = (
                            (suma_ventas / objetivo_valor) * 100
                            if objetivo_valor > 0
                            else 0
                        )

                        logro_porcentaje = round(logro_porcentaje, 2)

                        comision_75 = float(comision_75) if comision_75 is not None else 0
                        comision_100 = float(comision_100) if comision_100 is not None else 0

                        # Asignar la comisión según el porcentaje de logro
                        if logro_porcentaje >= 100 and comision_100 > 0:
                            comisiones[cat] = comision_100
                            print(f"Comision 100% para {cat}: {comision_100}")
                        elif logro_porcentaje >= 75 and comision_75 > 0:
                            comisiones[cat] = comision_75
                            print(f"Comision 75% para {cat}: {comision_75}")
                        else:
                            print(f"No aplica comisión para {cat}, logro: {logro_porcentaje}%")
                    break                

        logro = {}
        cat_obj_key = objetivos_map.get(cat)
        if cat_obj_key in objetivos and objetivos[cat_obj_key] > 0:
            logro[cat] = round((resultados[cat] / objetivos[cat_obj_key]) * 100, 2)
        else:
            logro[cat] = 0.0

        """for cat in resultados:
            cat_obj_key = cat.lower().replace("/", "_").replace(" ", "_")
            if cat_obj_key in objetivos and objetivos[cat_obj_key] > 0:
                logro[cat] = round((resultados[cat] / objetivos[cat_obj_key]) * 100, 2)
            else:
                logro[cat] = 0.0"""

        data = {
            "objetivos": objetivos,
            "resultados": resultados,
            "logro": logro,
            "incentivo": comisiones,
        }

        print("Objetivos:", objetivos)
        print("Resultados:", resultados)
        print("Logros calculados:", logro)
        print("Comisiones Calculadas:", comisiones)

        # Imprimir un mapa detallado para depuración
        print("\nMapa detallado de datos:")
        for cat in groups_map.keys():
            cat_obj_key = cat.lower().replace("/", "_").replace(" ", "_")
            obj = objetivos.get(cat_obj_key, 0)
            res = resultados.get(cat, 0)
            log = logro.get(cat, 0)
            inc = comisiones.get(cat, 0)
            print(f"{cat}: Objetivo={obj}, Resultado={res}, Logro={log}%, Incentivo=${inc}")

        return jsonify(data)
    except Exception as e:
        # Manejo de errores
        print(f"ERROR en incentivos(): {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route("/api/objetivos-y-resultados")
def resultados():
    empleado_id = request.args.get("empleado_id")

    if not empleado_id:
        return jsonify({"error": "Falta empleado_id"}), 400

    conn = sqlite3.connect(conect())
    cur = conn.cursor()

    # Consulta de OBJETIVOS
    sql_objetivos = """
    SELECT id_empleado, fecha,
           sim_card_prepago, flex_max, internet_pospago,
           migraciones_pospago_net, fidepuntos_pospago, fidepuntos_up,
           reemplazo_pospago, reemplazo_up, fide_reemp_internet_up,
           aumentos_plan_pos_net
    FROM objetivos
    WHERE id_empleado = ?
      AND strftime('%Y-%m', fecha) = strftime('%Y-%m', 'now', 'localtime')
    ORDER BY fecha DESC
    LIMIT 1
    """
    cur.execute(sql_objetivos, (empleado_id,))
    row_obj = cur.fetchone()

    objetivos = {}
    if row_obj:
        objetivos = {
            "id_empleado": row_obj[0],
            "fecha": row_obj[1],
            "sim_card_prepago": row_obj[2],
            "flex_max": row_obj[3],
            "internet_pospago": row_obj[4],
            "migraciones_pospago_net": row_obj[5],
            "fidepuntos_pospago": row_obj[6],
            "fidepuntos_up": row_obj[7],
            "reemplazo_pospago": row_obj[8],
            "reemplazo_up": row_obj[9],
            "fide_reemp_internet_up": row_obj[10],
            "aumentos_plan_pos_net": row_obj[11],
        }

    # Consulta de RESULTADOS y COMISIONES
    like_pattern = empleado_id + " - %"
    sql_resultados_comisiones = """
    SELECT tipo_venta, SUM(total_ventas) AS suma_ventas,
        COALESCE(SUM(Comision_75), 0) as comision_75_total,
        COALESCE(SUM(Comision_100), 0) as comision_100_total
    FROM ventas_detalle
    WHERE strftime('%Y-%m', fecha) = strftime('%Y-%m', 'now', 'localtime')
    AND (usuario_creo_orden LIKE ? OR supervisor = ?)
    GROUP BY tipo_venta;
    """
    cur.execute(sql_resultados_comisiones, (like_pattern, empleado_id))
    rows_res_com = cur.fetchall()
    conn.close()

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

    resultados = {key: 0 for key in groups_map}
    comisiones = {key: 0 for key in groups_map}

    for tv, suma_ventas, comision_75, comision_100 in rows_res_com:
        for cat, lista_tv in groups_map.items():
            if tv in lista_tv:
                resultados[cat] += suma_ventas
                cat_obj_key = cat.lower().replace("/", "_").replace(" ", "_")

                # Verificar si el objetivo existe y es mayor que 0
                if cat_obj_key in objetivos and objetivos[cat_obj_key] > 0:
                    objetivo_valor = objetivos[cat_obj_key]

                    # Calcular el logro porcentual
                    logro_porcentaje = (
                        (suma_ventas / objetivo_valor) * 100
                        if objetivo_valor > 0
                        else 0
                    )

                    logro_porcentaje = round(logro_porcentaje, 2)

                    print("Logros porcentuales:")
                    for categoria, valor in comisiones.items():
                        print(f"{categoria}: {valor}%")

                    print(f"Tipo de Venta (tv): {tv}")
                    print(f"Lista de Tipos de Venta (lista_tv): {lista_tv}")

                    print(
                        f"Logro {cat}: {logro_porcentaje}, Com75: {comision_75}, Com100: {comision_100}"
                    )

                    # Imprimir valores para depuración
                    print(f"Categoría: {cat}")
                    print(f"Suma Ventas: {suma_ventas}")
                    print(f"Objetivo Valor: {objetivo_valor}")
                    print(f"Logro Porcentaje: {logro_porcentaje}")  
                    
                break

    logro = {}
    for cat in resultados:
        cat_obj_key = cat.lower().replace("/", "_").replace(" ", "_")
        if cat_obj_key in objetivos and objetivos[cat_obj_key] > 0:
            logro[cat] = round((resultados[cat] / objetivos[cat_obj_key]) * 100, 2)
        else:
            logro[cat] = 0.0
    data = {
        "objetivos": objetivos,
        "resultados": resultados,
        "logro": logro,        
    }

    return jsonify(data)


if __name__ == "__main__":
    # debug=True para desarrollo
    app.run(debug=True)
