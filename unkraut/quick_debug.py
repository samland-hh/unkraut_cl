# quick_debug.py - Schnelle Diagnose für Unkraut-2025
import os
import sys

print("🔍 Unkraut-2025 Schnell-Diagnose")
print("================================")

# 1. Dateistruktur prüfen
print("\n📁 Dateien prüfen:")
files = [
    'app/main.py',
    'app/routes/api_routes.py', 
    'hardware/camera.py',
    'hardware/robot_arm.py',
    'hardware/motors.py',
    'hardware/sensors.py',
    'ai/weed_detection.py'
]

missing_files = []
for file in files:
    if os.path.exists(file):
        print(f"  ✅ {file}")
    else:
        print(f"  ❌ {file} - FEHLT!")
        missing_files.append(file)

# 2. Python-Imports testen
print("\n🐍 Import-Tests:")
try:
    import flask
    print("  ✅ Flask")
except:
    print("  ❌ Flask - pip install flask")

try:
    import cv2
    print("  ✅ OpenCV")
except:
    print("  ❌ OpenCV - pip install opencv-python")

try:
    import psutil
    print("  ✅ psutil")
except:
    print("  ❌ psutil - pip install psutil")

try:
    import numpy
    print("  ✅ numpy")
except:
    print("  ❌ numpy - pip install numpy")

# 3. App-Import testen
print("\n🚀 App-Import Test:")
try:
    from app.main import create_app
    print("  ✅ Flask-App importierbar")
except Exception as e:
    print(f"  ❌ Flask-App: {e}")

# 4. Hardware-Imports einzeln testen
print("\n🔧 Hardware-Imports:")
hardware_modules = [
    ('hardware.camera', 'camera_manager'),
    ('hardware.robot_arm', 'robot_arm'),
    ('hardware.motors', 'motor_controller'),
    ('hardware.sensors', 'sensor_manager'),
    ('ai.weed_detection', 'weed_detector')
]

failed_imports = []
for module, item in hardware_modules:
    try:
        exec(f"from {module} import {item}")
        print(f"  ✅ {module}.{item}")
    except Exception as e:
        print(f"  ❌ {module}.{item} - {e}")
        failed_imports.append(module)

# 5. Lösungsvorschläge
print("\n💡 Lösungsvorschläge:")
print("===================")

if missing_files:
    print("🔥 FEHLENDE DATEIEN:")
    for file in missing_files:
        print(f"  - {file}")
    print("  → Kopiere Hardware-Module aus den Artifacts!")

if failed_imports:
    print("🔥 IMPORT-PROBLEME:")
    for module in failed_imports:
        print(f"  - {module}")
    print("  → Stelle sicher, dass alle .py Dateien in den Ordnern sind")

print("\n🔧 SCHNELLE FIXES:")
print("1. Hardware-Module kopieren:")
print("   mkdir -p hardware ai")
print("   # Kopiere hardware/*.py und ai/*.py aus Artifacts")

print("\n2. Requirements installieren:")
print("   pip install flask opencv-python psutil numpy")

print("\n3. Test:")
print("   python app/main.py")

# 6. Server-Test
print("\n🌐 Server-Test:")
try:
    import requests
    response = requests.get('http://localhost:5000', timeout=2)
    print(f"  ✅ Server läuft: {response.status_code}")
except:
    print("  ❌ Server läuft nicht")
    print("  → Starte mit: python app/main.py")

print("\n✅ Diagnose abgeschlossen!")
print("Bei Problemen: Kopiere fehlende Dateien aus den Artifacts")