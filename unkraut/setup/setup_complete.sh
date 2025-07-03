#!/bin/bash

# Unkraut-2025 Komplettes Deployment Script
echo "🤖 Unkraut-2025 - Vollständige Installation"
echo "================================================"

# Prüfe ob in unkraut Verzeichnis
if [ ! -f "run.py" ]; then
    echo "❌ Bitte im unkraut-2025 Verzeichnis ausführen"
    exit 1
fi

echo "📁 Erstelle alle benötigten Verzeichnisse..."

# Hauptverzeichnisse
mkdir -p app/{routes,templates,static/{css,js,images},utils}
mkdir -p hardware
mkdir -p ai/{models,training_data}
mkdir -p config
mkdir -p scripts
mkdir -p logs
mkdir -p backups/{images,configs,data}
mkdir -p data/{images,videos,maps,sessions}
mkdir -p docs/images
mkdir -p tests
mkdir -p deployment/{docker,ansible,systemd}

echo "📄 Erstelle __init__.py Dateien..."

# Python __init__.py Dateien
touch app/__init__.py
touch app/routes/__init__.py
touch app/utils/__init__.py
touch hardware/__init__.py
touch ai/__init__.py
touch tests/__init__.py

echo "⚙️  Erstelle Hardware-Module..."

# hardware/gpio_config.py
cat > hardware/gpio_config.py << 'EOF'
"""
GPIO Pin-Konfiguration für Unkraut-2025
"""

# Motor Pins
MOTOR_LEFT_FORWARD = 18
MOTOR_LEFT_BACKWARD = 19  
MOTOR_RIGHT_FORWARD = 20
MOTOR_RIGHT_BACKWARD = 21
MOTOR_ENABLE_LEFT = 12
MOTOR_ENABLE_RIGHT = 13

# Sensor Pins
ULTRASONIC_TRIGGER = 23
ULTRASONIC_ECHO = 24
SOIL_MOISTURE_PIN = 25
TEMPERATURE_PIN = 4

# LED/Status Pins
STATUS_LED_GREEN = 16
STATUS_LED_RED = 17
STATUS_LED_BLUE = 27

# Camera
CAMERA_DEVICE = 0  # /dev/video0
EOF

# hardware/motors.py - Kurze Version für Test
cat > hardware/motors.py << 'EOF'
"""
Motorsteuerung für Unkraut-2025 (Mock-Version)
"""
import time

class MotorController:
    def __init__(self):
        self.is_moving = False
        self.current_speed = 0
        self.current_direction = 'stop'
        print("🚗 Mock-MotorController initialisiert")
    
    def move(self, direction, speed=50, duration=0):
        self.current_direction = direction
        self.current_speed = speed
        print(f"🚀 Mock: Moving {direction} at {speed}%")
        
        if duration > 0:
            time.sleep(duration)
            self.stop()
        
        return {'status': 'success', 'direction': direction, 'speed': speed}
    
    def stop(self):
        self.is_moving = False
        self.current_direction = 'stop'
        print("🛑 Mock: Motors stopped")
        return {'status': 'stopped'}
    
    def emergency_stop(self):
        print("🚨 EMERGENCY STOP")
        return self.stop()
    
    def get_status(self):
        return {
            'is_moving': self.is_moving,
            'direction': self.current_direction,
            'speed': self.current_speed
        }

# Globale Instanz
motor_controller = MotorController()
EOF

# hardware/sensors.py
cat > hardware/sensors.py << 'EOF'
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
EOF

# hardware/camera.py
cat > hardware/camera.py << 'EOF'
"""
Kamera-Manager für Unkraut-2025 (Mock-Version)
"""
import cv2
import numpy as np
import time
import threading

class CameraManager:
    def __init__(self):
        self.is_streaming = False
        self.current_frame = None
        self.frame_lock = threading.Lock()
        print("📷 Mock-CameraManager initialisiert")
    
    def start_stream(self):
        if not self.is_streaming:
            self.is_streaming = True
            threading.Thread(target=self._mock_stream, daemon=True).start()
            print("📹 Mock-Stream gestartet")
        return True
    
    def stop_stream(self):
        self.is_streaming = False
        print("📹 Stream gestoppt")
    
    def _mock_stream(self):
        while self.is_streaming:
            # Einfaches Mock-Bild
            img = np.zeros((480, 640, 3), dtype=np.uint8)
            img[:] = (0, 100, 0)  # Grün
            
            cv2.putText(img, 'Unkraut-2025 Mock Camera', (50, 240), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(img, time.strftime('%H:%M:%S'), (50, 280), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 1)
            
            with self.frame_lock:
                self.current_frame = img
            
            time.sleep(0.033)  # ~30 FPS
    
    def get_frame(self):
        with self.frame_lock:
            if self.current_frame is not None:
                ret, buffer = cv2.imencode('.jpg', self.current_frame)
                return buffer.tobytes() if ret else b''
        return b''
    
    def capture_image(self, filename=None):
        if filename is None:
            filename = f"capture_{int(time.time())}.jpg"
        
        frame_data = self.get_frame()
        if frame_data:
            filepath = f"data/images/{filename}"
            with open(filepath, 'wb') as f:
                f.write(frame_data)
            return filename
        return None
    
    def adjust_setting(self, setting, value):
        print(f"📷 Mock: {setting} -> {value}")
        return True

# Globale Instanz
camera_manager = CameraManager()
EOF

echo "🧠 Erstelle AI-Module..."

# ai/weed_detection.py
cat > ai/weed_detection.py << 'EOF'
"""
Unkraut-Erkennung (Mock-Version)
"""
import time
import random
import numpy as np

class WeedDetector:
    def __init__(self):
        self.classes = ['Gras', 'Unkraut', 'Löwenzahn', 'Klee']
        print("🧠 Mock-WeedDetector initialisiert")
    
    def load_model(self):
        print("✅ Mock-Model geladen")
        return True
    
    def detect_from_bytes(self, image_bytes):
        time.sleep(0.1)  # Simuliere Verarbeitung
        
        # Mock-Detektionen
        num_detections = random.randint(0, 3)
        detections = []
        
        for i in range(num_detections):
            detections.append({
                'id': i,
                'class': random.choice(self.classes),
                'confidence': random.uniform(0.6, 0.95),
                'x': random.randint(10, 80),
                'y': random.randint(10, 80),
                'width': random.randint(10, 30),
                'height': random.randint(10, 30)
            })
        
        avg_confidence = sum(d['confidence'] for d in detections) / len(detections) if detections else 0
        
        return {
            'status': 'success',
            'detections': detections,
            'confidence': avg_confidence,
            'processing_time': 0.1
        }

# Globale Instanz
weed_detector = WeedDetector()
EOF

echo "🔧 Erstelle Utils..."

# app/utils/robot_controller.py
cat > app/utils/robot_controller.py << 'EOF'
"""
Haupt-Roboter-Controller (Mock-Version)
"""
import time

class RobotController:
    def __init__(self):
        self.current_mode = 'manual'
        self.is_active = False
        self.mission_stats = {
            'start_time': None,
            'area_covered': 0,
            'weeds_detected': 0,
            'weeds_removed': 0
        }
        print("🤖 RobotController initialisiert")
    
    def set_operation_mode(self, mode):
        self.current_mode = mode
        print(f"🔄 Modus geändert zu: {mode}")
        return {'status': 'success', 'mode': mode}
    
    def get_mission_stats(self):
        return self.mission_stats
    
    def return_to_base(self):
        print("🏠 Kehre zur Basis zurück")
        return {'status': 'returning_to_base'}

# Globale Instanz
robot_controller = RobotController()
EOF

# app/utils/camera_handler.py
cat > app/utils/camera_handler.py << 'EOF'
"""
Kamera-Handler für Flask
"""
from hardware.camera import camera_manager
import time

class CameraHandler:
    def __init__(self):
        self.camera_manager = camera_manager
    
    def get_video_stream(self):
        self.camera_manager.start_stream()
        
        while True:
            frame = self.camera_manager.get_frame()
            if frame:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.033)
    
    def capture_image(self, filename=None):
        return self.camera_manager.capture_image(filename)
    
    def adjust_camera(self, setting, value):
        return self.camera_manager.adjust_setting(setting, value)

# Globale Instanz
camera_handler = CameraHandler()
EOF

echo "⚙️  Erstelle Konfiguration..."

# config/app_config.py
cat > config/app_config.py << 'EOF'
"""
Hauptkonfiguration für Unkraut-2025
"""
import os

class Config:
    SECRET_KEY = 'unkraut-2025-development-key'
    
    # Pfade
    DATA_DIR = 'data'
    IMAGE_DIR = 'data/images'
    VIDEO_DIR = 'data/videos'  
    LOG_DIR = 'logs'
    BACKUP_DIR = 'backups'
    
    # Hardware
    MOCK_HARDWARE = True

config = Config()
EOF

echo "📦 Aktualisiere requirements.txt..."

cat > requirements.txt << 'EOF'
Flask==2.3.3
Flask-SocketIO==5.3.6
gunicorn==21.2.0
opencv-python==4.8.1.78
numpy==1.24.3
psutil==5.9.5
requests==2.31.0
python-dotenv==1.0.0
eventlet==0.33.3
python-engineio==4.7.1
python-socketio==5.8.0
EOF

echo "🌐 Erstelle einfache Flask App..."

# Vereinfachte app/main.py für Tests
cat > app/main.py << 'EOF'
"""
Unkraut-2025 Flask App (Vereinfacht für Tests)
"""
from flask import Flask, render_template, jsonify, request, Response
import os
import time

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'unkraut-2025-test'
    
    # Verzeichnisse erstellen
    for directory in ['data', 'data/images', 'logs', 'backups']:
        os.makedirs(directory, exist_ok=True)
    
    @app.route('/')
    def dashboard():
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>🤖 Unkraut-2025 Dashboard</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: Arial; margin: 20px; background: #f0f0f0; }
                .container { max-width: 1200px; margin: 0 auto; }
                .card { background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .btn { padding: 10px 20px; margin: 5px; border: none; border-radius: 4px; cursor: pointer; }
                .btn-success { background: #28a745; color: white; }
                .btn-danger { background: #dc3545; color: white; }
                .btn-primary { background: #007bff; color: white; }
                .status { display: inline-block; padding: 4px 8px; border-radius: 4px; margin: 2px; }
                .status-ok { background: #d4edda; color: #155724; }
                .status-error { background: #f8d7da; color: #721c24; }
                #camera-stream { max-width: 100%; height: auto; border: 2px solid #ddd; }
                .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 Unkraut-2025 - Autonomer Roboter</h1>
                
                <div class="card">
                    <h3>📊 System Status</h3>
                    <div id="system-status">Lade Status...</div>
                    <button class="btn btn-primary" onclick="updateStatus()">Status aktualisieren</button>
                </div>
                
                <div class="grid">
                    <div class="card">
                        <h3>🎮 Steuerung</h3>
                        <button class="btn btn-success" onclick="moveRobot('forward')">⬆️ Vorwärts</button><br>
                        <button class="btn btn-success" onclick="moveRobot('left')">⬅️ Links</button>
                        <button class="btn btn-danger" onclick="stopRobot()">⏹️ Stopp</button>
                        <button class="btn btn-success" onclick="moveRobot('right')">➡️ Rechts</button><br>
                        <button class="btn btn-success" onclick="moveRobot('backward')">⬇️ Rückwärts</button>
                    </div>
                    
                    <div class="card">
                        <h3>📷 Kamera</h3>
                        <img id="camera-stream" src="/api/camera/stream" alt="Kamera Stream"><br>
                        <button class="btn btn-primary" onclick="captureImage()">📸 Foto aufnehmen</button>
                        <button class="btn btn-primary" onclick="detectWeeds()">🔍 Unkraut erkennen</button>
                    </div>
                </div>
                
                <div class="card">
                    <h3>🧠 KI-Erkennung</h3>
                    <div id="detection-results">Keine Erkennungen</div>
                </div>
                
                <div class="card">
                    <h3>📋 API Tests</h3>
                    <button class="btn btn-primary" onclick="testAPI('/api/system/status')">System Status</button>
                    <button class="btn btn-primary" onclick="testAPI('/api/control/status')">Robot Status</button>
                    <button class="btn btn-primary" onclick="testAPI('/api/ai/models')">AI Models</button>
                    <div id="api-results"></div>
                </div>
            </div>
            
            <script>
                function moveRobot(direction) {
                    fetch('/api/control/move', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({direction: direction, speed: 50, duration: 1})
                    })
                    .then(r => r.json())
                    .then(data => console.log('Move result:', data));
                }
                
                function stopRobot() {
                    fetch('/api/control/stop', {method: 'POST'})
                    .then(r => r.json())
                    .then(data => console.log('Stop result:', data));
                }
                
                function captureImage() {
                    fetch('/api/camera/capture', {method: 'POST'})
                    .then(r => r.json())
                    .then(data => alert('Bild gespeichert: ' + data.filename));
                }
                
                function detectWeeds() {
                    fetch('/api/ai/detect', {method: 'POST'})
                    .then(r => r.json())
                    .then(data => {
                        document.getElementById('detection-results').innerHTML = 
                            'Erkennungen: ' + data.detections.length + ' | Konfidenz: ' + 
                            (data.confidence * 100).toFixed(1) + '%';
                    });
                }
                
                function updateStatus() {
                    fetch('/api/control/status')
                    .then(r => r.json())
                    .then(data => {
                        document.getElementById('system-status').innerHTML = 
                            '<span class="status status-ok">CPU: ' + data.sensors.system.cpu_usage + '%</span>' +
                            '<span class="status status-ok">Temp: ' + data.sensors.temperature + '°C</span>' +
                            '<span class="status status-ok">Modus: ' + data.robot.mode + '</span>';
                    });
                }
                
                function testAPI(endpoint) {
                    fetch(endpoint)
                    .then(r => r.json())
                    .then(data => {
                        document.getElementById('api-results').innerHTML = 
                            '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                    });
                }
                
                // Auto-update
                setInterval(updateStatus, 5000);
                updateStatus();
            </script>
        </body>
        </html>
        '''
    
    @app.route('/api/camera/stream')
    def video_stream():
        from hardware.camera import camera_manager
        from app.utils.camera_handler import camera_handler
        return Response(camera_handler.get_video_stream(),
                       mimetype='multipart/x-mixed-replace; boundary=frame')
    
    @app.route('/api/camera/capture', methods=['POST'])
    def capture_image():
        from app.utils.camera_handler import camera_handler
        filename = camera_handler.capture_image()
        return jsonify({'status': 'captured', 'filename': filename})
    
    @app.route('/api/control/move', methods=['POST'])
    def move_robot():
        data = request.get_json()
        from hardware.motors import motor_controller
        result = motor_controller.move(data.get('direction'), 
                                     data.get('speed', 50), 
                                     data.get('duration', 1))
        return jsonify(result)
    
    @app.route('/api/control/stop', methods=['POST'])
    def stop_robot():
        from hardware.motors import motor_controller
        result = motor_controller.emergency_stop()
        return jsonify(result)
    
    @app.route('/api/control/status')
    def get_status():
        from hardware.sensors import get_sensor_data
        from hardware.motors import motor_controller
        from app.utils.robot_controller import robot_controller
        
        return jsonify({
            'timestamp': int(time.time()),
            'robot': {
                'mode': robot_controller.current_mode,
                'is_active': robot_controller.is_active,
                'motors': motor_controller.get_status()
            },
            'sensors': get_sensor_data(),
            'mission': robot_controller.get_mission_stats()
        })
    
    @app.route('/api/ai/detect', methods=['POST'])
    def detect_weeds():
        from ai.weed_detection import weed_detector
        from hardware.camera import camera_manager
        
        frame_data = camera_manager.get_frame()
        result = weed_detector.detect_from_bytes(frame_data)
        return jsonify(result)
    
    @app.route('/api/ai/models')
    def list_models():
        return jsonify({'models': ['mock_model.h5']})
    
    @app.route('/api/system/status')
    def system_status():
        from hardware.sensors import get_sensor_data
        sensor_data = get_sensor_data()
        
        return jsonify({
            'timestamp': int(time.time()),
            'system': sensor_data['system'],
            'hardware': {
                'camera_available': True,
                'gpio_available': False,
                'mock_mode': True
            }
        })
    
    return app

app = create_app()
EOF

echo "🔧 Aktualisiere run.py..."

cat > run.py << 'EOF'
#!/usr/bin/env python3
"""
Unkraut-2025 Main Entry Point
"""
import os
import sys

# Python path setzen
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    try:
        from app.main import app
        print("✅ Unkraut-2025 Module erfolgreich geladen")
        print("🚀 Starte Flask Server...")
        print("📡 Zugriff über: http://localhost:5000")
        print("🛑 Stoppen mit Ctrl+C")
        
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            threaded=True
        )
        
    except ImportError as e:
        print(f"❌ Import-Fehler: {e}")
        print("💡 Führe 'pip install -r requirements.txt' aus")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Unkraut-2025 gestoppt")
    except Exception as e:
        print(f"❌ Fehler: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
EOF

chmod +x run.py

echo "📋 Erstelle Makefile..."

cat > Makefile << 'EOF'
.PHONY: install run test clean

install:
	pip install -r requirements.txt
	@echo "✅ Installation abgeschlossen"

run:
	python run.py

test:
	@echo "🧪 Teste Hardware-Module..."
	@python -c "from hardware.motors import motor_controller; print('✅ Motors:', motor_controller.get_status())"
	@python -c "from hardware.sensors import get_sensor_data; print('✅ Sensors verfügbar')"
	@python -c "from ai.weed_detection import weed_detector; print('✅ AI geladen')"
	@echo "🧪 Teste Flask App..."
	@python -c "from app.main import app; print('✅ Flask App funktioniert')"

clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	rm -rf logs/*.log data/images/* 2>/dev/null || true

status:
	@curl -s http://localhost:5000/api/system/status | python -m json.tool 2>/dev/null || echo "❌ Server nicht erreichbar"
EOF

echo ""
echo "🎉 Installation abgeschlossen!"
echo "================================================"
echo ""
echo "📋 Nächste Schritte:"
echo "1. Dependencies installieren: make install"
echo "2. Module testen:            make test" 
echo "3. App starten:              make run"
echo "4. Browser öffnen:           http://localhost:5000"
echo ""
echo "🧪 Quick-Test:"
echo "python -c \"from app.main import app; print('✅ Alle Module geladen')\""
echo ""

# Einfacher Test
echo "🔍 Teste Installation..."
if python -c "from app.main import app; print('✅ Test erfolgreich')" 2>/dev/null; then
    echo "✅ Installation erfolgreich - bereit zum Starten!"
else
    echo "⚠️  Installiere noch Dependencies: pip install -r requirements.txt"
fi