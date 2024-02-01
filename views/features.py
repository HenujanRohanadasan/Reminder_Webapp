from flask import Blueprint, request, redirect, json, current_app, jsonify, flash, url_for, render_template
from flask_login import current_user, login_required
from pywebpush import webpush, WebPushException
from .models import User, Subscription, Switch, Feature_Note, Sensor, Id, Device, Zone
from . import db, mqtt_client
from datetime import datetime

features = Blueprint('features', __name__)
   
@features.route("/api/push-subscriptions", methods=["POST"])
@login_required
def create_push_subscription():
    json_data = request.get_json()
    subscription = Subscription.query.filter_by(
        user_id=current_user.id
    ).first()
    if subscription is None:
        subscription = Subscription(
            subscription_data=json_data['subscription_json'],
            user_id=current_user.id
        )
        db.session.add(subscription)
        db.session.commit()
    return jsonify({
        "status": "success"
    })
    
    
def push_notification(subject, body, push_subscription):
    try:
        response = webpush(
            subscription_info=json.loads(push_subscription.subscription_data),
            data=json.dumps({"title": subject, "body": body}),
            vapid_private_key=current_app.config['VAPID_PRIVATE_KEY'],
            vapid_claims={"sub": "mailto:webpush@mydomain.com"}
        )
        return response.ok
    except WebPushException as ex:
        if ex.response and ex.response.json():
            extra = ex.response.json()
            print("Remote service replied with a {}:{}, {}",
                  extra.code,
                  extra.errno,
                  extra.message
                  )
        return False
    

@features.route('/publish', methods=['GET'])
def change_state():
    switch_id = request.args['switch_id']
    switch = Switch.query.filter_by(id=switch_id).first()
    
    if switch.status == '0':
        switch.status = str(1)
        publish_result = mqtt_client.publish(f'switch/{switch.device_type}/{switch.device.device_location}/zone{switch.device.device_zone}', 1, qos=0)
    else:
        switch.status = str(0)
        publish_result = mqtt_client.publish(f'switch/{switch.device_type}/{switch.device.device_location}/zone{switch.device.device_zone}', 0, qos=0)

    db.session.commit()
    return str(publish_result)

@features.route('/features/notes/add', methods=['POST'])
def add_zone_feature():
    feature = request.form.get('feature')
    zone_id = request.form.get('zone_id')
    loc_time = datetime.now()

    new_feature = Feature_Note(feature=feature, zone_id=zone_id, date_time=loc_time)
    db.session.add(new_feature)
    db.session.commit()
    
    feature_notes = Feature_Note.query.filter_by(zone_id=zone_id)
    return render_template('feature_note_zone.html', feature_notes=feature_notes)

@features.route('/features/notes/delete', methods=['GET'])
def delete_zone_features():
    feature_note_id = request.args['feature_note_id']
    zone_id = request.args['zone_id']
    
    Feature_Note.query.filter_by(id=feature_note_id).delete()
    db.session.commit()
    
    feature_notes = Feature_Note.query.filter_by(zone_id=zone_id)
    return render_template('feature_note_zone.html', feature_notes=feature_notes)

@features.route('/features/notes/nearest')
def nearest_feature():
    time_selected = request.args['time_selected']
    zone_id = request.args['zone_id']
    feature_notes = Feature_Note.query.filter_by(zone_id=zone_id)
    time_difference = ''
    feature = ''
    
    for feature_note in feature_notes:
        if feature_note.date_time < datetime.strptime(time_selected, "%Y-%m-%d %H:%M:%S.%f"):
            feature = feature_note.feature
            time_difference = round((datetime.strptime(time_selected, "%Y-%m-%d %H:%M:%S.%f") - feature_note.date_time).seconds / 3600, 2)

    if feature:
        return render_template('toast.html', time_difference=time_difference, feature=feature)
    else:
        return render_template('toast.html', time_difference='0', feature='No Feature Added In This Time!')
    
    
@features.route('/features/notes/multiple/nearest')
def nearest_feature_multiple():
    time_selected = request.args['time_selected']
    name = request.args['name']
    name_seperated = name.split(' ')
    zones = Id.query.filter_by(switch_sensor_id=name_seperated[1])
    time_difference = ''
    feature = ''
    
    for zone in zones:
        feature_notes = Feature_Note.query.filter_by(zone_id=zone.zone.id)
        for feature_note in feature_notes:
            if feature_note.date_time < datetime.strptime(time_selected, "%Y-%m-%d %H:%M:%S.%f"):
                feature += feature_note.feature + ' on ' + zone.zone.zone_name + '| '
                time_difference = 'Unknown '

    if feature:
        return render_template('toast.html', time_difference=time_difference, feature=feature)
    else:
        return render_template('toast.html', time_difference='0', feature='No Feature Added In This Time!')
    
@features.route('/change_automation')
def change_automation_status():
    zone_id = request.args["zone_id"]
    zone = Zone.query.filter_by(id=zone_id).first()
    zone.automation_status = int(not(zone.automation_status))
    print(f"changing automation status to {zone.automation_status}")
    db.session.commit()
    return "automation changed"
