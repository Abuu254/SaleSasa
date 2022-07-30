from flask import Flask, current_app, request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_moment import Moment
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO



db = SQLAlchemy()
login = LoginManager()
mail= Mail()
migrate = Migrate()
moment = Moment()
bootstrap = Bootstrap()
login.login_view = 'auth.login'
login.login_message ='Please log in to access this page.'
socketio = SocketIO()

def create_app(configuration=Config):
    app = Flask(__name__)
    app.config.from_object(configuration)

    db.init_app(app)
    login.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    moment.init_app(app)
    bootstrap.init_app(app)
    socketio.init_app(app)

    from app.main import bp_main
    app.register_blueprint(bp_main)

    from app.auth import bp_auth as auth_bp
    app.register_blueprint(auth_bp)

    from app.users import bp_users
    app.register_blueprint(bp_users)

    return app

from app import models


