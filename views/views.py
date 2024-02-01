from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import current_user, login_required
from .models import Id, Switch, Sensor, Feature_Note, Device, Zone
from . import db
from datetime import datetime, timedelta

views = Blueprint('views', __name__)

@views.route('/', methods=['GET'])
@login_required
def home():
    sensors = Sensor.query.all()
    sensor_list = []
    sensor_type = ''
    for sensor in sensors:
        if not sensor.device_type == sensor_type:
            sensor_list.append(sensor.device_type)
            sensor_type = sensor.device_type
            
    return render_template('home.html', user=current_user, sensors=sensor_list)


@views.route('/monitor/<int:zone_id>', methods=['GET', 'POST'])
@login_required
def monitor(zone_id):
    if request.method == 'POST':
        selection = request.form.get('selected')
        selection_elements = selection.split(' ')
        _id = Id.query.filter_by(switch_sensor_id=selection_elements[1], device_type=selection_elements[0], zone_id=zone_id).first()
        if not _id:
            new_id = Id(switch_sensor_id=selection_elements[1], device_type=selection_elements[0], zone_id=zone_id)
            db.session.add(new_id)
            db.session.commit()
        else:
            flash('Element Already Added', category='error')
    
    ids = Id.query.filter_by(zone_id=zone_id)
    switches = Switch.query.all()
    sensors = Sensor.query.all()
    feature_notes = Feature_Note.query.filter_by(zone_id=zone_id)
    automation_status = Zone.query.filter_by(id=zone_id).first().automation_status
    return render_template('monitor_page.html', user=current_user, ids=ids, switches=switches, sensors=sensors, zone_id=zone_id, feature_notes=feature_notes, automation_status=automation_status)


@views.route('/monitor/delete/<int:_id>/<int:zone_id>', methods=['GET'])
def delete_id(_id, zone_id):
    Id.query.filter_by(id=_id).delete()
    db.session.commit()
    return redirect(url_for('views.monitor', zone_id=zone_id))


@views.route('/devices', methods=['GET'])
@login_required
def get_devices():
    sensors = Sensor.query.all()
    devices = Device.query.all()
    return render_template('devices.html', user=current_user, devices=devices)
