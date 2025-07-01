# app/routes/control.py
from flask import Blueprint, render_template, jsonify, request
import json
import time

bp = Blueprint('control', __name__)

@bp.route('/control')
def control_page():
    """Steuerungsseite anzeigen"""
    return render_template('control.html')

@bp.route('/api/vehicle/move', methods=['POST'])
def vehicle_move():
    """Fahrzeug bewegen"""
    try:
        data = request.get_json()
        command = data.get('command')
        
        # Hier würde die Hardware-Steuerung stehen
        # Beispiel für GPIO/Motor-Steuerung:
        if command == 'forward':
            # motor_controller.move_forward()
            print(f"🚗 Fahrzeug: Vorwärts")
        elif command == 'backward':
            # motor_controller.move_backward()
            print(f"🚗 Fahrzeug: Rückwärts")
        elif command == 'left':
            # motor_controller.turn_left()
            print(f"🚗 Fahrzeug: Links")
        elif command == 'right':
            # motor_controller.turn_right()
            print(f"🚗 Fahrzeug: Rechts")
        elif command == 'stop':
            # motor_controller.stop()
            print(f"🚗 Fahrzeug: Stopp")
        else:
            return jsonify({'error': 'Unbekannter Befehl'}), 400
            
        return jsonify({'status': 'success', 'command': command})
        
    except Exception as e:
        print(f"Fehler bei Fahrzeugsteuerung: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/arm/servo', methods=['POST'])
def servo_control():
    """Servo Motor steuern"""
    try:
        data = request.get_json()
        servo = data.get('servo')
        angle = data.get('angle')
        
        # Hier würde die Servo-Steuerung stehen
        # Beispiel für Servo-Steuerung:
        if servo in ['base', 'shoulder', 'elbow', 'wrist', 'gripper']:
            # servo_controller.move_servo(servo, angle)
            print(f"🦾 Servo {servo}: {angle}°")
        else:
            return jsonify({'error': 'Unbekannter Servo'}), 400
            
        return jsonify({'status': 'success', 'servo': servo, 'angle': angle})
        
    except Exception as e:
        print(f"Fehler bei Servosteuerung: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/emergency/stop', methods=['POST'])
def emergency_stop():
    """Notaus - Alle Systeme stoppen"""
    try:
        # Alle Motoren stoppen
        # motor_controller.emergency_stop()
        # servo_controller.emergency_stop()
        print("🛑 NOTAUS AKTIVIERT!")
        
        return jsonify({'status': 'emergency_stop_activated'})
        
    except Exception as e:
        print(f"Fehler bei Notaus: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/status')
def get_status():
    """System Status für Heartbeat"""
    try:
        status = {
            'camera': 'online',
            'motors': 'ready',
            'arm': 'ready',
            'timestamp': int(time.time())
        }
        return jsonify(status)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# app/routes/camera.py
from flask import Blueprint, Response
import cv2
import time

bp = Blueprint('camera', __name__)

class CameraStream:
    def __init__(self):
        self.camera = None
        self.init_camera()
    
    def init_camera(self):
        try:
            # Pi Camera initialization
            self.camera = cv2.VideoCapture(0)
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
        except Exception as e:
            print(f"Kamera Initialisierung fehlgeschlagen: {e}")
            self.camera = None
    
    def generate_frames(self):
        while True:
            if self.camera is None:
                # Fallback: Dummy Frame
                yield self.dummy_frame()
                time.sleep(0.1)
                continue
                
            success, frame = self.camera.read()
            if not success:
                yield self.dummy_frame()
                continue
            
            # Frame zu JPEG konvertieren
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
                
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    
    def dummy_frame(self):
        # Dummy Frame wenn keine Kamera verfügbar
        import numpy as np
        dummy = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(dummy, 'Kamera nicht verfügbar', (160, 240), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        ret, buffer = cv2.imencode('.jpg', dummy)
        frame_bytes = buffer.tobytes()
        return (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

camera_stream = CameraStream()

@bp.route('/video_feed')
def video_feed():
    """MJPEG Video Stream"""
    return Response(camera_stream.generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

# app/main.py (erweitert)
from flask import Flask, render_template
from .routes import camera, control, system

def create_app():
    app = Flask(__name__)
    
    # Routes registrieren
    app.register_blueprint(camera.bp)
    app.register_blueprint(control.bp)
    # app.register_blueprint(system.bp)  # falls vorhanden
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    return app

app = create_app()