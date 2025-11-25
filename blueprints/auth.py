from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, get_jwt, get_jwt_identity,
    jwt_required, set_access_cookies, unset_jwt_cookies
)
from flask_jwt_extended.utils import decode_token
import bcrypt
from extensions import db
from models import UsuariosLogin, RolUsuario
from services.auth_service import (
    user_by_usuario, create_or_replace_session, 
    set_ultimo_login, mark_session_revoked
)
from utils.decorators import require_active_single_session

auth_bp = Blueprint('auth', __name__)

@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    usuario = (data.get("email") or data.get("usuario") or "").strip()
    password = (data.get("password") or "").encode("utf-8")

    u = user_by_usuario(usuario)
    if not u or not u.activo:
        return jsonify(msg="Credenciales inválidas"), 401

    if not bcrypt.checkpw(password, u.clave_hash.encode("utf-8")):
        return jsonify(msg="Credenciales inválidas"), 401

    # Convertir Enum a string
    nivel_str = u.nivel_acceso.value if hasattr(u.nivel_acceso, 'value') else str(u.nivel_acceso)
    
    access_token = create_access_token(
        identity=usuario,
        additional_claims={"nivel": nivel_str}
    )

    jti = decode_token(access_token)["jti"]

    create_or_replace_session(u.id, jti)
    set_ultimo_login(u.id)

    resp = jsonify(
        access_token=access_token, 
        nivel=nivel_str,
        force_password_change=u.force_password_change
    )
    set_access_cookies(resp, access_token)
    return resp

@auth_bp.post("/logout")
@jwt_required()
@require_active_single_session
def logout():
    jti = get_jwt()["jti"]
    mark_session_revoked(jti)
    resp = jsonify(msg="Sesión cerrada")
    unset_jwt_cookies(resp)
    return resp

@auth_bp.get("/me")
@jwt_required()
@require_active_single_session
def me():
    identity = get_jwt_identity()
    user = UsuariosLogin.query.filter_by(usuario=identity).first()
    
    if not user:
        return jsonify(msg="Usuario no encontrado"), 404
    
    return jsonify(
        usuario=identity,
        nivel=user.nivel_acceso.value,  # Enum -> string
        codigo_usuario=user.codigo_usuario,
        nombre_empleado=user.empleado.nombre if user.empleado else None,
        puesto=user.empleado.puesto if user.empleado else None,
        force_password_change=user.force_password_change
    )

@auth_bp.post("/ping")
@jwt_required()
@require_active_single_session
def ping():
    return jsonify(ok=True)

@auth_bp.post("/api/admin/create-user")
@jwt_required()
@require_active_single_session
def create_user_admin():
    """
    Endpoint para que un ADMIN cree nuevos usuarios.
    Requiere: usuario (email), codigo_usuario, nivel (rol)
    La contraseña se genera temporalmente o se establece una por defecto.
    """
    current_user_identity = get_jwt_identity()
    admin_user = UsuariosLogin.query.filter_by(usuario=current_user_identity).first()
    
    if not admin_user or admin_user.nivel_acceso != RolUsuario.ADMIN:
        return jsonify(msg="Acceso denegado. Se requiere rol de Administrador."), 403

    try:
        data = request.get_json(silent=True) or {}
        usuario = (data.get("usuario") or "").strip()
        nivel = (data.get("nivel") or "").strip()
        codigo_usuario = (data.get("codigo_usuario") or "").strip() or None
        temp_password = (data.get("temp_password") or "").strip()

        # Validación de campos requeridos
        if not usuario:
            return jsonify(msg="El campo 'usuario' es requerido"), 400
        
        if not temp_password:
             return jsonify(msg="El campo 'temp_password' es requerido"), 400
        
        if not nivel:
            return jsonify(msg="Debe seleccionar un rol"), 400

        # Validar que el rol sea válido
        try:
            rol_enum = RolUsuario(nivel)
        except ValueError:
            return jsonify(msg=f"Rol inválido. Opciones: admin, supervisor, ventas"), 400

        # Validar que el código de usuario exista si se proporcionó
        if codigo_usuario:
            from models import Usuarios
            empleado = Usuarios.query.filter_by(codigo=codigo_usuario).first()
            if not empleado:
                return jsonify(msg=f"No existe un empleado con código {codigo_usuario}"), 400
            
            # Verificar si ya existe un usuario asociado a este empleado
            usuario_existente_empleado = UsuariosLogin.query.filter_by(codigo_usuario=codigo_usuario).first()
            if usuario_existente_empleado:
                return jsonify(msg=f"Ya existe un usuario asociado al empleado {codigo_usuario}"), 409

        # Verificar si el usuario ya existe
        existing_user = UsuariosLogin.query.filter_by(usuario=usuario).first()
        if existing_user:
            return jsonify(msg="El usuario ya existe"), 409

        # Hashear la contraseña temporal
        password_bytes = temp_password.encode("utf-8")
        clave_hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")

        # Crear nuevo usuario con force_password_change=True
        new_user = UsuariosLogin(
            usuario=usuario,
            clave_hash=clave_hash,
            nivel_acceso=rol_enum,
            codigo_usuario=codigo_usuario,
            force_password_change=True
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify(
            msg="Usuario creado correctamente. Se requerirá cambio de contraseña al primer inicio.",
            id=new_user.id,
            usuario=new_user.usuario
        ), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error en creación de usuario admin: {str(e)}")
        return jsonify(msg="Error al crear el usuario."), 500

@auth_bp.post("/api/change-password")
@jwt_required()
@require_active_single_session
def change_password():
    """
    Endpoint para cambiar la contraseña.
    Requiere: current_password, new_password
    """
    identity = get_jwt_identity()
    user = UsuariosLogin.query.filter_by(usuario=identity).first()
    
    if not user:
        return jsonify(msg="Usuario no encontrado"), 404

    data = request.get_json(silent=True) or {}
    current_password = (data.get("current_password") or "").encode("utf-8")
    new_password = (data.get("new_password") or "").strip()

    if not new_password or len(new_password) < 6:
        return jsonify(msg="La nueva contraseña debe tener al menos 6 caracteres"), 400

    # Verificar contraseña actual
    if not bcrypt.checkpw(current_password, user.clave_hash.encode("utf-8")):
        return jsonify(msg="La contraseña actual es incorrecta"), 401

    # Actualizar contraseña
    new_password_bytes = new_password.encode("utf-8")
    new_hash = bcrypt.hashpw(new_password_bytes, bcrypt.gensalt()).decode("utf-8")
    
    user.clave_hash = new_hash
    user.force_password_change = False # Ya no se requiere cambio
    
    try:
        db.session.commit()
        return jsonify(msg="Contraseña actualizada correctamente")
    except Exception as e:
        db.session.rollback()
        print(f"Error cambiando password: {e}")
        return jsonify(msg="Error al actualizar la contraseña"), 500


