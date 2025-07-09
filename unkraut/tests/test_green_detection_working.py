# unkraut/test/test_green_detection_working.py
"""
Funktionierendes Test-Script für vorhandene Grün-Erkennung
Arbeitet mit der bestehenden Projekt-Struktur
"""
import cv2
import numpy as np
import os
import sys
import time
import random
from datetime import datetime

# Pfad zum Projekt-Root hinzufügen
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

print(f"🔍 Projekt-Root: {project_root}")
print(f"📁 Aktuelles Verzeichnis: {current_dir}")

# Versuche Module zu importieren
try:
    from ai.weed_detection import WeedDetector
    print("✅ WeedDetector importiert")
    HAS_WEED_DETECTOR = True
except ImportError as e:
    print(f"❌ WeedDetector Import fehlgeschlagen: {e}")
    HAS_WEED_DETECTOR = False

try:
    from hardware.camera import CameraManager
    print("✅ CameraManager importiert")
    HAS_CAMERA = True
except ImportError as e:
    print(f"❌ CameraManager Import fehlgeschlagen: {e}")
    HAS_CAMERA = False

class SimpleGreenDetectionTester:
    """Einfacher Tester für vorhandene Grün-Erkennung"""
    
    def __init__(self):
        self.output_dir = os.path.join(project_root, "test", "output")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Detector initialisieren
        if HAS_WEED_DETECTOR:
            self.detector = WeedDetector()
            print("✅ WeedDetector initialisiert")
        else:
            self.detector = None
            print("❌ WeedDetector nicht verfügbar")
        
        # Kamera initialisieren
        if HAS_CAMERA:
            try:
                self.camera = CameraManager()
                print("✅ CameraManager initialisiert")
            except Exception as e:
                print(f"⚠️ CameraManager Init fehlgeschlagen: {e}")
                self.camera = None
        else:
            self.camera = None
    
    def create_test_images(self):
        """Einfache Test-Bilder erstellen"""
        test_images = {}
        
        print("📸 Erstelle Test-Bilder...")
        
        # 1. Einfaches Gras mit Unkraut
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Gras-Hintergrund
        image[:, :] = [30, 100, 30]  # Dunkelgrün
        
        # Unkraut-Flecken (helleres Grün)
        positions = [(150, 200), (400, 180), (320, 350), (500, 120)]
        for x, y in positions:
            radius = random.randint(25, 45)
            color = [50, 180, 50]  # Hellgrün
            cv2.circle(image, (x, y), radius, color, -1)
            
            # Kleine Satelliten
            for _ in range(3):
                offset_x = random.randint(-30, 30)
                offset_y = random.randint(-30, 30)
                small_radius = random.randint(8, 15)
                cv2.circle(image, (x + offset_x, y + offset_y), small_radius, color, -1)
        
        test_images['grass_with_weeds'] = image
        
        # 2. Schwieriges Bild mit verschiedenen Grüntönen
        complex_image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Verschiedene Grün-Bereiche
        complex_image[0:240, 0:320] = [25, 80, 25]     # Sehr dunkel
        complex_image[0:240, 320:640] = [45, 140, 45]  # Mittel
        complex_image[240:480, 0:320] = [65, 200, 65]  # Hell
        complex_image[240:480, 320:640] = [35, 110, 35] # Gemischt
        
        # Unkräuter in verschiedenen Bereichen
        cv2.circle(complex_image, (100, 100), 20, (70, 220, 70), -1)   # Sehr hell
        cv2.circle(complex_image, (500, 100), 30, (40, 160, 40), -1)   # Mittel
        cv2.circle(complex_image, (100, 350), 25, (80, 240, 80), -1)   # Hell
        cv2.circle(complex_image, (500, 350), 35, (30, 120, 30), -1)   # Dunkel
        
        test_images['complex_greens'] = complex_image
        
        # 3. Realistisches Feld
        realistic = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Boden mit Textur
        realistic[:, :] = [20, 70, 20]
        
        # Rauschen
        noise = np.random.randint(-10, 10, (480, 640, 3))
        realistic = np.clip(realistic.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        
        # Realistische Unkraut-Cluster
        clusters = [(180, 150), (420, 200), (300, 320), (520, 180)]
        for cx, cy in clusters:
            # Hauptunkraut
            main_radius = random.randint(20, 40)
            cv2.circle(realistic, (cx, cy), main_radius, (45, 165, 45), -1)
            
            # Umgebung
            for _ in range(random.randint(2, 5)):
                offset_x = random.randint(-50, 50)
                offset_y = random.randint(-50, 50)
                radius = random.randint(5, 15)
                brightness = random.randint(30, 60)
                color = (brightness, brightness + 80, brightness)
                cv2.circle(realistic, (cx + offset_x, cy + offset_y), radius, color, -1)
        
        test_images['realistic_field'] = realistic
        
        # Bilder speichern
        for name, img in test_images.items():
            filename = os.path.join(self.output_dir, f"test_image_{name}.jpg")
            cv2.imwrite(filename, img)
            print(f"   💾 {filename}")
        
        return test_images
    
    def test_basic_detection(self):
        """Basis-Erkennung testen"""
        print("\n🔍 Teste Basis-Erkennung...")
        print("=" * 40)
        
        if not self.detector:
            print("❌ Kein Detector verfügbar")
            return
        
        # Test-Bilder erstellen
        test_images = self.create_test_images()
        
        # Jedes Bild testen
        for name, image in test_images.items():
            print(f"\n📊 Teste Bild: {name}")
            
            start_time = time.time()
            result = self.detector.detect_in_image(image)
            end_time = time.time()
            
            print(f"   Erkennungen: {result.get('count', 0)}")
            print(f"   Durchschnittliche Konfidenz: {result.get('confidence', 0):.3f}")
            print(f"   Verarbeitungszeit: {end_time - start_time:.3f}s")
            print(f"   Methode: {result.get('method', 'unknown')}")
            
            # Detailierte Ergebnisse
            detections = result.get('detections', [])
            for i, detection in enumerate(detections[:3]):  # Max 3 anzeigen
                print(f"   Unkraut {i+1}: Konfidenz {detection.get('confidence', 0):.3f}, "
                      f"Position ({detection.get('x', 0)}, {detection.get('y', 0)}), "
                      f"Größe {detection.get('area', 0)}px²")
            
            # Ergebnis-Bild speichern
            if hasattr(self.detector, 'draw_detections'):
                try:
                    marked_image = self.detector.draw_detections(image, detections)
                    filename = os.path.join(self.output_dir, f"result_{name}.jpg")
                    cv2.imwrite(filename, marked_image)
                    print(f"   💾 Ergebnis: {filename}")
                except Exception as e:
                    print(f"   ⚠️ Ergebnis-Bild nicht gespeichert: {e}")
    
    def test_mock_detection(self):
        """Mock-Erkennung testen"""
        print("\n🎭 Teste Mock-Erkennung...")
        print("=" * 40)
        
        if not self.detector:
            print("❌ Kein Detector verfügbar")
            return
        
        # Mock-Test mit zufälligen Bildern
        for i in range(3):
            print(f"\n🎯 Mock-Test {i+1}:")
            
            # Zufälliges Test-Bild erstellen
            test_image = np.zeros((480, 640, 3), dtype=np.uint8)
            test_image[:, :] = [random.randint(20, 50), random.randint(80, 150), random.randint(20, 50)]
            
            # Mock-Erkennung
            result = self.detector.detect_in_image(test_image)
            
            print(f"   Erkennungen: {result.get('count', 0)}")
            print(f"   Konfidenz: {result.get('confidence', 0):.3f}")
            print(f"   Methode: {result.get('method', 'unknown')}")
            
            # Erwarte Mock-Daten
            detections = result.get('detections', [])
            if detections:
                detection = detections[0]
                has_mock = detection.get('mock', False)
                print(f"   Mock-Modus: {has_mock}")
    
    def test_camera_integration(self):
        """Kamera-Integration testen"""
        print("\n📷 Teste Kamera-Integration...")
        print("=" * 40)
        
        if not self.camera:
            print("❌ Kein CameraManager verfügbar")
            return
        
        if not self.detector:
            print("❌ Kein Detector verfügbar")
            return
        
        try:
            # Kamera-Frame holen
            frame_data = self.camera.get_frame()
            
            if frame_data and len(frame_data) > 1000:
                print("✅ Kamera-Frame erhalten")
                
                # Frame dekodieren
                nparr = np.frombuffer(frame_data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if frame is not None:
                    print(f"📊 Frame-Größe: {frame.shape}")
                    
                    # Erkennung durchführen
                    result = self.detector.detect_in_image(frame)
                    
                    print(f"🔍 Erkennungen: {result.get('count', 0)}")
                    print(f"📈 Konfidenz: {result.get('confidence', 0):.3f}")
                    
                    # Frame speichern
                    filename = os.path.join(self.output_dir, "camera_test.jpg")
                    cv2.imwrite(filename, frame)
                    print(f"💾 Frame gespeichert: {filename}")
                    
                    # Ergebnis speichern
                    if hasattr(self.detector, 'draw_detections'):
                        detections = result.get('detections', [])
                        marked_frame = self.detector.draw_detections(frame, detections)
                        result_filename = os.path.join(self.output_dir, "camera_result.jpg")
                        cv2.imwrite(result_filename, marked_frame)
                        print(f"💾 Ergebnis gespeichert: {result_filename}")
                else:
                    print("❌ Frame-Dekodierung fehlgeschlagen")
            else:
                print("⚠️ Kein gültiger Frame erhalten - verwende Mock")
        
        except Exception as e:
            print(f"❌ Kamera-Test fehlgeschlagen: {e}")
    
    def test_performance(self):
        """Performance-Test"""
        print("\n⚡ Performance-Test...")
        print("=" * 40)
        
        if not self.detector:
            print("❌ Kein Detector verfügbar")
            return
        
        # Test-Bild erstellen
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        test_image[:, :] = [30, 120, 30]
        
        # Unkräuter hinzufügen
        for _ in range(5):
            x = random.randint(50, 590)
            y = random.randint(50, 430)
            radius = random.randint(20, 40)
            cv2.circle(test_image, (x, y), radius, (60, 200, 60), -1)
        
        # Performance-Test
        num_tests = 20
        times = []
        
        print(f"🚀 Führe {num_tests} Erkennungen durch...")
        
        for i in range(num_tests):
            start = time.time()
            result = self.detector.detect_in_image(test_image)
            end = time.time()
            
            times.append(end - start)
            
            if (i + 1) % 5 == 0:
                print(f"   {i + 1}/{num_tests} abgeschlossen...")
        
        # Statistiken
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"\n📊 Performance-Ergebnisse:")
        print(f"   Durchschnitt: {avg_time * 1000:.1f}ms")
        print(f"   Minimum: {min_time * 1000:.1f}ms")
        print(f"   Maximum: {max_time * 1000:.1f}ms")
        print(f"   FPS: {1/avg_time:.1f}")
    
    def run_all_tests(self):
        """Alle Tests ausführen"""
        print("🌱 Unkraut-2025 - Grün-Erkennungstest")
        print("=" * 50)
        print(f"📂 Output-Verzeichnis: {self.output_dir}")
        
        # System-Info
        print(f"\n🔧 System-Status:")
        print(f"   WeedDetector: {'✅' if HAS_WEED_DETECTOR else '❌'}")
        print(f"   CameraManager: {'✅' if HAS_CAMERA else '❌'}")
        print(f"   OpenCV: {'✅' if 'cv2' in sys.modules else '❌'}")
        print(f"   NumPy: {'✅' if 'numpy' in sys.modules else '❌'}")
        
        # Tests ausführen
        self.test_basic_detection()
        self.test_mock_detection()
        self.test_camera_integration()
        self.test_performance()
        
        print(f"\n✅ Alle Tests abgeschlossen!")
        print(f"📁 Ergebnisse verfügbar in: {self.output_dir}")
        
        # Verfügbare Dateien auflisten
        if os.path.exists(self.output_dir):
            files = os.listdir(self.output_dir)
            if files:
                print(f"\n📋 Erstelle Dateien ({len(files)}):")
                for f in sorted(files):
                    print(f"   📄 {f}")

def main():
    """Hauptfunktion"""
    tester = SimpleGreenDetectionTester()
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == 'basic':
            tester.test_basic_detection()
        elif mode == 'mock':
            tester.test_mock_detection()
        elif mode == 'camera':
            tester.test_camera_integration()
        elif mode == 'performance':
            tester.test_performance()
        else:
            print(f"❌ Unbekannter Modus: {mode}")
            print("Verfügbare Modi: basic, mock, camera, performance")
    else:
        tester.run_all_tests()

if __name__ == "__main__":
    main()
