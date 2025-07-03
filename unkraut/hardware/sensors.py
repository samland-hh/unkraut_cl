# hardware/sensors.py
"""
Sensor-Manager für Unkraut-2025
Temperatursensor, GPS, Ultraschall, etc.
"""
import time
import psutil
import threading
import random

class SensorManager:
    def __init__(self):
        self.sensors_available = False
        self.temperature = 22.0
        self.humidity = 45.0
        self.gps_lat = 53.5511  # Hamburg
        self.gps_lon = 9.9937
        self.battery_voltage = 12.4
        self.init_sensors()
    
    def init_sensors(self):
        """Sensoren initialisieren"""
        try:
            # Versuche Hardware-Sensoren zu initialisieren
            self._init_temperature_sensor()
            self._init_gps()
            self.sensors_available = True
            print("✅ Sensoren initialisiert")
        except Exception as e:
            print(f"⚠️ Sensor-Hardware nicht verfügbar: {e}")
            print("🔧 Sensor Mock-Modus aktiviert")
            self.sensors_available = False
    
    def _init_temperature_sensor(self):
        """Temperatursensor (DS18B20) initialisieren"""
        try:
            # Beispiel für DS18B20 1-Wire Sensor
            import glob
            sensor_files = glob.glob('/sys/bus/w1/devices/28*/w1_slave')
            if sensor_files:
                self.temp_sensor_file = sensor_files[0]
                print("✅ DS18B20 Temperatursensor gefunden")
            else:
                raise Exception("Kein DS18B20 gefunden")
        except:
            self.temp_sensor_file = None
    
    def _init_gps(self):
        """GPS-Modul initialisieren"""
        try:
            # Hier würde GPS-Hardware initialisiert werden
            # z.B. UART-Verbindung zu GPS-Modul
            pass
        except:
            pass
    
    def get_temperature(self):
        """Temperatur auslesen"""
        if self.temp_sensor_file:
            try:
                with open(self.temp_sensor_file, 'r') as f:
                    lines = f.readlines()
                if lines[0].strip()[-3:] == 'YES':
                    temp_line = lines[1]
                    temp_c = float(temp_line.split('t=')[1]) / 1000.0
                    self.temperature = temp_c
                    return temp_c
            except:
                pass
        
        # Mock-Temperatur mit leichten Schwankungen
        self.temperature += random.uniform(-0.5, 0.5)
        self.temperature = max(15, min(35, self.temperature))
        return round(self.temperature, 1)
    
    def get_humidity(self):
        """Luftfeuchtigkeit auslesen"""
        # Mock-Luftfeuchtigkeit
        self.humidity += random.uniform(-2, 2)
        self.humidity = max(20, min(80, self.humidity))
        return round(self.humidity, 1)
    
    def get_gps_position(self):
        """GPS-Position abrufen"""
        if self.sensors_available:
            # Hier würde echte GPS-Position ausgelesen werden
            pass
        
        # Mock-GPS mit leichter Bewegung
        self.gps_lat += random.uniform(-0.0001, 0.0001)
        self.gps_lon += random.uniform(-0.0001, 0.0001)
        
        return {
            'latitude': round(self.gps_lat, 6),
            'longitude': round(self.gps_lon, 6),
            'accuracy': 3.2,
            'satellites': 8,
            'timestamp': int(time.time())
        }
    
    def get_battery_status(self):
        """Batterie-Status abrufen"""
        # Mock-Batterie mit langsamem Entladen
        self.battery_voltage -= 0.001
        if self.battery_voltage < 11.0:
            self.battery_voltage = 12.4  # "Aufgeladen"
        
        percentage = int(((self.battery_voltage - 11.0) / 1.4) * 100)
        
        return {
            'voltage': round(self.battery_voltage, 2),
            'percentage': max(0, min(100, percentage)),
            'charging': percentage < 20,
            'low_warning': percentage < 15
        }
    
    def get_ultrasonic_distance(self, sensor_id='front'):
        """Ultraschall-Abstandsmessung"""
        # Mock-Abstandssensor
        if sensor_id == 'front':
            base_distance = 50
        elif sensor_id == 'left':
            base_distance = 30
        elif sensor_id == 'right':
            base_distance = 40
        else:
            base_distance = 25
        
        # Zufällige Schwankungen
        distance = base_distance + random.uniform(-10, 15)
        return max(5, distance)  # Minimum 5cm
    
    def get_system_stats(self):
        """System-Statistiken"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Temperatur des Raspberry Pi
            try:
                with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                    cpu_temp = int(f.read().strip()) / 1000.0
            except:
                cpu_temp = 45.0 + random.uniform(-5, 10)
            
            return {
                'cpu_usage': round(cpu_percent, 1),
                'cpu_temperature': round(cpu_temp, 1),
                'memory_usage': round(memory.percent, 1),
                'memory_available': round(memory.available / 1024 / 1024, 0),  # MB
                'disk_usage': round(disk.percent, 1),
                'disk_free': round(disk.free / 1024 / 1024 / 1024, 1),  # GB
                'uptime': int(time.time() - psutil.boot_time()),
                'timestamp': int(time.time())
            }
        except Exception as e:
            return {
                'cpu_usage': 25.0,
                'cpu_temperature': 42.0,
                'memory_usage': 60.0,
                'memory_available': 1024,
                'disk_usage': 45.0,
                'disk_free': 8.5,
                'uptime': 3600,
                'timestamp': int(time.time())
            }
    
    def get_sensor_data(self):
        """Alle Sensor-Daten sammeln"""
        return {
            'temperature': self.get_temperature(),
            'humidity': self.get_humidity(),
            'gps': self.get_gps_position(),
            'battery': self.get_battery_status(),
            'distances': {
                'front': round(self.get_ultrasonic_distance('front'), 1),
                'left': round(self.get_ultrasonic_distance('left'), 1),
                'right': round(self.get_ultrasonic_distance('right'), 1),
                'back': round(self.get_ultrasonic_distance('back'), 1)
            },
            'system': self.get_system_stats(),
            'timestamp': int(time.time()),
            'hardware_available': self.sensors_available
        }
    
    def start_monitoring(self, interval=5):
        """Kontinuierliches Sensor-Monitoring starten"""
        def monitor_loop():
            while True:
                try:
                    data = self.get_sensor_data()
                    
                    # Warnungen prüfen
                    if data['battery']['low_warning']:
                        print("⚠️ Batterie-Warnung: " + str(data['battery']['percentage']) + "%")
                    
                    if data['system']['cpu_temperature'] > 70:
                        print("⚠️ CPU-Temperatur hoch: " + str(data['system']['cpu_temperature']) + "°C")
                    
                    # Hindernisse erkennen
                    for direction, distance in data['distances'].items():
                        if distance < 15:
                            print(f"⚠️ Hindernis {direction}: {distance}cm")
                    
                    time.sleep(interval)
                    
                except Exception as e:
                    print(f"Sensor-Monitor-Fehler: {e}")
                    time.sleep(interval)
        
        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()
        print(f"📊 Sensor-Monitoring gestartet (Intervall: {interval}s)")
        return thread

    def cleanup(self):
        """Sensoren aufräumen"""
        print("🧹 Sensor-Manager aufgeräumt")

# Globale Instanz und Funktionen für Kompatibilität
sensor_manager = SensorManager()

def get_sensor_data():
    """Kompatibilitätsfunktion"""
    return sensor_manager.get_sensor_data()

def get_system_stats():
    """Kompatibilitätsfunktion"""
    return sensor_manager.get_system_stats()

# Cleanup bei Programmende
import atexit
atexit.register(sensor_manager.cleanup)