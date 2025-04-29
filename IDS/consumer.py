import json
import time
from collections import defaultdict
from kafka import KafkaConsumer

# Initialize Kafka Consumer
consumer = KafkaConsumer(
    'network-traffic',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='ids-group'
)

print("Consumer started. Monitoring traffic...")

# Sensitive ports we want to monitor closely
sensitive_ports = {22, 23, 3389}  # SSH, Telnet, RDP

# Track ports accessed per source IP
connection_tracker = defaultdict(list)  # {src_ip: [(timestamp, dst_port)]}

# Expected protocols per common ports
expected_protocols = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    53: "DNS",
    80: "HTTP",
    443: "HTTPS",
}

# Alert logging function
def log_alert(alert_message):
    with open("alerts.log", "a") as f:
        f.write(alert_message + "\n")

# Main event loop
for message in consumer:
    event = json.loads(message.value.decode('utf-8'))
    print(f"Received event: {event}")

    src_ip = event.get('src_ip')
    dst_port = event.get('dst_port')
    protocol = event.get('protocol')
    timestamp = time.time()

    # 1. Sensitive Port Access Detection
    if dst_port in sensitive_ports:
        alert = f"[ALERT] Sensitive port {dst_port} accessed from {src_ip}"
        print(alert)
        log_alert(alert)

    # 2. Track Ports Per IP for Port Scanning
    connection_tracker[src_ip].append((timestamp, dst_port))

    # Clean up old entries older than 5 seconds
    connection_tracker[src_ip] = [
        (ts, port) for ts, port in connection_tracker[src_ip] if timestamp - ts <= 5
    ]

    # If an IP accesses 10 or more different ports within 5 seconds => Port Scan
    unique_ports = set(port for ts, port in connection_tracker[src_ip])
    if len(unique_ports) >= 10:
        alert = f"[ALERT] Potential port scan detected from {src_ip} ({len(unique_ports)} ports within 5 seconds)"
        print(alert)
        log_alert(alert)
        # Clear tracker for this IP to avoid repeated alerts
        connection_tracker[src_ip] = []

    # 3. Protocol Anomaly Detection
    expected = expected_protocols.get(dst_port)
    if expected and protocol != expected:
        alert = f"[ALERT] Protocol anomaly: Expected {expected} on port {dst_port} but got {protocol} from {src_ip}"
        print(alert)
        log_alert(alert)
