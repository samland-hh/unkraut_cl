# test_unkraut2025.py
"""
Umfassende Test-Suite für Unkraut-2025
Testet alle Endpoints, Hardware-Module und Funktionen
"""
import requests
import time
import json
import sys
import os
from datetime import datetime

class Unkraut2025Tester:
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = []
        
    def log(self, message, status='INFO'):
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {status}: {message}")
        
    def test_endpoint(self, method, endpoint, data=None, expected_status=200, timeout=5):
        """Teste einen einzelnen Endpoint"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, timeout=timeout)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, timeout=timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            success = response.status_code == expected_status
            
            result = {
                'endpoint': endpoint,
                'method': method,
                'status_code': response.status_code,
                'expected': expected_status,
                'success': success,
                'response_time': response.elapsed.total_seconds(),
                'content_length': len(response.content)
            }
            
            self.results.append(result)
            
            status = '✅' if success else '❌'
            self.log(f"{status} {method} {endpoint} - {response.status_code} ({response.elapsed.total_seconds():.3f}s)")
            
            return response
            
        except Exception as e:
            self.log(f"❌ {method} {endpoint} - ERROR: {str(e)}", 'ERROR')
            self.results.append({
                'endpoint': endpoint,
                'method': method,
                'status_code': 0,
                'expected': expected_status,
                'success': False,
                'error': str(e)
            })
            return None
    
    def test_web_pages(self):
        """Teste alle Web-Seiten"""
        self.log("🌐 Teste Web-Seiten...")
        
        pages = [
            ('/', 'Dashboard'),
            ('/control', 'Fahrzeug-Steuerung'),
            ('/arm', 'Roboterarm'),
            ('/camera', 'Kamera'),
            ('/ai', 'KI-Dashboard')
        ]
        
        for endpoint, name in pages:
            response = self.test_endpoint('GET', endpoint)
            if response and 'html' in response.headers.get('content-type', ''):
                self.log(f"  📄 {name}: HTML-Seite geladen")
            elif response:
                self.log(f"  ⚠️ {name}: Unerwarteter Content-Type", 'WARNING')
    
    def test_api_endpoints(self):
        """Teste alle API-Endpoints"""
        self.log("🔌 Teste API-Endpoints...")
        
        # System API
        self.test_endpoint('GET', '/api/system/status')
        
        # Kamera API
        self.test_endpoint('POST', '/api/camera/capture')
        
        # Fahrzeug API
        self.test_endpoint('POST', '/api/control/move', {
            'direction': 'forward',
            'speed': 50,
            'duration': 0.1
        })
        self.test_endpoint('POST', '/api/control/stop')
        self.test_endpoint('GET', '/api/control/status')
        
        # Roboterarm API
        self.test_endpoint('GET', '/api/arm/info')
        self.test_endpoint('POST', '/api/arm/move/joint', {
            'joint': 'base',
            'angle': 90
        })
        self.test_endpoint('POST', '/api/arm/move/preset', {
            'preset': 'home',
            'duration': 2.0
        })
        self.test_endpoint('POST', '/api/arm/emergency_stop')
        self.test_endpoint('POST', '/api/arm/weed_removal')
        self.test_endpoint('POST', '/api/arm/tool/activate', {
            'duration': 3.0
        })
        self.test_endpoint('POST', '/api/arm/calibrate')
        
        # AI API
        self.test_endpoint('POST', '/api/ai/detect')
    
    def test_hardware_modules(self):
        """Teste Hardware-Module direkt"""
        self.log("🔧 Teste Hardware-Module...")
        
        try:
            # Kamera testen
            from hardware.camera import camera_manager
            camera_info = camera_manager.get_camera_info()
            self.log(f"  📷 Kamera: {camera_info['type']} - {camera_info['width']}x{camera_info['height']}")
            
            # Roboterarm testen
            from hardware.robot_arm import robot_arm
            arm_info = robot_arm.get_arm_info()
            hw_status = "Hardware" if arm_info['controller']['hardware_available'] else "Mock"
            self.log(f"  🦾 Roboterarm: {hw_status} - {arm_info['controller']['servo_count']} Servos")
            
            # Motoren testen
            from hardware.motors import motor_controller
            motor_status = motor_controller.get_status()
            hw_status = "Hardware" if motor_status['hardware_available'] else "Mock"
            self.log(f"  🚗 Motoren: {hw_status}")
            
            # Sensoren testen
            from hardware.sensors import sensor_manager
            sensor_data = sensor_manager.get_sensor_data()
            hw_status = "Hardware" if sensor_data['hardware_available'] else "Mock"
            self.log(f"  📊 Sensoren: {hw_status} - Temp: {sensor_data['temperature']}°C")
            
            # AI testen
            from ai.weed_detection import weed_detector
            ai_stats = weed_detector.get_detection_stats()
            model_status = "TensorFlow" if ai_stats['model_loaded'] else "OpenCV+Mock"
            self.log(f"  🧠 KI: {model_status} - {ai_stats['total_detections']} Erkennungen")
            
        except Exception as e:
            self.log(f"  ❌ Hardware-Test fehlgeschlagen: {e}", 'ERROR')
    
    def test_camera_stream(self):
        """Teste Kamera-Stream (nur Header, nicht den ganzen Stream)"""
        self.log("📹 Teste Kamera-Stream...")
        
        try:
            response = self.session.get(f"{self.base_url}/api/camera/stream", 
                                      stream=True, timeout=3)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                if 'multipart/x-mixed-replace' in content_type:
                    self.log("  ✅ MJPEG-Stream verfügbar")
                else:
                    self.log(f"  ⚠️ Unerwarteter Content-Type: {content_type}", 'WARNING')
            else:
                self.log(f"  ❌ Stream-Fehler: {response.status_code}", 'ERROR')
                
        except Exception as e:
            self.log(f"  ❌ Stream-Test fehlgeschlagen: {e}", 'ERROR')
    
    def test_stress_test(self):
        """Stress-Test mit mehreren parallelen Anfragen"""
        self.log("💪 Starte Stress-Test...")
        
        import threading
        import time
        
        def stress_worker():
            for i in range(5):
                self.test_endpoint('GET', '/api/system/status')
                self.test_endpoint('POST', '/api/control/move', {
                    'direction': 'forward',
                    'speed': 30,
                    'duration': 0.1
                })
                time.sleep(0.1)
        
        # 3 parallele Worker
        threads = []
        start_time = time.time()
        
        for i in range(3):
            t = threading.Thread(target=stress_worker)
            t.start()
            threads.append(t)
        
        for t in threads:
            t.join()
        
        duration = time.time() - start_time
        self.log(f"  ✅ Stress-Test abgeschlossen in {duration:.2f}s")
    
    def test_error_handling(self):
        """Teste Fehlerbehandlung"""
        self.log("⚠️ Teste Fehlerbehandlung...")
        
        # Ungültige Endpoints
        self.test_endpoint('GET', '/nonexistent', expected_status=404)
        self.test_endpoint('POST', '/api/invalid', expected_status=404)
        
        # Ungültige Parameter
        self.test_endpoint('POST', '/api/arm/move/joint', {
            'joint': 'invalid',
            'angle': 'not_a_number'
        }, expected_status=400)
        
        # Fehlende Parameter
        self.test_endpoint('POST', '/api/control/move', {}, expected_status=400)
    
    def run_all_tests(self):
        """Führe alle Tests aus"""
        start_time = time.time()
        
        self.log("🚀 Starte Unkraut-2025 Test-Suite")
        self.log(f"📍 Teste Server: {self.base_url}")
        
        # Server-Erreichbarkeit prüfen
        try:
            response = self.session.get(self.base_url, timeout=5)
            if response.status_code != 200:
                self.log(f"❌ Server nicht erreichbar: {response.status_code}", 'ERROR')
                return False
            self.log("✅ Server erreichbar")
        except Exception as e:
            self.log(f"❌ Server nicht erreichbar: {e}", 'ERROR')
            return False
        
        # Tests ausführen
        self.test_web_pages()
        self.test_api_endpoints()
        self.test_camera_stream()
        self.test_hardware_modules()
        self.test_error_handling()
        self.test_stress_test()
        
        # Ergebnisse auswerten
        total_time = time.time() - start_time
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r.get('success', False))
        failed_tests = total_tests - successful_tests
        
        self.log("📊 Test-Ergebnisse:")
        self.log(f"  Gesamt: {total_tests} Tests")
        self.log(f"  Erfolgreich: {successful_tests} ✅")
        self.log(f"  Fehlgeschlagen: {failed_tests} ❌")
        self.log(f"  Erfolgsrate: {(successful_tests/total_tests*100):.1f}%")
        self.log(f"  Gesamtzeit: {total_time:.2f}s")
        
        if failed_tests > 0:
            self.log("❌ Fehlgeschlagene Tests:")
            for result in self.results:
                if not result.get('success', False):
                    endpoint = result['endpoint']
                    method = result['method']
                    error = result.get('error', f"Status {result['status_code']}")
                    self.log(f"  - {method} {endpoint}: {error}")
        
        return failed_tests == 0
    
    def save_report(self, filename='test_report.json'):
        """Speichere Test-Bericht als JSON"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'base_url': self.base_url,
            'total_tests': len(self.results),
            'successful_tests': sum(1 for r in self.results if r.get('success', False)),
            'results': self.results
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.log(f"📄 Test-Bericht gespeichert: {filename}")

def main():
    """Hauptfunktion"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Unkraut-2025 Test Suite')
    parser.add_argument('--url', default='http://localhost:5000', 
                       help='Base URL des Servers (default: http://localhost:5000)')
    parser.add_argument('--report', default='test_report.json',
                       help='Dateiname für Test-Bericht (default: test_report.json)')
    parser.add_argument('--quick', action='store_true',
                       help='Nur grundlegende Tests ausführen')
    
    args = parser.parse_args()
    
    tester = Unkraut2025Tester(args.url)
    
    if args.quick:
        # Nur Web-Seiten und System-Status testen
        tester.test_web_pages()
        tester.test_endpoint('GET', '/api/system/status')
    else:
        # Alle Tests
        success = tester.run_all_tests()
        tester.save_report(args.report)
        
        # Exit Code setzen
        sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()