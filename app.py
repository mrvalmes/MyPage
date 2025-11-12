from flask import Flask, render_template, jsonify, request, g
from chart_utils import get_chart_data, get_chart_data_logro
from cn import conect, empleados, supervisor, pagos, get_ventas, get_rank_pav, get_rank_pav_cc, get_recent_activity, get_sales_overview, insertar_pagos, generar_ventas, insertar_objetivos, get_recargas
import gestiondata
from datetime import datetime, timedelta, timezone
import sqlite3
import bcrypt
import json
import pandas as pd

# ======== NUEVO: JWT =========
from flask_jwt_extended import (
    JWTManager, create_access_token, get_jwt, get_jwt_identity,
    jwt_required
)

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "super-secret-key"   # cámbialo en producción
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)  # token largo, inactividad controla expiración
jwt = JWTManager(app)

INACTIVITY_SECONDS = 5 * 60  # 5 minutos


# ========= DB Helpers =========
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(conect())
        g.db.row_factory = sqlite3.Row

    return g.db

@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_auth_tables():
    """Crea tablas de usuarios y sesiones si no existen"""
    db = get_db()
    db.executescript("""
    CREATE TABLE IF NOT EXISTS usuariosligin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT NOT NULL UNIQUE,
        clave_hash TEXT NOT NULL,
        nivel_acceso TEXT NOT NULL DEFAULT 'viewer',
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ultimo_login TIMESTAMP NULL,
        activo INTEGER DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS sesiones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        jti TEXT NOT NULL UNIQUE,
        issued_at TEXT NOT NULL,
        last_seen TEXT NOT NULL,
        revoked INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES usuarios(id)
    );
    """)
    db.commit()

@app.before_request
def boot():
    if not hasattr(app, "_auth_tables_initialized"):
        init_auth_tables()
        app._auth_tables_initialized = True

# ========= Helpers de sesión =========
def utcnow():
    return datetime.now(timezone.utc)

def user_by_usuario(usuario: str):
    db = get_db()
    return db.execute("SELECT * FROM usuariosligin WHERE usuario = ?", (usuario,)).fetchone()

def set_ultimo_login(user_id: int):
    db = get_db()
    db.execute("UPDATE usuariosligin SET ultimo_login = CURRENT_TIMESTAMP WHERE id = ?", (user_id,))
    db.commit()

def create_or_replace_session(user_id: int, jti: str):
    db = get_db()
    # Revoca sesiones previas
    db.execute("UPDATE sesiones SET revoked=1 WHERE user_id=? AND revoked=0", (user_id,))
    now = utcnow().isoformat()
    db.execute("INSERT INTO sesiones (user_id,jti,issued_at,last_seen,revoked) VALUES (?,?,?,?,0)",
               (user_id, jti, now, now))
    db.commit()

def get_session_by_jti(jti: str):
    db = get_db()
    return db.execute("SELECT * FROM sesiones WHERE jti = ?", (jti,)).fetchone()

def get_active_session_for_user(user_id: int):
    db = get_db()
    return db.execute("SELECT * FROM sesiones WHERE user_id=? AND revoked=0 ORDER BY id DESC LIMIT 1",
                      (user_id,)).fetchone()

def mark_session_revoked(jti: str):
    db = get_db()
    db.execute("UPDATE sesiones SET revoked=1 WHERE jti=?", (jti,))
    db.commit()

def update_last_seen(jti: str):
    db = get_db()
    db.execute("UPDATE sesiones SET last_seen=? WHERE jti=?", (utcnow().isoformat(), jti))
    db.commit()

def seconds_since(dt_iso: str):
    dt = datetime.fromisoformat(dt_iso)
    return (utcnow() - dt).total_seconds()

# ========= Decorador de protección =========
def require_active_single_session(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        identity = get_jwt_identity()
        jti = claims["jti"]

        u = user_by_usuario(identity)
        if not u or u["activo"] != 1:
            return jsonify(msg="Usuario no válido"), 401

        s = get_session_by_jti(jti)
        if not s or s["revoked"] == 1:
            return jsonify(msg="Sesión inválida"), 401

        active = get_active_session_for_user(u["id"])
        if not active or active["jti"] != jti:
            return jsonify(msg="Sesión reemplazada en otro navegador"), 409

        if seconds_since(s["last_seen"]) > INACTIVITY_SECONDS:
            mark_session_revoked(jti)
            return jsonify(msg="Sesión expirada por inactividad"), 440

        update_last_seen(jti)
        return fn(*args, **kwargs)
    return wrapper

# ========= Rutas de autenticación =========
@app.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    usuario = (data.get("email") or data.get("usuario") or "").strip()
    password = (data.get("password") or "").encode("utf-8")

    u = user_by_usuario(usuario)
    if not u or u["activo"] != 1:
        return jsonify(msg="Credenciales inválidas"), 401

    if not bcrypt.checkpw(password, u["clave_hash"].encode("utf-8")):
        return jsonify(msg="Credenciales inválidas"), 401

    access_token = create_access_token(identity=usuario,
                                       additional_claims={"nivel": u["nivel_acceso"]})

    # obtener jti del token
    from flask_jwt_extended.utils import decode_token
    jti = decode_token(access_token)["jti"]

    create_or_replace_session(u["id"], jti)
    set_ultimo_login(u["id"])

    return jsonify(access_token=access_token, nivel=u["nivel_acceso"])

@app.post("/logout")
#@jwt_required()
#@require_active_single_session
def logout():
    jti = get_jwt()["jti"]
    mark_session_revoked(jti)
    return jsonify(msg="Sesión cerrada")

@app.get("/me")
#@jwt_required()
#@require_active_single_session
def me():
    identity = get_jwt_identity()
    claims = get_jwt()
    return jsonify(usuario=identity, nivel=claims.get("nivel"))

@app.post("/ping")
#@jwt_required()
#@require_active_single_session
def ping():
    return jsonify(ok=True)

# ========= rutas  =========
@app.route("/")
def index():
    return render_template("login.html")

@app.route("/home")
#@jwt_required()
#@require_active_single_session
def home():
    recent_activity = get_recent_activity()
    sales_overview = get_sales_overview()
    return render_template("Home.html", recent_activity=recent_activity, sales_overview=sales_overview)

@app.route("/Registro")
#@jwt_required()
#@require_active_single_session
def registro():
    return render_template("registro.html")

@app.route("/dashboard")
#@jwt_required()
#@require_active_single_session
def dashboard():
    return render_template("dashboard.html")

@app.route("/Mantenimientos")
#@jwt_required()
#@require_active_single_session
def Mantenimientos():
    return render_template("Mantenimientos.html")

@app.route("/Comisiones")
#@jwt_required()
#@require_active_single_session
def Comisiones():
    return render_template("Comisiones.html")

@app.route("/posiciones")
#@jwt_required()
#@require_active_single_session
def posiciones():
    return render_template("posiciones.html")

@app.route("/procesos")
#@jwt_required()
#@require_active_single_session
def procesos():
    return render_template("procesos.html")

# === APIs ===
# Puedes decidir si quieres que estas sean públicas o privadas
@app.route("/chart-data")
def chart_data():
    anio = request.args.get("anio", "2025")
    empleado_id = request.args.get("empleado")
    supervisor_id = request.args.get("supervisor")
    modo = request.args.get("modo")

    if not empleado_id or empleado_id.lower() == "none":
        empleado_id = None
    if not supervisor_id or supervisor_id.lower() == "none":
        supervisor_id = None
    if not modo or modo.lower() == "none":
        modo = "resultados"

    if modo == "logro":
        data = get_chart_data_logro(conect(), anio, empleado_id, supervisor_id)
    else:
        data = get_chart_data(conect(), anio, empleado_id, supervisor_id)

    return jsonify(data)

@app.route("/api/empleados")
def api_empleados():
    rows = empleados()
    return jsonify([{"id": r[0], "nombre": r[1]} for r in rows])

@app.route("/api/supervisor")
def api_supervisor():
    rows = supervisor()
    return jsonify([{"id": r[0], "nombre": r[1]} for r in rows])

@app.route("/api/pagos")
def api_pagos():
    empleado_id = request.args.get("empleado_id")
    return jsonify({"pagos": pagos(empleado_id)})

@app.route("/api/pav")
def api_pav():
    return jsonify({"pav": get_ventas()})

@app.route("/api/recargas")
def api_recargas():
    empleado_id = request.args.get("empleado_id")
    return jsonify({"recargas": get_recargas(empleado_id)})

@app.route("/api/top_ventas")
def api_topventas():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    top_ventas_data = get_rank_pav(start_date=start_date, end_date=end_date)
    formatted_data = [{"nombre": row[0], "total_pav": row[1]} for row in top_ventas_data]
    return jsonify(formatted_data)

@app.route("/api/top_ventas_cc")
def api_topventas_cc():
    return jsonify(get_rank_pav_cc())

@app.route("/api/recent-activity")
def api_recent_activity():    
    activity = get_recent_activity()
    return jsonify(activity)

@app.route("/api/sales-overview")
def api_sales_overview():
    overview = get_sales_overview()
    return jsonify(overview)

@app.route('/api/update_positions', methods=['POST'])
def update_positions():
    new_data = request.get_json()
    with open('static/data/positions.json', 'w') as f:
        json.dump(new_data, f)
    return jsonify(success=True)

@app.route("/api/incentivos")
def incentivos():
    try:
        empleado_id = request.args.get("empleado_id")
        selected_month = request.args.get("month")
        current_year = datetime.now().year
        selected_year = request.args.get("year", default=current_year)

        if not empleado_id:
            return jsonify({"error": "Falta empleado_id"}), 400

        # Crear el filtro de fecha
        if selected_month:
            month_str = f"{int(selected_month):02d}"
            year_month_filter = f"{selected_year}-{month_str}"
        else:
            year_month_filter = datetime.now().strftime('%Y-%m')

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
          AND strftime('%Y-%m', fecha) = ?
        ORDER BY fecha DESC
        LIMIT 1
        """
        cur.execute(sql_objetivos, (empleado_id, year_month_filter))
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
        WHERE strftime('%Y-%m', fecha) = ?
        AND (usuario_creo_orden LIKE ? OR supervisor = ?)
        GROUP BY tipo_venta;
        """
        cur.execute(sql_resultados_comisiones, (year_month_filter, like_pattern, empleado_id))
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

        """Debugging salidas        
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
        """
        return jsonify(data)
    except Exception as e:
        # Manejo de errores
        #print(f"ERROR en incentivos(): {str(e)}")
        import traceback
        #print(traceback.format_exc())
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

                    """                    
                    # Asignar la comisión según el porcentaje de logro  debugging prints                  
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
                    """
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

@app.route("/api/conversion-rate")
def api_conversion_rate():
    # Obtener parámetros del query string
    empleado_id = request.args.get("empleado_id")  # ID del supervisor o usuario
    dia = request.args.get("dia")  # Fecha en formato YYYY-MM-DD

    # Validar parámetros
    if not empleado_id or not dia:
        return jsonify({"error": "Faltan parámetros: empleado_id y dia son requeridos"}), 400

    # Conexión a la base
    conn = sqlite3.connect(conect())
    cur = conn.cursor()

    query = """
        WITH ventas_por_usuario AS (
            SELECT
                usuario_creo_orden,
                SUBSTR(usuario_creo_orden, 1, 7) AS user_prefix,
                SUM(total_ventas) AS ventas_count
            FROM ventas_detalle
            WHERE tipo_venta != 'Card'
                AND entity_code != 'EX332'
                AND DATE(fecha) = DATE(:day)
                AND supervisor = :supervisor
            GROUP BY usuario_creo_orden
        ),
        pagos_por_prefijo AS (
            SELECT
                SUBSTR(userlogin, 1, 7) AS user_prefix,
                COUNT(*) AS pagos_count
            FROM pagos
            WHERE DATE(dte) = DATE(:day)
            GROUP BY user_prefix
        )
        SELECT
            v.usuario_creo_orden,
            v.user_prefix,
            v.ventas_count,
            IFNULL(p.pagos_count, 0) AS pagos_count,
            ROUND(
                CASE 
                    WHEN p.pagos_count > 0 
                    THEN (v.ventas_count * 1.0 / p.pagos_count) * 100
                    ELSE 0
                END, 2
            ) AS conversion_rate_pct
        FROM ventas_por_usuario v
        LEFT JOIN pagos_por_prefijo p
        ON v.user_prefix = p.user_prefix
        ORDER BY conversion_rate_pct DESC;
    """

    # Parámetros seguros (todo en string o número, nada de funciones)
    print("Parámetros recibidos:", empleado_id, dia)
    params = {
        'day': dia,
        'supervisor': empleado_id
    }

    cur.execute(query, params)
    rows = cur.fetchall()

    conn.close()

    # Columnas esperadas
    columns = ["usuario_creo_orden", "user_prefix", "ventas_count", "pagos_count", "conversion_rate_pct"]

    # Convertir resultados a JSON
    return jsonify([dict(zip(columns, r)) for r in rows])

@app.post("/api/register")
def register():
    data = request.get_json(silent=True) or {}
    usuario = (data.get("usuario") or "").strip()
    password = (data.get("password") or "").encode("utf-8")
    nivel = (data.get("nivel") or "viewer").strip()

    if not usuario or not password:
        return jsonify(msg="Usuario y contraseña requeridos"), 400

    # Hashear clave
    clave_hash = bcrypt.hashpw(password, bcrypt.gensalt()).decode("utf-8")

    db = get_db()
    try:
        db.execute(
            "INSERT INTO usuariosligin (usuario, clave_hash, nivel_acceso) VALUES (?, ?, ?)",
            (usuario, clave_hash, nivel)
        )
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify(msg="Usuario ya existe"), 409

    return jsonify(msg="Usuario creado correctamente"), 201

@app.route('/api/upload_ventas', methods=['POST'])
def upload_ventas():
    if 'ventas_excel' not in request.files:
        return jsonify(success=False, error='No se encontró el archivo')

    file = request.files['ventas_excel']

    if file.filename == '':
        return jsonify(success=False, error='No se seleccionó ningún archivo')

    if file and file.filename.endswith('.xlsx'):
        try:
            df = pd.read_excel(file, header=9, usecols="B:BM")  # Leer desde la fila 10 (índice 9) 
            gestiondata.procesar_dataframe_ventas(df)
            return jsonify(success=True)
        except Exception as e:
            return jsonify(success=False, error=str(e))
    else:
        return jsonify(success=False, error='Formato de archivo no válido. Use .xlsx')

@app.route('/api/upload_pagos', methods=['POST'])
def upload_pagos():
    if 'pagos_excel' not in request.files:
        return jsonify(success=False, error='No se encontró el archivo')

    file = request.files['pagos_excel']

    if file.filename == '':
        return jsonify(success=False, error='No se seleccionó ningún archivo')

    if file and file.filename.endswith('.xlsx'):
        try:
            df = pd.read_excel(file, header=9, usecols="B:Y")  # Leer desde la fila 10 (índice 9) 
            # Convertir la columna 'dte' a datetime y establecer el formato de salida
            df["dte"] = pd.to_datetime(
                df["dte"], dayfirst=True, errors="coerce"
            ).dt.strftime('%Y-%m-%d').fillna("")
            df = df.where(pd.notnull(df), None)
            # Normalizar columnas numéricas, truncando decimales para asegurar conversión a entero.
            columnas_texto = ['tel_contacto', 'tel_contacto2', 'entity_name', 'plan_name', 'supervisor', 'tipo_pago']
            for col in columnas_texto:
                if col in df.columns:
                    df[col] = gestiondata.limpiar_campo_texto(df[col])
            # ---------------------------                        
            insertar_pagos(df)
            return jsonify(success=True)
        except Exception as e:
            return jsonify(success=False, error=str(e))
    else:
        return jsonify(success=False, error='Formato de archivo no válido. Use .xlsx')

@app.route('/api/upload_objetivos', methods=['POST'])
def upload_objetivos():
    if 'objetivos_excel' not in request.files:
        return jsonify(success=False, error='No se encontró el archivo')

    file = request.files['objetivos_excel']

    if file.filename == '':
        return jsonify(success=False, error='No se seleccionó ningún archivo')

    if file and file.filename.endswith('.xlsx'):
        try:
            # Pasamos el objeto de archivo directamente
            insertar_objetivos(file)
            return jsonify(success=True)
        except Exception as e:
            return jsonify(success=False, error=str(e))
    else:
        return jsonify(success=False, error='Formato de archivo no válido. Use .xlsx')
    
@app.route('/api/procesar')
def procesar():
    generar_ventas()    
    return jsonify(success=True)

    
if __name__ == "__main__":
    app.run(debug=True)
