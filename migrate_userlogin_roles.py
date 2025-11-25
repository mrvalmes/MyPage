# migrate_userlogin_roles.py
"""
Script de migración para recrear la tabla usuariosligin con:
- FK codigo_usuario a tabla usuarios
- Columna nivel_acceso como Enum
"""
from extensions import db
from models import UsuariosLogin, Usuarios, RolUsuario
from sqlalchemy import text
from app import create_app

def migrate():
    app = create_app()
    
    with app.app_context():
        print("🔧 Iniciando migración de usuariosligin...")
        
        # 1. Crear tipo ENUM en PostgreSQL si no existe
        print("📝 Creando tipo ENUM rolusuario...")
        with db.engine.connect() as conn:
            conn.execute(text("""
                DO $$ BEGIN
                    CREATE TYPE rolusuario AS ENUM ('admin', 'supervisor', 'ventas');
                EXCEPTION
                    WHEN duplicate_object THEN null;
                END $$;
            """))
            conn.commit()
        
        # 2. Respaldar datos existentes
        print("💾 Respaldando datos existentes...")
        with db.engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM usuariosligin"))
            usuarios_backup = result.fetchall()
            conn.commit()
        
        print(f"   ✓ {len(usuarios_backup)} usuarios respaldados")
        
        # 3. Eliminar y recrear la tabla
        print("🗑️  Eliminando tabla antigua...")
        with db.engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS usuariosligin CASCADE"))
            conn.commit()
        
        print("✨ Creando nueva tabla con estructura actualizada...")
        db.create_all()
        
        # 4. Restaurar datos existentes con migración de roles
        print("📥 Restaurando datos...")
        for usuario in usuarios_backup:
            # Mapear roles antiguos a nuevos
            nivel_antiguo = usuario[3]  # index 3 es nivel_acceso
            if nivel_antiguo == 'admin':
                nuevo_nivel = RolUsuario.ADMIN
            elif nivel_antiguo == 'viewer':
                nuevo_nivel = RolUsuario.VENTAS
            else:
                nuevo_nivel = RolUsuario.VENTAS  # default
            
            nuevo_usuario = UsuariosLogin(
                id=usuario[0],
                usuario=usuario[1],
                clave_hash=usuario[2],
                nivel_acceso=nuevo_nivel,
                codigo_usuario=None,  # Se asignará manualmente después
                fecha_creacion=usuario[4] if len(usuario) > 4 else None,
                ultimo_login=usuario[5] if len(usuario) > 5 else None,
                activo=usuario[6] if len(usuario) > 6 else 1
            )
            db.session.add(nuevo_usuario)
        
        db.session.commit()
        print(f"   ✓ {len(usuarios_backup)} usuarios restaurados")
        
        # 5. Mostrar usuarios existentes para que se les asigne código
        print("\n📋 Usuarios existentes (asignar codigo_usuario manualmente):")
        usuarios = UsuariosLogin.query.all()
        for u in usuarios:
            print(f"   - ID: {u.id}, Usuario: {u.usuario}, Rol: {u.nivel_acceso.value}, Código: {u.codigo_usuario}")
        
        print("\n✅ Migración completada exitosamente!")
        print("\n⚠️  SIGUIENTE PASO: Asigna codigo_usuario a los usuarios existentes desde el formulario de registro")

if __name__ == '__main__':
    migrate()
