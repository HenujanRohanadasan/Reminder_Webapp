import time
import atexit
from . import scheduler, db, app
from datetime import datetime, timedelta
from .models import Device

ctx = app.app_context()

@scheduler.task('interval', id='job1', minutes=5)
def check_device_status():
    with ctx:
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
    