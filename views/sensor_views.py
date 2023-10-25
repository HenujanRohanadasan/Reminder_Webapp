from flask import Blueprint, request, render_template, redirect, url_for
from flask_login import current_user, login_required

sensor_views = Blueprint('sensor_manager', __name__)

#LIVE
@sensor_views.route('/live/sensor_data', methods=['GET'])
@login_required
def sensor_data_live():
    return redirect(url_for('sensor_manager.temperature_live'))


@sensor_views.route('/sensor_data/live/temperature', methods=['GET'])
@login_required
def temperature_live():
    return render_template('sensor_data.html', user=current_user, href='/charts/live/temp', chart_type='line', active='temperature', live=True)


@sensor_views.route('/sensor_data/live/humidity', methods=['GET'])
@login_required
def humidity_live():
    return render_template('sensor_data.html', user=current_user, href='/charts/live/hum', chart_type='bar', active='humidity', live=True)


#NOT_LIVE
@sensor_views.route('/sensor_data', methods=['GET'])
@login_required
def sensor_data():
    return redirect(url_for('sensor_manager.temperature'))


@sensor_views.route('/sensor_data/temperature', methods=['GET'])
@login_required
def temperature():
    return render_template('sensor_data.html', user=current_user, href='/charts/temp', chart_type='line', active='temperature', live=False)


@sensor_views.route('/sensor_data/humidity', methods=['GET'])
@login_required
def humidity():
    return render_template('sensor_data.html', user=current_user, href='/charts/hum', chart_type='bar', active='humidity', live=False)

