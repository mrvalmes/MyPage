from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, get_jwt, get_jwt_identity,
    jwt_required, set_access_cookies, unset_jwt_cookies
)
from flask_jwt_extended.utils import decode_token
import bcrypt
from extensions import db
from models import UsuariosLogin
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

    access_token = create_access_token(identity=usuario,
                                       additional_claims={"nivel": u.nivel_acceso})

    jti = decode_token(access_token)["jti"]

    create_or_replace_session(u.id, jti)
    set_ultimo_login(u.id)

    resp = jsonify(access_token=access_token, nivel=u.nivel_acceso)
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
    claims = get_jwt()
    return jsonify(usuario=identity, nivel=claims.get("nivel"))

@auth_bp.post("/ping")
@jwt_required()
@require_active_single_session
def ping():
    return jsonify(ok=True)

@auth_bp.post("/api/register")
def register():
    data = request.get_json(silent=True) or {}
    usuario = (data.get("usuario") or "").strip()
    password = (data.get("password") or "").encode("utf-8")
    nivel = (data.get("nivel") or "viewer").strip()

    if not usuario or not password:
        return jsonify(msg="Usuario y contraseña requeridos"), 400

    clave_hash = bcrypt.hashpw(password, bcrypt.gensalt()).decode("utf-8")

    existing_user = UsuariosLogin.query.filter_by(usuario=usuario).first()
    if existing_user:
        return jsonify(msg="Usuario ya existe"), 409

    new_user = UsuariosLogin(usuario=usuario, clave_hash=clave_hash, nivel_acceso=nivel)
    db.session.add(new_user)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify(msg=f"Error al crear usuario: {str(e)}"), 500

    return jsonify(msg="Usuario creado correctamente"), 201
