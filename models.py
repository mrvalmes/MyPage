# models.py
from extensions import db
from datetime import datetime, timezone
from sqlalchemy import UniqueConstraint
import enum

# Enum para roles de usuario
class RolUsuario(enum.Enum):
    ADMIN = "admin"
    SUPERVISOR = "supervisor"
    VENTAS = "ventas"
    
    @classmethod
    def values(cls):
        return [rol.value for rol in cls]

class UsuariosLogin(db.Model):
    """ Modelo para la tabla usuariosligin, para autenticación """
    __tablename__ = 'usuariosligin'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario = db.Column(db.String, unique=True, nullable=False)
    clave_hash = db.Column(db.String, nullable=False)
    
    # FK a usuarios (empleado asociado)
    codigo_usuario = db.Column(db.String, db.ForeignKey('usuarios.codigo'), nullable=True)
    
    # Usar Enum para roles
    nivel_acceso = db.Column(db.Enum(RolUsuario), nullable=False, default=RolUsuario.VENTAS)
    
    fecha_creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    ultimo_login = db.Column(db.DateTime, nullable=True)
    activo = db.Column(db.Integer, default=1)
    force_password_change = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relación con Usuarios
    empleado = db.relationship('Usuarios', backref=db.backref('usuario_login', uselist=False))

    def __repr__(self):
        return f'<UsuarioLogin {self.usuario}>'
    
    def tiene_permiso(self, ruta: str) -> bool:
        """Verifica si el usuario tiene permiso para acceder a una ruta"""
        permisos = {
            RolUsuario.ADMIN: ['home', 'dashboard', 'posiciones', 'comisiones', 'procesos', 'mantenimientos', 'audios'],
            RolUsuario.SUPERVISOR: ['home', 'dashboard', 'posiciones', 'comisiones', 'audios'],
            RolUsuario.VENTAS: ['dashboard', 'comisiones', 'posiciones']
        }
        return ruta in permisos.get(self.nivel_acceso, [])

class Usuarios(db.Model):
    """ Modelo para la tabla 'usuarios' con información general de empleados/supervisores """
    __tablename__ = 'usuarios'
    codigo = db.Column(db.String, primary_key=True)
    nombre = db.Column(db.String)
    localidad = db.Column(db.String)
    supervisor = db.Column(db.String)
    puesto = db.Column(db.String)
    status = db.Column(db.Integer)
    nivel_acceso = db.Column(db.Integer)

    def __repr__(self):
        return f'<Usuario {self.nombre}>'

class Sesiones(db.Model):
    __tablename__ = 'sesiones'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuariosligin.id'), nullable=False)
    jti = db.Column(db.String, unique=True, nullable=False)
    issued_at = db.Column(db.DateTime, nullable=False)
    last_seen = db.Column(db.DateTime, nullable=False)
    revoked = db.Column(db.Integer, default=0, nullable=False)

    usuario_rel = db.relationship('UsuariosLogin', backref=db.backref('sesiones_rel', lazy=True))

    def __repr__(self):
        return f'<Sesion {self.jti}>'

class Localidades(db.Model):
    __tablename__ = 'localidades'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cod_pos = db.Column(db.Integer, unique=True, nullable=False)
    nombre = db.Column(db.String, nullable=False)
    direccion = db.Column(db.String)
    status = db.Column(db.Integer, default=1, nullable=False)
    supervisor = db.Column(db.Integer, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Localidad {self.nombre}>'

class TiposVenta(db.Model):
    __tablename__ = 'tipos_venta'
    id_tipo_venta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    codigo = db.Column(db.String, unique=True, nullable=False)
    descripcion = db.Column(db.String, nullable=False)
    categoria = db.Column(db.String)
    activo = db.Column(db.Integer, default=1)

    def __repr__(self):
        return f'<TiposVenta {self.descripcion}>'

class Transacciones(db.Model):
    __tablename__ = 'transacciones'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_transaccion = db.Column(db.String, nullable=False)
    fecha_digitacion_orden = db.Column(db.Date)
    fecha_termino_orden = db.Column(db.Date)
    estado_transaccion = db.Column(db.String)
    usuario_creo_orden = db.Column(db.String, nullable=False)
    entity_code = db.Column(db.String)
    subcanal = db.Column(db.Integer)
    tipo_actividad = db.Column(db.String)
    razon_servicio = db.Column(db.String, nullable=False)
    telefono = db.Column(db.String, nullable=False)
    imei = db.Column(db.String, nullable=False)
    nom_plan = db.Column(db.String)
    grupo_activacion_orden = db.Column(db.String)
    grupo_activacion_anterior = db.Column(db.String)

    __table_args__ = (UniqueConstraint('id_transaccion', 'usuario_creo_orden', 'razon_servicio', 'telefono', name='_transaccion_uc'),)

    def __repr__(self):
        return f'<Transaccion {self.id_transaccion}>'

class VentasDetalle(db.Model):
    __tablename__ = 'ventas_detalle'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    entity_code = db.Column(db.String)
    subcanal = db.Column(db.Integer)
    fecha = db.Column(db.Date)
    supervisor = db.Column(db.String)
    usuario_creo_orden = db.Column(db.String)
    tipo_venta = db.Column(db.String)
    Grupo = db.Column(db.Integer)
    Grupo_Anterior = db.Column(db.Integer)
    total_ventas = db.Column(db.Integer)
    Comision_100 = db.Column(db.Integer)
    Comision_75 = db.Column(db.Integer)

    def __repr__(self):
        return f'<VentaDetalle {self.id}>'

class Pagos(db.Model):
    __tablename__ = 'pagos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_tipo_compania = db.Column(db.Integer)
    compania = db.Column(db.String)
    ent_code = db.Column(db.String)
    estado = db.Column(db.String)
    entity_name = db.Column(db.String)
    id_canal = db.Column(db.Integer)
    id_subcanal = db.Column(db.Integer)
    dte = db.Column(db.String)
    monto = db.Column(db.Float)
    custcode = db.Column(db.String)
    id_cuenta = db.Column(db.String)
    cn = db.Column(db.String)
    fn = db.Column(db.String)
    cachknum = db.Column(db.String)
    userlogin = db.Column(db.String)
    caja = db.Column(db.String)
    concepto_pago = db.Column(db.String)
    transaction_id = db.Column(db.Integer)
    fp_efectivo = db.Column(db.Float)
    fp_tarjeta = db.Column(db.Float)
    fp_cheque = db.Column(db.Float)
    fp_otras = db.Column(db.Float)
    tel_contacto = db.Column(db.String)
    tel_contacto2 = db.Column(db.String)
    
    __table_args__ = (UniqueConstraint('ent_code', 'transaction_id', 'custcode', 'dte', 'monto', name='_pago_uc'),)

    def __repr__(self):
        return f'<Pago {self.id}>'

class Objetivos(db.Model):
    __tablename__ = 'objetivos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # Se cambia referencia a usuarios.codigo
    id_empleado = db.Column(db.String, db.ForeignKey('usuarios.codigo'), nullable=False) 
    fecha = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    sim_card_prepago = db.Column(db.Integer)
    flex_max = db.Column(db.Integer)
    fijos_hfc_dth = db.Column(db.Integer)
    internet_pospago = db.Column(db.Integer)
    migraciones_pospago_net = db.Column(db.Integer)
    fidepuntos_pospago = db.Column(db.Integer)
    fidepuntos_up = db.Column(db.Integer)
    reemplazo_pospago = db.Column(db.Integer)
    reemplazo_up = db.Column(db.Integer)
    fide_reemp_internet_up = db.Column(db.Integer)
    aumentos_plan_pos_net = db.Column(db.Integer)
    recargas = db.Column(db.Integer)

    usuario_rel = db.relationship('Usuarios', backref=db.backref('objetivos_rel', lazy=True))

    def __repr__(self):
        return f'<Objetivo {self.id}>'

class Incentivos(db.Model):
    __tablename__ = 'incentivosEmpleados'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo_venta = db.Column(db.String, nullable=False)
    Grupo = db.Column(db.Integer, nullable=False)
    Grupo_Anterior = db.Column(db.Integer)
    Comision_100 = db.Column(db.Integer, nullable=False)
    Comision_75 = db.Column(db.Integer, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f'<Incentivo {self.tipo_venta}>'