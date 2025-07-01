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
