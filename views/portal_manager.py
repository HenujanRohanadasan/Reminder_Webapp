from flask import Blueprint, request, url_for, redirect, flash, render_template
from flask_login import current_user, login_required
from . import db
from .models import Location, Zone, Switch, Sensor, Id

portal_manager = Blueprint('portal_manager', __name__)


@portal_manager.route('/add/location', methods=['POST'])
@login_required
def add_location():
    location_name = request.form.get('name') 
    location = Location.query.filter_by(location_name=location_name).first()
               
    if not location:
        new_location = Location(location_name=location_name, user_id=current_user.id)
        db.session.add(new_location)
        db.session.commit()
    else:
        flash('Location name already exists!', category='error')
    
    return redirect(url_for('portal_manager.portal'))


@portal_manager.route('/add/zone/<location_id>', methods=['POST'])
@login_required
def add_zone(location_id):
    zone_name = request.form.get('name') 
    zone = Zone.query.filter_by(zone_name=zone_name).first()
    
    if not zone:
        new_zone = Zone(zone_name=zone_name, location_id=location_id)
        db.session.add(new_zone)
        db.session.commit()
    else:
        flash('Zone name already exists!', category='error')
        
    for name, value in request.form.items():
        if not name == 'name':
            if name.startswith('Switch'):
                new_id = Id(switch_sensor_id=value, device_type='Switch', zone_id=new_zone.id)
            else:
                new_id = Id(switch_sensor_id=value, device_type='Sensor', zone_id=new_zone.id)
                
            db.session.add(new_id)
            db.session.commit()
    
    return redirect(url_for('portal_manager.portal'))


@portal_manager.route('/delete/location/<location_id>', methods=['GET'])
@login_required
def delete_location(location_id):
    location = Location.query.get(location_id)
    for zone in location.zones:
        for _id in zone:
            db.session.delete(_id)
        db.session.delete(zone)
        
    db.session.delete(location)
    db.session.commit()
    return redirect(url_for('portal_manager.portal'))

    
@portal_manager.route('/delete/zone/<zone_id>', methods=['GET'])
@login_required
def delete_zone(zone_id):
    zone = Zone.query.get(zone_id)
    for _id in zone.switch_sensor_ids:
        db.session.delete(_id)
         
    db.session.delete(zone)
    db.session.commit()
    return redirect(url_for('portal_manager.portal'))


@portal_manager.route('/portal/zones/<location>', methods=['GET'])
@login_required
def get_zones(location):
    location = Location.query.filter_by(location_name=location).first()
    switches = Switch.query.all()
    sensors = Sensor.query.all()
    return render_template('portal_zone.html', user=current_user, location=location, switches=switches, sensors=sensors)


@portal_manager.route('/portal', methods=['GET'])
@login_required
def portal():
    return redirect(url_for('portal_manager.get_locations'))


@portal_manager.route('/portal/locations', methods=['GET'])
@login_required
def get_locations():
    return render_template('portal_location.html', user=current_user)
    
