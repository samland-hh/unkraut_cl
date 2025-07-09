# debug_run.py
"""
Debug-Version für Unkraut-2025 mit umfassendem Terminal-Logging
Ersetzt run.py für Debug-Sessions
"""
import os
import sys
import datetime
import signal
import threading
import time

def debug_log(message, level="INFO"):
    """Debug-Ausgabe auf Terminal"""
    timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
    colors = {
        "INFO": "\033[36m",    # Cyan
        "SUCCESS": "\033[92m", # Grün
        "ERROR": "\033[91m",   # Rot
        "STARTUP": "\033[93m"  # Gelb
    }
    
    color = colors.get(level, "\033[0m")
    reset = "\033[0m"
    
    print(f"{color}[{timestamp}] [DEBUG] {message}{reset}")

def signal_handler(sig, frame):
    """Graceful Shutdown"""
    debug_log("🛑 SIGINT empfangen - Stoppe Server...", "INFO")
    sys.exit(0)

def check_project_structure():
    """Prüfe Projekt-Struktur"""
    debug_log("🔍 Prüfe Projekt-Struktur...", "INFO")
    
    required_dirs = [
        'app', 'app/routes', 'app/templates', 'app/static', 
        'hardware', 'data', 'data/images'
    ]
    
    missing_dirs = []
    for directory in required_dirs:
        if not os.path.exists(directory):
            missing_dirs.append(directory)
            debug_log(f"❌ Verzeichnis fehlt: {directory}", "ERROR")
        else:
            debug_log(f"✅ {directory}", "SUCCESS")
    
    if missing_dirs:
        debug_log(f"⚠️ {len(missing_dirs)} Verzeichnisse fehlen!", "ERROR")
        for directory in missing_dirs:
            os.makedirs(directory, exist_ok=True)
            debug_log(f"📁 Erstellt: {directory}", "SUCCESS")
    
    return len(missing_dirs) == 0

def check_dependencies():
    """Prüfe Python-Dependencies"""
    debug_log("🐍 Prüfe Python-Dependencies...", "INFO")
    
    required_modules = [
        'flask', 'cv2', 'numpy', 'psutil'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
            debug_log(f"✅ {module}", "SUCCESS")
        except ImportError:
            missing_modules.append(module)
            debug_log(f"❌ {module} - FEHLT", "ERROR")
    
    if missing_modules:
        debug_log(f"⚠️ Installiere fehlende Module:", "ERROR")
        for module in missing_modules:
            debug_log(f"   pip install {module}", "INFO")
        return False
    
    return True

def create_debug_app():
    """Flask-App mit Debug-Konfiguration erstellen"""
    debug_log("🚀 Erstelle Debug-Flask-App...", "STARTUP")
    
    try:
        from flask import Flask
        app = Flask(__name__)
        
        # Debug-Konfiguration
        app.config['DEBUG'] = True
        app.config['TESTING'] = False
        app.config['SECRET_KEY'] = 'debug-key-unkraut-2025'
        app.config['WTF_CSRF_ENABLED'] = False
        
        debug_log("✅ Flask-App erstellt", "SUCCESS")
        
        # Routes registrieren
        debug_log("📡 Registriere Routes...", "STARTUP")
        
        try:
            # Standard Routes
            from app.routes import main_routes, camera_routes
            app.register_blueprint(main_routes.bp)
            app.register_blueprint(camera_routes.bp)
            debug_log("✅ Standard-Routes", "SUCCESS")
            
        except ImportError as e:
            debug_log(f"⚠️ Standard-Routes Fehler: {e}", "ERROR")
        
        try:
            # Debug API Routes (unsere neue Debug-API)
            from app.routes.api_routes import bp as api_bp
            app.register_blueprint(api_bp)
            debug_log("✅ Debug-API-Routes", "SUCCESS")
            
        except ImportError as e:
            debug_log(f"❌ Debug-API-Routes Fehler: {e}", "ERROR")
            debug_log("💡 Stelle sicher dass api_routes.py existiert!", "ERROR")
        
        # Error Handler mit Debug-Logging
        @app.errorhandler(404)
        def not_found(error):
            debug_log(f"404: {error}", "ERROR")
            return {'error': 'Endpoint nicht gefunden', 'debug': True}, 404
        
        @app.errorhandler(500)
        def internal_error(error):
            debug_log(f"500: {error}", "ERROR")
            return {'error': 'Interner Server-Fehler', 'debug': True}, 500
        
        # Request-Logging für alle Requests
        @app.before_request
        def log_request():
            from flask import request
            debug_log(f"📨 {request.method} {request.path} von {request.remote_addr}", "INFO")
        
        debug_log("🎯 Flask-App mit Debug-Features bereit!", "SUCCESS")
        return app
        
    except Exception as e:
        debug_log(f"💥 Flask-App Erstellung fehlgeschlagen: {e}", "ERROR")
        raise

def print_startup_banner():
    """Startup-Banner anzeigen"""
    banner = """
    ╔══════════════════════════════════════════╗
    ║           🔍 UNKRAUT-2025 DEBUG          ║
    ║          Terminal Logging Aktiv          ║
    ╚══════════════════════════════════════════╝
    """
    print(banner)
    
    debug_log("🎯 DEBUG-MODUS AKTIV", "STARTUP")
    debug_log("📱 Alle Mobile Touch-Events werden geloggt", "STARTUP")
    debug_log("🌐 Alle Browser-Events werden geloggt", "STARTUP")
    debug_log("📸 Alle Kamera-Aktionen werden geloggt", "STARTUP")
    debug_log("💻 Alle API-Calls werden geloggt", "STARTUP")

def print_access_info():
    """Zugriffs-Informationen anzeigen"""
    debug_log("🌐 Server-Zugriff:", "STARTUP")
    debug_log("   📱 Mobile/Tablet: http://192.168.251.1:5000/camera", "STARTUP")
    debug_log("   💻 Desktop:       http://localhost:5000/camera", "STARTUP")
    debug_log("   🔍 Debug-API:     http://192.168.251.1:5000/api/debug/status", "STARTUP")

def start_heartbeat():
    """Heartbeat-Thread für Terminal-Logs"""
    def heartbeat():
        while True:
            time.sleep(30)  # Alle 30 Sekunden
            debug_log("💓 Server läuft... (Heartbeat)", "INFO")
    
    heartbeat_thread = threading.Thread(target=heartbeat, daemon=True)
    heartbeat_thread.start()
    debug_log("💓 Heartbeat-Thread gestartet", "SUCCESS")

def main():
    """Hauptfunktion für Debug-Server"""
    
    # Signal Handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Banner
    print_startup_banner()
    
    # Projekt prüfen
    if not check_project_structure():
        debug_log("⚠️ Projekt-Struktur unvollständig - trotzdem fortfahren", "ERROR")
    
    if not check_dependencies():
        debug_log("❌ Dependencies fehlen - Server wird trotzdem gestartet", "ERROR")
        debug_log("💡 Installiere fehlende Pakete mit: pip install flask opencv-python numpy psutil", "ERROR")
    
    # Flask-App erstellen
    try:
        app = create_debug_app()
        
        # Heartbeat starten
        start_heartbeat()
        
        # Zugriffs-Info
        print_access_info()
        
        debug_log("🚀 STARTE DEBUG-SERVER...", "STARTUP")
        debug_log("🔥 Alle Nachrichten erscheinen hier im Terminal!", "STARTUP")
        debug_log("📱 Teste jetzt das Foto machen auf dem Handy!", "STARTUP")
        
        # Server starten
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,  # Wir haben unser eigenes Debug-System
            threaded=True,
            use_reloader=False  # Verhindert doppelte Logs
        )
        
    except Exception as e:
        debug_log(f"💥 Server-Start fehlgeschlagen: {e}", "ERROR")
        debug_log("🔧 Mögliche Lösungen:", "ERROR")
        debug_log("   1. Prüfe ob Port 5000 frei ist: lsof -i :5000", "ERROR")
        debug_log("   2. Prüfe ob alle Dateien vorhanden sind", "ERROR")
        debug_log("   3. Prüfe Python-Version: python3 --version", "ERROR")
        sys.exit(1)

if __name__ == '__main__':
    main()