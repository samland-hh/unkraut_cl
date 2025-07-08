# unkraut/test/camera_debug.py
"""
Kamera Debug Test - Teste alle reparierten Funktionen
"""
import requests
import time
import json
import os
import sys

# Pfad für Imports setzen
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = 'http://localhost:5000'

def test_api_endpoint(endpoint, method='GET', data=None):
    """Teste einen API-Endpunkt"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == 'GET':
            response = requests.get(url, timeout=5)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=5)
        
        return {
            'endpoint': endpoint,
            'status_code': response.status_code,
            'success': response.status_code < 400,
            'response_time': response.elapsed.total_seconds(),
            'content': response.text[:200] if response.status_code < 400 else response.text
        }
    except Exception as e:
        return {
            'endpoint': endpoint,
            'status_code': 0,
            'success': False,
            'error': str(e)
        }

def test_camera_functionality():
    """Teste alle Kamera-Funktionen"""
    print("🔍 Teste Kamera-API-Funktionalität...")
    print("=" * 50)
    
    tests = [
        # Basis-Tests
        ('/', 'GET', None, 'Dashboard'),
        ('/camera', 'GET', None, 'Kamera-Seite'),
        
        # API-Tests
        ('/api/camera/stats', 'GET', None, 'Kamera-Statistiken'),
        ('/api/camera/gallery', 'GET', None, 'Bildergalerie'),
        ('/api/camera/capture', 'POST', None, 'Foto aufnehmen'),
        ('/api/ai/detect', 'POST', None, 'KI-Erkennung'),
        ('/api/system/status', 'GET', None, 'System-Status'),
        
        # Stream-Test (nur Status prüfen)
        ('/api/camera/stream', 'GET', None, 'Stream-Endpunkt'),
    ]
    
    results = []
    for endpoint, method, data, description in tests:
        print(f"🧪 Teste {description}: {method} {endpoint}")
        result = test_api_endpoint(endpoint, method, data)
        results.append(result)
        
        if result['success']:
            print(f"   ✅ OK ({result['status_code']}) - {result.get('response_time', 0):.2f}s")
        else:
            print(f"   ❌ FEHLER ({result.get('status_code', 'N/A')}) - {result.get('error', 'Unbekannt')}")
        
        time.sleep(0.5)  # Kurze Pause zwischen Tests
    
    return results

def test_file_structure():
    """Prüfe Dateistruktur"""
    print("\n📁 Prüfe Dateistruktur...")
    print("=" * 30)
    
    required_files = [
        'app/routes/api_routes.py',
        'app/static/js/camera.js', 
        'app/templates/camera.html',
        'app/main.py'
    ]
    
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    for file_path in required_files:
        full_path = os.path.join(base_path, file_path)
        if os.path.exists(full_path):
            size = os.path.getsize(full_path)
            print(f"   ✅ {file_path} ({size} bytes)")
        else:
            print(f"   ❌ {file_path} - FEHLT!")

def test_directories():
    """Prüfe und erstelle notwendige Verzeichnisse"""
    print("\n📂 Prüfe Verzeichnisse...")
    print("=" * 25)
    
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    directories = [
        'data',
        'data/images',
        'logs',
        'backups'
    ]
    
    for directory in directories:
        full_path = os.path.join(base_path, directory)
        if os.path.exists(full_path):
            files = len(os.listdir(full_path)) if os.path.isdir(full_path) else 0
            print(f"   ✅ {directory}/ ({files} Dateien)")
        else:
            print(f"   📁 {directory}/ - erstelle...")
            try:
                os.makedirs(full_path, exist_ok=True)
                print(f"   ✅ {directory}/ - erstellt")
            except Exception as e:
                print(f"   ❌ {directory}/ - Fehler: {e}")

def create_test_images():
    """Erstelle Test-Bilder für Galerie"""
    print("\n🖼️ Erstelle Test-Bilder...")
    print("=" * 25)
    
    try:
        import cv2
        import numpy as np
        from datetime import datetime
        
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        images_path = os.path.join(base_path, 'data', 'images')
        
        # Erstelle 3 Test-Bilder
        for i in range(3):
            # Erstelle Test-Bild
            img = np.zeros((480, 640, 3), dtype=np.uint8)
            
            # Hintergrundfarbe
            colors = [(50, 50, 50), (40, 60, 40), (60, 40, 40)]
            img[:] = colors[i]
            
            # Text hinzufügen
            timestamp = datetime.now().strftime("%H:%M:%S")
            cv2.putText(img, f'Test Bild {i+1}', (50, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)
            cv2.putText(img, f'Erstellt: {timestamp}', (50, 150), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 2)
            
            # Geometrische Formen
            if i == 0:
                cv2.circle(img, (320, 300), 80, (0, 255, 0), 3)
            elif i == 1:
                cv2.rectangle(img, (240, 220), (400, 380), (255, 0, 0), 3)
            else:
                points = np.array([[320, 220], [270, 320], [370, 320]], np.int32)
                cv2.polylines(img, [points], True, (0, 0, 255), 3)
            
            # Speichern
            filename = f'test_image_{i+1}_{int(time.time())}.jpg'
            filepath = os.path.join(images_path, filename)
            cv2.imwrite(filepath, img)
            
            print(f"   ✅ {filename} erstellt")
            
    except ImportError:
        print("   ⚠️ OpenCV nicht verfügbar - überspringe Bild-Erstellung")
    except Exception as e:
        print(f"   ❌ Fehler bei Bild-Erstellung: {e}")

def generate_report(results):
    """Erstelle Test-Report"""
    print("\n📊 Test-Report")
    print("=" * 20)
    
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r['success'])
    failed_tests = total_tests - successful_tests
    
    print(f"Gesamt-Tests: {total_tests}")
    print(f"Erfolgreich: {successful_tests}")
    print(f"Fehlgeschlagen: {failed_tests}")
    print(f"Erfolgsrate: {(successful_tests/total_tests*100):.1f}%")
    
    if failed_tests > 0:
        print("\n❌ Fehlgeschlagene Tests:")
        for result in results:
            if not result['success']:
                print(f"   - {result['endpoint']}: {result.get('error', 'Unbekannt')}")
    
    # Speichere Report
    report = {
        'timestamp': time.time(),
        'total_tests': total_tests,
        'successful_tests': successful_tests,
        'failed_tests': failed_tests,
        'success_rate': successful_tests/total_tests*100,
        'results': results
    }
    
    try:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        report_path = os.path.join(base_path, 'test', 'camera_test_report.json')
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 Report gespeichert: {report_path}")
        
    except Exception as e:
        print(f"\n❌ Fehler beim Speichern des Reports: {e}")

def main():
    """Hauptfunktion"""
    print("🔧 Kamera Debug Test - Unkraut-2025")
    print("===================================")
    print(f"Basis-URL: {BASE_URL}")
    print(f"Zeit: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Dateistruktur prüfen
    test_file_structure()
    
    # 2. Verzeichnisse prüfen
    test_directories()
    
    # 3. Test-Bilder erstellen
    create_test_images()
    
    # 4. Server-Verbindung testen
    print(f"\n🌐 Teste Server-Verbindung zu {BASE_URL}...")
    try:
        response = requests.get(BASE_URL, timeout=3)
        if response.status_code == 200:
            print("   ✅ Server erreichbar")
        else:
            print(f"   ⚠️ Server antwortet mit Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Server nicht erreichbar: {e}")
        print("   💡 Starte den Server mit: python app/main.py")
        return
    
    # 5. API-Tests durchführen
    results = test_camera_functionality()
    
    # 6. Report erstellen
    generate_report(results)
    
    print("\n🎉 Debug-Test abgeschlossen!")
    print("\nNächste Schritte:")
    print("1. Öffne http://localhost:5000/camera im Browser")
    print("2. Teste alle Kamera-Funktionen manuell")
    print("3. Prüfe Browser-Konsole auf JavaScript-Fehler")

if __name__ == '__main__':
    main()