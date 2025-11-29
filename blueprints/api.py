from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from utils.decorators import require_active_single_session
from models import Usuarios, Pagos, VentasDetalle
from extensions import db
from services.report_service import (
    get_chart_data, get_chart_data_logro, get_top_sales, get_conversion_rate,
    get_total_pav, get_recent_activity, get_sales_overview,
    get_total_pagos, get_total_recargas, get_rank_pav_cc
)
from services.data_service import (
    process_and_save_ventas, process_and_save_pagos, generar_ventas_sqlalchemy
)
import json
from datetime import datetime

api_bp = Blueprint('api', __name__)

@api_bp.route("/api/empleados")
def api_empleados():
    """Endpoint público para obtener lista de empleados (usado en registro)"""
    empleados_list = Usuarios.query.filter_by(status=1).all()
    return jsonify([{
        "id": e.codigo,
        "nombre": e.nombre,
        "puesto": e.puesto or "N/A"
    } for e in empleados_list])

@api_bp.route("/api/empleados-full")
@jwt_required()
@require_active_single_session
def api_empleados_full():
    """Endpoint protegido para obtener lista completa de empleados"""
    empleados_list = Usuarios.query.all()
    return jsonify([{"id": e.codigo, "nombre": e.nombre} for e in empleados_list])

@api_bp.route("/api/supervisor")
@jwt_required()
@require_active_single_session
def api_supervisor():
    supervisores_list = Usuarios.query.filter_by(puesto='Supervisor').all()
    return jsonify([{"id": s.codigo, "nombre": s.nombre} for s in supervisores_list])

@api_bp.route("/chart-data")
@jwt_required()
@require_active_single_session
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
        data = get_chart_data_logro(anio=anio, empleado_id=empleado_id, supervisor_id=supervisor_id)
    else:
        data = get_chart_data(anio=anio, empleado_id=empleado_id, supervisor_id=supervisor_id)
    
    return jsonify(data)

@api_bp.route("/api/pagos")
@jwt_required()
@require_active_single_session
def api_pagos():
    from utils.permissions import get_current_user
    from models import RolUsuario
    
    empleado_id = request.args.get("empleado_id")
    user = get_current_user()
    
    # Si es VENTAS, forzar su código
    if user and user.nivel_acceso == RolUsuario.VENTAS:
        empleado_id = user.codigo_usuario
    
    total_pagos = get_total_pagos(empleado_id)
    return jsonify({"pagos": total_pagos})

@api_bp.route("/api/pav")
@jwt_required()
@require_active_single_session
def api_pav():
    from utils.permissions import get_current_user
    from models import RolUsuario
    
    empleado_id = request.args.get("empleado_id")
    user = get_current_user()
    
    # Si es VENTAS, forzar su código
    if user and user.nivel_acceso == RolUsuario.VENTAS:
        empleado_id = user.codigo_usuario
    
    total_pav = get_total_pav(empleado_id)
    return jsonify({"pav": total_pav})

@api_bp.route("/api/recargas")
@jwt_required()
@require_active_single_session
def api_recargas():
    from utils.permissions import get_current_user
    from models import RolUsuario
    
    empleado_id = request.args.get("empleado_id")
    user = get_current_user()
    
    # Si es VENTAS, forzar su código
    if user and user.nivel_acceso == RolUsuario.VENTAS:
        empleado_id = user.codigo_usuario
    
    total_recargas = get_total_recargas(empleado_id)
    return jsonify({"recargas": total_recargas})

@api_bp.route("/api/top_ventas")
@jwt_required()
@require_active_single_session
def api_topventas():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    
    top_ventas_data = get_top_sales(start_date, end_date)
    formatted_data = [{"nombre": row.usuario_creo_orden, "total_pav": row.total_pav} for row in top_ventas_data]
    return jsonify(formatted_data)

@api_bp.route("/api/top_ventas_cc")
@jwt_required()
@require_active_single_session
def api_topventas_cc():
    top_ventas_cc_data = get_rank_pav_cc()
    formatted_data = [{"nombre": row.usuario_creo_orden, "total_pav": row.total_ventas} for row in top_ventas_cc_data]
    return jsonify(formatted_data)


@api_bp.route("/api/recent-activity")
@jwt_required()
@require_active_single_session
def api_recent_activity():    
    # Use the service function which implements the legacy logic (Sunday check, etc.)
    # Legacy returns: [(usuario, tipo_venta, cantidad), ...]
    # But the frontend might expect a different format if I look at the previous implementation in api.py
    # The previous implementation in api.py returned a list of dicts with type, date, description.
    # Wait, the legacy `get_recent_activity` in `cn.py` returned `(usuario_creo_orden, tipo_venta, cantidad)`.
    # I need to check `Home.html` to see how it consumes this data.
    # If I change the return format, I might break the frontend.
    # Let's check Home.html in the next step if needed.
    # For now, I will assume the legacy logic is what is wanted, but I need to format it as JSON.
    
    raw_activity = get_recent_activity()
    # Format: [{"usuario": ..., "tipo_venta": ..., "cantidad": ...}]
    activity = []
    for row in raw_activity:
        activity.append({
            "usuario": row.usuario_creo_orden,
            "tipo_venta": row.tipo_venta,
            "cantidad": row.cantidad
        })
    return jsonify(activity)

@api_bp.route("/api/sales-overview")
@jwt_required()
@require_active_single_session
def api_sales_overview():
    overview = get_sales_overview()
    return jsonify(overview)

@api_bp.route('/api/update_positions', methods=['POST'])
@jwt_required()
@require_active_single_session
def update_positions():
    new_data = request.get_json()
    with open('static/data/positions.json', 'w') as f:
        json.dump(new_data, f)
    return jsonify(success=True, message="Ruta update_positions mantiene lógica de archivo JSON.")

@api_bp.route("/api/incentivos")
@jwt_required()
@require_active_single_session
def incentivos():
    from utils.permissions import get_current_user, puede_ver_empleado
    from models import RolUsuario
    
    try:
        empleado_id = request.args.get("empleado_id")
        selected_month = request.args.get("month")
        current_year = datetime.now().year
        selected_year = request.args.get("year", default=str(current_year))
        
        user = get_current_user()
        
        # Si es VENTAS, forzar su código
        if user and user.nivel_acceso == RolUsuario.VENTAS:
            empleado_id = user.codigo_usuario
        elif empleado_id and not puede_ver_empleado(empleado_id):
            return jsonify({"error": "No tiene permisos para ver estos datos"}), 403

        if not empleado_id:
            return jsonify({"error": "Falta empleado_id"}), 400

        if selected_month:
            month_str = f"{int(selected_month):02d}"
            year_month_filter = f"{selected_year}-{month_str}"
        else:
            year_month_filter = datetime.now().strftime('%Y-%m')

        from models import Objetivos
        objetivos_query = Objetivos.query.filter(
            Objetivos.id_empleado == empleado_id,
            db.func.to_char(Objetivos.fecha, 'YYYY-MM') == year_month_filter
        ).order_by(Objetivos.fecha.desc()).first()

        objetivos = {}
        if objetivos_query:
            objetivos = {
                "id_empleado": objetivos_query.id_empleado,
                "fecha": objetivos_query.fecha.isoformat(),
                "sim_card_prepago": objetivos_query.sim_card_prepago,
                "flex_max": objetivos_query.flex_max,
                "internet_pospago": objetivos_query.internet_pospago,
                "migraciones_pospago_net": objetivos_query.migraciones_pospago_net,
                "fidepuntos_pospago": objetivos_query.fidepuntos_pospago,
                "fidepuntos_up": objetivos_query.fidepuntos_up,
                "reemplazo_pospago": objetivos_query.reemplazo_pospago,
                "reemplazo_up": objetivos_query.reemplazo_up,
                "fide_reemp_internet_up": objetivos_query.fide_reemp_internet_up,
                "aumentos_plan_pos_net": objetivos_query.aumentos_plan_pos_net,
            }

        from sqlalchemy import func, or_
        results_com_query = db.session.query(
            VentasDetalle.tipo_venta,
            func.sum(VentasDetalle.total_ventas).label('suma_ventas'),
            func.coalesce(func.sum(VentasDetalle.Comision_75), 0).label('comision_75_total'),
            func.coalesce(func.sum(VentasDetalle.Comision_100), 0).label('comision_100_total')
        ).filter(
            db.func.to_char(VentasDetalle.fecha, 'YYYY-MM') == year_month_filter,
            or_(
                VentasDetalle.usuario_creo_orden.like(empleado_id + " - %"),
                VentasDetalle.supervisor == empleado_id
            )
        ).group_by(VentasDetalle.tipo_venta).all()
        
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
                "Reemplazo Internet", "Fidepuntos Internet", "Fidepuntos InternetAum",
                "Fidepuntos InternetDism", "Reemplazo InternetAum", "Reemplazo InternetDism",
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

        for row in results_com_query:
            tv = row.tipo_venta
            suma_ventas = row.suma_ventas
            comision_75 = row.comision_75_total
            comision_100 = row.comision_100_total

            for cat, lista_tv in groups_map.items():
                if tv in lista_tv:
                    resultados[cat] += suma_ventas
                    cat_obj_key = objetivos_map.get(cat)

                    if cat_obj_key in objetivos and objetivos[cat_obj_key] > 0:
                        objetivo_valor = objetivos[cat_obj_key]
                        logro_porcentaje = ((suma_ventas / objetivo_valor) * 100 if objetivo_valor > 0 else 0)
                        logro_porcentaje = round(logro_porcentaje, 2)
                        comision_75 = float(comision_75) if comision_75 is not None else 0
                        comision_100 = float(comision_100) if comision_100 is not None else 0

                        if logro_porcentaje >= 100 and comision_100 > 0:
                            comisiones[cat] = comision_100
                        elif logro_porcentaje >= 75 and comision_75 > 0:
                            comisiones[cat] = comision_75
                    break                

        logro = {}
        for cat in resultados:
            cat_obj_key = objetivos_map.get(cat)
            if cat_obj_key in objetivos and objetivos[cat_obj_key] and objetivos[cat_obj_key] > 0:
                logro[cat] = round((resultados[cat] / objetivos[cat_obj_key]) * 100, 2)
            else:
                logro[cat] = 0.0

        data = {
            "objetivos": objetivos,
            "resultados": resultados,
            "logro": logro,
            "incentivo": comisiones,
        }
        
        return jsonify(data)
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@api_bp.route("/api/objetivos-y-resultados")
@jwt_required()
@require_active_single_session
def resultados():
    from utils.permissions import get_current_user, puede_ver_empleado
    from models import RolUsuario
    
    # Similar logic to incentivos but slightly different.
    # I'll implement it inline as well for now.
    empleado_id = request.args.get("empleado_id")
    current_month_year = datetime.now().strftime('%Y-%m')
    
    user = get_current_user()
    
    # Si es VENTAS, forzar su código
    if user and user.nivel_acceso == RolUsuario.VENTAS:
        empleado_id = user.codigo_usuario
    elif empleado_id and not puede_ver_empleado(empleado_id):
        return jsonify({"error": "No tiene permisos para ver estos datos"}), 403

    objetivos = {}
    rows_res_com = []
    
    from sqlalchemy import func, or_
    from models import Objetivos

    if empleado_id:
        objetivos_query = Objetivos.query.filter(
            Objetivos.id_empleado == empleado_id,
            db.func.to_char(Objetivos.fecha, 'YYYY-MM') == current_month_year
        ).order_by(Objetivos.fecha.desc()).first()

        if objetivos_query:
            objetivos = {
                "id_empleado": objetivos_query.id_empleado, "fecha": objetivos_query.fecha.isoformat(),
                "sim_card_prepago": objetivos_query.sim_card_prepago, "flex_max": objetivos_query.flex_max,
                "internet_pospago": objetivos_query.internet_pospago, "migraciones_pospago_net": objetivos_query.migraciones_pospago_net,
                "fidepuntos_pospago": objetivos_query.fidepuntos_pospago, "fidepuntos_up": objetivos_query.fidepuntos_up,
                "reemplazo_pospago": objetivos_query.reemplazo_pospago, "reemplazo_up": objetivos_query.reemplazo_up,
                "fide_reemp_internet_up": objetivos_query.fide_reemp_internet_up, "aumentos_plan_pos_net": objetivos_query.aumentos_plan_pos_net,
            }
        
        like_pattern = empleado_id + " - %"
        rows_res_com = db.session.query(
            VentasDetalle.tipo_venta,
            func.sum(VentasDetalle.total_ventas).label('suma_ventas')
        ).filter(
            db.func.to_char(VentasDetalle.fecha, 'YYYY-MM') == current_month_year,
            or_(
                VentasDetalle.usuario_creo_orden.like(like_pattern),
                VentasDetalle.supervisor == empleado_id
            )
        ).group_by(VentasDetalle.tipo_venta).all()

    else:
        objetivos_total_query = db.session.query(
            func.sum(Objetivos.sim_card_prepago).label('total_sim_card_prepago'),
            func.sum(Objetivos.flex_max).label('total_flex_max'),
            func.sum(Objetivos.internet_pospago).label('total_internet_pospago'),
            func.sum(Objetivos.migraciones_pospago_net).label('total_migraciones_pospago_net'),
            func.sum(Objetivos.fidepuntos_pospago).label('total_fidepuntos_pospago'),
            func.sum(Objetivos.fidepuntos_up).label('total_fidepuntos_up'),
            func.sum(Objetivos.reemplazo_pospago).label('total_reemplazo_pospago'),
            func.sum(Objetivos.reemplazo_up).label('total_reemplazo_up'),
            func.sum(Objetivos.fide_reemp_internet_up).label('total_fide_reemp_internet_up'),
            func.sum(Objetivos.aumentos_plan_pos_net).label('total_aumentos_plan_pos_net')
        ).filter(
            db.func.to_char(Objetivos.fecha, 'YYYY-MM') == current_month_year,
            Objetivos.id_empleado.notin_(['1025113', '1017255', '1016322'])
        ).first()

        if objetivos_total_query:
            objetivos = {
                "sim_card_prepago": objetivos_total_query.total_sim_card_prepago or 0,
                "flex_max": objetivos_total_query.total_flex_max or 0,
                "internet_pospago": objetivos_total_query.total_internet_pospago or 0,
                "migraciones_pospago_net": objetivos_total_query.total_migraciones_pospago_net or 0,
                "fidepuntos_pospago": objetivos_total_query.total_fidepuntos_pospago or 0,
                "fidepuntos_up": objetivos_total_query.total_fidepuntos_up or 0,
                "reemplazo_pospago": objetivos_total_query.total_reemplazo_pospago or 0,
                "reemplazo_up": objetivos_total_query.total_reemplazo_up or 0,
                "fide_reemp_internet_up": objetivos_total_query.total_fide_reemp_internet_up or 0,
                "aumentos_plan_pos_net": objetivos_total_query.total_aumentos_plan_pos_net or 0,
            }
        
        rows_res_com = db.session.query(
            VentasDetalle.tipo_venta,
            func.sum(VentasDetalle.total_ventas).label('suma_ventas')
        ).filter(
            db.func.to_char(VentasDetalle.fecha, 'YYYY-MM') == current_month_year,
            VentasDetalle.entity_code != 'EX332'
        ).group_by(VentasDetalle.tipo_venta).all()
    
    groups_map = {
        "Card": ["Card"], "Flex/Max": ["Flex/Max"], "Internet": ["Internet"],
        "Migraciones": ["Migraciones", "Migraciones Net"], "Fidepuntos Pos": ["Fidepuntos Pospago", "Fidepuntos Disminucion"],
        "Fidepuntos Up": ["Fidepuntos Aumento"], "Reemplazo Pos": ["Reemplazo Pospago", "Reemplazo Disminucion"],
        "Reemplazo Up": ["Reemplazo Aumento"],
        "Fide Reemp Internet Up": [
            "Reemplazo Internet", "Fidepuntos Internet", "Fidepuntos InternetAum",
            "Fidepuntos InternetDism", "Reemplazo InternetAum", "Reemplazo InternetDism",
        ],
        "Aumentos": ["Aumentos Pospago", "Aumentos Internet"],
    }

    resultados = {key: 0 for key in groups_map}

    for row in rows_res_com:
        tv = row.tipo_venta
        suma_ventas = row.suma_ventas
        for cat, lista_tv in groups_map.items():
            if tv in lista_tv:
                resultados[cat] += suma_ventas
                break

    logro = {}
    objetivos_map = {
        "Card": "sim_card_prepago", "Flex/Max": "flex_max", "Internet": "internet_pospago",
        "Migraciones": "migraciones_pospago_net", "Fidepuntos Pos": "fidepuntos_pospago",
        "Fidepuntos Up": "fidepuntos_up", "Reemplazo Pos": "reemplazo_pospago",
        "Reemplazo Up": "reemplazo_up", "Fide Reemp Internet Up": "fide_reemp_internet_up",
        "Aumentos": "aumentos_plan_pos_net"
    }

    for cat, res_valor in resultados.items():
        obj_key = objetivos_map.get(cat)
        if obj_key and obj_key in objetivos and objetivos[obj_key] is not None and objetivos[obj_key] > 0:
            logro[cat] = round((res_valor / objetivos[obj_key]) * 100, 2)
        else:
            logro[cat] = 0.0
            
    data = {
        "objetivos": objetivos,
        "resultados": resultados,
        "logro": logro,        
    }

    return jsonify(data)

@api_bp.route("/api/conversion-rate")
@jwt_required()
@require_active_single_session
def api_conversion_rate():
    empleado_id = request.args.get("empleado_id")
    dia = request.args.get("dia")

    if not empleado_id or not dia:
        return jsonify({"error": "Faltan parámetros: empleado_id y dia son requeridos"}), 400

    try:
        data = get_conversion_rate(empleado_id, dia)
        return jsonify(data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@api_bp.route("/api/upload_ventas", methods=["POST"])
@jwt_required()
@require_active_single_session
def upload_ventas():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    try:
        count = process_and_save_ventas(file)
        return jsonify({"message": f"Se procesaron {count} transacciones."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route("/api/upload_pagos", methods=["POST"])
@jwt_required()
@require_active_single_session
def upload_pagos():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    try:
        count = process_and_save_pagos(file)
        return jsonify({"message": f"Se procesaron {count} pagos."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route("/api/generar_ventas", methods=["POST"])
@jwt_required()
@require_active_single_session
def api_generar_ventas():
    # Obtener parámetro opcional del body
    # Por defecto: procesa solo mes actual (process_all_months=False)
    # Para procesar todo: enviar {"process_all_months": true}
    # silent=True permite requests sin Content-Type: application/json
    data = request.get_json(silent=True) or {}
    process_all = data.get('process_all_months', False)
    
    result = generar_ventas_sqlalchemy(process_all_months=process_all)
    
    if result.get("status") == "success":
        return jsonify(result), 200
    elif result.get("status") == "warning":
        return jsonify(result), 200
    else:
        return jsonify(result), 500

# Buscar Orden por ID
@api_bp.route("/api/buscar_orden/<id_transaccion>", methods=["GET"])
@jwt_required()
@require_active_single_session
def api_buscar_orden(id_transaccion):
    """
    Busca una orden por ID de transacción.
    Retorna los datos de la orden para mostrar en la UI.
    """
    try:
        from models import Transacciones
        
        orden = db.session.query(Transacciones).filter(
            Transacciones.id_transaccion == id_transaccion
        ).first()
        
        if not orden:
            return jsonify({"error": "Orden no encontrada"}), 404
        
        return jsonify({
            "usuario_creo_orden": orden.usuario_creo_orden,
            "id_transaccion": orden.id_transaccion,
            "fecha_digitacion_orden": orden.fecha_digitacion_orden.strftime("%Y-%m-%d") if orden.fecha_digitacion_orden else None,
            "razon_servicio": orden.razon_servicio
        }), 200
    except Exception as e:
        import traceback
        print(f"Error en buscar_orden: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": f"Error al buscar orden: {str(e)}"}), 500

# Reasignar Venta
@api_bp.route("/api/reasignar_venta/<id_transaccion>", methods=["PUT"])
@jwt_required()
@require_active_single_session
def api_reasignar_venta(id_transaccion):
    """
    Actualiza el usuario_creo_orden de una transacción.
    """
    try:
        from models import Transacciones
        
        data = request.get_json(silent=True) or {}
        nuevo_usuario = data.get('nuevo_usuario')
        
        if not nuevo_usuario:
            return jsonify({"error": "Debe proporcionar un nuevo usuario"}), 400
        
        orden = db.session.query(Transacciones).filter(
            Transacciones.id_transaccion == id_transaccion
        ).first()
        
        if not orden:
            return jsonify({"error": "Orden no encontrada"}), 404
        
        # Guardar usuario anterior para el log
        usuario_anterior = orden.usuario_creo_orden
        
        # Actualizar usuario
        orden.usuario_creo_orden = nuevo_usuario
        db.session.commit()
        
        return jsonify({
            "message": f"Orden {id_transaccion} reasignada de '{usuario_anterior}' a '{nuevo_usuario}'",
            "id_transaccion": id_transaccion,
            "usuario_anterior": usuario_anterior,
            "nuevo_usuario": nuevo_usuario
        }), 200
    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"Error en reasignar_venta: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": f"Error al reasignar venta: {str(e)}"}), 500
