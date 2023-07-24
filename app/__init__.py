import redis
from flask import Flask
from datetime import datetime, timedelta
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import app_config
from flask_migrate import Migrate
from flask_session import Session
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, unset_jwt_cookies
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
# load_dotenv()

def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')

    app.config["SESSION-COOKIE_SAMESITE"] = None
    # app.config["SESSION_PERMANENT"] = False
    # app.config["SESSION_USE_SIGNER"] = True
    # app.config["SESSION_TYPE"] = "redis"
    # app.config["SESSION_REDIS"] = redis.from_url("redis://127.0.0.1:6379")

    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=3)
    app.config["JWT_SECRET_KEY"] = "Thainghia02"
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False
    app.config['JWT_ACCESS_CSRF_HEADER_NAME'] = 'X-CSRF-TOKEN'
    app.config['JWT_COOKIE_SAMESITE'] = 'NONE'
    JWTManager(app)

    # app.config['WTF_CSRF_ENABLED'] = False
    # csrf = CSRFProtect(app)

    # Session(app)
    # Bcrypt(app)

    db.init_app(app)

    login_manager.init_app(app)

    migrate = Migrate(app, db)

    from app import models

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .customer import customer as customer_blueprint
    app.register_blueprint(customer_blueprint)

    from .barber import barber as barber_blueprint
    app.register_blueprint(barber_blueprint)

    from .service import service as service_blueprint
    app.register_blueprint(service_blueprint)

    from .booking import booking as booking_blueprint
    app.register_blueprint(booking_blueprint)

    from .worktime import worktime as worktime_blueprint
    app.register_blueprint(worktime_blueprint)

    from .customerimage import customerimage as customerimage_blueprint
    app.register_blueprint(customerimage_blueprint)
    return app