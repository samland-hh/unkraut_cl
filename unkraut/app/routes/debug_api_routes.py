# app/routes/debug_api_routes.py
"""
Debug API Routes mit umfassendem Terminal-Logging
Alle Mobile Touch Events und API-Calls werden auf Terminal ausgegeben
"""
from flask import Blueprint, request, jsonify, Response
import datetime
import time
import json
import traceback
import threading
from functools import wraps

bp = Blueprint('debug_api', __name__)

# Terminal Logging Funktionen
def debug_log(message, level="INFO", source="API"):
    """Einheitliche Debug-Ausgabe auf Terminal"""
    timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
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
            debug_log(f"   URL: {request.url}", "INFO", "REQUEST")
            debug_log(f"   User-Agent: {request.headers.get('User-Agent', 'Unknown')[:50]}", "INFO", "REQUEST")
            debug_log(f"   Remote-IP: {request.remote_addr}", "INFO", "REQUEST")
            
            # Content-Type check für Mobile
            if 'Mobile' in request.headers.get('User-Agent', ''):
                debug_log(f"📱 MOBILE REQUEST erkannt!", "MOBILE", "DEVICE")
            
            # JSON-Body loggen falls vorhanden
            if request.is_json:
                try:
                    body = request.get_json()
                    debug_log(f"   JSON-Body: {json.dumps(body, indent=2)}", "INFO", "REQUEST")
                except:
                    debug_log(f"   JSON-Body: Konnte nicht geparst werden", "ERROR", "REQUEST")
            
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

# Browser -> Python Terminal Logging
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
            debug_log(f"   {key}: {value}", level, source)
            
        return jsonify({'status': 'logged'})
        
    except Exception as e:
        debug_log(f"Browser-Log Fehler: {e}", "ERROR", "DEBUG")
        return jsonify({'error': str(e)}), 500

# Touch Event Logging
@bp.route('/api/debug/touch', methods=['POST'])
def touch_event():
    """Spezielle Touch-Event-Logs für Mobile-Debugging"""
    try:
        data = request.get_json()
        
        event_type = data.get('type', 'unknown')
        element = data.get('element', 'unknown')
        coordinates = data.get('coordinates', {})
        timestamp = data.get('timestamp', time.time())
        
        debug_log(f"👆 TOUCH {event_type.upper()}: {element}", "TOUCH", "MOBILE")
        
        if coordinates:
            x, y = coordinates.get('x', 0), coordinates.get('y', 0)
            debug_log(f"   Position: ({x}, {y})", "TOUCH", "MOBILE")
            
        # Spezielle Behandlung für Foto-Button
        if 'foto' in element.lower() or 'capture' in element.lower():
            debug_log(f"📸 FOTO-BUTTON Touch erkannt!", "CAMERA", "MOBILE")
            
        return jsonify({'status': 'touch_logged'})
        
    except Exception as e:
        debug_log(f"Touch-Event Fehler: {e}", "ERROR", "TOUCH")
        return jsonify({'error': str(e)}), 500

# KAMERA API mit Debug-Logging
@bp.route('/api/camera/capture', methods=['POST'])
@log_request_details("FOTO_AUFNAHME")
def capture_image_debug():
    """Kamera-Capture mit umfassendem Debug-Logging"""
    
    debug_log("📸 FOTO-AUFNAHME gestartet", "CAMERA", "CAPTURE")
    
    try:
        # JSON-Body parsen falls vorhanden
        filename = None
        if request.is_json:
            data = request.get_json()
            filename = data.get('filename')
            debug_log(f"   Gewünschter Dateiname: {filename}", "CAMERA", "CAPTURE")
        
        # Kamera-Modul laden
        debug_log("   Lade Kamera-Modul...", "CAMERA", "CAPTURE")
        
        try:
            from hardware.camera import camera_manager
            debug_log("   ✅ camera_manager erfolgreich importiert", "CAMERA", "CAPTURE")
        except ImportError as e:
            debug_log(f"   ❌ camera_manager Import-Fehler: {e}", "ERROR", "CAPTURE")
            debug_log("   🔄 Fallback auf Mock-Modus", "CAMERA", "CAPTURE")
            
            # Mock-Response
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
        debug_log("   Prüfe Kamera-Status...", "CAMERA", "CAPTURE")
        camera_info = camera_manager.get_camera_info()
        debug_log(f"   Kamera-Typ: {camera_info.get('type', 'unknown')}", "CAMERA", "CAPTURE")
        debug_log(f"   Verfügbar: {camera_info.get('available', False)}", "CAMERA", "CAPTURE")
        
        # Stream starten falls nötig
        if not camera_manager.is_streaming():
            debug_log("   Stream nicht aktiv - starte...", "CAMERA", "CAPTURE")
            if camera_manager.start_stream():
                debug_log("   ✅ Stream erfolgreich gestartet", "CAMERA", "CAPTURE")
            else:
                debug_log("   ❌ Stream-Start fehlgeschlagen", "ERROR", "CAPTURE")
        
        # Foto aufnehmen
        debug_log("   📸 Nehme Foto auf...", "CAMERA", "CAPTURE")
        result_filename = camera_manager.capture_image(filename)
        
        if result_filename:
            debug_log(f"   ✅ Foto erfolgreich: {result_filename}", "SUCCESS", "CAPTURE")
            
            # Datei-Info
            try:
                import os
                file_path = f"data/images/{result_filename}"
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    debug_log(f"   📁 Dateigröße: {file_size} bytes", "CAMERA", "CAPTURE")
                else:
                    debug_log(f"   ⚠️  Datei nicht gefunden: {file_path}", "ERROR", "CAPTURE")
            except Exception as e:
                debug_log(f"   ⚠️  Datei-Info Fehler: {e}", "ERROR", "CAPTURE")
            
            return jsonify({
                'status': 'captured',
                'filename': result_filename,
                'mock': False,
                'message': 'Foto erfolgreich aufgenommen'
            })
        else:
            debug_log("   ❌ Foto-Aufnahme fehlgeschlagen", "ERROR", "CAPTURE")
            return jsonify({
                'status': 'failed',
                'error': 'Capture fehlgeschlagen',
                'message': 'Kamera konnte kein Foto aufnehmen'
            }), 500
            
    except Exception as e:
        debug_log(f"❌ KRITISCHER FEHLER: {str(e)}", "ERROR", "CAPTURE")
        debug_log(f"   Traceback: {traceback.format_exc()}", "ERROR", "CAPTURE")
        
        return jsonify({
            'status': 'error',
            'error': str(e),
            'message': 'Unerwarteter Fehler bei Foto-Aufnahme'
        }), 500

# System-Status mit Debug-Logs
@bp.route('/api/system/status')
@log_request_details("SYSTEM_STATUS")
def system_status_debug():
    """System-Status mit Debug-Logging"""
    
    try:
        debug_log("📊 System-Status abgerufen", "INFO", "SYSTEM")
        
        status = {
            'system': {
                'cpu_usage': 25.0,
                'memory_usage': 45.0,
                'cpu_temperature': 42.5,
                'uptime': '2d 3h 15m'
            },
            'hardware': {
                'camera_available': True,
                'arm_available': True,
                'motor_available': True,
                'sensors_available': True
            },
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        return jsonify(status)
        
    except Exception as e:
        debug_log(f"System-Status Fehler: {e}", "ERROR", "SYSTEM")
        return jsonify({'error': str(e)}), 500

# Debug-Dashboard Endpoint
@bp.route('/api/debug/status')
def debug_status():
    """Debug-Status für Terminal-Übersicht"""
    
    try:
        import psutil
        import platform
        
        debug_info = {
            'debug_mode': True,
            'timestamp': datetime.datetime.now().isoformat(),
            'system': {
                'platform': platform.platform(),
                'python_version': platform.python_version(),
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'disk_usage': psutil.disk_usage('/').percent
            },
            'flask': {
                'debug': True,
                'testing': False,
                'threaded': True
            },
            'logging': {
                'terminal_logging': True,
                'mobile_debugging': True,
                'touch_events': True,
                'api_tracing': True
            }
        }
        
        debug_log("🔍 Debug-Status abgerufen", "INFO", "DEBUG")
        return jsonify(debug_info)
        
    except Exception as e:
        debug_log(f"Debug-Status Fehler: {e}", "ERROR", "DEBUG")
        return jsonify({'error': str(e)}), 500

# Startup-Log
debug_log("🚀 DEBUG API Routes geladen - Terminal Logging aktiv!", "SUCCESS", "STARTUP")