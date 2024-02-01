from . import db, mqtt_client, ts_db, app
from tinyflux import Point
import json
from .models import Device
from datetime import datetime

ctx = app.app_context()

@mqtt_client.on_message()
def handle_message(client, userdata, message):
    topic = message.topic
    payload = message.payload.decode('utf-8')
    can_execute = False
    topic_elements = topic.split('/')
    print(f'message recieved topic: {topic}, msg: {payload}')
    
    try: 
        payload_float = float(payload)
    except:
        print('invalid format sent')
    else:
        can_execute = True

    if can_execute and len(topic_elements) == 4 and topic.startswith('sensor'):   
        point = Point(
            tags={"type": topic_elements[1], "location": topic_elements[2], "zone": topic_elements[3]},
            fields={"value": payload_float}
        )
        ts_db.insert(point)
        
    if topic.startswith("status") and len(topic_elements) == 3:
        with ctx:
            device = Device.query.filter_by(device_location=topic_elements[1], device_zone=topic_elements[2]).first()
            device.status = payload
            device.status_time = datetime.now()
            db.session.commit()
        
        