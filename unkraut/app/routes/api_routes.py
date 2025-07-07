# app/routes/api_routes.py
"""
Zentrale API Endpoints für Unkraut-2025
Robuste API mit verbesserter Fehlerbehandlung und Mock-Fallbacks
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

# ===== health =====
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
            return "Kamera-Modul nicht verfügbar", 503
            
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
        return f"Kamera-Fehler: {e}", 500

@bp.route('/api/camera/capture', methods=['POST'])
def capture_image():
    """Einfacher Capture-Endpoint ohne JSON-Abhängigkeit"""
    try:
        print("📸 Capture-Anfrage erhalten...")
        
        camera_manager = get_hardware_module('camera')
        if not camera_manager:
            print("❌ Kamera-Modul nicht verfügbar - Mock-Modus")
            # Mock-Response für Tests
            timestamp = int(time.time())
            mock_filename = f"mock_capture_{timestamp}.jpg"
            return jsonify({
                'status': 'captured',
                'filename': mock_filename,
                'mock': True,
                'message': 'Mock-Aufnahme erstellt (Kamera nicht verfügbar)'
            }), 200
        
        # Einfacher Capture-Aufruf
        filename = camera_manager.capture_image()
        
        if filename:
            print(f"✅ Capture erfolgreich: {filename}")
            return jsonify({
                'status': 'captured', 
                'filename': filename,
                'timestamp': int(time.time())
            })
        else:
            print("❌ Capture fehlgeschlagen")
            return jsonify({
                'error': 'Capture failed',
                'message': 'camera_manager.capture_image() gab None zurück'
            }), 500
            
    except Exception as e:
        print(f"❌ Capture-Fehler: {e}")
        return jsonify({
            'error': str(e),
            'message': 'API-Exception beim Capture'
        }), 500
# ===== FAHRZEUG-STEUERUNG API =====
@bp.route('/api/control/move', methods=['POST'])
def move_robot():
    """Roboter-Fahrzeug bewegen"""
    try:
        data = request.get_json()
        direction = data.get('direction')
        speed = data.get('speed', 50)
        duration = data.get('duration', 0.1)
        
        # Eingabe validieren
        valid_directions = ['forward', 'backward', 'left', 'right', 'stop']
        if direction not in valid_directions:
            return jsonify({'error': f'Ungültige Richtung: {direction}'}), 400
        
        try:
            speed = max(0, min(100, int(speed)))
            duration = max(0.1, min(10.0, float(duration)))
        except (ValueError, TypeError):
            return jsonify({'error': 'Ungültige Speed/Duration Parameter'}), 400
        
        motor_controller = get_hardware_module('motors')
        if not motor_controller:
            return jsonify({
                'status': 'success',
                'direction': direction,
                'speed': speed,
                'duration': duration,
                'mock': True,
                'message': f'Mock: Fahre {direction} @ {speed}% für {duration}s'
            })
        
        result = motor_controller.move(direction, speed, duration)
        return jsonify(result)
        
    except Exception as e:
        print(f"Motor-Move-Fehler: {e}")
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@bp.route('/api/control/stop', methods=['POST'])
def emergency_stop():
    """Not-Stopp für alle Systeme"""
    try:
        results = []
        
        # Motor-Controller stoppen
        motor_controller = get_hardware_module('motors')
        if motor_controller:
            try:
                result = motor_controller.emergency_stop()
                results.append({'motors': result})
            except Exception as e:
                results.append({'motors': {'error': str(e)}})
        else:
            results.append({'motors': {'mock': True, 'status': 'stopped'}})
        
        # Roboterarm stoppen
        robot_arm = get_hardware_module('robot_arm')
        if robot_arm:
            try:
                robot_arm.emergency_stop()
                results.append({'arm': {'status': 'emergency_stop_activated'}})
            except Exception as e:
                results.append({'arm': {'error': str(e)}})
        else:
            results.append({'arm': {'mock': True, 'status': 'emergency_stop_activated'}})
        
        return jsonify({
            'status': 'emergency_stop_completed',
            'systems': results,
            'timestamp': int(time.time())
        })
        
    except Exception as e:
        print(f"Emergency-Stop-Fehler: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/control/status')
def get_control_status():
    """Fahrzeug-Status abrufen"""
    try:
        # Motor-Status
        motor_controller = get_hardware_module('motors')
        if motor_controller:
            try:
                motor_status = motor_controller.get_status()
            except Exception as e:
                motor_status = {'error': str(e), 'mock': True}
        else:
            motor_status = {'is_moving': False, 'mock': True}
        
        # Sensor-Daten
        sensor_manager = get_hardware_module('sensors')
        if sensor_manager:
            try:
                sensor_data = sensor_manager.get_sensor_data()
            except Exception as e:
                sensor_data = {'error': str(e), 'mock': True}
        else:
            sensor_data = {
                'temperature': 22.5,
                'humidity': 45.0,
                'battery': {'percentage': 85, 'voltage': 12.4},
                'mock': True
            }
        
        # Roboterarm-Status
        robot_arm = get_hardware_module('robot_arm')
        if robot_arm:
            try:
                arm_status = robot_arm.get_status()
            except Exception as e:
                arm_status = {'error': str(e), 'available': False}
        else:
            arm_status = {'available': False, 'mock': True}
        
        status = {
            'timestamp': int(time.time()),
            'robot': {
                'mode': 'manual',
                'is_active': motor_status.get('is_moving', False),
                'motors': motor_status
            },
            'sensors': sensor_data,
            'arm': arm_status,
            'battery': sensor_data.get('battery', {
                'percentage': 85,
                'voltage': 12.4,
                'charging': False
            })
        }
        
        return jsonify(status)
        
    except Exception as e:
        print(f"Control-Status-Fehler: {e}")
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

# ===== AI API =====
@bp.route('/api/ai/detect', methods=['POST'])
def detect_weeds():
    """Unkraut-Erkennung durchführen"""
    try:
        data = request.get_json() or {}
        
        weed_detector = get_hardware_module('ai')
        camera_manager = get_hardware_module('camera')
        
        if not weed_detector:
            # Mock-Erkennung mit realistischen Daten
            import random
            mock_detections = []
            
            # 70% Chance für Unkraut-Erkennung
            if random.random() > 0.3:
                num_weeds = random.randint(1, 3)
                for i in range(num_weeds):
                    mock_detections.append({
                        'class': 'weed',
                        'confidence': round(random.uniform(0.6, 0.95), 3),
                        'x': random.randint(50, 590),
                        'y': random.randint(50, 430),
                        'bbox': {
                            'x': random.randint(50, 500),
                            'y': random.randint(50, 380),
                            'width': random.randint(20, 80),
                            'height': random.randint(15, 60)
                        },
                        'species': random.choice(['dandelion', 'clover', 'unknown']),
                        'size': random.choice(['small', 'medium', 'large'])
                    })
            
            return jsonify({
                'detections': mock_detections,
                'count': len(mock_detections),
                'confidence': round(sum(d['confidence'] for d in mock_detections) / len(mock_detections), 3) if mock_detections else 0,
                'processing_time': round(random.uniform(0.08, 0.25), 3),
                'method': 'mock_detection',
                'image_size': {'width': 640, 'height': 480},
                'mock': True,
                'message': 'KI-Modul nicht verfügbar - Mock-Erkennung'
            })
        
        # Kamera-Frame holen
        frame_data = None
        if camera_manager:
            frame_data = camera_manager.get_frame()
        
        if frame_data and len(frame_data) > 1000:
            result = weed_detector.detect_from_bytes(frame_data)
            
            # Optional: Auto-Entfernung wenn Unkraut erkannt
            if result.get('detections') and len(result['detections']) > 0:
                detection = result['detections'][0]
                target_x = detection.get('x', 0)
                target_y = detection.get('y', 0)
                
                # Nur wenn Auto-Entfernung aktiviert ist
                auto_removal = data.get('auto_removal', False)
                if auto_removal:
                    robot_arm = get_hardware_module('robot_arm')
                    if robot_arm:
                        try:
                            threading.Thread(
                                target=robot_arm.weed_removal_sequence,
                                args=(target_x, target_y),
                                daemon=True
                            ).start()
                            result['arm_action'] = 'weed_removal_started'
                        except Exception as e:
                            result['arm_action'] = f'arm_error: {str(e)}'
                    else:
                        result['arm_action'] = 'arm_not_available'
            
            return jsonify(result)
        else:
            return jsonify({'error': 'Kein Kamera-Frame verfügbar'}), 400
            
    except Exception as e:
        print(f"AI-Detection-Fehler: {e}")
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

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
                system_stats = {
                    'cpu_usage': 25.0,
                    'memory_usage': 60.0,
                    'cpu_temperature': 42.0,
                    'uptime': 3600,
                    'error': str(e)
                }
        else:
            # Fallback System-Stats
            try:
                import psutil
                system_stats = {
                    'cpu_usage': psutil.cpu_percent(),
                    'memory_usage': psutil.virtual_memory().percent,
                    'cpu_temperature': 45.0,
                    'uptime': int(time.time() - psutil.boot_time()),
                    'fallback': True
                }
            except ImportError:
                system_stats = {
                    'cpu_usage': 25.0,
                    'memory_usage': 60.0,
                    'cpu_temperature': 42.0,
                    'uptime': 3600,
                    'mock': True
                }
        
        # Hardware-Verfügbarkeit prüfen
        hardware_status = {}
        
        # Kamera
        camera_manager = get_hardware_module('camera')
        hardware_status['camera_available'] = camera_manager is not None
        if camera_manager:
            try:
                camera_info = camera_manager.get_camera_info()
                hardware_status['camera_type'] = camera_info.get('type', 'unknown')
            except:
                hardware_status['camera_type'] = 'unknown'
        
        # Roboterarm
        robot_arm = get_hardware_module('robot_arm')
        if robot_arm:
            try:
                arm_info = robot_arm.get_arm_info()
                hardware_status['arm_available'] = arm_info['controller']['hardware_available']
                hardware_status['servo_count'] = arm_info['controller']['servo_count']
            except Exception as e:
                hardware_status['arm_available'] = False
                hardware_status['arm_error'] = str(e)
        else:
            hardware_status['arm_available'] = False
            hardware_status['arm_mock'] = True
        
        # GPIO
        try:
            import RPi.GPIO as GPIO
            hardware_status['gpio_available'] = True
        except ImportError:
            hardware_status['gpio_available'] = False
            hardware_status['mock_mode'] = True
        
        status = {
            'timestamp': int(time.time()),
            'system': system_stats,
            'hardware': hardware_status,
            'version': '1.0.0',
            'uptime_formatted': _format_uptime(system_stats.get('uptime', 0))
        }
        
        return jsonify(status)
        
    except Exception as e:
        print(f"System-Status-Fehler: {e}")
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500
# ===== GALERIE API =====
@bp.route('/api/gallery/images')
def get_gallery_images():
    """Liste aller aufgenommenen Bilder"""
    try:
        images_dir = "data/images"
        if not os.path.exists(images_dir):
            return jsonify({'images': [], 'count': 0})
        
        images = []
        for filename in os.listdir(images_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                filepath = os.path.join(images_dir, filename)
                if os.path.isfile(filepath):
                    stat = os.stat(filepath)
                    images.append({
                        'filename': filename,
                        'size': stat.st_size,
                        'created': stat.st_mtime,
                        'url': f'/api/gallery/image/{filename}'
                    })
        
        # Nach Erstelldatum sortieren (neueste zuerst)
        images.sort(key=lambda x: x['created'], reverse=True)
        
        return jsonify({
            'images': images,
            'count': len(images),
            'total_size': sum(img['size'] for img in images)
        })
        
    except Exception as e:
        print(f"Gallery-API-Fehler: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/gallery/image/<filename>')
def get_gallery_image(filename):
    """Einzelnes Bild aus der Galerie"""
    try:
        # Sicherheitscheck: Nur erlaubte Zeichen
        import re
        if not re.match(r'^[a-zA-Z0-9._-]+\.jpg$', filename):
            return jsonify({'error': 'Ungültiger Dateiname'}), 400
        
        filepath = os.path.join("data/images", filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'Datei nicht gefunden'}), 404
        
        return send_file(filepath, mimetype='image/jpeg')
        
    except Exception as e:
        print(f"Image-Serve-Fehler: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/gallery/download', methods=['POST'])
def download_images():
    """Alle Bilder als ZIP herunterladen"""
    try:
        images_dir = "data/images"
        if not os.path.exists(images_dir):
            return jsonify({'error': 'Keine Bilder gefunden'}), 404
        
        # Alle JPG-Dateien finden
        image_files = []
        for filename in os.listdir(images_dir):
            if filename.lower().endswith(('.jpg', '.jpeg')):
                filepath = os.path.join(images_dir, filename)
                if os.path.isfile(filepath):
                    image_files.append((filename, filepath))
        
        if not image_files:
            return jsonify({'error': 'Keine Bilder zum Download gefunden'}), 404
        
        # Temporäre ZIP-Datei erstellen
        temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        temp_zip.close()
        
        with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename, filepath in image_files:
                zipf.write(filepath, filename)
        
        print(f"📦 ZIP erstellt: {len(image_files)} Bilder, {os.path.getsize(temp_zip.name)} bytes")
        
        return send_file(
            temp_zip.name,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'unkraut_bilder_{int(time.time())}.zip'
        )
        
    except Exception as e:
        print(f"Download-Fehler: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/gallery/clear', methods=['POST'])
def clear_gallery():
    """Alle Bilder löschen"""
    try:
        images_dir = "data/images"
        if not os.path.exists(images_dir):
            return jsonify({'message': 'Keine Bilder vorhanden', 'deleted': 0})
        
        deleted_count = 0
        for filename in os.listdir(images_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                filepath = os.path.join(images_dir, filename)
                try:
                    os.remove(filepath)
                    deleted_count += 1
                    print(f"🗑️ Gelöscht: {filename}")
                except Exception as e:
                    print(f"❌ Löschen fehlgeschlagen {filename}: {e}")
        
        return jsonify({
            'message': f'{deleted_count} Bilder gelöscht',
            'deleted': deleted_count
        })
        
    except Exception as e:
        print(f"Clear-Gallery-Fehler: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/gallery/delete/<filename>', methods=['DELETE'])
def delete_single_image(filename):
    """Einzelnes Bild löschen"""
    try:
        # Sicherheitscheck
        import re
        if not re.match(r'^[a-zA-Z0-9._-]+\.jpg$', filename):
            return jsonify({'error': 'Ungültiger Dateiname'}), 400
        
        filepath = os.path.join("data/images", filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'Datei nicht gefunden'}), 404
        
        os.remove(filepath)
        print(f"🗑️ Einzelnes Bild gelöscht: {filename}")
        
        return jsonify({'message': f'Bild {filename} gelöscht'})
        
    except Exception as e:
        print(f"Delete-Single-Fehler: {e}")
        return jsonify({'error': str(e)}), 500

# ===== ERWEITERTE GALERIE API =====

@bp.route('/api/gallery/download-selected', methods=['POST'])
def download_selected_images():
    """Ausgewählte Bilder als ZIP herunterladen"""
    try:
        data = request.get_json()
        if not data or 'files' not in data:
            return jsonify({'error': 'Keine Dateien ausgewählt'}), 400
        
        selected_files = data['files']
        if not selected_files:
            return jsonify({'error': 'Leere Dateiliste'}), 400
        
        images_dir = "data/images"
        if not os.path.exists(images_dir):
            return jsonify({'error': 'Bilderverzeichnis nicht gefunden'}), 404
        
        # Prüfe ob alle Dateien existieren
        existing_files = []
        for filename in selected_files:
            # Sicherheitscheck
            if not re.match(r'^[a-zA-Z0-9._-]+\.jpg$', filename):
                continue
                
            filepath = os.path.join(images_dir, filename)
            if os.path.exists(filepath):
                existing_files.append((filename, filepath))
        
        if not existing_files:
            return jsonify({'error': 'Keine der ausgewählten Dateien gefunden'}), 404
        
        # Temporäre ZIP-Datei erstellen
        temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        temp_zip.close()
        
        with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename, filepath in existing_files:
                zipf.write(filepath, filename)
        
        print(f"📦 Bulk-ZIP erstellt: {len(existing_files)} Bilder, {os.path.getsize(temp_zip.name)} bytes")
        
        return send_file(
            temp_zip.name,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'ausgewaehlte_bilder_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
        )
        
    except Exception as e:
        print(f"Bulk-Download-Fehler: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/gallery/delete-selected', methods=['POST'])
def delete_selected_images():
    """Ausgewählte Bilder löschen"""
    try:
        data = request.get_json()
        if not data or 'files' not in data:
            return jsonify({'error': 'Keine Dateien ausgewählt'}), 400
        
        selected_files = data['files']
        if not selected_files:
            return jsonify({'error': 'Leere Dateiliste'}), 400
        
        images_dir = "data/images"
        if not os.path.exists(images_dir):
            return jsonify({'error': 'Bilderverzeichnis nicht gefunden'}), 404
        
        deleted_count = 0
        errors = []
        
        for filename in selected_files:
            try:
                # Sicherheitscheck
                if not re.match(r'^[a-zA-Z0-9._-]+\.jpg$', filename):
                    errors.append(f"Ungültiger Dateiname: {filename}")
                    continue
                
                filepath = os.path.join(images_dir, filename)
                
                if os.path.exists(filepath):
                    os.remove(filepath)
                    deleted_count += 1
                    print(f"🗑️ Bulk-Gelöscht: {filename}")
                else:
                    errors.append(f"Datei nicht gefunden: {filename}")
                    
            except Exception as e:
                errors.append(f"Fehler bei {filename}: {str(e)}")
                print(f"❌ Bulk-Löschen Fehler {filename}: {e}")
        
        result = {
            'deleted': deleted_count,
            'requested': len(selected_files),
            'errors': errors
        }
        
        if deleted_count > 0:
            result['message'] = f'{deleted_count} von {len(selected_files)} Bildern gelöscht'
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Bulk-Delete-Fehler: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/gallery/tag-images', methods=['POST'])
def tag_selected_images():
    """Ausgewählte Bilder taggen (Metadaten hinzufügen)"""
    try:
        data = request.get_json()
        if not data or 'files' not in data or 'tag' not in data:
            return jsonify({'error': 'Dateien und Tag erforderlich'}), 400
        
        selected_files = data['files']
        tag = data['tag'].strip()
        
        if not selected_files or not tag:
            return jsonify({'error': 'Leere Dateiliste oder Tag'}), 400
        
        images_dir = "data/images"
        metadata_dir = "data/metadata"
        os.makedirs(metadata_dir, exist_ok=True)
        
        tagged_count = 0
        errors = []
        
        for filename in selected_files:
            try:
                # Sicherheitscheck
                if not re.match(r'^[a-zA-Z0-9._-]+\.jpg$', filename):
                    errors.append(f"Ungültiger Dateiname: {filename}")
                    continue
                
                filepath = os.path.join(images_dir, filename)
                if not os.path.exists(filepath):
                    errors.append(f"Datei nicht gefunden: {filename}")
                    continue
                
                # Metadaten-Datei
                metadata_file = os.path.join(metadata_dir, f"{filename}.json")
                
                # Bestehende Metadaten laden oder neue erstellen
                metadata = {}
                if os.path.exists(metadata_file):
                    try:
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                    except:
                        metadata = {}
                
                # Tags hinzufügen
                if 'tags' not in metadata:
                    metadata['tags'] = []
                
                if tag not in metadata['tags']:
                    metadata['tags'].append(tag)
                
                metadata['last_tagged'] = datetime.now().isoformat()
                metadata['filename'] = filename
                
                # Metadaten speichern
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                
                tagged_count += 1
                print(f"🏷️ Getaggt: {filename} mit '{tag}'")
                
            except Exception as e:
                errors.append(f"Fehler bei {filename}: {str(e)}")
                print(f"❌ Tag-Fehler {filename}: {e}")
        
        result = {
            'tagged': tagged_count,
            'requested': len(selected_files),
            'tag': tag,
            'errors': errors
        }
        
        if tagged_count > 0:
            result['message'] = f'{tagged_count} Bilder mit "{tag}" getaggt'
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Tag-Fehler: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/gallery/images-enhanced')
def get_gallery_images_enhanced():
    """Erweiterte Bilderliste mit Metadaten und Filteroptionen"""
    try:
        # Filter-Parameter
        date_filter = request.args.get('date', 'all')
        size_filter = request.args.get('size', 'all')
        tag_filter = request.args.get('tag', 'all')
        sort_by = request.args.get('sort', 'date')  # date, size, name
        sort_order = request.args.get('order', 'desc')  # asc, desc
        
        images_dir = "data/images"
        metadata_dir = "data/metadata"
        
        if not os.path.exists(images_dir):
            return jsonify({'images': [], 'count': 0, 'filters_applied': {}})
        
        images = []
        for filename in os.listdir(images_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                filepath = os.path.join(images_dir, filename)
                if os.path.isfile(filepath):
                    stat = os.stat(filepath)
                    
                    # Basis-Info
                    image_info = {
                        'filename': filename,
                        'size': stat.st_size,
                        'created': stat.st_mtime,
                        'url': f'/api/gallery/image/{filename}',
                        'tags': []
                    }
                    
                    # Metadaten laden falls vorhanden
                    metadata_file = os.path.join(metadata_dir, f"{filename}.json")
                    if os.path.exists(metadata_file):
                        try:
                            with open(metadata_file, 'r', encoding='utf-8') as f:
                                metadata = json.load(f)
                                image_info['tags'] = metadata.get('tags', [])
                                image_info['metadata'] = metadata
                        except:
                            pass
                    
                    images.append(image_info)
        
        # Filter anwenden
        filtered_images = self._apply_filters(images, date_filter, size_filter, tag_filter)
        
        # Sortierung
        if sort_by == 'date':
            filtered_images.sort(key=lambda x: x['created'], reverse=(sort_order == 'desc'))
        elif sort_by == 'size':
            filtered_images.sort(key=lambda x: x['size'], reverse=(sort_order == 'desc'))
        elif sort_by == 'name':
            filtered_images.sort(key=lambda x: x['filename'], reverse=(sort_order == 'desc'))
        
        # Statistiken
        total_size = sum(img['size'] for img in filtered_images)
        unique_tags = set()
        for img in filtered_images:
            unique_tags.update(img['tags'])
        
        return jsonify({
            'images': filtered_images,
            'count': len(filtered_images),
            'total_count': len(images),
            'total_size': total_size,
            'unique_tags': list(unique_tags),
            'filters_applied': {
                'date': date_filter,
                'size': size_filter,
                'tag': tag_filter,
                'sort_by': sort_by,
                'sort_order': sort_order
            }
        })
        
    except Exception as e:
        print(f"Enhanced-Gallery-API-Fehler: {e}")
        return jsonify({'error': str(e)}), 500

def _apply_filters(images, date_filter, size_filter, tag_filter):
    """Filter auf Bilderliste anwenden"""
    filtered = images.copy()
    
    # Datum-Filter
    if date_filter != 'all':
        now = time.time()
        if date_filter == 'today':
            cutoff = now - 24 * 60 * 60
        elif date_filter == 'week':
            cutoff = now - 7 * 24 * 60 * 60
        elif date_filter == 'month':
            cutoff = now - 30 * 24 * 60 * 60
        else:
            cutoff = 0
        
        filtered = [img for img in filtered if img['created'] >= cutoff]
    
    # Größen-Filter
    if size_filter != 'all':
        if size_filter == 'small':
            filtered = [img for img in filtered if img['size'] < 500 * 1024]
        elif size_filter == 'medium':
            filtered = [img for img in filtered if 500 * 1024 <= img['size'] < 2 * 1024 * 1024]
        elif size_filter == 'large':
            filtered = [img for img in filtered if img['size'] >= 2 * 1024 * 1024]
    
    # Tag-Filter
    if tag_filter != 'all':
        filtered = [img for img in filtered if tag_filter in img['tags']]
    
    return filtered

@bp.route('/api/gallery/stats')
def get_gallery_stats():
    """Galerie-Statistiken für Dashboard"""
    try:
        images_dir = "data/images"
        metadata_dir = "data/metadata"
        
        if not os.path.exists(images_dir):
            return jsonify({'error': 'Bilderverzeichnis nicht gefunden'}), 404
        
        total_images = 0
        total_size = 0
        oldest_date = None
        newest_date = None
        all_tags = set()
        
        for filename in os.listdir(images_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                filepath = os.path.join(images_dir, filename)
                if os.path.isfile(filepath):
                    stat = os.stat(filepath)
                    total_images += 1
                    total_size += stat.st_size
                    
                    # Datum-Range
                    if oldest_date is None or stat.st_mtime < oldest_date:
                        oldest_date = stat.st_mtime
                    if newest_date is None or stat.st_mtime > newest_date:
                        newest_date = stat.st_mtime
                    
                    # Tags sammeln
                    metadata_file = os.path.join(metadata_dir, f"{filename}.json")
                    if os.path.exists(metadata_file):
                        try:
                            with open(metadata_file, 'r', encoding='utf-8') as f:
                                metadata = json.load(f)
                                all_tags.update(metadata.get('tags', []))
                        except:
                            pass
        
        # Heute aufgenommen
        today_start = time.time() - 24 * 60 * 60
        today_count = 0
        
        for filename in os.listdir(images_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                filepath = os.path.join(images_dir, filename)
                if os.path.isfile(filepath):
                    stat = os.stat(filepath)
                    if stat.st_mtime >= today_start:
                        today_count += 1
        
        return jsonify({
            'total_images': total_images,
            'total_size': total_size,
            'today_count': today_count,
            'oldest_date': oldest_date,
            'newest_date': newest_date,
            'unique_tags': list(all_tags),
            'tag_count': len(all_tags),
            'average_size': total_size / total_images if total_images > 0 else 0
        })
        
    except Exception as e:
        print(f"Gallery-Stats-Fehler: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/gallery/cleanup', methods=['POST'])
def cleanup_gallery():
    """Galerie aufräumen - alte/große Dateien entfernen"""
    try:
        data = request.get_json() or {}
        
        # Cleanup-Optionen
        days_old = data.get('days_old', 30)  # Älter als X Tage
        max_size_mb = data.get('max_size_mb', 10)  # Größer als X MB
        keep_tagged = data.get('keep_tagged', True)  # Getaggte Bilder behalten
        dry_run = data.get('dry_run', True)  # Testlauf ohne echtes Löschen
        
        images_dir = "data/images"
        metadata_dir = "data/metadata"
        
        if not os.path.exists(images_dir):
            return jsonify({'error': 'Bilderverzeichnis nicht gefunden'}), 404
        
        cutoff_time = time.time() - (days_old * 24 * 60 * 60)
        max_size_bytes = max_size_mb * 1024 * 1024
        
        candidates_for_deletion = []
        
        for filename in os.listdir(images_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                filepath = os.path.join(images_dir, filename)
                if os.path.isfile(filepath):
                    stat = os.stat(filepath)
                    
                    # Prüfe Alter und Größe
                    too_old = stat.st_mtime < cutoff_time
                    too_large = stat.st_size > max_size_bytes
                    
                    if too_old or too_large:
                        # Prüfe ob getaggt (falls keep_tagged=True)
                        is_tagged = False
                        if keep_tagged:
                            metadata_file = os.path.join(metadata_dir, f"{filename}.json")
                            if os.path.exists(metadata_file):
                                try:
                                    with open(metadata_file, 'r', encoding='utf-8') as f:
                                        metadata = json.load(f)
                                        is_tagged = len(metadata.get('tags', [])) > 0
                                except:
                                    pass
                        
                        if not (keep_tagged and is_tagged):
                            candidates_for_deletion.append({
                                'filename': filename,
                                'size': stat.st_size,
                                'age_days': (time.time() - stat.st_mtime) / (24 * 60 * 60),
                                'reason': 'alt' if too_old else 'groß',
                                'is_tagged': is_tagged
                            })
        
        # Löschen (falls nicht Testlauf)
        deleted_count = 0
        freed_space = 0
        
        if not dry_run:
            for item in candidates_for_deletion:
                try:
                    filepath = os.path.join(images_dir, item['filename'])
                    if os.path.exists(filepath):
                        os.remove(filepath)
                        deleted_count += 1
                        freed_space += item['size']
                        
                        # Metadaten-Datei auch löschen
                        metadata_file = os.path.join(metadata_dir, f"{item['filename']}.json")
                        if os.path.exists(metadata_file):
                            os.remove(metadata_file)
                        
                        print(f"🧹 Cleanup: {item['filename']} gelöscht ({item['reason']})")
                        
                except Exception as e:
                    print(f"❌ Cleanup-Fehler {item['filename']}: {e}")
        
        return jsonify({
            'candidates': candidates_for_deletion,
            'candidate_count': len(candidates_for_deletion),
            'deleted_count': deleted_count,
            'freed_space': freed_space,
            'dry_run': dry_run,
            'settings': {
                'days_old': days_old,
                'max_size_mb': max_size_mb,
                'keep_tagged': keep_tagged
            }
        })
        
    except Exception as e:
        print(f"Cleanup-Fehler: {e}")
        return jsonify({'error': str(e)}), 500
        
def _format_uptime(seconds):
    """Uptime in menschenlesbares Format"""
    try:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    except:
        return "Unbekannt"