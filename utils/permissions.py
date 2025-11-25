# utils/permissions.py
"""
Sistema de permisos basado en roles.
Define decoradores y helpers para controlar acceso a rutas y filtrar datos.
"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from models import UsuariosLogin, RolUsuario

def require_role(*roles_permitidos):
    """
    Decorador que valida si el usuario tiene uno de los roles permitidos.
    
    Uso:
        @require_role(RolUsuario.ADMIN, RolUsuario.SUPERVISOR)
        def vista_solo_admin_supervisor():
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            identity = get_jwt_identity()
            user = UsuariosLogin.query.filter_by(usuario=identity).first()
            
            if not user:
                return jsonify(msg="Usuario no encontrado"), 401
            
            if user.nivel_acceso not in roles_permitidos:
                return jsonify(msg="No tiene permisos para acceder a este recurso"), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def require_route_access(ruta: str):
    """
    Decorador que valida si el usuario tiene permiso para acceder a una ruta específica.
    
    Uso:
        @require_route_access('dashboard')
        def vista_dashboard():
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            identity = get_jwt_identity()
            user = UsuariosLogin.query.filter_by(usuario=identity).first()
            
            if not user:
                return jsonify(msg="Usuario no encontrado"), 401
            
            if not user.tiene_permiso(ruta):
                return jsonify(msg=f"No tiene permisos para acceder a {ruta}"), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def get_current_user():
    """Helper para obtener el usuario actual desde el JWT"""
    identity = get_jwt_identity()
    return UsuariosLogin.query.filter_by(usuario=identity).first()

def get_empleado_filtro():
    """
    Retorna el código de empleado para filtrar datos según el rol.
    
    Returns:
        - None: Si es ADMIN o SUPERVISOR (ve todos los datos)
        - codigo_usuario: Si es VENTAS (solo ve sus datos)
    """
    user = get_current_user()
    
    if not user:
        return None
    
    # Solo VENTAS ve únicamente sus propios datos
    if user.nivel_acceso == RolUsuario.VENTAS:
        return user.codigo_usuario
    
    # ADMIN y SUPERVISOR ven todos los datos
    return None

def puede_ver_empleado(empleado_id: str) -> bool:
    """
    Verifica si el usuario actual puede ver los datos de un empleado específico.
    
    Args:
        empleado_id: Código del empleado a verificar
    
    Returns:
        True si puede ver, False si no
    """
    user = get_current_user()
    
    if not user:
        return False
    
    # ADMIN y SUPERVISOR pueden ver cualquier empleado
    if user.nivel_acceso in [RolUsuario.ADMIN, RolUsuario.SUPERVISOR]:
        return True
    
    # VENTAS solo puede ver sus propios datos
    if user.nivel_acceso == RolUsuario.VENTAS:
        return empleado_id == user.codigo_usuario
    
    return False
