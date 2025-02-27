# app/__init__.py
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'  # Redireciona para a rota de login se não autenticado
login.login_message = 'Por favor, faça login para acessar esta página.'
login.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    # from app.admin import bp as admin_bp  # Blueprint para rotas de admin
    # app.register_blueprint(admin_bp, url_prefix='/admin')

    # Registrar blueprints (organização das rotas)
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.war import bp as war_bp
    app.register_blueprint(war_bp)

    from app.players import bp as players_bp
    app.register_blueprint(players_bp)
    return app

from app import models

# Adicione isso *APÓS* a definição de 'login' e *ANTES* da função create_app.
# Mas *DEPOIS* de importar 'db' e 'models'.  A ordem é importante!
from app.models import User

@login.user_loader
def load_user(id):
    return User.query.get(int(id))