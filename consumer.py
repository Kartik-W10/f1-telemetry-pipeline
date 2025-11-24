import json
from kafka import KafkaConsumer
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import time

# 1. Configure InfluxDB
token = "password"  # Your DOCKER_INFLUXDB_INIT_PASSWORD
org = "f1"
bucket = "telemetry"

# Retry connection to InfluxDB
influx_ready = False
print("Attempting to connect to InfluxDB...")
while not influx_ready:
    try:
        client = InfluxDBClient(url="http://localhost:8086", token=token, org=org)
        health = client.health()
        if health.status == "pass":
            influx_ready = True
            print("InfluxDB client connected and healthy.")
        else:
            print("InfluxDB not ready, retrying in 5s...")
            time.sleep(5)
    except Exception as e:
        print(f"InfluxDB connection failed: {e}. Retrying in 5s...")
        time.sleep(5)

write_api = client.write_api(write_options=SYNCHRONOUS)

# 2. Configure Kafka Consumer
print("Attempting to connect to Kafka consumer...")
consumer = KafkaConsumer(
    'telemetry-raw',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest', # Start from the beginning
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)
print("Kafka consumer connected. Waiting for messages...")

# 3. Read from Kafka and Write to InfluxDB
for message in consumer:
    data = message.value

    # Skip if essential data is missing
    if 'Driver' not in data or 'Speed' not in data or 'Date' not in data:
        continue

    # Ensure numeric fields are correctly typed
    try:
        speed = int(data.get('Speed'))
        rpm = int(data.get('RPM'))
        gear = int(data.get('nGear'))
        throttle = int(data.get('Throttle'))
        brake = bool(data.get('Brake')) # InfluxDB handles boolean
    except (ValueError, TypeError):
        continue # Skip record if data is bad

    point = Point("car_telemetry") \
        .tag("driver", data.get('Driver')) \
        .tag("car", data.get('Car', 'Unknown')) \
        .field("speed", speed) \
        .field("rpm", rpm) \
        .field("gear", gear) \
        .field("throttle", throttle) \
        .field("brake", brake) \
        .time(data['Date'], WritePrecision.NS) # Use the real event time

    write_api.write(bucket=bucket, org=org, record=point)
    print(f"Wrote to InfluxDB: {data['Date']} - Driver: {data['Driver']} - Speed: {speed}")