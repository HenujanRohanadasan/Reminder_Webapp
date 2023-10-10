from flask import Blueprint
from flask_login import login_required
import json, random

charts = Blueprint('charts', __name__)

@charts.route('/chart', methods=['GET', 'POST'])
def charts_data():
    temperature = []
    for i in range(0,10):
        temperature.append(random.randint(0, 100))
        
    data = {
        "temperature":temperature
    }
    
    return data
