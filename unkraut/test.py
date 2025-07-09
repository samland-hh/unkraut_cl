#!/usr/bin/env python3
"""
Unkraut-2025 Main Entry Point
Startet die Flask-Anwendung für den autonomen Unkraut-Roboter
"""

import os
import sys
import subprocess
from flask import Flask, render_template

# Füge das aktuelle Verzeichnis zum Python Path hinzu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def get_wlan0_ip():
    """Ermittelt die IP-Adresse des wlan0 Interfaces"""
    try:
        # Verwende ip a | grep wie in der Shell
        result = subprocess.run(['sh', '-c', 'ip a | grep -A2 wlan0 | grep "inet " | head -1'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            # Extrahiere IP aus: "    inet 192.168.251.1/24 scope global wlan0"
            line = result.stdout.strip()
            parts = line.split()
            for part in parts:
                if '.' in part and '/' in part:  # Finde IP/Maske
                    return part.split('/')[0]
                    
    except Exception as e:
        print(f"Debug: Fehler: {e}")
    
    return "127.0.0.1"

def create_basic_app():
    """
    Erstellt eine einfache Flask App mit Mock-Funktionalität
    zum Testen ohne Hardware
    """
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'unkraut-2025-development-key'
    
    # Basic routes für erste Tests
    @app.route('/')
    def dashboard():
        return '''
        <h1>🤖 Unkraut-2025 - Test Dashboard</h1>
        <p>Flask App läuft erfolgreich!</p>
        <ul>
            <li><a href="/test">Test Seite</a></li>
            <li><a href="/api/status">API Status</a></li>
        </ul>
        '''
    
    @app.route('/test')
    def test():
        return '''
        <h2>Test Seite</h2>
        <p>Grundfunktionen sind verfügbar</p>
        <p><a href="/">← Zurück zum Dashboard</a></p>
        '''
    
    @app.route('/api/status')
    def api_status():
        return {
            'status': 'running',
            'version': '1.0.0',
            'message': 'Unkraut-2025 Flask App ist aktiv',
            'hardware_connected': False,
            'camera_available': False,
            'ai_loaded': False
        }
    
    return app

def create_full_app():
    """
    Versucht die vollständige App zu laden
    Falls Hardware-Module fehlen, fällt auf Basic App zurück
    """
    try:
        # Versuche die vollständige App zu importieren
        from app.main import create_app
        print("✅ Lade vollständige Unkraut-2025 App...")
        return create_app()
    except ImportError as e:
        print(f"⚠️  Hardware-Module nicht gefunden: {e}")
        print("📱 Starte Basic-Version zum Testen...")
        return create_basic_app()

if __name__ == '__main__':
    # App erstellen
    app = create_full_app()
    
    # Entwicklungs-Konfiguration
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    
    print("🚀 Starte Unkraut-2025 Flask Server...")
    print(f"📡 Zugriff über: http://{host}:{port}")
    
    # Ermittle und zeige wlan0 IP-Adresse
    hostap = get_wlan0_ip()
    print(f"📡 Zugriff über: http://{hostap}:{port}")
   
    print("🛑 Stoppen mit Ctrl+C")
    
    try:
        app.run(
            host=host,
            port=port,
            debug=debug_mode,
            threaded=True  # Für bessere Performance
        )
    except KeyboardInterrupt:
        print("\n👋 Unkraut-2025 gestoppt")
    except Exception as e:
        print(f"❌ Fehler beim Starten: {e}")
        sys.exit(1)