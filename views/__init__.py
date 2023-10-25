from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager
from influxdb import InfluxDBClient

DB_NAME = 'database.db'
db = SQLAlchemy()
idb_client = InfluxDBClient(host='0.0.0.0', port=8086)

print(idb_client.get_list_database())
if not idb_client.get_list_database():
    idb_client.create_database('ts_database')

idb_client.switch_database('ts_database')


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
    from .features import features
    from .sensor_manager import sensor_manager
    from .sensor_views import sensor_views
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(features, url_prefix='/')
    app.register_blueprint(sensor_manager, url_prefix='/')
    app.register_blueprint(sensor_views, url_prefix='/')
    
    #create Database
    from .models import User, Subscription, Temp_Data
    with app.app_context():
        db.create_all()
        from . import sensor_manager
        sensor_manager.start_all_add()
        
    #Login Manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
        
    return app
