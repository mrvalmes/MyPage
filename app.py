import os
from flask import Flask
from datetime import timedelta
from config import config
from extensions import db, jwt
from blueprints.auth import auth_bp
from blueprints.main import main_bp
from blueprints.api import api_bp

def create_app(config_name=None):
    """
    Application Factory: Crea y configura la instancia de la aplicación Flask.
    """
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'default')

    app = Flask(__name__)
    
    # 2. Cargar la configuración desde el objeto importado
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # 3. Inicializar las extensiones con la app
    db.init_app(app)
    jwt.init_app(app)
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)
    
    # Configuración para Cookies
    app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]
    app.config["JWT_COOKIE_SECURE"] = False # Cambiar a True en producción con HTTPS
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False # Simplificado para este caso
    
    # Registrar Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)

    # Contexto de la aplicación para operaciones de BD fuera de las rutas
    with app.app_context():
        db.create_all() # Asegura que las tablas existen al iniciar la app si no están

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)