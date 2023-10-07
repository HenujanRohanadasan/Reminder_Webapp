from . import db
from flask_login import UserMixin

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
    