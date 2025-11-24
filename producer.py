import fastf1
import time
import json
from kafka import KafkaProducer
import pandas as pd

try:
    # 1. Configure Kafka Producer
    producer = KafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    print("Producer connected to Kafka.")
except Exception as e:
    print(f"Error connecting to Kafka: {e}")
    print("Is Kafka running? Start it with 'docker compose up'.")
    exit()

# 2. Get F1 Data
print("Enabling Fast-F1 cache...")
fastf1.Cache.enable_cache('fastf1_cache') 

print("Loading F1 session data (2023, Bahrain, R)... This may take a moment.")
session = fastf1.get_session(2023, 'Bahrain', 'R')
session.load()
print(f"Loaded session data for {session.event['EventName']} {session.event.year}")

print("Building combined telemetry data... This may take a few minutes.")

all_telemetry = []
for index, lap in session.laps.iterlaps():
    try:
        telemetry_lap = lap.get_car_data() 
        if not telemetry_lap.empty:
            
            # -----------------------------------------------------------------
            # THE FIX: Enrich the data with the Driver's ID
            # -----------------------------------------------------------------
            telemetry_lap['Driver'] = lap.Driver  # <-- THIS IS THE FIX
            # -----------------------------------------------------------------
            
            all_telemetry.append(telemetry_lap)
    except Exception as e:
        print(f"Could not load telemetry for lap {lap.LapNumber}: {e}")

if not all_telemetry:
    print("Error: No telemetry data could be loaded.")
    exit()

print("Combining and sorting telemetry data...")
telemetry = pd.concat(all_telemetry)
telemetry = telemetry.sort_values(by='Date')

print("Telemetry data built. Starting stream...")

# 3. Stream Data
for index, row in telemetry.iterrows():
    message = row.to_dict()
    
    for key, value in message.items():
        if isinstance(value, pd.Timedelta):
            message[key] = str(value)
        elif isinstance(value, pd.Timestamp):
            message[key] = value.isoformat()
        elif pd.isna(value):
            message[key] = None
    
    producer.send('telemetry-raw', value=message)
    
    print(f"Sent: {message.get('Date')} - Driver: {message.get('Driver')} - Speed: {message.get('Speed')}")
    
    time.sleep(0.01) # <-- Speeding up the stream slightly

producer.flush()

print("Data streaming complete.")