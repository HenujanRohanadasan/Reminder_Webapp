from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True)
    user_name = db.Column(db.String(128))
    password = db.Column(db.String(128))
    subscriptions = db.relationship('Subscription')
    locations = db.relationship('Location')
 
    
class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subscription_data = db.Column(db.Text, nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
 
class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_zone = db.Column(db.Text)
    device_location = db.Column(db.Text)
    status = db.Column(db.Text, default='0')
    status_time = db.Column(db.DateTime(timezone=True), default=func.now())
    sensors = db.relationship('Sensor', backref='device')
    switches = db.relationship('Switch', backref='device')

   
class Sensor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_type = db.Column(db.Text)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'))


class Switch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_type = db.Column(db.Text)
    status = db.Column(db.Text, default='0')
    watering_min_bound = db.Column(db.Integer, default=20)
    watering_max_bound = db.Column(db.Integer, default=60)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'))
    

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location_name = db.Column(db.String(255))
    zones = db.relationship('Zone', backref='location')   
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) 
    
    
class Zone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    zone_name = db.Column(db.String(255))
    automation_status = db.Column(db.Integer, default=1)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    switch_sensor_ids = db.relationship('Id', backref='zone')
    feature_notes = db.relationship('Feature_Note', backref='zone')

    
class Id(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    switch_sensor_id = db.Column(db.Integer)
    device_type = db.Column(db.String(255))
    zone_id = db.Column(db.Integer, db.ForeignKey('zone.id'))
    
class Feature_Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_time = db.Column(db.DateTime(timezone=True), default=func.now())
    feature = db.Column(db.Text)
    zone_id = db.Column(db.Integer, db.ForeignKey('zone.id'))
    