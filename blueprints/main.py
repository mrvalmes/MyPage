from flask import Blueprint, render_template
from flask_jwt_extended import jwt_required
from utils.decorators import require_active_single_session
from utils.permissions import require_route_access
from services.report_service import get_recent_activity, get_sales_overview

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def index():
    return render_template("login.html")

@main_bp.route("/home")
@jwt_required()
@require_active_single_session
@require_route_access('home')  # Solo ADMIN y SUPERVISOR
def home():
    recent_activity = get_recent_activity()
    sales_overview = get_sales_overview()
    return render_template("Home.html", recent_activity=recent_activity, sales_overview=sales_overview)

@main_bp.route("/Registro")
def registro():
    # Registro es público (no requiere autenticación)
    return render_template("registro.html")

@main_bp.route("/dashboard")
@jwt_required()
@require_active_single_session
@require_route_access('dashboard')  # ADMIN, SUPERVISOR, VENTAS
def dashboard():
    return render_template("dashboard.html")

@main_bp.route("/Mantenimientos")
@jwt_required()
@require_active_single_session
@require_route_access('mantenimientos')  # Solo ADMIN
def mantenimientos():
    return render_template("Mantenimientos.html")

@main_bp.route("/Comisiones")
@jwt_required()
@require_active_single_session
@require_route_access('comisiones')  # ADMIN, SUPERVISOR, VENTAS
def comisiones():
    return render_template("Comisiones.html")

@main_bp.route("/posiciones")
@jwt_required()
@require_active_single_session
@require_route_access('posiciones')  # ADMIN, SUPERVISOR, VENTAS
def posiciones():
    return render_template("posiciones.html")

@main_bp.route("/procesos")
@jwt_required()
@require_active_single_session
@require_route_access('procesos')  # Solo ADMIN
def procesos():
    return render_template("procesos.html")

