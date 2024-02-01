from flask import Blueprint, request, redirect, url_for
from . import db, ts_db, mqtt_client, create_app
from .models import Sensor, Switch, Device, Subscription
from datetime import datetime
from tinyflux import Point
import json, time
from .features import push_notification

sensor_manager = Blueprint('sensor_manager', __name__)

@sensor_manager.route('/boards/register', methods=['POST'])
def register_device_zone():
    device_details = request.get_json()
    location = device_details["location"]
    zone = device_details["zone"]
    sensors = device_details["sensors"]
    switches = device_details["switches"]
    device_id = 0
    
    device = Device.query.filter_by(device_location=location, device_zone=zone).first()
    if not device:
        new_device = Device(device_location=location, device_zone=zone, status='1', status_time=datetime.now())
        db.session.add(new_device)
        db.session.commit()
        device_id = new_device.id
        subscriptions = Subscription.query.all()
        subject = 'New Device Added'
        body = f'Location: {location}, Zone: {zone}'
        for subscription in subscriptions:
            push_notification(subject, body, subscription)
    else:
        device_id = device.id
        device.status = '1'
        device.status_time = datetime.now()
        sensors_db = Sensor.query.all()
        switches_db = Switch.query.all()
        for sensor in sensors_db:
            if not sensor.device_type in sensors:
                db.session.delete(sensor)
        for switch in switches_db:
            if not switch.device_type in switches:
                db.session.delete(sensor)
        db.session.commit()
            
        
    for sensor in sensors:
        sensor_device = Sensor.query.filter_by(device_type=sensor, device_id=device_id).first()
        if not sensor_device:
            new_sensor = Sensor(device_type=sensor, device_id=device_id)
            db.session.add(new_sensor)
            db.session.commit()
            
                
    for switch in switches:
        device = Switch.query.filter_by(device_type=switch, device_id=device_id).first()
        if not device:
            new_switch = Switch(device_type=switch, device_id=device_id)
            db.session.add(new_switch)
            db.session.commit()

    return "register success"


@sensor_manager.route('/delete/device')
def delete_device():
    device_id = request.args['device_id']
    Device.query.filter_by(id=device_id).delete()
    Sensor.query.filter_by(device_id=device_id).delete()
    Switch.query.filter_by(device_id=device_id).delete()
    db.session.commit()
    
    return redirect(url_for('views.get_devices'))
 