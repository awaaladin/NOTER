from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path, remove
from flask_login import LoginManager
from flask_mail import Mail
from itsdangerous import URLSafeTimedSerializer
import os



db = SQLAlchemy()
DB_NAME = "database.db"
mail = Mail()


def generate_token(email):
    serializer = URLSafeTimedSerializer('SECRET_KEY')
    return serializer.dumps(email, salt='email-confirm-salt')

def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer('SECRET_KEY')
    try:
        email = serializer.loads(token, salt='email-confirm-salt', max_age=expiration)
    except:
        return False
    return email


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.getenv('EMAIL_USER')
    app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASS')
    db.init_app(app)
    mail.init_app(app)



    from .models import User, Note
    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    with app.app_context():
        db.create_all()
        print("database created.")

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'  # fixed typo
    login_manager.login_message = 'Please log in to access this page'
    login_manager.login_message_category = 'warning'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app  


