from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True)
    user_name = db.Column(db.String(128))
    password = db.Column(db.String(128))
    subscriptions = db.relationship('Subscription')
    
class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subscription_data = db.Column(db.Text, nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
class Temp_Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    temperatures = db.Column(db.JSON, nullable=False)
    time = db.Column(db.DateTime, default=func.now())
    