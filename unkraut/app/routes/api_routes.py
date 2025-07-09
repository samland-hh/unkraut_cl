# app/routes/api_routes.py
"""
API Routes mit Debug-Terminal-Logging (CLEAN VERSION)
Keine doppelten Funktionen!
"""
from flask import Blueprint, jsonify, request, Response, send_file
from datetime import datetime
from functools import wraps
import threading
import time
import traceback
import os
import zipfile
import tempfile  # ← DIESER IMPORT FEHLTE!
import json
import re


# Einmalige Pfad-Berechnung
def get_project_root():
    """Finde das Projekt-Root-Verzeichnis (unkraut/)"""
    current_file = os.path.abspath(__file__)  # /home/jan/.../unkraut/app/routes/api_routes.py
    
    # Gehe hoch bis wir das unkraut-Verzeichnis finden
    path = current_file
    while path != '/':
        path = os.path.dirname(path)
        if os.path.basename(path) == 'unkraut':
            return path
    
    # Fallback: 3 Verzeichnisse hoch von app/routes/
    return os.path.dirname(os.path.dirname(os.path.dirname(current_file)))

PROJECT_ROOT = get_project_root()
IMAGES_DIR = os.path.join(PROJECT_ROOT, 'data', 'images')


bp = Blueprint('api', __name__)

# ===== DEBUG LOGGING SYSTEM =====
def debug_log(message, level="INFO", source="API"):
    """Einheitliche Debug-Ausgabe auf Terminal"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    thread_id = threading.current_thread().ident % 10000
    
    level_colors = {
        "INFO": "\033[36m",    # Cyan
        "TOUCH": "\033[93m",   # Gelb
        "ERROR": "\033[91m",   # Rot  
        "SUCCESS": "\033[92m", # Grün
        "MOBILE": "\033[95m",  # Magenta
        "CAMERA": "\033[94m"   # Blau
    }
    
    color = level_colors.get(level, "\033[0m")
    reset = "\033[0m"
    
    print(f"{color}[{timestamp}] [{level:6}] [{source:8}] [T:{thread_id}] {message}{reset}")

def log_request_details(endpoint_name):
    """Decorator für detailliertes Request-Logging"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            # Request-Details loggen
            debug_log(f"🔍 {endpoint_name} - Start", "INFO", "REQUEST")
            debug_log(f"   Method: {request.method}", "INFO", "REQUEST")
            debug_log(f"   Path: {request.path}", "INFO", "REQUEST")
            debug_log(f"   Remote-IP: {request.remote_addr}", "INFO", "REQUEST")
            
            # User-Agent analysieren
            user_agent = request.headers.get('User-Agent', 'Unknown')
            if 'Mobile' in user_agent or 'Android' in user_agent or 'iPhone' in user_agent:
                debug_log(f"📱 MOBILE REQUEST: {user_agent[:50]}...", "MOBILE", "DEVICE")
            else:
                debug_log(f"💻 DESKTOP REQUEST: {user_agent[:30]}...", "INFO", "DEVICE")
            
            # JSON-Body loggen falls vorhanden
            if request.is_json:
                try:
                    body = request.get_json()
                    debug_log(f"   JSON-Body: {json.dumps(body)[:100]}...", "INFO", "REQUEST")
                except:
                    debug_log(f"   JSON-Body: Parse-Fehler", "ERROR", "REQUEST")
            
            try:
                # Endpoint ausführen
                result = func(*args, **kwargs)
                
                duration = (time.time() - start_time) * 1000
                debug_log(f"✅ {endpoint_name} - Erfolgreich ({duration:.1f}ms)", "SUCCESS", "RESPONSE")
                
                return result
                
            except Exception as e:
                duration = (time.time() - start_time) * 1000
                debug_log(f"❌ {endpoint_name} - Fehler ({duration:.1f}ms)", "ERROR", "RESPONSE")
                debug_log(f"   Exception: {str(e)}", "ERROR", "RESPONSE")
                debug_log(f"   Traceback: {traceback.format_exc()}", "ERROR", "RESPONSE")
                
                return jsonify({'error': str(e)}), 500
                
        return wrapper
    return decorator

# ===== HARDWARE MODULE LOADER =====
_hardware_cache = {}

def get_hardware_module(module_type):
    """Hardware-Module mit Caching und Error-Handling laden"""
    
    if module_type in _hardware_cache:
        return _hardware_cache[module_type]
    
    debug_log(f"🔧 Lade Hardware-Modul: {module_type}", "INFO", "HARDWARE")
    
    try:
        if module_type == 'camera':
            from hardware.camera import camera_manager
            _hardware_cache[module_type] = camera_manager
            debug_log(f"✅ camera_manager geladen", "SUCCESS", "HARDWARE")
        elif module_type == 'robot_arm':
            from hardware.robot_arm import robot_arm
            _hardware_cache[module_type] = robot_arm
            debug_log(f"✅ robot_arm geladen", "SUCCESS", "HARDWARE")
        elif module_type == 'motors':
            from hardware.motors import motor_controller
            _hardware_cache[module_type] = motor_controller
            debug_log(f"✅ motor_controller geladen", "SUCCESS", "HARDWARE")
        elif module_type == 'sensors':
            from hardware.sensors import sensor_manager
            _hardware_cache[module_type] = sensor_manager
            debug_log(f"✅ sensor_manager geladen", "SUCCESS", "HARDWARE")
        else:
            debug_log(f"❌ Unbekannter Hardware-Typ: {module_type}", "ERROR", "HARDWARE")
            return None
            
        return _hardware_cache[module_type]
        
    except ImportError as e:
        debug_log(f"❌ Hardware-Import fehlgeschlagen: {module_type} - {e}", "ERROR", "HARDWARE")
        _hardware_cache[module_type] = None
        return None
    except Exception as e:
        debug_log(f"❌ Hardware-Ladung fehlgeschlagen: {module_type} - {e}", "ERROR", "HARDWARE")
        _hardware_cache[module_type] = None
        return None

# ===== DEBUG API ENDPOINTS =====
@bp.route('/api/debug/log', methods=['POST'])
def browser_log():
    """Empfängt Browser-Logs und gibt sie auf Terminal aus"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'no_data'}), 400
            
        level = data.get('level', 'INFO').upper()
        message = data.get('message', 'Keine Nachricht')
        source = data.get('source', 'BROWSER')
        extra = data.get('extra', {})
        
        # Browser-Log auf Terminal ausgeben
        debug_log(f"🌐 {message}", level, source)
        
        # Extra-Daten falls vorhanden
        for key, value in extra.items():
            if key not in ['sessionId', 'timestamp', 'url']:  # Spam vermeiden
                debug_log(f"   {key}: {str(value)[:50]}...", level, source)
            
        return jsonify({'status': 'logged'})
        
    except Exception as e:
        debug_log(f"Browser-Log Fehler: {e}", "ERROR", "DEBUG")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/debug/touch', methods=['POST'])
def touch_event():
    """Spezielle Touch-Event-Logs für Mobile-Debugging"""
    try:
        data = request.get_json()
        
        event_type = data.get('type', 'unknown')
        element = data.get('element', 'unknown')
        coordinates = data.get('coordinates', {})
        
        debug_log(f"👆 TOUCH {event_type.upper()}: {element[:50]}...", "TOUCH", "MOBILE")
        
        if coordinates:
            x, y = coordinates.get('x', 0), coordinates.get('y', 0)
            debug_log(f"   📍 Position: ({x}, {y})", "TOUCH", "MOBILE")
            
        # Spezielle Behandlung für wichtige Buttons
        if any(keyword in element.lower() for keyword in ['foto', 'capture', '📸']):
            debug_log(f"📸 FOTO-BUTTON Touch erkannt!", "CAMERA", "MOBILE")
            
        return jsonify({'status': 'touch_logged'})
        
    except Exception as e:
        debug_log(f"Touch-Event Fehler: {e}", "ERROR", "TOUCH")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/debug/status')
def debug_status():
    """Debug-Status Endpoint"""
    debug_log("🔍 Debug-Status abgerufen", "INFO", "DEBUG")
    
    return jsonify({
        'debug_mode': True,
        'timestamp': datetime.now().isoformat(),
        'logging': {
            'terminal_logging': True,
            'mobile_debugging': True,
            'touch_events': True,
            'api_tracing': True
        },
        'device_info': {
            'user_agent': request.headers.get('User-Agent', 'Unknown'),
            'remote_ip': request.remote_addr,
            'is_mobile': 'Mobile' in request.headers.get('User-Agent', '')
        }
    })

# ===== KAMERA API MIT DEBUG =====
@bp.route('/api/camera/stream')
def video_stream():
    """Kamera Video-Stream mit Debug-Logging"""
    debug_log("📹 Stream-Anfrage erhalten", "CAMERA", "STREAM")
    
    try:
        camera_manager = get_hardware_module('camera')
        if not camera_manager:
            debug_log("❌ Kamera-Hardware nicht verfügbar - Dummy-Stream", "ERROR", "STREAM")
            return create_dummy_stream()
            
        def generate():
            debug_log("📹 Stream-Generator gestartet", "CAMERA", "STREAM")
            frame_count = 0
            
            try:
                if not camera_manager.is_streaming:
                    debug_log("🔄 Starte Kamera-Stream...", "CAMERA", "STREAM")
                    camera_manager.start_stream()
                
                while True:
                    frame = camera_manager.get_frame()
                    if frame:
                        frame_count += 1
                        if frame_count % 30 == 0:  # Alle Sekunde loggen
                            debug_log(f"📹 Frame #{frame_count} ({len(frame)} bytes)", "CAMERA", "STREAM")
                        
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                    else:
                        debug_log("⚠️ Kein Frame verfügbar", "ERROR", "STREAM")
                        
                    time.sleep(0.033)  # ~30 FPS
                    
            except Exception as e:
                debug_log(f"❌ Stream-Generator Fehler: {e}", "ERROR", "STREAM")
                
        return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')
        
    except Exception as e:

        return create_dummy_stream()

def create_dummy_stream():
    """Dummy-Stream wenn Kamera nicht verfügbar"""
    import cv2
    import numpy as np
    
    def generate_dummy():
        debug_log("🔄 Dummy-Stream gestartet", "CAMERA", "DUMMY")
        
        while True:
            # Dummy-Frame erstellen
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(frame, 'Kamera nicht verfügbar', (160, 240), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(frame, f'{datetime.now().strftime("%H:%M:%S")}', (250, 280), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(0.1)
    
    return Response(generate_dummy(), mimetype='multipart/x-mixed-replace; boundary=frame')

@bp.route('/api/camera/capture', methods=['POST'])
@log_request_details("FOTO_AUFNAHME")
def capture_image():
    """Kamera-Capture mit umfassendem Debug-Logging"""
    
    debug_log("📸 FOTO-AUFNAHME GESTARTET", "CAMERA", "CAPTURE")
    
    try:
        # JSON-Body parsen falls vorhanden
        filename = None
        if request.is_json:
            data = request.get_json()
            filename = data.get('filename')
            debug_log(f"   📝 Gewünschter Dateiname: {filename}", "CAMERA", "CAPTURE")
        
        # Kamera-Modul laden
        debug_log("   🔧 Lade Kamera-Modul...", "CAMERA", "CAPTURE")
        camera_manager = get_hardware_module('camera')
        
        if not camera_manager:
            debug_log("   ❌ Kamera-Hardware nicht verfügbar - Mock-Modus", "ERROR", "CAPTURE")
            
            # Mock-Response für Tests
            timestamp = int(time.time())
            mock_filename = f"mock_capture_{timestamp}.jpg"
            debug_log(f"   📁 Mock-Datei erstellt: {mock_filename}", "CAMERA", "CAPTURE")
            
            return jsonify({
                'status': 'captured',
                'filename': mock_filename,
                'mock': True,
                'message': 'Mock-Aufnahme (Hardware nicht verfügbar)'
            })
        
        # Kamera-Status prüfen
        debug_log("   🔍 Prüfe Kamera-Status...", "CAMERA", "CAPTURE")
        camera_info = camera_manager.get_camera_info()
        debug_log(f"   📊 Typ: {camera_info.get('type', 'unknown')}, Verfügbar: {camera_info.get('available', False)}", "CAMERA", "CAPTURE")
        
        # Stream-Status prüfen
        if not camera_manager.is_streaming:
            debug_log("   ⚠️ Stream nicht aktiv - starte...", "CAMERA", "CAPTURE")
            if camera_manager.start_stream():
                debug_log("   ✅ Stream erfolgreich gestartet", "SUCCESS", "CAPTURE")
            else:
                debug_log("   ❌ Stream-Start fehlgeschlagen", "ERROR", "CAPTURE")
        else:
            debug_log("   ✅ Stream bereits aktiv", "SUCCESS", "CAPTURE")
        
        # Foto aufnehmen
        debug_log("   📸 Nehme Foto auf...", "CAMERA", "CAPTURE")
        result_filename = camera_manager.capture_image(filename)
        
        if result_filename:
            debug_log(f"   ✅ FOTO ERFOLGREICH: {result_filename}", "SUCCESS", "CAPTURE")
            
            # Datei-Info sammeln
            try:
                file_path = os.path.join("data", "images", result_filename)
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    debug_log(f"   📁 Dateigröße: {file_size:,} bytes ({file_size/1024:.1f} KB)", "CAMERA", "CAPTURE")
                else:
                    debug_log(f"   ⚠️ Datei nicht gefunden: {file_path}", "ERROR", "CAPTURE")
            except Exception as e:
                debug_log(f"   ⚠️ Datei-Info Fehler: {e}", "ERROR", "CAPTURE")
            
            debug_log("🎉 FOTO-AUFNAHME KOMPLETT ERFOLGREICH!", "SUCCESS", "CAPTURE")
            
            return jsonify({
                'status': 'captured',
                'filename': result_filename,
                'mock': False,
                'message': 'Foto erfolgreich aufgenommen',
                'timestamp': datetime.now().isoformat()
            })
        else:
            debug_log("   ❌ FOTO-AUFNAHME FEHLGESCHLAGEN", "ERROR", "CAPTURE")
            return jsonify({
                'status': 'failed',
                'error': 'Capture fehlgeschlagen',
                'message': 'Kamera konnte kein Foto aufnehmen'
            }), 500
            
    except Exception as e:
        debug_log(f"💥 KRITISCHER FEHLER BEI FOTO-AUFNAHME: {str(e)}", "ERROR", "CAPTURE")
        debug_log(f"   📋 Traceback: {traceback.format_exc()}", "ERROR", "CAPTURE")
        
        return jsonify({
            'status': 'error',
            'error': str(e),
            'message': 'Unerwarteter Fehler bei Foto-Aufnahme'
        }), 500

# ===== SYSTEM API =====
@bp.route('/api/system/status')
@log_request_details("SYSTEM_STATUS")
def system_status():
    """System-Status mit Debug-Logging"""
    
    try:
        debug_log("📊 System-Status wird gesammelt...", "INFO", "SYSTEM")
        
        # Hardware-Status prüfen
        camera_available = get_hardware_module('camera') is not None
        arm_available = get_hardware_module('robot_arm') is not None
        motor_available = get_hardware_module('motors') is not None
        sensors_available = get_hardware_module('sensors') is not None
        
        debug_log(f"🔧 Hardware: Kamera={camera_available}, Arm={arm_available}, Motor={motor_available}, Sensoren={sensors_available}", "INFO", "SYSTEM")
        
        status = {
            'system': {
                'cpu_usage': 25.0,
                'memory_usage': 45.0,
                'cpu_temperature': 42.5,
                'uptime': '2d 3h 15m'
            },
            'hardware': {
                'camera_available': camera_available,
                'arm_available': arm_available,
                'motor_available': motor_available,
                'sensors_available': sensors_available
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(status)
        
    except Exception as e:
        debug_log(f"System-Status Fehler: {e}", "ERROR", "SYSTEM")
        return jsonify({'error': str(e)}), 500

# ===== TOUCH-TEST SEITE =====
@bp.route('/touch_test')
def touch_test():
    """Touch-Test Seite für Mobile Debugging"""
    debug_log("🧪 Touch-Test Seite aufgerufen", "INFO", "TOUCHTEST")
    
    return """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🔍 Mobile Touch Test</title><style>
body{font-family:Arial,sans-serif;padding:20px;background:#222;color:white;text-align:center}
.btn{background:#28a745;color:white;border:none;padding:20px 40px;font-size:18px;border-radius:10px;margin:15px auto;display:block;width:80%;max-width:300px;cursor:pointer;user-select:none}
.btn:active{background:#1e7e34;transform:scale(0.95)}
.log{background:#333;padding:15px;border-radius:5px;margin:15px 0;font-family:monospace;text-align:left;height:250px;overflow-y:auto;font-size:12px}
.info{background:#444;padding:10px;border-radius:5px;margin:10px 0;font-size:14px}
</style></head><body>

<h1>🔍 Mobile Touch Test</h1>

<div class="info">
<strong>User-Agent:</strong> <span id="user-agent"></span><br>
<strong>Touch Support:</strong> <span id="touch-support"></span><br>
<strong>Viewport:</strong> <span id="viewport"></span>
</div>

<button class="btn" id="btn1">📱 TEST 1: Touch Events</button>
<button class="btn" id="btn2">📸 TEST 2: Foto Capture</button>
<button class="btn" id="btn3">🌐 TEST 3: API Status</button>

<div class="log" id="log"></div>

<script>
let logCount = 0;

function log(message) {
    logCount++;
    const logDiv = document.getElementById('log');
    const time = new Date().toLocaleTimeString();
    logDiv.innerHTML += `[${time}] ${logCount}: ${message}<br>`;
    logDiv.scrollTop = logDiv.scrollHeight;
    
    // An Python Terminal senden
    fetch('/api/debug/log', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            level: 'INFO',
            message: message,
            source: 'TOUCHTEST'
        })
    }).catch(e => console.warn('Debug-Log failed:', e));
}

// Gerät-Info
document.getElementById('user-agent').textContent = navigator.userAgent.substring(0, 60) + '...';
document.getElementById('touch-support').textContent = 'ontouchstart' in window ? '✅ JA' : '❌ NEIN';
document.getElementById('viewport').textContent = window.innerWidth + 'x' + window.innerHeight;

log('🔍 Touch-Test gestartet');
log('📱 Mobile Device: ' + (/Mobile|Android|iPhone|iPad/i.test(navigator.userAgent) ? 'JA' : 'NEIN'));
log('👆 Touch Support: ' + ('ontouchstart' in window ? 'JA' : 'NEIN'));

// TEST 1: Touch Events
const btn1 = document.getElementById('btn1');
btn1.addEventListener('touchstart', function(e) {
    log('✅ TEST 1: touchstart erkannt!');
    e.preventDefault();
}, {passive: false});

btn1.addEventListener('click', function(e) {
    log('✅ TEST 1: click erkannt!');
});

// TEST 2: Foto Capture
const btn2 = document.getElementById('btn2');
btn2.addEventListener('touchstart', function(e) {
    log('📸 TEST 2: Foto touchstart');
    e.preventDefault();
    testCapture();
}, {passive: false});

btn2.addEventListener('click', function(e) {
    log('📸 TEST 2: Foto click');
    testCapture();
});

function testCapture() {
    log('📸 Starte Foto-Test...');
    
    fetch('/api/camera/capture', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({filename: 'touch_test.jpg'})
    })
    .then(response => response.json())
    .then(data => {
        if (data.filename) {
            log('✅ FOTO ERFOLGREICH: ' + data.filename);
        } else {
            log('❌ Foto fehlgeschlagen: ' + JSON.stringify(data));
        }
    })
    .catch(error => {
        log('❌ Foto-Fehler: ' + error.message);
    });
}

// TEST 3: API Status
const btn3 = document.getElementById('btn3');
btn3.addEventListener('touchstart', function(e) {
    log('🌐 TEST 3: API touchstart');
    e.preventDefault();
    testAPI();
}, {passive: false});

btn3.addEventListener('click', function(e) {
    log('🌐 TEST 3: API click');
    testAPI();
});

function testAPI() {
    log('🌐 Teste API-Status...');
    
    fetch('/api/debug/status')
    .then(response => response.json())
    .then(data => {
        log('✅ API-Status OK: debug_mode=' + data.debug_mode);
    })
    .catch(error => {
        log('❌ API-Fehler: ' + error.message);
    });
}

// Global Touch Logging
document.addEventListener('touchstart', function(e) {
    const target = e.target.tagName + (e.target.className ? '.' + e.target.className : '');
    log('👆 Global touchstart: ' + target);
}, {passive: true});

</script></body></html>"""

# ===== HEALTH CHECK =====
@bp.route('/api/health')
def health():
    debug_log("💓 Health-Check", "INFO", "HEALTH")
    return jsonify({
        'status': 'healthy', 
        'timestamp': datetime.now().isoformat(),
        'debug': True
    })
# FÜGE DAS ZU DEINER api_routes.py HINZU:

@bp.route('/camera_com')
def camera_complete():
    """Komplette Kamera-Seite mit sauber getrennten HTML/CSS/JS Dateien"""
    debug_log("🧪 Komplette Kamera-Seite aufgerufen (getrennte Dateien)", "INFO", "TEST")
    from flask import render_template
    return render_template('camera_complete.html')

# ===== Camera minimal =====
@bp.route('/camera_test')
def camera_test():
    """Test-Seite für getrennte HTML/CSS/JS Dateien"""
    debug_log("🧪 Kamera-Test Seite aufgerufen (getrennte Dateien)", "INFO", "TEST")
    from flask import render_template
    return render_template('camera_minimal.html')

# ERSETZE die Galerie-Funktionen in deiner api_routes.py mit diesen korrigierten Pfaden:

# ===== GALERIE API (KORRIGIERTE PFADE) =====
@bp.route('/api/camera/images')
def get_images():
    """Liste aller Bilder"""
    try:
        debug_log(f"🔍 Suche Bilder in: {IMAGES_DIR}", "INFO", "GALLERY")
        
        # Verzeichnis erstellen falls nicht vorhanden
        os.makedirs(IMAGES_DIR, exist_ok=True)
        
        images = []
        total_size = 0
        
        if os.path.exists(IMAGES_DIR):
            for filename in os.listdir(IMAGES_DIR):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    file_path = os.path.join(IMAGES_DIR, filename)
                    try:
                        file_size = os.path.getsize(file_path)
                        file_time = os.path.getmtime(file_path)
                        
                        images.append({
                            'filename': filename,
                            'size': file_size,
                            'timestamp': file_time
                        })
                        total_size += file_size
                        
                    except OSError:
                        continue
        
        # Nach Zeit sortieren (neueste zuerst)
        images.sort(key=lambda x: x['timestamp'], reverse=True)
        
        debug_log(f"📁 Galerie: {len(images)} Bilder gefunden", "INFO", "GALLERY")
        
        return jsonify({
            'images': images,
            'count': len(images),
            'total_size_mb': total_size / (1024 * 1024)
        })
        
    except Exception as e:
        debug_log(f"❌ Galerie-Fehler: {e}", "ERROR", "GALLERY")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/camera/image/<filename>')
def get_image(filename):
    """Einzelnes Bild abrufen"""
    try:
        from flask import send_file
        
        file_path = os.path.join(IMAGES_DIR, filename)
        
        debug_log(f"🖼️ Lade Bild: {file_path}", "INFO", "GALLERY")
        
        if not os.path.exists(file_path):
            debug_log(f"❌ Datei nicht gefunden: {file_path}", "ERROR", "GALLERY")
            return "Datei nicht gefunden", 404
            
        return send_file(file_path)
        
    except Exception as e:
        debug_log(f"❌ Bild-Fehler: {e}", "ERROR", "GALLERY")
        return str(e), 500

@bp.route('/api/camera/image/<filename>', methods=['DELETE'])
def delete_image(filename):
    """Bild löschen"""
    try:
        file_path = os.path.join(IMAGES_DIR, filename)
        
        debug_log(f"🗑️ Lösche Bild: {file_path}", "INFO", "GALLERY")
        
        if os.path.exists(file_path):
            os.remove(file_path)
            debug_log(f"✅ Bild gelöscht: {filename}", "SUCCESS", "GALLERY")
            return jsonify({'status': 'deleted', 'filename': filename})
        else:
            debug_log(f"❌ Datei nicht gefunden: {file_path}", "ERROR", "GALLERY")
            return jsonify({'error': 'Datei nicht gefunden'}), 404
            
    except Exception as e:
        debug_log(f"❌ Lösch-Fehler: {e}", "ERROR", "GALLERY")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/camera/images/clear', methods=['POST'])
def clear_images():
    """Alle Bilder löschen"""
    try:
        debug_log(f"🗑️ Lösche alle Bilder in: {IMAGES_DIR}", "INFO", "GALLERY")
        
        deleted_count = 0
        
        if os.path.exists(IMAGES_DIR):
            for filename in os.listdir(IMAGES_DIR):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    file_path = os.path.join(IMAGES_DIR, filename)
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                    except OSError:
                        continue
        
        debug_log(f"✅ {deleted_count} Bilder gelöscht", "SUCCESS", "GALLERY")
        return jsonify({'status': 'cleared', 'deleted_count': deleted_count})
        
    except Exception as e:
        debug_log(f"❌ Clear-Fehler: {e}", "ERROR", "GALLERY")
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

# Startup-Message
debug_log("🚀 SAUBERE API ROUTES GELADEN - Terminal Logging aktiv!", "SUCCESS", "STARTUP")
debug_log(f"📡 Verfügbare Endpoints:", "INFO", "STARTUP")
debug_log(f"   GET  /api/debug/status - Debug-Info", "INFO", "STARTUP")
debug_log(f"   POST /api/debug/log - Browser-Logs", "INFO", "STARTUP")
debug_log(f"   POST /api/debug/touch - Touch-Events", "INFO", "STARTUP")
debug_log(f"   POST /api/camera/capture - Foto mit Debug", "INFO", "STARTUP")
debug_log(f"   GET  /api/camera/stream - Stream mit Debug", "INFO", "STARTUP")
debug_log(f"   GET  /api/system/status - Status mit Debug", "INFO", "STARTUP")
debug_log(f"   GET  /touch_test - Touch-Test Seite", "INFO", "STARTUP")