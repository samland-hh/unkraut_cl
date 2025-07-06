# app/main.py - Erweiterte Unkraut-2025 Flask App mit Combined Route
"""
Unkraut-2025 Flask Hauptanwendung
Modulare Architektur mit separaten Routes und Templates
"""
from flask import Flask
import os

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'unkraut-2025-secret'
    
    # Verzeichnisse erstellen
    for directory in ['data', 'data/images', 'logs', 'backups']:
        os.makedirs(directory, exist_ok=True)
    
    # Routes importieren und registrieren
    from .routes import main_routes, control_routes, arm_routes, camera_routes, ai_routes, api_routes, combined_routes, debug_routes
    
    app.register_blueprint(main_routes.bp)
    app.register_blueprint(control_routes.bp)
    app.register_blueprint(arm_routes.bp)
    app.register_blueprint(camera_routes.bp)
    app.register_blueprint(ai_routes.bp)
    app.register_blueprint(api_routes.bp)
    app.register_blueprint(combined_routes.bp)  # Neue kombinierte Route
    app.register_blueprint(debug_routes.bp)     # Debug-Route für Mobile
    
    print("✅ Unkraut-2025 Flask App geladen (modulare Architektur + Combined)")
    return app

# Für den Import
app = create_app()

if __name__ == '__main__':
    print("🚀 Starte Unkraut-2025 direkt aus main.py")
    app.run(host='0.0.0.0', port=5000, debug=True)