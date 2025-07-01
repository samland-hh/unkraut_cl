#!/usr/bin/env python3
"""
Unkraut-2025 Main Entry Point
"""
import os
import sys
import subprocess

# Konstanten
C_FLASKPORT = 5000  # Flask Port

# Python path setzen
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

def main():
    # Port aus Umgebungsvariable oder Default
    port = int(os.environ.get('FLASK_PORT', C_FLASKPORT))
    
    try:
        from app.main import app
        print("✅ Unkraut-2025 Module erfolgreich geladen")
        print("🚀 Starte Flask Server...")
        print(f"📡 Zugriff über: http://localhost:{port}")
        # Ermittle und zeige wlan0 IP-Adresse
        hostap = get_wlan0_ip()
        print(f"📡 Zugriff über: http://{hostap}:{port}")
        print("🛑 Stoppen mit Ctrl+C")
        
        app.run(
            host='0.0.0.0',
            port=port,
            debug=True,
            threaded=True
        )
        
    except ImportError as e:
        print(f"❌ Import-Fehler: {e}")
        print("💡 Führe 'pip install -r requirements.txt' aus")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Unkraut-2025 gestoppt")
    except Exception as e:
        print(f"❌ Fehler: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()