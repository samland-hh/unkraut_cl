# unkraut/app/routes/api_routes.py - CLEAN VERSION

"""
Zentrale API Endpoints für Unkraut-2025
CLEAN: Overlay entfernt, img_ Dateinamen, Pfad korrigiert
"""
from flask import Blueprint, jsonify, request, Response, send_file
from datetime import datetime
import threading
import time
import traceback
import os
import zipfile
import tempfile
import json

bp = Blueprint('api', __name__)

# Globale Hardware-Status Cache
_hardware_status = {
    'camera': None,
    'robot_arm': None,
    'motors': None,
    'sensors': None,
    'ai': None
}

# Korrekter Pfad zum data-Verzeichnis
IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'images')

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

# ===== HEALTH =====
@bp.route('/health')
def health():
    return {'status': 'healthy', 'timestamp': datetime.now().isoformat()}

# ===== KAMERA API =====
@bp.route('/api/camera/stream')
def video_stream():
    """Kamera Video-Stream (MJPEG)"""
    try:
        camera_manager = get_hardware_module('camera')
        if not camera_manager:
            print("❌ Kamera-Modul nicht verfügbar - Mock-Stream")
            return _mock_camera_stream()
            
        def generate():
            try:
                camera_manager.start_stream()
                while True:
                    frame = camera_manager.get_frame()
                    if frame:
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                    time.sleep(0.033)  # ~30 FPS
            except Exception as e:
                print(f"Stream-Fehler: {e}")
                
        return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        print(f"Kamera-Stream-Fehler: {e}")
        return _mock_camera_stream()

def _mock_camera_stream():
    """Mock-Kamera-Stream wenn Hardware nicht verfügbar"""
    def generate_mock():
        import cv2
        import numpy as np
        frame_count = 0
        
        while True:
            # Mock-Frame erstellen
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            frame[:] = (20, 50, 20)  # Dunkles Grün
            
            # Beweglicher Kreis
            center_x = int(320 + 200 * np.sin(frame_count * 0.05))
            center_y = int(240 + 100 * np.cos(frame_count * 0.08))
            cv2.circle(frame, (center_x, center_y), 25, (0, 255, 0), -1)
            
            # Status-Text
            cv2.putText(frame, "UNKRAUT-2025 MOCK CAMERA", (120, 400),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(frame, f"Frame: {frame_count}", (20, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            # Frame zu JPEG
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            if ret:
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            frame_count += 1
            time.sleep(0.033)  # ~30 FPS
    
    return Response(generate_mock(), mimetype='multipart/x-mixed-replace; boundary=frame')

@bp.route('/api/camera/capture', methods=['POST'])
def capture_image():
    """Foto aufnehmen mit img_ Dateinamen"""
    try:
        print("📸 Capture-Anfrage erhalten...")
        
        # Custom Filename aus Request (von JavaScript)
        data = request.get_json() if request.is_json else {}
        custom_filename = data.get('filename') if data else None
        
        # Fallback: img_ Dateiname generieren falls nicht angegeben
        if not custom_filename:
            timestamp = datetime.now().strftime("%y.%m.%d_%H.%M_%S")
            custom_filename = f"img_{timestamp}.jpg"
        
        camera_manager = get_hardware_module('camera')
        if not camera_manager:
            print("❌ Kamera-Modul nicht verfügbar - Mock-Capture")
            
            # Mock-Bild erstellen mit korrektem Pfad
            os.makedirs(IMAGES_DIR, exist_ok=True)
            mock_filepath = os.path.join(IMAGES_DIR, custom_filename)
            _create_mock_image(mock_filepath)
            
            return jsonify({
                'status': 'captured',
                'filename': custom_filename,
                'mock': True,
                'message': 'Mock-Aufnahme erstellt (Kamera nicht verfügbar)'
            }), 200
        
        # Echte Kamera-Aufnahme mit custom filename
        filename = camera_manager.capture_image(custom_filename)
        
        if filename:
            return jsonify({
                'status': 'captured',
                'filename': filename,
                'message': f'Foto gespeichert: {filename}'
            }), 200
        else:
            return jsonify({
                'status': 'failed',
                'error': 'Foto-Aufnahme fehlgeschlagen'
            }), 500
            
    except Exception as e:
        print(f"❌ Capture-Fehler: {e}")
        return jsonify({'error': str(e)}), 500

def _create_mock_image(filepath):
    """Mock-Bild für Tests erstellen"""
    try:
        import cv2
        import numpy as np
        
        # Mock-Bild erstellen
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        frame[:] = (20, 80, 20)  # Grün
        
        cv2.putText(frame, "MOCK CAPTURE", (200, 240),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
        cv2.putText(frame, f"Zeit: {time.strftime('%H:%M:%S')}", (200, 280),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        cv2.imwrite(filepath, frame)
        print(f"📸 Mock-Bild erstellt: {filepath}")
        
    except Exception as e:
        print(f"❌ Mock-Image-Fehler: {e}")

# ===== KAMERA GALERIE API =====
@bp.route('/api/camera/images')
def get_camera_images():
    """Liste aller aufgenommenen Bilder"""
    try:
        os.makedirs(IMAGES_DIR, exist_ok=True)
        
        images = []
        total_size = 0
        
        # Alle Bilddateien finden
        for filename in os.listdir(IMAGES_DIR):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                filepath = os.path.join(IMAGES_DIR, filename)
                if os.path.isfile(filepath):
                    try:
                        stat = os.stat(filepath)
                        size_bytes = stat.st_size
                        total_size += size_bytes
                        
                        images.append({
                            'filename': filename,
                            'size_bytes': size_bytes,
                            'size_kb': round(size_bytes / 1024, 1),
                            'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            'url': f'/api/camera/image/{filename}'
                        })
                    except Exception as e:
                        print(f"❌ Bild-Info-Fehler für {filename}: {e}")
        
        # Nach Erstelldatum sortieren (neueste zuerst)
        images.sort(key=lambda x: x['created'], reverse=True)
        
        return jsonify({
            'status': 'success',
            'images': images,
            'total_count': len(images),
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'images_dir': IMAGES_DIR
        })
        
    except Exception as e:
        print(f"❌ Camera-Images-API-Fehler: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/camera/image/<filename>')
def get_camera_image(filename):
    """Einzelnes Bild aus der Kamera-Galerie"""
    try:
        # Sicherheitscheck: Nur erlaubte Zeichen
        import re
        if not re.match(r'^[a-zA-Z0-9._-]+\.(jpg|jpeg|png)$', filename, re.IGNORECASE):
            return jsonify({'error': 'Ungültiger Dateiname'}), 400
        
        filepath = os.path.join(IMAGES_DIR, filename)
        
        # Sicherheitscheck - nur Dateien im images-Verzeichnis
        if not os.path.abspath(filepath).startswith(os.path.abspath(IMAGES_DIR)):
            return jsonify({'error': 'Unerlaubter Dateipfad'}), 403
        
        print(f"🔍 Suche Bild: {filepath}")  # DEBUG
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'Bild nicht gefunden'}), 404
        
        return send_file(filepath, as_attachment=False)
        
    except Exception as e:
        print(f"❌ Image-Serve-Fehler: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/camera/image/<filename>', methods=['DELETE'])
def delete_camera_image(filename):
    """Einzelnes Bild löschen"""
    try:
        filepath = os.path.join(IMAGES_DIR, filename)
        
        # Sicherheitschecks
        import re
        if not re.match(r'^[a-zA-Z0-9._-]+\.(jpg|jpeg|png)$', filename, re.IGNORECASE):
            return jsonify({'error': 'Ungültiger Dateiname'}), 400
        
        if not os.path.abspath(filepath).startswith(os.path.abspath(IMAGES_DIR)):
            return jsonify({'error': 'Unerlaubter Dateipfad'}), 403
        
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"🗑️ Bild gelöscht: {filename}")
            return jsonify({
                'status': 'deleted',
                'filename': filename,
                'message': f'Bild {filename} gelöscht'
            })
        else:
            return jsonify({'error': 'Bild nicht gefunden'}), 404
            
    except Exception as e:
        print(f"❌ Image-Delete-Fehler: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/camera/images/clear', methods=['POST'])
def clear_camera_images():
    """Alle Bilder löschen"""
    try:
        if not os.path.exists(IMAGES_DIR):
            return jsonify({
                'status': 'success',
                'deleted_count': 0,
                'message': 'Keine Bilder vorhanden'
            })
        
        deleted_count = 0
        for filename in os.listdir(IMAGES_DIR):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                filepath = os.path.join(IMAGES_DIR, filename)
                try:
                    os.remove(filepath)
                    deleted_count += 1
                    print(f"🗑️ Gelöscht: {filename}")
                except Exception as e:
                    print(f"❌ Löschen fehlgeschlagen {filename}: {e}")
        
        return jsonify({
            'status': 'success',
            'deleted_count': deleted_count,
            'message': f'{deleted_count} Bilder gelöscht'
        })
        
    except Exception as e:
        print(f"❌ Clear-Images-Fehler: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/camera/download_all')
def download_all_camera_images():
    """Alle Bilder als ZIP herunterladen"""
    try:
        if not os.path.exists(IMAGES_DIR):
            return "Keine Bilder vorhanden", 404
        
        # Alle Bilddateien finden
        image_files = []
        for filename in os.listdir(IMAGES_DIR):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                filepath = os.path.join(IMAGES_DIR, filename)
                if os.path.isfile(filepath):
                    image_files.append((filename, filepath))
        
        if not image_files:
            return "Keine Bilder zum Download gefunden", 404
        
        # Temporäre ZIP-Datei erstellen
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_zip:
            with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for filename, filepath in image_files:
                    try:
                        zipf.write(filepath, filename)
                    except Exception as e:
                        print(f"❌ Fehler beim Hinzufügen von {filepath}: {e}")
        
        print(f"📦 ZIP erstellt: {len(image_files)} Bilder")
        
        # ZIP-Datei senden
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        download_name = f"unkraut_bilder_{timestamp}.zip"
        
        return send_file(
            temp_zip.name,
            as_attachment=True,
            download_name=download_name,
            mimetype='application/zip'
        )
        
    except Exception as e:
        print(f"❌ Download-All-Fehler: {e}")
        return f"Download-Fehler: {e}", 500

# ===== SYSTEM API =====
@bp.route('/api/system/status')
def system_status():
    """System-Status abrufen"""
    try:
        # System-Stats
        sensor_manager = get_hardware_module('sensors')
        if sensor_manager:
            try:
                system_stats = sensor_manager.get_system_stats()
            except Exception as e:
                print(f"System-Stats-Fehler: {e}")
                system_stats = _get_fallback_system_stats()
        else:
            system_stats = _get_fallback_system_stats()
        
        # Hardware-Verfügbarkeit prüfen
        hardware_status = {}
        
        # Kamera
        camera_manager = get_hardware_module('camera')
        hardware_status['camera_available'] = camera_manager is not None
        
        # Roboterarm
        robot_arm = get_hardware_module('robot_arm')
        hardware_status['arm_available'] = robot_arm is not None
        
        # GPIO
        try:
            import RPi.GPIO as GPIO
            hardware_status['gpio_available'] = True
        except ImportError:
            hardware_status['gpio_available'] = False
        
        status = {
            'timestamp': int(time.time()),
            'system': system_stats,
            'hardware': hardware_status,
            'version': '1.0.0'
        }
        
        return jsonify(status)
        
    except Exception as e:
        print(f"System-Status-Fehler: {e}")
        return jsonify({'error': str(e)}), 500

def _get_fallback_system_stats():
    """Fallback System-Stats wenn Sensor-Modul nicht verfügbar"""
    try:
        import psutil
        return {
            'cpu_usage': psutil.cpu_percent(interval=1),
            'memory_usage': psutil.virtual_memory().percent,
            'cpu_temperature': _get_cpu_temperature(),
            'uptime': int(time.time() - psutil.boot_time()) if hasattr(psutil, 'boot_time') else 3600,
            'fallback': True
        }
    except ImportError:
        return {
            'cpu_usage': 25.0,
            'memory_usage': 60.0,
            'cpu_temperature': 42.0,
            'uptime': 3600,
            'mock': True
        }

def _get_cpu_temperature():
    """CPU-Temperatur auslesen (Raspberry Pi)"""
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp = int(f.read().strip()) / 1000.0
            return temp
    except:
        return 45.0  # Fallback

# ===== AI API =====
@bp.route('/api/ai/detect', methods=['POST'])
def ai_detect():
    """KI-Unkrauterkennung"""
    try:
        print("🔍 AI-Detection-Anfrage erhalten...")
        
        # Aktueller Frame von Kamera holen
        camera_manager = get_hardware_module('camera')
        if camera_manager:
            frame_data = camera_manager.get_frame()
            if not frame_data:
                return jsonify({'error': 'Kein Kamera-Frame verfügbar'}), 400
        else:
            print("⚠️ Kamera nicht verfügbar - Mock-Detection")
            return _mock_ai_detection()
        
        # AI-Erkennung
        weed_detector = get_hardware_module('ai')
        if weed_detector:
            try:
                # Frame zu numpy array konvertieren
                import cv2
                import numpy as np
                np_arr = np.frombuffer(frame_data, np.uint8)
                frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                
                # Unkraut-Erkennung durchführen
                detection_result = weed_detector.detect_weeds(frame)
                
                return jsonify(detection_result)
                
            except Exception as e:
                print(f"AI-Detection-Fehler: {e}")
                return _mock_ai_detection()
        else:
            print("⚠️ AI-Modul nicht verfügbar - Mock-Detection")
            return _mock_ai_detection()
            
    except Exception as e:
        print(f"AI-Detection-Fehler: {e}")
        return jsonify({'error': str(e)}), 500

def _mock_ai_detection():
    """Mock-AI-Erkennung für Tests"""
    import random
    
    # Zufällige Mock-Erkennungen
    weeds = []
    weed_count = random.randint(0, 3)
    
    for i in range(weed_count):
        weeds.append({
            'x': random.randint(50, 590),
            'y': random.randint(50, 430),
            'width': random.randint(20, 80),
            'height': random.randint(20, 80),
            'confidence': random.uniform(0.6, 0.95),
            'type': random.choice(['Löwenzahn', 'Brennnessel', 'Unkraut'])
        })
    
    result = {
        'status': 'success',
        'weeds': weeds,
        'total_detected': len(weeds),
        'processing_time': random.uniform(0.1, 0.5),
        'mock': True
    }
    
    print(f"🔍 Mock-Detection: {len(weeds)} Unkräuter erkannt")
    return jsonify(result)

# ===== ROBOTERARM API =====
@bp.route('/api/arm/move/joint', methods=['POST'])
def move_arm_joint():
    """Einzelnes Gelenk bewegen"""
    try:
        data = request.get_json()
        joint_id = data.get('joint_id')
        angle = data.get('angle')
        
        robot_arm = get_hardware_module('robot_arm')
        if robot_arm:
            result = robot_arm.move_joint(joint_id, angle)
            return jsonify(result)
        else:
            return jsonify({
                'status': 'mock',
                'joint_id': joint_id,
                'angle': angle,
                'message': 'Mock-Arm-Bewegung (Hardware nicht verfügbar)'
            })
            
    except Exception as e:
        print(f"Arm-Move-Fehler: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/arm/emergency_stop', methods=['POST'])
def arm_emergency_stop():
    """Roboterarm-Notaus"""
    try:
        robot_arm = get_hardware_module('robot_arm')
        if robot_arm:
            result = robot_arm.emergency_stop()
            return jsonify(result)
        else:
            return jsonify({
                'status': 'mock_stop',
                'message': 'Mock-Notaus (Hardware nicht verfügbar)'
            })
            
    except Exception as e:
        print(f"Arm-Emergency-Stop-Fehler: {e}")
        return jsonify({'error': str(e)}), 500

#print("✅ Clean API-Routes geladen - img_ Dateinamen, Overlay entfernt, Pfad korrigiert!")