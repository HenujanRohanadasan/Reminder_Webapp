from flask import Blueprint
from flask_login import login_required
from . import idb_client 
import json, random
import time as Time
import threading as th

sensor_manager = Blueprint('charts', __name__)


def start_all_add():
    temp_add_db(True)


#temp related
#write
def get_temp():
    data = random.randint(0, 100)
    time = Time.localtime()
    current_time = Time.strftime('%H:%M:%S', time)
    
    return data, current_time


def temp_add_db(start_timer):
    if start_timer:
        th.Timer(60, temp_add_db, args=[False]).start()
    
    data, current_time = get_temp()
    
    data_point = [{
        "measurement": "temperature",
        "tags": {
            "location": "farm",
            "sensor_id": f"{1}"
            },
        "time": f"{current_time}",
        "fields": {
            "value": f"{data}"
            }
    }]
    
    idb_client.switch_database('ts_database')
    idb_client.write_points(data_point)


def get_live_temp():
    data, current_time = get_temp()
    chart_data = {
        "data": data,
        "time": current_time
    }
    
    return chart_data


#read
def read_temp():    
    idb_client.switch_database('ts_database')

    result = idb_client.query('SELECT "value" FROM "ts_database"."autogen"."temperature" WHERE time > now() - 4d GROUP BY "location"')
    points = result.get_points(tags={"location": "farm"})

    chart_data = {
        "data": [],
        "time": []
    }
    
    for point in points:
        cart_data_len = len(chart_data["data"])
        if cart_data_len < 20:
            chart_data["data"].append(point["value"])
            chart_data["time"].append(point["time"])
        else:
            break
        
    return chart_data
#temp related


def hum_add():
    th.Timer(1, temp_add).start()
    data = random.randint(0, 100)
    time = Time.localtime()
    current_time = Time.strftime('%H:%M:%S', time)

    chart_data = {
        "data": data_point["fields"]["value"],
        "time": data_point["time"]
    }
    
    return chart_data
    

@sensor_manager.route('/charts/live/temp', methods=['GET'])
def chart_temp_live():
    return get_live_temp()


@sensor_manager.route('/charts/live/hum', methods=['GET'])
def chart_hum_live():
    return hum_add()

@sensor_manager.route('/charts/temp', methods=['GET'])
def chart_temp():
    return read_temp()


@sensor_manager.route('/charts/hum', methods=['GET'])
def chart_hum():
    return read_temp()