from datetime import datetime, timezone
from extensions import db
from models import UsuariosLogin, Sesiones

INACTIVITY_SECONDS = 10 * 60  # 10 minutos

def utcnow():
    return datetime.now(timezone.utc)

def user_by_usuario(usuario: str):
    return UsuariosLogin.query.filter_by(usuario=usuario).first()

def set_ultimo_login(user_id: int):
    user = db.session.get(UsuariosLogin, user_id)
    if user:
        user.ultimo_login = utcnow()
        db.session.commit()

def create_or_replace_session(user_id: int, jti: str):
    # Revoca sesiones previas
    Sesiones.query.filter_by(user_id=user_id, revoked=0).update({'revoked': 1})
    
    new_session = Sesiones(
        user_id=user_id,
        jti=jti,
        issued_at=utcnow(),
        last_seen=utcnow(),
        revoked=0
    )
    db.session.add(new_session)
    db.session.commit()

def get_session_by_jti(jti: str):
    return Sesiones.query.filter_by(jti=jti).first()

def get_active_session_for_user(user_id: int):
    return Sesiones.query.filter_by(user_id=user_id, revoked=0).order_by(Sesiones.id.desc()).first()

def mark_session_revoked(jti: str):
    session = Sesiones.query.filter_by(jti=jti).first()
    if session:
        session.revoked = 1
        db.session.commit()

def update_last_seen(jti: str):
    session = Sesiones.query.filter_by(jti=jti).first()
    if session:
        session.last_seen = utcnow()
        db.session.commit()

def seconds_since(dt_obj: datetime):
    if dt_obj.tzinfo is None:
        dt_obj = dt_obj.replace(tzinfo=timezone.utc)
    return (utcnow() - dt_obj).total_seconds()
