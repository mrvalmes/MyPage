# test_roles_permissions.py
"""
Script de prueba para verificar el sistema de roles y permisos
"""
from app import create_app
from models import UsuariosLogin, Usuarios, RolUsuario, db
import bcrypt

def test_roles():
    app = create_app()
    
    with app.app_context():
        print("🧪 Probando sistema de roles y permisos\n")
        
        # 1. Verificar usuarios existentes
        print("📋 Usuarios existentes:")
        usuarios = UsuariosLogin.query.all()
        for u in usuarios:
            empleado_info = f" - {u.empleado.nombre}" if u.empleado else ""
            print(f"   ✓ {u.usuario} | Rol: {u.nivel_acceso.value} | Código: {u.codigo_usuario}{empleado_info}")
        
        print()
        
        # 2. Verificar permisos de cada rol
        print("🔐 Verificando permisos:")
        
        rutas_test = ['home', 'dashboard', 'posiciones', 'comisiones', 'procesos', 'mantenimientos']
        
        for user in usuarios:
            print(f"\n   Usuario: {user.usuario} ({user.nivel_acceso.value})")
            for ruta in rutas_test:
                tiene = user.tiene_permiso(ruta)
                icono = "✅" if tiene else "❌"
                print(f"      {icono} {ruta}")
        
        print("\n" + "="*60)
        print("✅ Prueba de permisos completada")
        print("="*60)
        
        # 3. Mostrar matriz de permisos
        print("\n📊 Matriz de Permisos:\n")
        print(f"{'Ruta':<20} {'Admin':<10} {'Supervisor':<12} {'Ventas':<10}")
        print("-" * 60)
        
        permisos_matriz = {
            RolUsuario.ADMIN: ['home', 'dashboard', 'posiciones', 'comisiones', 'procesos', 'mantenimientos'],
            RolUsuario.SUPERVISOR: ['home', 'dashboard', 'posiciones', 'comisiones'],
            RolUsuario.VENTAS: ['dashboard', 'comisiones', 'posiciones']
        }
        
        for ruta in rutas_test:
            admin_check = "✅" if ruta in permisos_matriz[RolUsuario.ADMIN] else "❌"
            super_check = "✅" if ruta in permisos_matriz[RolUsuario.SUPERVISOR] else "❌"
            ventas_check = "✅" if ruta in permisos_matriz[RolUsuario.VENTAS] else "❌"
            
            print(f"{ruta:<20} {admin_check:<10} {super_check:<12} {ventas_check:<10}")
        
        print("\n" + "="*60)
        print("📝 Instrucciones para crear usuarios de prueba:")
        print("="*60)
        print("\n1. Navega a: http://localhost:5000/Registro")
        print("2. Crea usuarios con diferentes roles:")
        print("   - Admin: Acceso total")
        print("   - Supervisor: Home, Dashboard, Posiciones, Comisiones")
        print("   - Ventas: Dashboard, Comisiones, Posiciones (solo sus datos)")
        print("\n")

if __name__ == '__main__':
    test_roles()
