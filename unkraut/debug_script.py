# debug.py
"""
Debug-Script für Unkraut-2025
Zeigt detaillierte Fehler und Import-Probleme
"""
import sys
import os
import traceback
import requests
import json

def test_imports():
    """Teste alle Import-Dependencies"""
    print("🔍 Teste Python-Imports...")
    
    imports = [
        ('flask', 'Flask'),
        ('hardware.camera', 'camera_manager'),
        ('hardware.robot_arm', 'robot_arm'),
        ('hardware.motors', 'motor_controller'),
        ('hardware.sensors', 'sensor_manager, get_sensor_data'),
        ('ai.weed_detection', 'weed_detector'),
        ('cv2', 'OpenCV'),
        ('psutil', 'psutil'),
        ('numpy', 'numpy'),
    ]
    
    for module, desc in imports:
        try:
            __import__(module)
            print(f"  ✅ {desc}: OK")
        except ImportError as e:
            print(f"  ❌ {desc}: FEHLT - {e}")
        except Exception as e:
            print(f"  ⚠️ {desc}: FEHLER - {e}")

def test_hardware_modules():
    """Teste Hardware-Module direkt"""
    print("\n🔧 Teste Hardware-Module direkt...")
    
    # Kamera testen
    try:
        from hardware.camera import camera_manager
        info = camera_manager.get_camera_info()
        print(f"  ✅ Kamera: {info['type']} - {info['width']}x{info['height']}")
    except Exception as e:
        print(f"  ❌ Kamera: {e}")
        traceback.print_exc()
    
    # Roboterarm testen
    try:
        from hardware.robot_arm import robot_arm
        info = robot_arm.get_arm_info()
        print(f"  ✅ Roboterarm: {'Hardware' if info['controller']['hardware_available'] else 'Mock'}")
    except Exception as e:
        print(f"  ❌ Roboterarm: {e}")
        traceback.print_exc()
    
    # Motoren testen
    try:
        from hardware.motors import motor_controller
        status = motor_controller.get_status()
        print(f"  ✅ Motoren: {'Hardware' if status['hardware_available'] else 'Mock'}")
    except Exception as e:
        print(f"  ❌ Motoren: {e}")
        traceback.print_exc()
    
    # Sensoren testen
    try:
        from hardware.sensors import sensor_manager, get_sensor_data
        data = get_sensor_data()
        print(f"  ✅ Sensoren: Temp {data['temperature']}°C")
    except Exception as e:
        print(f"  ❌ Sensoren: {e}")
        traceback.print_exc()
    
    # AI testen
    try:
        from ai.weed_detection import weed_detector
        stats = weed_detector.get_detection_stats()
        print(f"  ✅ KI: {stats['method']}")
    except Exception as e:
        print(f"  ❌ KI: {e}")
        traceback.print_exc()

def test_api_detailed(base_url='http://localhost:5000'):
    """Teste API-Endpoints mit detaillierten Fehlern"""
    print(f"\n🔌 Teste API-Endpoints detailliert ({base_url})...")
    
    failed_endpoints = [
        '/api/system/status',
        '/api/control/status', 
        '/api/arm/move/joint'
    ]
    
    for endpoint in failed_endpoints:
        print(f"\n🔍 Debugge {endpoint}:")
        try:
            if endpoint == '/api/arm/move/joint':
                response = requests.post(f"{base_url}{endpoint}", 
                                       json={'joint': 'base', 'angle': 90}, 
                                       timeout=5)
            else:
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
            
            print(f"  Status: {response.status_code}")
            print(f"  Headers: {dict(response.headers)}")
            
            if response.status_code != 200:
                print(f"  Response: {response.text[:500]}")
                
                # Versuche JSON zu parsen
                try:
                    error_data = response.json()
                    print(f"  Error: {error_data}")
                except:
                    pass
                    
        except Exception as e:
            print(f"  Exception: {e}")

def check_file_structure():
    """Prüfe Dateistruktur"""
    print("\n📁 Prüfe Dateistruktur...")
    
    required_files = [
        'app/main.py',
        'app/routes/__init__.py',
        'app/routes/api_routes.py',
        'hardware/__init__.py',
        'hardware/camera.py',
        'hardware/robot_arm.py',
        'hardware/motors.py',
        'hardware/sensors.py',
        'ai/__init__.py',
        'ai/weed_detection.py',
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - FEHLT!")

def main():
    print("🐛 Unkraut-2025 Debug Script")
    print("==============================")
    
    check_file_structure()
    test_imports()
    test_hardware_modules()
    
    # Teste APIs nur wenn Server läuft
    try:
        response = requests.get('http://localhost:5000', timeout=2)
        if response.status_code == 200:
            test_api_detailed()
        else:
            print(f"\n⚠️ Server läuft aber antwortet mit {response.status_code}")
    except:
        print("\n⚠️ Server läuft nicht - starte mit: python app/main.py")
    
    print("\n💡 Lösungsvorschläge:")
    print("===================")
    print("1. Fehlende Module installieren: pip install opencv-python psutil numpy")
    print("2. Hardware-Verzeichnis prüfen: ls -la hardware/")
    print("3. Server-Logs prüfen: python app/main.py (im Debug-Modus)")
    print("4. Import-Test: python -c 'from hardware.camera import camera_manager'")

if __name__ == '__main__':
    main()