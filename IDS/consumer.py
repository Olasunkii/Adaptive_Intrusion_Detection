import json
import time
import os
from collections import defaultdict
from kafka import KafkaConsumer

# ========== CONFIG ==========
TOPIC = 'network-logs'
BOOTSTRAP_SERVERS = ['localhost:9092']
ALERT_LOG_FILE = os.path.join("logs", "alerts.log")
PORT_SCAN_THRESHOLD = 10
TIME_WINDOW = 60  # seconds
SENSITIVE_PORTS = {22, 23, 3389}
SUSPICIOUS_PROTOCOLS = {"xmas", "null", "udp flood"}
# ============================

# Ensure log directory exists
os.makedirs("logs", exist_ok=True)

# Initialize Kafka consumer
consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=BOOTSTRAP_SERVERS,
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='ids-group'
)

print("Consumer started. Monitoring traffic...")

# Track connections for each source IP
connection_tracker = defaultdict(list)

def log_alert(alert_message: str):
    print(alert_message)  # Also print to console
    with open(ALERT_LOG_FILE, "a") as f:
        f.write(alert_message + "\n")
        f.flush()   # Ensure that alert is written in log file
        os.fsync(f.fileno())

# Consume messages from Kafka
for message in consumer:
    event = message.value
    src_ip = event.get('src_ip')
    dst_port = event.get('dst_port')
    protocol = event.get('protocol')
    timestamp = time.time()

    # === Port Scan Detection ===
    connection_tracker[src_ip].append((dst_port, timestamp))
    recent_connections = [conn for conn in connection_tracker[src_ip] if timestamp - conn[1] < TIME_WINDOW]
    connection_tracker[src_ip] = recent_connections
    unique_ports = set(conn[0] for conn in recent_connections)

    if len(unique_ports) > PORT_SCAN_THRESHOLD:
        alert = f"[ALERT] Port scanning detected from {src_ip}! (Ports tried: {sorted(unique_ports)})"
        log_alert(alert)
        connection_tracker[src_ip] = []  # Reset after detection

    # === Sensitive Port Access ===
    if dst_port in SENSITIVE_PORTS:
        alert = f"[ALERT] Sensitive port {dst_port} accessed from {src_ip}"
        log_alert(alert)

    # === Suspicious Protocols ===
    if protocol.lower() in SUSPICIOUS_PROTOCOLS:
        alert = f"[ALERT] Suspicious protocol detected: {protocol} from {src_ip}"
        log_alert(alert)

    # === Debug/Info ===
    print(f"Received event: {event}")
