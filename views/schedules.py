import time
import atexit
from . import scheduler, db, app, mqtt_client, ts_db
from datetime import datetime, timedelta
from .models import Device, Zone, Id, Switch, Subscription
from tinyflux import TagQuery
from .features import push_notification

tg = TagQuery()

@scheduler.task('interval', id='job1', minutes=1)
def check_device_status():
    with app.app_context():
        devices = Device.query.all()
        for device in devices:
            five_minutes_before = datetime.now() - timedelta(minutes=5)
            device_status_time = device.status_time
            
            if device_status_time >= five_minutes_before:
                device.status = '1'
            else:
                device.status = '0'
                
            switches = device.switches
            for switch in switches:
                switch.status = '0'
                
            db.session.commit()
                        
@scheduler.task("interval", id="job2", minutes=1)
def check_watering_ststus():
     with app.app_context():
        zones = Zone.query.all()
        queries = ts_db.search(tg.type == "s_moist")
        
        for zone in zones:
            ids = Id.query.filter_by(zone_id=zone.id, device_type="Switch")
            for _id in ids:
                switch = Switch.query.filter_by(id=_id.switch_sensor_id).first()
                s_moist = 0
                
                for query in queries:   
                    if query.tags["location"] == switch.device.device_location and query.tags["zone"] == f'zone{switch.device.device_zone}': 
                        s_moist =  query.fields["value"]
                        break
                    
                if s_moist < switch.watering_min_bound:
                    if zone.automation_status == 1:
                        publish_result = mqtt_client.publish(f'switch/{switch.device_type}/{switch.device.device_location}/zone{switch.device.device_zone}', 1, qos=0)
                        print(publish_result)
                        
                    subject = "Open valve"
                    body = f'switch/{switch.device_type}/{switch.device.device_location}/zone{switch.device.device_zone} -> value:{s_moist}'
                    subscriptions = Subscription.query.all()
                    
                    for subscription in subscriptions:
                        push_notification(subject, body, subscription)
                elif s_moist > switch.watering_max_bound:
                    if zone.automation_status == 1:
                        publish_result = mqtt_client.publish(f'switch/{switch.device_type}/{switch.device.device_location}/zone{switch.device.device_zone}', 0, qos=0)
                        print(publish_result)
                        
                    subject = "Close valve"
                    body = f'switch/{switch.device_type}/{switch.device.device_location}/zone{switch.device.device_zone} -> value:{s_moist}'
                    subscriptions = Subscription.query.all()
                    
                    for subscription in subscriptions:
                        push_notification(subject, body, subscription)