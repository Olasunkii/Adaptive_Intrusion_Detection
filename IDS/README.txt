# Simple Intrusion Detection System (IDS)

This project simulates network traffic and detects basic attacks using Kafka.

## Project Structure
- **producer.py**: Simulates network events and sends them to Kafka.
- **consumer.py**: Monitors Kafka events, detects simple attacks, and logs alerts to `alerts.log`.
- **alerts.log**: Stores detected attack alerts with timestamps.
- **ids-env/**: Python virtual environment.

## How to Run
1. Start Docker containers (Zookeeper and Kafka):
    ```bash
    docker-compose up
    ```

2. Activate the Python virtual environment:
    ```bash
    source ids-env/Scripts/activate  # On Windows: ids-env\Scripts\activate
    ```

3. Start the producer:
    ```bash
    python producer.py
    ```

4. In a new terminal (still in the virtual environment), start the consumer:
    ```bash
    python consumer.py
    ```

## Current Detections
- Sensitive port access (ports 22, 23, 445).

## Requirements
- Python 3.8+
- Kafka-python library
- Docker

## Future Improvements
- Add more complex attack patterns (e.g., port scanning detection).
- Visualize real-time alerts in a simple dashboard.

---
