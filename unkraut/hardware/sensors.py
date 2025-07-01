"""
Sensordaten für Unkraut-2025 (Mock-Version)
"""
import time
import random
import psutil

def get_sensor_data():
    return {
        'timestamp': int(time.time()),
        'distance': round(random.uniform(10, 200), 1),
        'soil_moisture': random.randint(20, 80),
        'temperature': round(random.uniform(15, 35), 1),
        'humidity': random.randint(30, 90),
        'gps': {
            'latitude': 53.5511 + random.uniform(-0.01, 0.01),
            'longitude': 9.9937 + random.uniform(-0.01, 0.01),
        },
        'system': {
            'cpu_usage': psutil.cpu_percent(interval=1) if psutil else 50,
            'memory_usage': psutil.virtual_memory().percent if psutil else 60,
        }
    }
