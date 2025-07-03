# fix_common_issues.py
"""
Automatisches Fix-Script für häufige Unkraut-2025 Probleme
"""
import os
import sys
import subprocess

def create_missing_files():
    """Erstelle fehlende __init__.py Dateien"""
    print("📁 Erstelle fehlende Dateien...")
    
    init_files = [
        'app/__init__.py',
        'app/routes/__init__.py', 
        'hardware/__init__.py',
        'ai/__init__.py'
    ]
    
    for file in init_files:
        if not os.path.exists(file):
            os.makedirs(os.path.dirname(file), exist_ok=True)
            with open(file, 'w') as f:
                f.write(f'# {file}\n')
            print(f"  ✅ Erstellt: {file}")
        else:
            print(f"  ✅ Vorhanden: {file}")

def fix_import_issues():
    """Behebe häufige Import-Probleme"""
    print("\n🔧 Behebe Import-Probleme...")
    
    # Prüfe ob alle Hardware-Module existieren
    hardware_files = [
        'hardware/camera.py',
        'hardware/robot_arm.py', 
        'hardware/motors.py',
        'hardware/sensors.py'
    ]
    
    for file in hardware_files:
        if not os.path.exists(file):
            print(f"  ❌ {file} fehlt!")
        else:
            print(f"  ✅ {file} vorhanden")
    
    # Prüfe AI-Module
    ai_files = ['ai/weed_detection.py']
    for file in ai_files:
        if not os.path.exists(file):
            print(f"  ❌ {file} fehlt!")
        else:
            print(f"  ✅ {file} vorhanden")

def fix_sensor_import():
    """Behebe spezifische Sensor-Import-Probleme"""
    print("\n🔧 Behebe Sensor-Imports...")
    
    sensor_file = 'hardware/sensors.py'
    if os.path.exists(sensor_file):
        with open(sensor_file, 'r') as f:
            content = f.read()
        
        # Prüfe auf häufige Probleme
        if 'def get_sensor_data' not in content:
            print("  ⚠️ get_sensor_data Funktion fehlt in sensors.py")
        else:
            print("  ✅ get_sensor_data Funktion vorhanden")
        
        if 'sensor_manager =' not in content:
            print("  ⚠️ sensor_manager Instanz fehlt in sensors.py")
        else:
            print("  ✅ sensor_manager Instanz vorhanden")

def check_dependencies():
    """Prüfe und installiere fehlende Dependencies"""
    print("\n📦 Prüfe Dependencies...")
    
    required_packages = [
        'flask',
        'opencv-python', 
        'psutil',
        'numpy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'opencv-python':
                import cv2
                print(f"  ✅ {package} (cv2) installiert")
            else:
                __import__(package)
                print(f"  ✅ {package} installiert")
        except ImportError:
            print(f"  ❌ {package} fehlt")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n💡 Installiere fehlende Pakete:")
        print(f"pip install {' '.join(missing_packages)}")
        
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("✅ Pakete erfolgreich installiert")
        except subprocess.CalledProcessError as e:
            print(f"❌ Installation fehlgeschlagen: {e}")

def fix_api_routes():
    """Behebe API-Route Probleme"""
    print("\n🔌 Prüfe API-Routes...")
    
    routes_file = 'app/routes/api_routes.py'
    if os.path.exists(routes_file):
        with open(routes_file, 'r') as f:
            content = f.read()
        
        # Prüfe kritische Imports
        critical_imports = [
            'from hardware.sensors import',
            'from hardware.motors import', 
            'from hardware.robot_arm import'
        ]
        
        for imp in critical_imports:
            if imp in content:
                print(f"  ✅ {imp} vorhanden")
            else:
                print(f"  ⚠️ {imp} fehlt möglicherweise")
    else:
        print(f"  ❌ {routes_file} nicht gefunden")

def create_minimal_main_py():
    """Erstelle eine minimale main.py wenn sie fehlt"""
    main_file = 'app/main.py'
    
    if not os.path.exists(main_file):
        print(f"\n📝 Erstelle minimale {main_file}...")
        
        minimal_content = '''# app/main.py - Minimal Unkraut-2025 Flask App
from flask import Flask

def create_app():
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        return '<h1>🤖 Unkraut-2025</h1><p>Minimal-Version läuft!</p>'
    
    @app.route('/api/system/status')
    def system_status():
        return {'status': 'ok', 'mode': 'minimal'}
    
    return app

app = create_app()

if __name__ == '__main__':
    print("🚀 Starte Unkraut-2025 (Minimal-Version)")
    app.run(host='0.0.0.0', port=5000, debug=True)
'''
        
        os.makedirs(os.path.dirname(main_file), exist_ok=True)
        with open(main_file, 'w') as f:
            f.write(minimal_content)
        
        print(f"  ✅ {main_file} erstellt")
        print("  💡 Starte mit: python app/main.py")

def test_quick_fix():
    """Schneller Test nach Fixes"""
    print("\n🧪 Teste nach Fixes...")
    
    try:
        # Teste grundlegende Imports
        from app.main import create_app
        app = create_app()
        print("  ✅ Flask-App kann erstellt werden")
        
        # Teste Hardware-Imports (optional)
        try:
            from hardware.camera import camera_manager
            print("  ✅ Kamera-Modul importierbar")
        except:
            print("  ⚠️ Kamera-Modul problematisch (OK in Mock-Modus)")
        
        try:
            from hardware.sensors import get_sensor_data
            print("  ✅ Sensoren-Funktionen importierbar")
        except:
            print("  ⚠️ Sensoren-Funktionen problematisch")
            
    except Exception as e:
        print(f"  ❌ Grundlegende Imports fehlgeschlagen: {e}")

def main():
    print("🔧 Unkraut-2025 Auto-Fix Script")
    print("================================")
    
    print("🔍 Analysiere Probleme...")
    
    create_missing_files()
    fix_import_issues()
    fix_sensor_import()
    check_dependencies()
    fix_api_routes()
    test_quick_fix()
    
    print("\n✅ Auto-Fix abgeschlossen!")
    print("\n💡 Nächste Schritte:")
    print("1. Starte Server: python app/main.py")
    print("2. Teste wieder: bash test.sh")
    print("3. Bei Problemen: python debug.py")
    
    print("\n🔧 Manuelle Fixes falls nötig:")
    print("- Hardware-Module fehlen: Kopiere aus Artifacts")
    print("- Import-Fehler: pip install -r requirements.txt")
    print("- 500-Fehler: Prüfe Logs mit python debug.py")

if __name__ == '__main__':
    main()