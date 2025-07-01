# app/main.py - Komplette Unkraut-2025 Flask App mit Roboterarm
"""
Unkraut-2025 Flask Hauptanwendung
Vollständig integriert mit Kamera, Motoren, AI und Roboterarm
"""
from flask import Flask, render_template, jsonify, request, Response
import threading
import time
import os

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'unkraut-2025-secret'
    
    # Verzeichnisse erstellen
    for directory in ['data', 'data/images', 'logs', 'backups']:
        os.makedirs(directory, exist_ok=True)
    
    # ===== HAUPTROUTEN =====
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
                .btn { padding: 10px 20px; margin: 5px; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; }
                .btn-success { background: #28a745; color: white; }
                .btn-danger { background: #dc3545; color: white; }
                .btn-primary { background: #007bff; color: white; }
                .btn-warning { background: #ffc107; color: black; }
                .status { display: inline-block; padding: 4px 8px; border-radius: 4px; margin: 2px; }
                .status-ok { background: #d4edda; color: #155724; }
                .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
                #camera-stream { max-width: 100%; height: auto; border: 2px solid #ddd; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 Unkraut-2025 - Autonomer Roboter mit Arm</h1>
                
                <div class="card">
                    <h3>🧭 Navigation</h3>
                    <a href="/control" class="btn btn-success">🎮 Fahrzeug-Steuerung</a>
                    <a href="/arm" class="btn btn-warning">🦾 Roboterarm</a>
                    <a href="/camera" class="btn btn-primary">📷 Kamera</a>
                    <a href="/ai" class="btn btn-info">🧠 KI-Erkennung</a>
                </div>
                
                <div class="grid">
                    <div class="card">
                        <h3>📊 System Status</h3>
                        <div id="system-status">Lade Status...</div>
                        <button class="btn btn-primary" onclick="updateStatus()">Aktualisieren</button>
                    </div>
                    
                    <div class="card">
                        <h3>📷 Live Kamera</h3>
                        <img id="camera-stream" src="/api/camera/stream" alt="Kamera Stream"><br>
                        <button class="btn btn-primary" onclick="captureImage()">📸 Foto</button>
                        <button class="btn btn-success" onclick="detectWeeds()">🔍 Unkraut erkennen</button>
                    </div>
                </div>
                
                <div class="card">
                    <h3>🚀 Schnellaktionen</h3>
                    <button class="btn btn-success" onclick="moveRobot('forward')">⬆️ Vorwärts</button>
                    <button class="btn btn-success" onclick="moveRobot('left')">⬅️ Links</button>
                    <button class="btn btn-danger" onclick="stopAll()">⏹️ Alles stoppen</button>
                    <button class="btn btn-success" onclick="moveRobot('right')">➡️ Rechts</button>
                    <button class="btn btn-success" onclick="moveRobot('backward')">⬇️ Rückwärts</button>
                    <br><br>
                    <button class="btn btn-warning" onclick="armHome()">🏠 Arm Home</button>
                    <button class="btn btn-warning" onclick="armWeedRemove()">🌿 Unkraut entfernen</button>
                </div>
                
                <div class="card">
                    <h3>🔄 Status Updates</h3>
                    <div id="live-status"></div>
                </div>
            </div>
            
            <script>
                function moveRobot(direction) {
                    fetch('/api/control/move', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({direction: direction, speed: 50, duration: 1})
                    }).then(r => r.json()).then(data => console.log('Move:', data));
                }
                
                function stopAll() {
                    fetch('/api/control/stop', {method: 'POST'});
                    fetch('/api/arm/emergency_stop', {method: 'POST'});
                    alert('🚨 ALLES GESTOPPT');
                }
                
                function captureImage() {
                    fetch('/api/camera/capture', {method: 'POST'})
                    .then(r => r.json())
                    .then(data => alert('📸 Foto: ' + data.filename));
                }
                
                function detectWeeds() {
                    fetch('/api/ai/detect', {method: 'POST'})
                    .then(r => r.json())
                    .then(data => alert('🔍 ' + data.detections.length + ' Unkraut erkannt'));
                }
                
                function armHome() {
                    fetch('/api/arm/move/preset', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({preset: 'home'})
                    }).then(r => r.json()).then(data => alert('🏠 Arm fährt Home'));
                }
                
                function armWeedRemove() {
                    fetch('/api/arm/weed_removal', {method: 'POST'})
                    .then(r => r.json())
                    .then(data => alert('🌿 Unkraut-Entfernung gestartet'));
                }
                
                function updateStatus() {
                    fetch('/api/system/status')
                    .then(r => r.json())
                    .then(data => {
                        document.getElementById('system-status').innerHTML = 
                            '<div class="status status-ok">CPU: ' + data.system.cpu_usage + '%</div>' +
                            '<div class="status status-ok">RAM: ' + data.system.memory_usage + '%</div>' +
                            '<div class="status status-ok">Hardware: ' + (data.hardware.arm_available ? 'Arm OK' : 'Mock') + '</div>';
                    });
                }
                
                setInterval(updateStatus, 5000);
                updateStatus();
            </script>
        </body>
        </html>
        '''
    
    @app.route('/control')
    def control_panel():
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>🎮 Fahrzeug-Steuerung</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: Arial; margin: 20px; background: #f0f0f0; }
                .container { max-width: 800px; margin: 0 auto; }
                .card { background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .btn { padding: 15px 25px; margin: 5px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
                .btn-success { background: #28a745; color: white; }
                .btn-danger { background: #dc3545; color: white; }
                .btn-primary { background: #007bff; color: white; }
                .control-pad { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; max-width: 300px; margin: 0 auto; }
                .nav-link { text-decoration: none; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎮 Fahrzeug-Steuerung</h1>
                
                <div class="card">
                    <h3>🧭 Navigation</h3>
                    <a href="/" class="btn btn-primary nav-link">🏠 Dashboard</a>
                    <a href="/arm" class="btn btn-warning nav-link">🦾 Roboterarm</a>
                    <a href="/camera" class="btn btn-success nav-link">📷 Kamera</a>
                </div>
                
                <div class="card">
                    <h3>🚗 Bewegungssteuerung</h3>
                    <div class="control-pad">
                        <div></div>
                        <button class="btn btn-success" onmousedown="startMove('forward')" onmouseup="stopMove()">⬆️</button>
                        <div></div>
                        <button class="btn btn-success" onmousedown="startMove('left')" onmouseup="stopMove()">⬅️</button>
                        <button class="btn btn-danger" onclick="emergencyStop()">🛑</button>
                        <button class="btn btn-success" onmousedown="startMove('right')" onmouseup="stopMove()">➡️</button>
                        <div></div>
                        <button class="btn btn-success" onmousedown="startMove('backward')" onmouseup="stopMove()">⬇️</button>
                        <div></div>
                    </div>
                </div>
                
                <div class="card">
                    <h3>⚡ Geschwindigkeit</h3>
                    <input type="range" min="10" max="100" value="50" style="width: 100%;" oninput="setSpeed(this.value)">
                    <div>Geschwindigkeit: <span id="speed-display">50</span>%</div>
                </div>
                
                <div class="card">
                    <h3>📊 Status</h3>
                    <div id="robot-status">Lade Status...</div>
                </div>
            </div>
            
            <script>
                let currentSpeed = 50;
                
                function startMove(direction) {
                    fetch('/api/control/move', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({direction: direction, speed: currentSpeed, duration: 0.1})
                    });
                }
                
                function stopMove() {
                    fetch('/api/control/stop', {method: 'POST'});
                }
                
                function emergencyStop() {
                    fetch('/api/control/stop', {method: 'POST'});
                    alert('🚨 NOT-STOPP AKTIVIERT');
                }
                
                function setSpeed(speed) {
                    currentSpeed = speed;
                    document.getElementById('speed-display').textContent = speed;
                }
                
                function updateStatus() {
                    fetch('/api/control/status')
                    .then(r => r.json())
                    .then(data => {
                        document.getElementById('robot-status').innerHTML = 
                            'Modus: ' + data.robot.mode + '<br>' +
                            'Motoren: ' + (data.robot.motors.is_moving ? 'Bewegt sich' : 'Gestoppt') + '<br>' +
                            'Temperatur: ' + data.sensors.temperature + '°C';
                    });
                }
                
                setInterval(updateStatus, 3000);
                updateStatus();
            </script>
        </body>
        </html>
        '''
    
    @app.route('/arm')
    def arm_control():
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>🦾 Roboterarm Steuerung</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: Arial; margin: 20px; background: #f0f0f0; }
                .container { max-width: 1200px; margin: 0 auto; }
                .card { background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .btn { padding: 10px 20px; margin: 5px; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; }
                .btn-success { background: #28a745; color: white; }
                .btn-danger { background: #dc3545; color: white; }
                .btn-primary { background: #007bff; color: white; }
                .btn-warning { background: #ffc107; color: black; }
                .servo-control { margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 4px; }
                .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
                .status-display { font-family: monospace; background: #f8f9fa; padding: 10px; border-radius: 4px; white-space: pre-line; }
                .nav-link { color: white; text-decoration: none; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🦾 Unkraut-2025 Roboterarm</h1>
                
                <div class="card">
                    <h3>🧭 Navigation</h3>
                    <a href="/" class="btn btn-primary nav-link">🏠 Dashboard</a>
                    <a href="/control" class="btn btn-success nav-link">🎮 Fahrzeug</a>
                    <a href="/camera" class="btn btn-warning nav-link">📷 Kamera</a>
                </div>
                
                <div class="card">
                    <h3>🎯 Preset-Positionen</h3>
                    <div class="grid">
                        <button class="btn btn-primary" onclick="moveToPreset('home')">🏠 Home Position</button>
                        <button class="btn btn-success" onclick="moveToPreset('weed_detect')">🔍 Unkraut Erkennen</button>
                        <button class="btn btn-warning" onclick="moveToPreset('weed_remove')">🌿 Unkraut Entfernen</button>
                        <button class="btn btn-danger" onclick="emergencyStop()">🚨 Not-Stopp</button>
                    </div>
                </div>
                
                <div class="card">
                    <h3>🎮 Manuelle Servo-Steuerung</h3>
                    <div class="grid">
                        <div class="servo-control">
                            <label><strong>Base (Drehung):</strong> <span id="base-angle">90</span>°</label><br>
                            <input type="range" min="0" max="180" value="90" style="width: 100%;" oninput="moveServo('base', this.value)">
                        </div>
                        <div class="servo-control">
                            <label><strong>Shoulder (Heben):</strong> <span id="shoulder-angle">90</span>°</label><br>
                            <input type="range" min="0" max="180" value="90" style="width: 100%;" oninput="moveServo('shoulder', this.value)">
                        </div>
                        <div class="servo-control">
                            <label><strong>Elbow (Ellbogen):</strong> <span id="elbow-angle">90</span>°</label><br>
                            <input type="range" min="0" max="180" value="90" style="width: 100%;" oninput="moveServo('elbow', this.value)">
                        </div>
                        <div class="servo-control">
                            <label><strong>Wrist (Handgelenk):</strong> <span id="wrist-angle">90</span>°</label><br>
                            <input type="range" min="0" max="180" value="90" style="width: 100%;" oninput="moveServo('wrist', this.value)">
                        </div>
                        <div class="servo-control">
                            <label><strong>Gripper (Greifer):</strong> <span id="gripper-angle">90</span>°</label><br>
                            <input type="range" min="0" max="180" value="90" style="width: 100%;" oninput="moveServo('gripper', this.value)">
                        </div>
                        <div class="servo-control">
                            <label><strong>Tool (Werkzeug):</strong> <span id="tool-angle">0</span>°</label><br>
                            <input type="range" min="0" max="180" value="0" style="width: 100%;" oninput="moveServo('tool', this.value)">
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <h3>🤖 Automatische Aktionen</h3>
                    <button class="btn btn-success" onclick="weedRemovalSequence()">🌿 Unkraut-Entfernung Sequenz</button>
                    <button class="btn btn-primary" onclick="activateTool()">🔧 Werkzeug aktivieren (3s)</button>
                    <button class="btn btn-warning" onclick="calibrateServos()">⚙️ Servo-Kalibrierung</button>
                    <button class="btn btn-info" onclick="getArmStatus()">📊 Status anzeigen</button>
                </div>
                
                <div class="card">
                    <h3>📊 Roboterarm Status</h3>
                    <div id="arm-status" class="status-display">Lade Status...</div>
                </div>
            </div>
            
            <script>
                function moveServo(joint, angle) {
                    document.getElementById(joint + '-angle').textContent = angle;
                    
                    fetch('/api/arm/move/joint', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({joint: joint, angle: parseInt(angle)})
                    })
                    .then(r => r.json())
                    .then(data => {
                        if (data.error) {
                            alert('❌ Fehler: ' + data.error);
                        }
                    })
                    .catch(err => console.error('Servo-Fehler:', err));
                }
                
                function moveToPreset(preset) {
                    fetch('/api/arm/move/preset', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({preset: preset, duration: 2.0})
                    })
                    .then(r => r.json())
                    .then(data => {
                        if (data.status === 'success') {
                            alert('✅ Fahre zu Position: ' + preset);
                            setTimeout(getArmStatus, 2500);
                        } else {
                            alert('❌ Fehler: ' + data.error);
                        }
                    })
                    .catch(err => console.error('Preset-Fehler:', err));
                }
                
                function emergencyStop() {
                    fetch('/api/arm/emergency_stop', {method: 'POST'})
                        .then(r => r.json())
                        .then(data => alert('🚨 ROBOTERARM NOT-STOPP AKTIVIERT'))
                        .catch(err => console.error('Stop-Fehler:', err));
                }
                
                function weedRemovalSequence() {
                    if (confirm('Unkraut-Entfernung Sequenz starten?')) {
                        fetch('/api/arm/weed_removal', {method: 'POST'})
                            .then(r => r.json())
                            .then(data => alert('🌿 Unkraut-Entfernung Sequenz gestartet'))
                            .catch(err => console.error('Sequenz-Fehler:', err));
                    }
                }
                
                function activateTool() {
                    fetch('/api/arm/tool/activate', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({duration: 3.0})
                    })
                    .then(r => r.json())
                    .then(data => alert('🔧 Werkzeug aktiviert für 3 Sekunden'))
                    .catch(err => console.error('Tool-Fehler:', err));
                }
                
                function calibrateServos() {
                    if (confirm('Servo-Kalibrierung starten? Das dauert etwa 30 Sekunden.')) {
                        fetch('/api/arm/calibrate', {method: 'POST'})
                            .then(r => r.json())
                            .then(data => alert('⚙️ Servo-Kalibrierung gestartet'))
                            .catch(err => console.error('Kalibrierung-Fehler:', err));
                    }
                }
                
                function getArmStatus() {
                    fetch('/api/arm/info')
                        .then(r => r.json())
                        .then(data => {
                            const status = `Hardware: ${data.controller.hardware_available ? 'Echt (PCA9685)' : 'Mock'}
I2C Adresse: ${data.controller.i2c_address}
Servos: ${data.controller.servo_count}
Gelenke: ${data.joints.join(', ')}
Presets: ${data.presets.join(', ')}

Aktuelle Position:
${Object.entries(data.current_position).map(([joint, angle]) => `${joint}: ${angle}°`).join('\\n')}`;
                            document.getElementById('arm-status').textContent = status;
                        })
                        .catch(err => console.error('Status-Fehler:', err));
                }
                
                // Auto-Status-Update
                setInterval(getArmStatus, 5000);
                getArmStatus();
            </script>
        </body>
        </html>
        '''
    
    @app.route('/camera')
    def camera_view():
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>📷 Kamera</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: Arial; margin: 20px; background: #f0f0f0; }
                .container { max-width: 1000px; margin: 0 auto; }
                .card { background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .btn { padding: 10px 20px; margin: 5px; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; }
                .btn-success { background: #28a745; color: white; }
                .btn-primary { background: #007bff; color: white; }
                #camera-stream { max-width: 100%; height: auto; border: 2px solid #ddd; border-radius: 8px; }
                .nav-link { color: white; text-decoration: none; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📷 Kamera-Ansicht</h1>
                
                <div class="card">
                    <h3>🧭 Navigation</h3>
                    <a href="/" class="btn btn-primary nav-link">🏠 Dashboard</a>
                    <a href="/control" class="btn btn-success nav-link">🎮 Fahrzeug</a>
                    <a href="/arm" class="btn btn-warning nav-link">🦾 Roboterarm</a>
                </div>
                
                <div class="card">
                    <h3>📹 Live Stream</h3>
                    <img id="camera-stream" src="/api/camera/stream" alt="Kamera Stream"><br><br>
                    <button class="btn btn-success" onclick="captureImage()">📸 Foto aufnehmen</button>
                    <button class="btn btn-primary" onclick="detectWeeds()">🔍 Unkraut erkennen</button>
                </div>
                
                <div class="card">
                    <h3>🔍 KI-Ergebnisse</h3>
                    <div id="detection-results">Keine Erkennungen</div>
                </div>
            </div>
            
            <script>
                function captureImage() {
                    fetch('/api/camera/capture', {method: 'POST'})
                    .then(r => r.json())
                    .then(data => {
                        if (data.filename) {
                            alert('📸 Foto gespeichert: ' + data.filename);
                        } else {
                            alert('❌ Foto-Fehler: ' + data.error);
                        }
                    });
                }
                
                function detectWeeds() {
                    fetch('/api/ai/detect', {method: 'POST'})
                    .then(r => r.json())
                    .then(data => {
                        if (data.detections) {
                            const result = `🔍 ${data.detections.length} Unkraut-Objekte erkannt
Konfidenz: ${(data.confidence * 100).toFixed(1)}%
Verarbeitungszeit: ${data.processing_time}s`;
                            document.getElementById('detection-results').textContent = result;
                            
                            if (data.detections.length > 0) {
                                alert('🌿 ' + data.detections.length + ' Unkraut erkannt!');
                            }
                        } else {
                            alert('❌ Erkennung fehlgeschlagen: ' + data.error);
                        }
                    });
                }
            </script>
        </body>
        </html>
        '''
    
    # ===== KAMERA API =====
    @app.route('/api/camera/stream')
    def video_stream():
        try:
            from hardware.camera import camera_manager
            def generate():
                camera_manager.start_stream()
                while True:
                    frame = camera_manager.get_frame()
                    if frame:
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                    time.sleep(0.033)
            return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')
        except Exception as e:
            return f"Kamera-Fehler: {e}", 500
    
    @app.route('/api/camera/capture', methods=['POST'])
    def capture_image():
        try:
            from hardware.camera import camera_manager
            filename = camera_manager.capture_image()
            if filename:
                return jsonify({'status': 'captured', 'filename': filename})
            return jsonify({'error': 'Capture failed'}), 500
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ===== ROBOTERARM API =====
    @app.route('/api/arm/info')
    def get_arm_info():
        try:
            from hardware.robot_arm import robot_arm
            info = robot_arm.get_arm_info()
            return jsonify(info)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/arm/move/joint', methods=['POST'])
    def move_arm_joint():
        try:
            data = request.get_json()
            joint = data.get('joint')
            angle = data.get('angle')
            
            if not joint or angle is None:
                return jsonify({'error': 'Joint und Angle erforderlich'}), 400
            
            from hardware.robot_arm import robot_arm
            success = robot_arm.move_joint(joint, float(angle))
            
            if success:
                return jsonify({'status': 'success', 'joint': joint, 'angle': angle})
            else:
                return jsonify({'error': 'Bewegung fehlgeschlagen'}), 500
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/arm/move/preset', methods=['POST'])
    def move_arm_to_preset():
        try:
            data = request.get_json()
            preset = data.get('preset')
            duration = data.get('duration', 2.0)
            
            if not preset:
                return jsonify({'error': 'Preset erforderlich'}), 400
            
            from hardware.robot_arm import robot_arm
            success = robot_arm.move_to_preset(preset, duration)
            
            if success:
                return jsonify({'status': 'success', 'preset': preset, 'duration': duration})
            else:
                return jsonify({'error': f'Preset {preset} nicht gefunden'}), 404
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/arm/emergency_stop', methods=['POST'])
    def arm_emergency_stop():
        try:
            from hardware.robot_arm import robot_arm
            robot_arm.emergency_stop()
            return jsonify({'status': 'emergency_stop_activated'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/arm/weed_removal', methods=['POST'])
    def arm_weed_removal():
        try:
            data = request.get_json() or {}
            target_x = data.get('target_x', 0)
            target_y = data.get('target_y', 0)
            
            from hardware.robot_arm import robot_arm
            import threading
            
            thread = threading.Thread(
                target=robot_arm.weed_removal_sequence,
                args=(target_x, target_y),
                daemon=True
            )
            thread.start()
            
            return jsonify({'status': 'sequence_started', 'target_x': target_x, 'target_y': target_y})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/arm/tool/activate', methods=['POST'])  
    def activate_arm_tool():
        try:
            data = request.get_json() or {}
            duration = data.get('duration', 3.0)
            
            from hardware.robot_arm import robot_arm
            import threading
            
            thread = threading.Thread(
                target=robot_arm.activate_tool,
                args=(duration,),
                daemon=True
            )
            thread.start()
            
            return jsonify({'status': 'tool_activated', 'duration': duration})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/arm/calibrate', methods=['POST'])
    def calibrate_arm_servos():
        try:
            from hardware.robot_arm import robot_arm
            import threading
            
            thread = threading.Thread(target=robot_arm.calibrate_servos, daemon=True)
            thread.start()
            
            return jsonify({'status': 'calibration_started'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ===== FAHRZEUG-STEUERUNG API =====
    @app.route('/api/control/move', methods=['POST'])
    def move_robot():
        try:
            data = request.get_json()
            direction = data.get('direction')
            speed = data.get('speed', 50)
            duration = data.get('duration', 0.1)
            
            from hardware.motors import motor_controller
            result = motor_controller.move(direction, speed, duration)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/control/stop', methods=['POST'])
    def emergency_stop():
        try:
            from hardware.motors import motor_controller
            result = motor_controller.emergency_stop()
            
            # Auch Roboterarm stoppen
            try:
                from hardware.robot_arm import robot_arm
                robot_arm.emergency_stop()
            except:
                pass
            
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/control/status')
    def get_control_status():
        try:
            from hardware.sensors import get_sensor_data
            from hardware.motors import motor_controller
            
            status = {
                'timestamp': int(time.time()),
                'robot': {
                    'mode': 'manual',
                    'is_active': False,
                    'motors': motor_controller.get_status()
                },
                'sensors': get_sensor_data(),
                'battery': {
                    'percentage': 85,
                    'voltage': 12.4,
                    'charging': False
                }
            }
            
            # Roboterarm-Status hinzufügen
            try:
                from hardware.robot_arm import robot_arm
                arm_position = robot_arm.get_current_position()
                status['arm'] = {
                    'available': True,
                    'position': arm_position
                }
            except:
                status['arm'] = {'available': False}
            
            return jsonify(status)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ===== AI API =====
    @app.route('/api/ai/detect', methods=['POST'])
    def detect_weeds():
        try:
            from ai.weed_detection import weed_detector
            from hardware.camera import camera_manager
            
            frame_data = camera_manager.get_frame()
            if frame_data:
                result = weed_detector.detect_from_bytes(frame_data)
                
                # Optional: Roboterarm zu erkanntem Unkraut bewegen
                if result.get('detections') and len(result['detections']) > 0:
                    detection = result['detections'][0]
                    target_x = detection.get('x', 0)
                    target_y = detection.get('y', 0)
                    
                    try:
                        from hardware.robot_arm import robot_arm
                        threading.Thread(
                            target=robot_arm.weed_removal_sequence,
                            args=(target_x, target_y),
                            daemon=True
                        ).start()
                        result['arm_action'] = 'weed_removal_started'
                    except:
                        result['arm_action'] = 'arm_not_available'
                
                return jsonify(result)
            else:
                return jsonify({'error': 'No camera frame available'}), 400
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ===== SYSTEM API =====
    @app.route('/api/system/status')
    def system_status():
        try:
            from hardware.sensors import sensor_manager
            
            status = {
                'timestamp': int(time.time()),
                'system': sensor_manager.get_system_stats(),
                'hardware': {
                    'camera_available': True,
                    'gpio_available': False,
                    'mock_mode': True
                }
            }
            
            # Roboterarm-Hardware-Status
            try:
                from hardware.robot_arm import robot_arm
                arm_info = robot_arm.get_arm_info()
                status['hardware']['arm_available'] = arm_info['controller']['hardware_available']
                status['hardware']['servo_count'] = arm_info['controller']['servo_count']
            except:
                status['hardware']['arm_available'] = False
            
            return jsonify(status)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    print("✅ Unkraut-2025 Flask App mit Roboterarm vollständig geladen")
    return app

# Für den Import
app = create_app()

if __name__ == '__main__':
    print("🚀 Starte Unkraut-2025 direkt aus main.py")
    app.run(host='0.0.0.0', port=5000, debug=True)