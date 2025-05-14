from flask import Flask, render_template,jsonify, request
from chart_utils import get_chart_data, get_chart_data_logro
import sqlite3


DB_PATH = r"C:\Users\Spectre\Documents\DBHeromovil\VentasHeromovil.db"

app = Flask(__name__)


@app.route("/")
def index():
    # Renderiza tu archivo index.html (que ahora está en templates/)
    return render_template("index.html")


@app.route("/home")
def home():   
    # Renderiza reportes.html
    return render_template("Home.html")


@app.route("/dashboard")
def dashboard():    
    # Renderiza dashboard.html
    return render_template("dashboard.html")


@app.route("/chart-data")
def chart_data():
    anio = request.args.get("anio", "2025")
    empleado_id = request.args.get("empleado")  # None si no viene
    modo = request.args.get("modo")

    # Si 'empleado_id' es "None" (cadena) o está vacío, conviértelo a None real:
    if not empleado_id or empleado_id.lower() == "none":
        empleado_id = None

    if not modo or modo.lower() == "none":
        modo = "resultados"

    if modo == "logro":
        data = get_chart_data_logro(DB_PATH, anio, empleado_id)

    elif modo == "resultados":
        data = get_chart_data(DB_PATH, anio, empleado_id)

    return jsonify(data)
# falta crear la validacion, del tipo de reporte a solicitar/crear

@app.route("/api/empleados")
def api_empleados():
    """
    Retorna un JSON con la lista de empleados en la tabla 'empleados'.
    Formato:
    [
      { "id": 1016312, "nombre": "JENS PYDDE" },
      { "id": 1013794, "nombre": "CARINA DE LA CRUZ CASTILLO" },
      ...
    ]
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, nombre FROM empleados ORDER BY nombre")
    rows = cur.fetchall()
    conn.close()

    # rows es como [(1016312, 'JENS PYDDE'), (1013794, 'CARINA...'), ...]
    empleado_id = []
    for r in rows:
        empleado_id.append({"id": r[0], "nombre": r[1]})

    return jsonify(empleado_id)

@app.route("/api/objetivos-y-resultados")
def objetivos_y_resultados():
    # 1) Obtener los parámetros
    empleado_id = request.args.get("empleado_id")  # p.ej. "1016312"
    if not empleado_id:
        return jsonify({"error": "Falta empleado_id"}), 400

    # Conexión
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 2) Consulta de OBJETIVOS
    sql_objetivos = """
    SELECT id_empleado, fecha,
           flex_max, internet_pospago,
           migraciones_pospago_net, fidepuntos_pospago, fidepuntos_up,
           reemplazo_pospago, reemplazo_up, fide_reemp_internet_up,
           aumentos_plan_pos_net
    FROM objetivos
    WHERE id_empleado = ?
      AND strftime('%Y-%m', fecha) = strftime('%Y-%m', 'now')
    ORDER BY fecha DESC
    LIMIT 1
    """
    cur.execute(sql_objetivos, (empleado_id,))
    row_obj = cur.fetchone()

    # Convertimos a dict
    objetivos = {}
    if row_obj:
        objetivos = {
            "id_empleado": row_obj[0],
            "fecha": row_obj[1],
            #"sim_card_prepago": row_obj[2],
            "flex_max": row_obj[2],
            #"fijos_hfc_dth": row_obj[3],
            "internet_pospago": row_obj[3],
            "migraciones_pospago_net": row_obj[4],
            "fidepuntos_pospago": row_obj[5],
            "fidepuntos_up": row_obj[6],
            "reemplazo_pospago": row_obj[7],
            "reemplazo_up": row_obj[8],
            "fide_reemp_internet_up": row_obj[9],
            "aumentos_plan_pos_net": row_obj[10],
            #"recargas": row_obj[11],
        }

    # 3) Consulta de RESULTADOS    
    #   => Filtramos con: "AND usuario_creo_orden LIKE '1016312 - %'"
    like_pattern = empleado_id + " - %"

    sql_resultados = """
    SELECT tipo_venta,
           SUM(total_ventas) as suma
    FROM ventas_detalle
    WHERE strftime('%Y-%m', fecha) = strftime('%Y-%m', 'now')
      AND usuario_creo_orden LIKE ?
    GROUP BY tipo_venta
    """
    cur.execute(sql_resultados, (like_pattern,))
    rows_res = cur.fetchall()
    conn.close()

    # rows_res => [(tipo_venta, suma), ...]
    # 4) Reagrupar en "Card", "Flex/Max", "Internet", "Migraciones", etc.
    #    Creas un "mapa" para que varias "tipo_venta" sumen en la misma categoría.
    groups_map = {
        #"Card": ["Card"],  # Ejemplo
        "Flex/Max": ["Flex/Max"],
        "Internet": ["Internet"],
        "Migraciones": ["Migraciones", "Migraciones Net"],
        "Fidepuntos Pos": ["Fidepuntos Pospago"],
        "Fidepuntos Up": ["Fidepuntos Aumento"],
        "Reemplazo Pos": ["Reemplazo Pospago"],
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

    # Inicializamos en 0
    resultados = {
        #"Card": 0,
        "Flex/Max": 0,
        "Internet": 0,
        "Migraciones": 0,
        "Fidepuntos Pos": 0,
        "Fidepuntos Up": 0,
        "Reemplazo Pos": 0,
        "Reemplazo Up": 0,
        "Fide Reemp Internet Up": 0,
        "Aumentos": 0,
    }

    # Llenar la suma real
    for tv, suma in rows_res:
        # tv => tipo_venta real, e.g. "Migraciones" o "Fidepuntos Internet"
        # Encuentras a qué categoría pertenece:
        for cat, lista_tv in groups_map.items():
            if tv in lista_tv:
                resultados[cat] += suma
                break

    # 5) Construir el objeto final
    data = {"objetivos": objetivos, "resultados": resultados}

    return jsonify(data)


if __name__ == "__main__":
    # debug=True para desarrollo
    app.run(debug=True)
