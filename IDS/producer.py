# producer.py
import json
import random
import time
from kafka import KafkaProducer

"""
Section | What it does
Normal Events | Sends 5 random "good" events first
Attack Events | Sends realistic suspicious activities (e.g., port 23, 445, unknown protocol)
Purpose | Triggers your IDS to recognize and print "ALERTS"
"""

# Initialize Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print('Prodcer started. Sending network events...')

try:
    while True:
        # Send 5 normal events
        for _ in range(5):
            event = {
                'src_ip': f'192.168.1.{random.randint(2, 254)}',
                'dst_ip': f'10.0.0.{random.randint(2, 254)}',
                'dst_port': random.choice([80, 443, 22, 21, 53]),
                'protocol': random.choice(['HTTP', 'HTTPS', 'FTP', 'DNS', 'SSH'])
            }
            producer.send('network-logs', event)
            print(f'[NORMAL] Sent event: {event}')
            time.sleep(1)

        # Occasionally inject attack events
        attack_events = [
            {
                'src_ip': f'192.168.1.{random.randint(100, 110)}',
                'dst_ip': f'10.0.0.{random.randint(2, 254)}',
                'dst_port': random.choice([23, 22, 8888]), # Sensitive or suspicious
                'protocol': random.choice(['Unknown', 'TCP', 'HTPP'])
            }
        ]

        for attack in attack_events:
            producer.send('network-logs', attack)
            print(f'[ATTACK] Sent event: {attack}')
            time.sleep(1)

        # Sleep a bit before next batch
        time.sleep(5)
        
except KeyboardInterrupt:
    print('\nProducer stopped by user.')
finally:
    producer.close()


# # ---- Normal Event Simulation ---
# protocols = ['HTPP', 'HTTPS', 'FTP', 'DNS', 'SSH']

# for _ in range(5): # Send 5 normal events first
#     event = {
#         'src_ip': f'192.168.1.{random.randint(2, 254)}',
#         'dst_ip': f'10.0.0.{random.randint(2, 254)}',
#         'dst_port': random.choice([80, 443, 22, 21, 53]),
#         'protocol': random.choice(protocols)
#     }
#     producer.send('network-logs', event)
#     print(f'Sent normal event: {event}')
#     time.sleep(1)

# # ---Inject Mannual Attack events ---
# # --- Inject Manual Attack Events ---
# attack_events = [
#     {
#         'src_ip': '192.168.1.100',  # Same source, scanning multiple ports
#         'dst_ip': '10.0.0.5',
#         'dst_port': 23,  # Telnet (sensitive)
#         'protocol': 'TCP'
#     },
#     {
#         'src_ip': '192.168.1.100',
#         'dst_ip': '10.0.0.5',
#         'dst_port': 445,  # SMB (sensitive)
#         'protocol': 'TCP'
#     },
#     {
#         'src_ip': '192.168.1.100',
#         'dst_ip': '10.0.0.5',
#         'dst_port': 21,  # FTP (known weak protocol sometimes)
#         'protocol': 'FTP'
#     },
#     {
#         'src_ip': '192.168.1.105',
#         'dst_ip': '10.0.0.8',
#         'dst_port': 8888,
#         'protocol': 'Unknown'  # Suspicious protocol
#     }
# ]

# for attack in attack_events:
#     producer.send('network-logs', attack)
#     print(f"Sent attack event: {attack}")
#     time.sleep(1)

# producer.flush()

# # Normal IPs and Ports
# normal_ips = ['192.168.1.2', '192.168.1.3', '192.168.1.4']
# normal_ports = [80, 443, 53, 25]

# # Attack IPs
# attack_ips = ['10.10.10.5', '172.16.0.8']

# # Function to simulate normal traffic
# def generate_normal_traffic():
#     return {
#         'src_ip': random.choice(normal_ips),
#         'dst_ip': '192.168.1.100',
#         'dst_port': random.choice(normal_ports),
#         'protocol': random.choice(['TCP', 'UDP', 'HTTP', 'HTTPS']),
#         'payload_size': random.randint(100, 1000)
#     }

# # Function to simulate attack traffic
# def generate_attack_traffic():
#     attack_type = random.choice(['port_scan', 'suspicious_protocol'])

#     if attack_type == 'port_scan':
#         # Random destination ports for port scanning
#         return {
#             'src_ip': random.choice(attack_ips),
#             'dst_ip': '192.168.1.100',
#             'dst_port': random.randint(1, 65535),
#             'protocol': 'TCP',
#             'payload_size': random.randint(40, 120)
#         }
#     elif attack_type == 'suspicious_protocol':
#         return {
#             'src_ip': random.choice(attack_ips),
#             'dst_ip': '192.168.1.100',
#             'dst_port': random.randint(1024, 65535),
#             'protocol': 'ICMP',  # Not normal in this context
#             'payload_size': random.randint(50, 500)
#         }

# # Main event loop
# while True:
#     if random.random() < 0.8:
#         event = generate_normal_traffic()
#     else:
#         event = generate_attack_traffic()

#     print(f"Sending event: {event}")
#     producer.send('network-logs', event)
#     time.sleep(1)  # send every second
