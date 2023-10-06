from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager

DB_NAME = 'database.db'
db = SQLAlchemy()

def create_app():
    #Configure and Initiate App (private key, public key, secret key, database uri)
    app = Flask(__name__, instance_relative_config=True)
    app.config['VAPID_PUBLIC_KEY'] = 'BL3IYRhzyEIvojcvkd2UgfVu9KR-p4rW9g5Q5oqHS8LSHiryirZasyRz4Vl6ibA2ZTeIVUsZ1vQXYzbheT_JMcA'
    app.config['VAPID_PRIVATE_KEY'] = 'hVAzxGFpDi1H-weRbpyX7nHGZp_OUjt08-BKpr4Juew'
    app.config['SECRET_KEY'] = 'henujanIStheKING'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)
    
    #Register Blueprints
    from .views import views
    from .auth import auth
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    
    #create Database
    from .models import User
    with app.app_context():
        db.create_all()
        
    return app