from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager
from tinyflux import TinyFlux
from flask_mqtt import Mqtt
from dotenv import load_dotenv
from flask_apscheduler import APScheduler
import os

DB_NAME = 'database.db'
db = SQLAlchemy()
ts_db = TinyFlux('instance/tiny.db')
mqtt_client = Mqtt()
scheduler = APScheduler()
app = None

def create_app():
    #Configure and Initiate App (private key, public key, secret key, database uri)
    global app
    app = Flask(__name__, instance_relative_config=True)
    load_dotenv()
    app.config.from_prefixed_env()
    mqtt_client.init_app(app)
    scheduler.init_app(app)
    db.init_app(app)

    #Register Blueprints
    from .views import views
    from .auth import auth
    from .features import features
    from .sensor_manager import sensor_manager
    from .portal_manager import portal_manager
    from .charts import charts
    
    from . import schedules
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(features, url_prefix='/')
    app.register_blueprint(sensor_manager, url_prefix='/')
    app.register_blueprint(portal_manager, url_prefix='/')
    app.register_blueprint(charts, url_prefix='/')

    #create Database
    from .models import User, Subscription, Sensor, Switch, Location, Zone, Id, Feature_Note, Device
    with app.app_context():
        db.create_all()
        c_app = current_app
        
    #Login Manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    from . import mqtt
    
    return app


@mqtt_client.on_connect()
def handle_connect(client, userdata, flags, rc):
    topic = 'sensor/#'
    topic2 = 'status/client/#'
    if rc == 0:
        print('Connected successfully')
        mqtt_client.subscribe(topic)
        mqtt_client.subscribe(topic2) 
    else:
        print('Bad connection. Code:', rc)
        

