# unkraut/app/main.py
"""
Unkraut-2025 Flask Hauptanwendung
Bereinigte modulare Architektur mit System-Shutdown-Funktionalität
"""
from flask import Flask
import os

def create_app():
    """Flask-App erstellen und konfigurieren"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'unkraut-2025-secret-key-change-in-production'
    
    # Verzeichnisse erstellen falls nicht vorhanden
    directories = [
        'data',
        'data/images', 
        'data/videos',
        'data/maps',
        'data/sessions',
        'logs',
        'backups',
        'backups/images',
        'backups/configs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    # Routes importieren und registrieren
    try:
        from .routes import (
            main_routes, 
            control_routes, 
            arm_routes, 
            camera_routes, 
            ai_routes, 
            api_routes, 
            combined_routes, 
            debug_routes, 
            docs_routes
        )
        
        # Blueprint registrieren
        app.register_blueprint(main_routes.bp)
        app.register_blueprint(control_routes.bp)
        app.register_blueprint(arm_routes.bp)        # Bereinigte Arm-Routes
        app.register_blueprint(camera_routes.bp)
        app.register_blueprint(ai_routes.bp)
        app.register_blueprint(api_routes.bp)        # Bereinigte API-Routes  
        app.register_blueprint(combined_routes.bp)
        app.register_blueprint(debug_routes.bp)
        app.register_blueprint(docs_routes.bp)       # Docs-Route
        
        print("✅ Standard Route-Module erfolgreich geladen")
        
    except ImportError as e:
        print(f"❌ Route-Import-Fehler: {e}")
        print("💡 Prüfe ob alle Route-Dateien existieren")
        # Nicht abbrechen - System-Routes können trotzdem funktionieren
    
    # System-Routes separat laden (für Shutdown-Funktionalität)
    try:
        from .routes import system_routes
        app.register_blueprint(system_routes.bp)
        print("✅ System-Routes (Shutdown) erfolgreich geladen")
    except ImportError as e:
        print(f"⚠️  System-Routes nicht gefunden: {e}")
        print("💡 Erstelle app/routes/system_routes.py für Shutdown-Funktionalität")
    
    # Error Handler
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Endpoint nicht gefunden'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Interner Server-Fehler'}, 500
    
    print("✅ Unkraut-2025 Flask App initialisiert")
    print(f"📁 Datenverzeichnisse erstellt: {len(directories)} Ordner")
    
    return app

# App-Instanz für Import (wird von run.py verwendet)
app = create_app()

if __name__ == '__main__':
    print("🚀 Starte Unkraut-2025 direkt aus main.py")
    print("💡 Für Produktion: verwende run.py oder gunicorn")
    app.run(host='0.0.0.0', port=5000, debug=True)