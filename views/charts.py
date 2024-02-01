from flask import Blueprint, request
from flask_login import current_user, login_required
from tinyflux import TagQuery
from .models import Sensor
from . import ts_db
import pandas as pd
import plotly.graph_objs as go
import plotly, json
from datetime import datetime
from dateutil import tz


charts = Blueprint('charts', __name__)
tg = TagQuery()

@charts.route('/chart', methods=['GET'])
def load_chart():
    device_id = request.args['sensor_id']
    chart_type = request.args['chart_type']
    fig = go.Figure()
    graphJson = json.dumps(chart_data(device_id=device_id, chart_type=chart_type, fig=fig, show_title=True), cls=plotly.utils.PlotlyJSONEncoder)
    
    return graphJson

@charts.route('/chart/multiple', methods=['GET'])
def load_multiple_chart():
    chart_type = request.args['chart_type']
    device_type = request.args['device_type']
    
    devices = Sensor.query.filter_by(device_type=device_type)
    
    fig = go.Figure()
    for device in devices:
        fig = chart_data(device_id=device.id, chart_type=chart_type, fig=fig, show_title=False)
    
    graphJson = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJson


def chart_data(device_id, chart_type, fig, show_title):
    sensor = Sensor.query.filter_by(id=device_id).first()
    queries = ts_db.search(tg.type == f'{sensor.device_type}')

    x = []
    y = []
    for query in queries:
        if query.tags["location"] == sensor.device.device_location and query.tags["zone"] == f'zone{sensor.device.device_zone}':
            utc_time = query.time
            utc_time = utc_time.replace(tzinfo=tz.tzutc())
            loc_time = utc_time.astimezone(tz.tzlocal())
            x.append(loc_time)
            y.append(query.fields["value"])

    df = pd.DataFrame({'x': x, 'y': y})
    
    if chart_type == 'Line':
        fig.add_trace(go.Scatter(x = df['x'], y = df['y'],
                                mode = 'lines + markers',
                                name=f'sensor/{sensor.device_type}/{sensor.device.device_location}/zone{sensor.device.device_zone} {sensor.id}'))
        
        if show_title:
            fig.update_layout(title = f'sensor/{sensor.device_type}/{sensor.device.device_location}/zone{sensor.device.device_zone}', xaxis_title='time', yaxis_title=f'{sensor.device_type}')
            
        else:
            fig.update_layout(title = f'Compare {sensor.device_type} sensor datas', xaxis_title='time', yaxis_title=f'{sensor.device_type}')

        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=30, label="30m", step="minute", stepmode="backward"),
                    dict(count=1, label="1d", step="day", stepmode="backward"),
                    dict(count=7, label="1w", step="day", stepmode="backward"),
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )
    
    return fig
