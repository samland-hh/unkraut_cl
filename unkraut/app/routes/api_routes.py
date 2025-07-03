# app/routes/api_routes.py
"""
Robuste API Endpoints für Unkraut-2025 mit verbesserter Fehlerbehandlung
"""
from flask import Blueprint, jsonify, request, Response
import threading
import time
import traceback

bp = Blueprint('api', __name__)

# Globale Hardware-Status
_hardware_status = {
    'camera': None,
    'robot_arm': None,
    'motors': None,
    'sensors': None,
    'ai': None
}

def safe_import(module_name, item_name):
    """Sicherer Import mit Fehlerbehandlung"""
    try:
        module = __import__(module_name, fromlist=[item_name])
        return getattr(module, item_name)
    except Exception as e:
        print(f"⚠️ Import-Fehler {module_name}.{item_name}: {e}")
        return None

def get_hardware_module(module_type):
    """Lade Hardware-Module mit Caching"""
    if _hardware_status[module_type] is None:
        if module_type == 'camera':
            _hardware_status[module_type] = safe_import('hardware.camera', 'camera_manager')
        elif module_type == 'robot_arm':
            _hardware_status[module_type] = safe_import('hardware.robot_arm', 'robot_arm')
        elif module_type == 'motors':
            _hardware_status[module_type] = safe_import('hardware.motors', 'motor_controller')
        elif module_type == 'sensors':
            _hardware_status[module_type] = safe_import('hardware.sensors', 'sensor_manager')
        elif module_type == 'ai':
            _hardware_status[module_type] = safe_import('ai.weed_detection', 'weed_detector')
    
    return _hardware_status[module_type]

# ===== KAMERA API =====
@bp.route('/api/camera/stream')
def video_stream():
    try:
        camera_manager = get_hardware_module('camera')
        if not camera_manager:
            return "Kamera-Modul nicht verfügbar", 503
            
        def generate():
            try:
                camera_manager.start_stream()
                while True:
                    frame = camera_manager.get_frame()
                    if frame:
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                    time.sleep(0.033)
            except Exception as e:
                print(f"Stream-Fehler: {e}")
                
        return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        print(f"Kamera-Stream-Fehler: {e}")
        return f"Kamera-Fehler: {e}", 500

@bp.route('/api/camera/capture', methods=['POST'])
def capture_image():
    try:
        camera_manager = get_hardware_module('camera')
        if not camera_manager:
            return jsonify({'error': 'Kamera-Modul nicht verfügbar', 'mock': True}), 200
            
        filename = camera_manager.capture_image()
        if filename:
            return jsonify({'status': 'captured', 'filename': filename})
        return jsonify({'error': 'Capture failed'}), 500
    except Exception as e:
        print(f"Capture-Fehler: {e}")
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

# ===== ROBOTERARM API =====
@bp.route('/api/arm/info')
def get_arm_info():
    try:
        robot_arm = get_hardware_module('robot_arm')
        if not robot_arm:
            # Mock-Antwort wenn Modul nicht verfügbar
            return jsonify({
                'controller': {
                    'hardware_available': False,
                    'i2c_address': '0x40',
                    'servo_count': 6,
                    'is_moving': False,
                    'emergency_stopped': False
                },
                'joints': ['base', 'shoulder', 'elbow', 'wrist', 'gripper', 'tool'],
                'presets': ['home', 'weed_detect', 'weed_remove'],
                'current_position': {
                    'base': 90, 'shoulder': 90, 'elbow': 90, 
                    'wrist': 90, 'gripper': 90, 'tool': 0
                },
                'mock': True
            })
            
        info = robot_arm.get_arm_info()
        return jsonify(info)
    except Exception as e:
        print(f"Arm-Info-Fehler: {e}")
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@bp.route('/api/arm/move/joint', methods=['POST'])
def move_arm_joint():
    try:
        data = request.get_json()
        joint = data.get('joint')
        angle = data.get('angle')
        
        if not joint or angle is None:
            return jsonify({'error': 'Joint und Angle erforderlich'}), 400
        
        robot_arm = get_hardware_module('robot_arm')
        if not robot_arm:
            # Mock-Antwort
            return jsonify({
                'status': 'success', 
                'joint': joint, 
                'angle': angle,
                'mock': True,
                'message': 'Roboterarm-Modul nicht verfügbar - Mock-Modus'
            })
        
        success = robot_arm.move_joint(joint, float(angle))
        
        if success:
            return jsonify({'status': 'success', 'joint': joint, 'angle': angle})
        else:
            return jsonify({'error': 'Bewegung fehlgeschlagen'}), 500
            
    except Exception as e:
        print(f"Joint-Move-Fehler: {e}")
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@bp.route('/api/arm/move/preset', methods=['POST'])
def move_arm_to_preset():
    try:
        data = request.get_json()
        preset = data.get('preset')
        duration = data.get('duration', 2.0)
        
        if not preset:
            return jsonify({'error': 'Preset erforderlich'}), 400
        
        robot_arm = get_hardware_module('robot_arm')
        if not robot_arm:
            # Mock-Antwort
            return jsonify({
                'status': 'success', 
                'preset': preset, 
                'duration': duration,
                'mock': True,
                'message': f'Fahre zu {preset} (Mock-Modus)'
            })
        
        success = robot_arm.move_to_preset(preset, duration)
        
        if success:
            return jsonify({'status': 'success', 'preset': preset, 'duration': duration})
        else:
            return jsonify({'error': f'Preset {preset} nicht gefunden'}), 404
            
    except Exception as e:
        print(f"Preset-Move-Fehler: {e}")
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@bp.route('/api/arm/emergency_stop', methods=['POST'])
def arm_emergency_stop():
    try:
        robot_arm = get_hardware_module('robot_arm')
        if robot_arm:
            robot_arm.emergency_stop()
        return jsonify({'status': 'emergency_stop_activated', 'mock': robot_arm is None})
    except Exception as e:
        print(f"Emergency-Stop-Fehler: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/arm/weed_removal', methods=['POST'])
def arm_weed_removal():
    try:
        data = request.get_json() or {}
        target_x = data.get('target_x', 0)
        target_y = data.get('target_y', 0)
        
        robot_arm = get_hardware_module('robot_arm')
        if not robot_arm:
            return jsonify({
                'status': 'sequence_started', 
                'target_x': target_x, 
                'target_y': target_y,
                'mock': True,
                'message': 'Unkraut-Entfernung (Mock-Modus)'
            })
        
        thread = threading.Thread(
            target=robot_arm.weed_removal_sequence,
            args=(target_x, target_y),
            daemon=True
        )
        thread.start()
        
        return jsonify({'status': 'sequence_started', 'target_x': target_x, 'target_y': target_y})
    except Exception as e:
        print(f"Weed-Removal-Fehler: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/arm/tool/activate', methods=['POST'])  
def activate_arm_tool():
    try:
        data = request.get_json() or {}
        duration = data.get('duration', 3.0)
        
        robot_arm = get_hardware_module('robot_arm')
        if not robot_arm:
            return jsonify({
                'status': 'tool_activated', 
                'duration': duration,
                'mock': True,
                'message': f'Werkzeug aktiviert für {duration}s (Mock-Modus)'
            })
        
        thread = threading.Thread(
            target=robot_arm.activate_tool,
            args=(duration,),
            daemon=True
        )
        thread.start()
        
        return jsonify({'status': 'tool_activated', 'duration': duration})
    except Exception as e:
        print(f"Tool-Aktivierung-Fehler: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/arm/calibrate', methods=['POST'])
def calibrate_arm_servos():
    try:
        robot_arm = get_hardware_module('robot_arm')
        if not robot_arm:
            return jsonify({
                'status': 'calibration_started',
                'mock': True,
                'message': 'Servo-Kalibrierung (Mock-Modus)'
            })
        
        thread = threading.Thread(target=robot_arm.calibrate_servos, daemon=True)
        thread.start()
        
        return jsonify({'status': 'calibration_started'})
    except Exception as e:
        print(f"Kalibrierung-Fehler: {e}")
        return jsonify({'error': str(e)}), 500

# ===== FAHRZEUG-STEUERUNG API =====
@bp.route('/api/control/move', methods=['POST'])
def move_robot():
    try:
        data = request.get_json()
        direction = data.get('direction')
        speed = data.get('speed', 50)
        duration = data.get('duration', 0.1)
        
        motor_controller = get_hardware_module('motors')
        if not motor_controller:
            return jsonify({
                'status': 'success',
                'direction': direction,
                'speed': speed,
                'duration': duration,
                'mock': True,
                'message': f'Fahre {direction} @ {speed}% (Mock-Modus)'
            })
        
        result = motor_controller.move(direction, speed, duration)
        return jsonify(result)
    except Exception as e:
        print(f"Motor-Move-Fehler: {e}")
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@bp.route('/api/control/stop', methods=['POST'])
def emergency_stop():
    try:
        motor_controller = get_hardware_module('motors')
        result = {'status': 'stopped', 'mock': motor_controller is None}
        
        if motor_controller:
            result = motor_controller.emergency_stop()
        
        # Auch Roboterarm stoppen
        robot_arm = get_hardware_module('robot_arm')
        if robot_arm:
            try:
                robot_arm.emergency_stop()
            except:
                pass
        
        return jsonify(result)
    except Exception as e:
        print(f"Emergency-Stop-Fehler: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/control/status')
def get_control_status():
    try:
        # Sensoren mit Fallback
        sensor_data = {}
        try:
            get_sensor_data = safe_import('hardware.sensors', 'get_sensor_data')
            if get_sensor_data:
                sensor_data = get_sensor_data()
            else:
                # Mock-Sensordaten
                sensor_data = {
                    'temperature': 22.5,
                    'humidity': 45.0,
                    'battery': {'percentage': 85, 'voltage': 12.4}
                }
        except Exception as e:
            print(f"Sensor-Daten-Fehler: {e}")
            sensor_data = {'error': str(e), 'mock': True}
        
        # Motoren-Status mit Fallback
        motor_status = {}
        motor_controller = get_hardware_module('motors')
        if motor_controller:
            try:
                motor_status = motor_controller.get_status()
            except:
                motor_status = {'error': 'Motor-Status nicht verfügbar', 'mock': True}
        else:
            motor_status = {'is_moving': False, 'mock': True}
        
        status = {
            'timestamp': int(time.time()),
            'robot': {
                'mode': 'manual',
                'is_active': False,
                'motors': motor_status
            },
            'sensors': sensor_data,
            'battery': {
                'percentage': 85,
                'voltage': 12.4,
                'charging': False
            }
        }
        
        # Roboterarm-Status hinzufügen
        robot_arm = get_hardware_module('robot_arm')
        if robot_arm:
            try:
                arm_position = robot_arm.get_current_position()
                status['arm'] = {
                    'available': True,
                    'position': arm_position
                }
            except:
                status['arm'] = {'available': False, 'error': 'Status nicht abrufbar'}
        else:
            status['arm'] = {'available': False, 'mock': True}
        
        return jsonify(status)
    except Exception as e:
        print(f"Control-Status-Fehler: {e}")
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

# ===== AI API =====
@bp.route('/api/ai/detect', methods=['POST'])
def detect_weeds():
    try:
        weed_detector = get_hardware_module('ai')
        camera_manager = get_hardware_module('camera')
        
        if not weed_detector:
            # Mock-Erkennung
            import random
            mock_detections = []
            if random.random() > 0.5:  # 50% Chance für Unkraut
                mock_detections = [{
                    'class': 'weed',
                    'confidence': round(random.uniform(0.7, 0.95), 2),
                    'x': random.randint(100, 500),
                    'y': random.randint(100, 300),
                    'bbox': {'x': 100, 'y': 100, 'width': 50, 'height': 40},
                    'mock': True
                }]
            
            return jsonify({
                'detections': mock_detections,
                'count': len(mock_detections),
                'confidence': 0.85,
                'processing_time': 0.12,
                'method': 'mock',
                'mock': True,
                'message': 'KI-Modul nicht verfügbar - Mock-Erkennung'
            })
        
        frame_data = None
        if camera_manager:
            frame_data = camera_manager.get_frame()
        
        if frame_data:
            result = weed_detector.detect_from_bytes(frame_data)
            
            # Optional: Roboterarm zu erkanntem Unkraut bewegen
            if result.get('detections') and len(result['detections']) > 0:
                detection = result['detections'][0]
                target_x = detection.get('x', 0)
                target_y = detection.get('y', 0)
                
                robot_arm = get_hardware_module('robot_arm')
                if robot_arm:
                    try:
                        threading.Thread(
                            target=robot_arm.weed_removal_sequence,
                            args=(target_x, target_y),
                            daemon=True
                        ).start()
                        result['arm_action'] = 'weed_removal_started'
                    except:
                        result['arm_action'] = 'arm_error'
                else:
                    result['arm_action'] = 'arm_not_available'
            
            return jsonify(result)
        else:
            return jsonify({'error': 'No camera frame available'}), 400
            
    except Exception as e:
        print(f"AI-Detection-Fehler: {e}")
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

# ===== SYSTEM API =====
@bp.route('/api/system/status')
def system_status():
    try:
        # System-Stats mit Fallback
        try:
            sensor_manager = get_hardware_module('sensors')
            if sensor_manager:
                system_stats = sensor_manager.get_system_stats()
            else:
                # Mock-System-Stats
                import psutil
                system_stats = {
                    'cpu_usage': psutil.cpu_percent(),
                    'memory_usage': psutil.virtual_memory().percent,
                    'cpu_temperature': 45.0,
                    'uptime': 3600,
                    'timestamp': int(time.time())
                }
        except Exception as e:
            print(f"System-Stats-Fehler: {e}")
            system_stats = {
                'cpu_usage': 25.0,
                'memory_usage': 60.0,
                'cpu_temperature': 42.0,
                'uptime': 3600,
                'timestamp': int(time.time()),
                'error': str(e)
            }
        
        status = {
            'timestamp': int(time.time()),
            'system': system_stats,
            'hardware': {
                'camera_available': get_hardware_module('camera') is not None,
                'gpio_available': False,
                'mock_mode': True
            }
        }
        
        # Roboterarm-Hardware-Status
        robot_arm = get_hardware_module('robot_arm')
        if robot_arm:
            try:
                arm_info = robot_arm.get_arm_info()
                status['hardware']['arm_available'] = arm_info['controller']['hardware_available']
                status['hardware']['servo_count'] = arm_info['controller']['servo_count']
            except:
                status['hardware']['arm_available'] = False
                status['hardware']['arm_error'] = 'Status nicht abrufbar'
        else:
            status['hardware']['arm_available'] = False
            status['hardware']['arm_mock'] = True
        
        return jsonify(status)
    except Exception as e:
        print(f"System-Status-Fehler: {e}")
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500