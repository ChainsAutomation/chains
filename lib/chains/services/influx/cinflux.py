import datetime
from influxdb import InfluxDBClient

# TODO: support writing with udp


class Influx():

    def __init__(self, host='localhost', port=8086, user='influx', password=None, database='test', method='http', writeport=None):
        self.client = InfluxDBClient(host, port, user, password, database)

    def insert(self, data):
        self.client.write_points(data)

    def data_template(self, name, tags, fields):
        return {
            "measurement": name,
            "tags": tags,  # tags dict (e.g. {location: home, type: temperature})
            "time": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "fields": fields  # values dict (e.g. {value=1, temp=12 } etc)
        }
