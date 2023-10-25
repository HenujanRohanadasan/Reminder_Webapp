from influxdb import InfluxDBClient

client = InfluxDBClient('localhost', 8086)
client.create_database('time_series_db')
client.get_list_database()
client.switch_database('time_series_db')