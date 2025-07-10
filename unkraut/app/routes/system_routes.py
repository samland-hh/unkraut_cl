# unkraut/app/routes/system_routes.py
"""
System-Shutdown API für Unkraut-2025
REINE PYTHON-DATEI - Keine HTML/CSS/JS!
"""
from flask import Blueprint, jsonify
import threading
import time
import subprocess
import os

bp = Blueprint('system', __name__)

def safe_import(module_name, item_name):
    """Sicherer Import mit Fehlerbehandlung"""
    try:
        module = __import__(module_name, fromlist=[item_name])
        return getattr(module, item_name)
    except Exception:
        return None

@bp.route('/api/system/shutdown', methods=['POST'])
def system_shutdown():
    """System sicher herunterfahren - Nur JSON Response"""
    try:
        shutdown_thread = threading.Thread(
            target=_shutdown_sequence,
            daemon=True
        )
        shutdown_thread.start()
        
        return jsonify({
            'status': 'shutdown_initiated',
            'message': 'System wird heruntergefahren...',
            'timestamp': int(time.time())
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/system/reboot', methods=['POST'])
def system_reboot():
    """System neu starten - Nur JSON Response"""
    try:
        reboot_thread = threading.Thread(
            target=_reboot_sequence,
            daemon=True
        )
        reboot_thread.start()
        
        return jsonify({
            'status': 'reboot_initiated',
            'message': 'System wird neu gestartet...',
            'timestamp': int(time.time())
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/system/emergency_shutdown', methods=['POST'])
def emergency_shutdown():
    """Not-Shutdown - Nur JSON Response"""
    try:
        emergency_thread = threading.Thread(
            target=_emergency_sequence,
            daemon=True
        )
        emergency_thread.start()
        
        return jsonify({
            'status': 'emergency_shutdown_initiated',
            'message': 'NOT-SHUTDOWN aktiviert!',
            'timestamp': int(time.time())
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/system/uptime', methods=['GET'])
def get_uptime():
    """Verbleibende Zeit bis Auto-Shutdown (8 Stunden ab Boot-Zeit)"""
    try:
        # Boot-Zeit vom System ermitteln (wie im auto_shutdown.sh Script)
        boot_time = _get_system_boot_time()
        current_time = time.time()
        
        # 8 Stunden in Sekunden (wie im Script definiert)
        shutdown_duration = 8 * 60 * 60  # 8 Stunden
        
        # Verbleibende Zeit berechnen
        elapsed_time = current_time - boot_time
        remaining_time = max(0, shutdown_duration - elapsed_time)
        
        # In Stunden und Minuten umwandeln
        hours = int(remaining_time // 3600)
        minutes = int((remaining_time % 3600) // 60)
        
        # Warnung-Status berechnen
        warning_status = "normal"
        if remaining_time <= 1800:  # 30 Minuten (wie im Script)
            warning_status = "critical"
        elif remaining_time <= 3600:  # 1 Stunde
            warning_status = "warning"
        
        return jsonify({
            'remaining_seconds': int(remaining_time),
            'remaining_formatted': f"{hours:02d}:{minutes:02d}",
            'hours': hours,
            'minutes': minutes,
            'warning_status': warning_status,
            'shutdown_duration': shutdown_duration,
            'elapsed_seconds': int(elapsed_time),
            'boot_time': boot_time,
            'script_compatible': True
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def _get_system_boot_time():
    """Ermittelt die Boot-Zeit des Systems (wie auto_shutdown.sh)"""
    try:
        # Methode 1: uptime -s (wie im Script verwendet)
        result = subprocess.run(['uptime', '-s'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            import datetime
            boot_time_str = result.stdout.strip()
            # Format: "2025-01-10 14:30:15"
            boot_time = datetime.datetime.strptime(boot_time_str, '%Y-%m-%d %H:%M:%S')
            return boot_time.timestamp()
    except Exception:
        pass
    
    try:
        # Methode 2: /proc/uptime
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.read().split()[0])
        return time.time() - uptime_seconds
    except Exception:
        pass
    
    try:
        # Methode 3: psutil (fallback)
        import psutil
        return psutil.boot_time()
    except Exception:
        pass
    
    # Fallback: Aktuelle Zeit (für Tests)
    return time.time()

def _shutdown_sequence():
    """Shutdown-Sequence - Reine Python-Logik"""
    print("🔄 Starte System-Shutdown...")
    
    # Motoren stoppen
    motor_controller = safe_import('hardware.motors', 'motor_controller')
    if motor_controller:
        motor_controller.stop_all()
    
    # Roboterarm parken
    robot_arm = safe_import('hardware.robot_arm', 'robot_arm')
    if robot_arm:
        robot_arm.park_position()
    
    # Kamera stoppen
    camera_manager = safe_import('hardware.camera', 'camera_manager')
    if camera_manager:
        camera_manager.stop_stream()
    
    # GPIO cleanup
    try:
        import RPi.GPIO as GPIO
        GPIO.cleanup()
    except ImportError:
        pass
    
    time.sleep(3)
    
    # System herunterfahren
    try:
        subprocess.run(['sudo', 'shutdown', '-h', 'now'], check=True)
    except subprocess.CalledProcessError:
        os._exit(0)

def _reboot_sequence():
    """Reboot-Sequence - Reine Python-Logik"""
    print("🔄 Starte System-Reboot...")
    _cleanup_hardware()
    time.sleep(2)
    subprocess.run(['sudo', 'reboot'], check=True)

def _emergency_sequence():
    """Emergency-Sequence - Reine Python-Logik"""
    print("🚨 NOT-SHUTDOWN AKTIVIERT!")
    _cleanup_hardware()
    subprocess.run(['sudo', 'shutdown', '-h', 'now'], check=False)

def _cleanup_hardware():
    """Hardware-Cleanup - Reine Python-Logik"""
    try:
        motor_controller = safe_import('hardware.motors', 'motor_controller')
        if motor_controller:
            motor_controller.emergency_stop()
        
        robot_arm = safe_import('hardware.robot_arm', 'robot_arm')
        if robot_arm:
            robot_arm.emergency_stop()
        
        import RPi.GPIO as GPIO
        GPIO.cleanup()
    except Exception as e:
        print(f"Cleanup-Fehler: {e}")