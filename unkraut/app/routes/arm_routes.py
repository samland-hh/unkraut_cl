# app/routes/arm_routes.py
"""
Roboterarm-Steuerung Routes für Unkraut-2025
Saubere API ohne HTML-Templates - ersetzt roboter_arm_api.py
"""
from flask import Blueprint, render_template, jsonify, request
import time
import threading
import traceback

bp = Blueprint('arm', __name__)

@bp.route('/arm')
def arm_control():
    """Roboterarm-Steuerungsseite anzeigen"""
    return render_template('arm.html')

@bp.route('/api/arm/info')
def get_arm_info():
    """Roboterarm-Informationen abrufen"""
    try:
        # Hardware-Modul importieren
        from hardware.robot_arm import robot_arm
        info = robot_arm.get_arm_info()
        return jsonify(info)
    except ImportError:
        # Fallback wenn Hardware-Modul nicht verfügbar
        return jsonify({
            'controller': {
                'hardware_available': False,
                'i2c_address': '0x40',
                'servo_count': 6,
                'is_moving': False,
                'emergency_stopped': False
            },
            'joints': ['base', 'shoulder', 'elbow', 'wrist', 'gripper', 'tool'],
            'presets': ['home', 'weed_detect', 'weed_remove', 'park'],
            'current_position': {
                'base': 90, 'shoulder': 90, 'elbow': 90, 
                'wrist': 90, 'gripper': 90, 'tool': 0
            },
            'servo_ranges': {
                'base': {'min': 0, 'max': 180},
                'shoulder': {'min': 0, 'max': 180},
                'elbow': {'min': 0, 'max': 180},
                'wrist': {'min': 0, 'max': 180},
                'gripper': {'min': 0, 'max': 180},
                'tool': {'min': 0, 'max': 180}
            },
            'mock': True
        })
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@bp.route('/api/arm/position')
def get_position():
    """Aktuelle Arm-Position abrufen"""
    try:
        from hardware.robot_arm import robot_arm
        position = robot_arm.get_current_position()
        return jsonify({'position': position})
    except ImportError:
        # Mock-Positionen
        return jsonify({
            'position': {
                'base': 90, 'shoulder': 90, 'elbow': 90, 
                'wrist': 90, 'gripper': 90, 'tool': 0
            },
            'mock': True
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/arm/move/joint', methods=['POST'])
def move_joint():
    """Einzelnes Gelenk bewegen"""
    try:
        data = request.get_json()
        joint = data.get('joint')
        angle = data.get('angle')
        
        if not joint or angle is None:
            return jsonify({'error': 'Joint und Angle erforderlich'}), 400
        
        # Eingabe validieren
        valid_joints = ['base', 'shoulder', 'elbow', 'wrist', 'gripper', 'tool']
        if joint not in valid_joints:
            return jsonify({'error': f'Ungültiges Gelenk: {joint}'}), 400
        
        try:
            angle = float(angle)
        except (ValueError, TypeError):
            return jsonify({'error': 'Angle muss eine Zahl sein'}), 400
        
        if not (0 <= angle <= 180):
            return jsonify({'error': 'Angle muss zwischen 0 und 180 sein'}), 400
        
        try:
            from hardware.robot_arm import robot_arm
            success = robot_arm.move_joint(joint, angle)
            
            if success:
                return jsonify({
                    'status': 'success', 
                    'joint': joint, 
                    'angle': angle,
                    'hardware': True
                })
            else:
                return jsonify({'error': 'Bewegung fehlgeschlagen'}), 500
                
        except ImportError:
            # Mock-Modus
            return jsonify({
                'status': 'success', 
                'joint': joint, 
                'angle': angle,
                'mock': True,
                'message': f'Mock: {joint} zu {angle}°'
            })
            
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@bp.route('/api/arm/move/preset', methods=['POST'])
def move_to_preset():
    """Zu Preset-Position fahren"""
    try:
        data = request.get_json()
        preset = data.get('preset')
        duration = data.get('duration', 2.0)
        
        if not preset:
            return jsonify({'error': 'Preset erforderlich'}), 400
        
        # Gültige Presets
        valid_presets = ['home', 'weed_detect', 'weed_remove', 'park', 'spray_position']
        if preset not in valid_presets:
            return jsonify({'error': f'Ungültiges Preset: {preset}'}), 400
        
        try:
            duration = float(duration)
        except (ValueError, TypeError):
            duration = 2.0
        
        duration = max(0.5, min(10.0, duration))  # Begrenzen auf 0.5-10s
        
        try:
            from hardware.robot_arm import robot_arm
            success = robot_arm.move_to_preset(preset, duration)
            
            if success:
                return jsonify({
                    'status': 'success', 
                    'preset': preset, 
                    'duration': duration,
                    'hardware': True
                })
            else:
                return jsonify({'error': f'Preset {preset} nicht gefunden'}), 404
                
        except ImportError:
            # Mock-Modus
            return jsonify({
                'status': 'success', 
                'preset': preset, 
                'duration': duration,
                'mock': True,
                'message': f'Mock: Fahre zu {preset} in {duration}s'
            })
            
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@bp.route('/api/arm/move/custom', methods=['POST'])
def move_custom():
    """Zu benutzerdefinierten Positionen fahren"""
    try:
        data = request.get_json()
        positions = data.get('positions', {})
        duration = data.get('duration', 1.5)
        
        if not positions:
            return jsonify({'error': 'Positionen erforderlich'}), 400
        
        # Positionen validieren
        valid_joints = ['base', 'shoulder', 'elbow', 'wrist', 'gripper', 'tool']
        validated_positions = {}
        
        for joint, angle in positions.items():
            if joint not in valid_joints:
                continue
            try:
                angle = float(angle)
                if 0 <= angle <= 180:
                    validated_positions[joint] = angle
            except (ValueError, TypeError):
                continue
        
        if not validated_positions:
            return jsonify({'error': 'Keine gültigen Positionen gefunden'}), 400
        
        try:
            from hardware.robot_arm import robot_arm
            success = robot_arm.set_custom_position(validated_positions, duration)
            
            if success:
                return jsonify({
                    'status': 'success', 
                    'positions': validated_positions,
                    'hardware': True
                })
            else:
                return jsonify({'error': 'Bewegung fehlgeschlagen'}), 500
                
        except ImportError:
            # Mock-Modus
            return jsonify({
                'status': 'success', 
                'positions': validated_positions,
                'mock': True,
                'message': f'Mock: Custom-Position mit {len(validated_positions)} Gelenken'
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/arm/weed_removal', methods=['POST'])
def weed_removal_sequence():
    """Unkraut-Entfernung Sequenz starten"""
    try:
        data = request.get_json() or {}
        target_x = data.get('target_x', 0)
        target_y = data.get('target_y', 0)
        
        # Koordinaten validieren
        try:
            target_x = float(target_x)
            target_y = float(target_y)
        except (ValueError, TypeError):
            target_x, target_y = 0, 0
        
        # Begrenzen auf sinnvolle Werte
        target_x = max(-100, min(100, target_x))
        target_y = max(-100, min(100, target_y))
        
        try:
            from hardware.robot_arm import robot_arm
            
            # Sequenz in separatem Thread ausführen (non-blocking)
            thread = threading.Thread(
                target=robot_arm.weed_removal_sequence,
                args=(target_x, target_y),
                daemon=True
            )
            thread.start()
            
            return jsonify({
                'status': 'sequence_started',
                'target_x': target_x,
                'target_y': target_y,
                'hardware': True
            })
            
        except ImportError:
            # Mock-Modus
            return jsonify({
                'status': 'sequence_started',
                'target_x': target_x,
                'target_y': target_y,
                'mock': True,
                'message': f'Mock: Unkraut-Entfernung bei ({target_x}, {target_y})'
            })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/arm/tool/activate', methods=['POST'])  
def activate_tool():
    """Werkzeug aktivieren"""
    try:
        data = request.get_json() or {}
        duration = data.get('duration', 3.0)
        
        try:
            duration = float(duration)
        except (ValueError, TypeError):
            duration = 3.0
        
        duration = max(0.5, min(30.0, duration))  # Begrenzen auf 0.5-30s
        
        try:
            from hardware.robot_arm import robot_arm
            
            # Tool-Aktivierung in Thread
            thread = threading.Thread(
                target=robot_arm.activate_tool,
                args=(duration,),
                daemon=True
            )
            thread.start()
            
            return jsonify({
                'status': 'tool_activated', 
                'duration': duration,
                'hardware': True
            })
            
        except ImportError:
            # Mock-Modus
            return jsonify({
                'status': 'tool_activated', 
                'duration': duration,
                'mock': True,
                'message': f'Mock: Werkzeug aktiviert für {duration}s'
            })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/arm/emergency_stop', methods=['POST'])
def emergency_stop():
    """Not-Stopp für Roboterarm"""
    try:
        try:
            from hardware.robot_arm import robot_arm
            robot_arm.emergency_stop()
            return jsonify({
                'status': 'emergency_stop_activated',
                'hardware': True
            })
        except ImportError:
            return jsonify({
                'status': 'emergency_stop_activated',
                'mock': True,
                'message': 'Mock: Roboterarm Not-Stopp aktiviert'
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/arm/home', methods=['POST'])
def home_position():
    """Zur Home-Position fahren"""
    try:
        try:
            from hardware.robot_arm import robot_arm
            success = robot_arm.home_position()
            return jsonify({
                'status': 'success' if success else 'failed',
                'hardware': True
            })
        except ImportError:
            return jsonify({
                'status': 'success',
                'mock': True,
                'message': 'Mock: Fahre zu Home-Position'
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/arm/park', methods=['POST'])
def park_position():
    """Zur Park-Position fahren und Servos deaktivieren"""
    try:
        try:
            from hardware.robot_arm import robot_arm
            success = robot_arm.park_position()
            return jsonify({
                'status': 'success' if success else 'failed',
                'hardware': True
            })
        except ImportError:
            return jsonify({
                'status': 'success',
                'mock': True,
                'message': 'Mock: Fahre zu Park-Position'
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/arm/calibrate', methods=['POST'])
def calibrate_servos():
    """Servo-Kalibrierung durchführen"""
    try:
        try:
            from hardware.robot_arm import robot_arm
            
            # Kalibrierung in Thread (dauert länger)
            thread = threading.Thread(
                target=robot_arm.calibrate_servos,
                daemon=True
            )
            thread.start()
            
            return jsonify({
                'status': 'calibration_started',
                'hardware': True
            })
        except ImportError:
            return jsonify({
                'status': 'calibration_started',
                'mock': True,
                'message': 'Mock: Servo-Kalibrierung gestartet'
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500