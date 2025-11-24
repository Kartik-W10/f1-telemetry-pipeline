F1 Real-Time Telemetry Data Platform

Project Overview

This project is an end-to-end real-time data pipeline designed to simulate the high-velocity telemetry processing used in Formula 1.

It addresses the critical engineering challenge of "Hot Path" analytics: delivering sensor data from the car to the pit wall with minimal latency for strategic decision-making.

The system streams granular telemetry data (Speed, RPM, Throttle, etc.) from actual F1 races (via fastf1), buffers it through a decoupled Kafka message broker, processes it via Python microservices, and provides instant visualization using InfluxDB and Grafana.

Architecture

The pipeline follows a modern, event-driven microservices architecture:



Producer (The Edge): Replays historical race data (Bahrain 2023) lap-by-lap to simulate a live car. Enriches raw telemetry with Driver IDs.

Broker (The Highway): Apache Kafka decouples ingestion from processing, ensuring data is never lost even if consumers fail.

Storage (The Memory): InfluxDB (Time-Series Database) is optimized for high-write, high-read loads typical of sensor data.

Visualization (The Strategy): Grafana connects to InfluxDB to render live speed traces, allowing for comparison of driver performance and tire degradation analysis.

🛠️ Tech Stack

Language: Python 3.9+

Orchestration: Docker & Docker Compose

Message Broker: Apache Kafka (Confluent Image)

Database: InfluxDB v2 (Time-Series)

Visualization: Grafana

Libraries: fastf1, kafka-python, influxdb-client, pandas

📊 Dashboard Preview

Live Telemetry Trace:
Visualizing speed comparisons between drivers (e.g., VER vs PER) in real-time.

(Note: Replace this line with your actual screenshot after uploading)

🚀 Getting Started

Prerequisites

Docker Desktop (installed and running)

Python 3.9+

Installation & Run

Clone the Repository

git clone [https://github.com/YOUR_USERNAME/f1-telemetry-pipeline.git](https://github.com/YOUR_USERNAME/f1-telemetry-pipeline.git)
cd f1-telemetry-pipeline


Set Up Environment

python -m venv .venv
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

pip install -r requirements.txt


Start the Infrastructure
This command spins up Kafka, Zookeeper, InfluxDB, and Grafana in Docker containers.

docker compose up -d


Start the Pipeline
Open two separate terminals (ensure .venv is active in both):

Terminal 1 (The Pit Wall - Consumer):

python consumer.py


Terminal 2 (The Car - Producer):

python producer.py


View the Dashboard

Go to http://localhost:3000

Login: admin / admin

Data Source: InfluxDB (URL: http://influxdb:8086, Org: f1, Token: password)

Query (Flux):

from(bucket: "telemetry")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "car_telemetry")
  |> filter(fn: (r) => r._field == "speed")
  |> group(columns: ["driver"])
  |> yield(name: "mean")




🤝 Contributing

 Suggestions and pull requests are welcome.
