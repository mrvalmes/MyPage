from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity
from services.auth_service import (
    user_by_usuario, get_session_by_jti, 
    get_active_session_for_user, mark_session_revoked, 
    update_last_seen, seconds_since, INACTIVITY_SECONDS
)

def require_active_single_session(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        identity = get_jwt_identity()
        jti = claims["jti"]

        u = user_by_usuario(identity)
        if not u or not u.activo:
            return jsonify(msg="Usuario no válido"), 401

        s = get_session_by_jti(jti)
        if not s or s.revoked:
            return jsonify(msg="Sesión inválida"), 401

        active = get_active_session_for_user(u.id)
        if not active or active.jti != jti:
            return jsonify(msg="Sesión reemplazada en otro navegador"), 409
        
        if seconds_since(s.last_seen) > INACTIVITY_SECONDS:
            mark_session_revoked(jti)
            return jsonify(msg="Sesión expirada por inactividad"), 440

        update_last_seen(jti)
        return fn(*args, **kwargs)
    return wrapper
