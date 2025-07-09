# unkraut/test/test_green_detection_improved.py
"""
Verbessertes Test-Script für Grün-Erkennung
Behebt Hardware-Initialisierungsprobleme und verbessert Tests
"""
import cv2
import numpy as np
import os
import sys
import time
import random
from datetime import datetime

# Pfad-Setup
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

print(f"🔍 Projekt-Root: {project_root}")

# Hardware-Initialisierung nur einmal
HARDWARE_INITIALIZED = False
detector = None
camera = None

def init_hardware():
    """Hardware nur einmal initialisieren"""
    global HARDWARE_INITIALIZED, detector, camera
    
    if HARDWARE_INITIALIZED:
        return detector, camera
    
    print("🔧 Initialisiere Hardware...")
    
    # WeedDetector
    try:
        from ai.weed_detection import WeedDetector
        detector = WeedDetector()
        detector.debug_mode = False  # Weniger Debug-Output
        print("✅ WeedDetector initialisiert")
    except ImportError as e:
        print(f"❌ WeedDetector Import fehlgeschlagen: {e}")
        detector = None
    
    # CameraManager
    try:
        from hardware.camera import CameraManager
        camera = CameraManager()
        camera.debug_mode = False  # Weniger Debug-Output
        print("✅ CameraManager initialisiert")
    except ImportError as e:
        print(f"❌ CameraManager Import fehlgeschlagen: {e}")
        camera = None
    except Exception as e:
        print(f"⚠️ CameraManager Init fehlgeschlagen: {e}")
        camera = None
    
    HARDWARE_INITIALIZED = True
    return detector, camera

class ImprovedGreenDetectionTester:
    """Verbesserter Tester mit Hardware-Optimierung"""
    
    def __init__(self):
        self.output_dir = os.path.join(project_root, "test", "output")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Hardware nur einmal initialisieren
        self.detector, self.camera = init_hardware()
        
        # Test-Statistiken
        self.test_results = []
    
    def create_realistic_test_images(self):
        """Realistische Test-Bilder mit verschiedenen Szenarien"""
        test_images = {}
        
        print("📸 Erstelle realistische Test-Bilder...")
        
        # 1. Leichter Unkrautbefall
        light_image = np.zeros((480, 640, 3), dtype=np.uint8)
        light_image[:, :] = [25, 90, 25]  # Dunkler Gras-Hintergrund
        
        # Wenige große Unkräuter
        positions = [(180, 200), (450, 180)]
        for x, y in positions:
            radius = random.randint(30, 50)
            # Helleres Grün für Unkraut
            color = [40, 160, 40]
            cv2.circle(light_image, (x, y), radius, color, -1)
            
            # Kleine Satelliten
            for _ in range(2):
                offset_x = random.randint(-25, 25)
                offset_y = random.randint(-25, 25)
                small_radius = random.randint(8, 15)
                cv2.circle(light_image, (x + offset_x, y + offset_y), small_radius, color, -1)
        
        test_images['light_infestation'] = light_image
        
        # 2. Starker Unkrautbefall
        heavy_image = np.zeros((480, 640, 3), dtype=np.uint8)
        heavy_image[:, :] = [30, 110, 30]  # Mittelgrüner Hintergrund
        
        # Viele Unkräuter verschiedener Größen
        cluster_centers = [(120, 150), (300, 120), (480, 200), (200, 320), (520, 350)]
        for cx, cy in cluster_centers:
            # Hauptunkraut
            main_radius = random.randint(20, 45)
            main_color = [50, 180, 50]
            cv2.circle(heavy_image, (cx, cy), main_radius, main_color, -1)
            
            # Umgebende Unkräuter
            for _ in range(random.randint(3, 6)):
                offset_x = random.randint(-60, 60)
                offset_y = random.randint(-60, 60)
                radius = random.randint(10, 25)
                brightness = random.randint(35, 65)
                color = [brightness, brightness + 100, brightness]
                cv2.circle(heavy_image, (cx + offset_x, cy + offset_y), radius, color, -1)
        
        test_images['heavy_infestation'] = heavy_image
        
        # 3. Gemischte Grüntöne (schwierig)
        mixed_image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Verschiedene Hintergrund-Bereiche
        mixed_image[0:240, 0:320] = [20, 80, 20]     # Sehr dunkel
        mixed_image[0:240, 320:640] = [40, 140, 40]   # Mittel
        mixed_image[240:480, 0:320] = [60, 180, 60]   # Hell
        mixed_image[240:480, 320:640] = [30, 100, 30] # Gemischt
        
        # Unkräuter in verschiedenen Bereichen (verschiedene Kontraste)
        mixed_positions = [
            (100, 100, [70, 200, 70]),   # Hell auf dunkel
            (500, 100, [25, 90, 25]),    # Dunkel auf mittel
            (100, 350, [80, 220, 80]),   # Sehr hell auf hell
            (500, 350, [45, 120, 45])    # Mittel auf gemischt
        ]
        
        for x, y, color in mixed_positions:
            radius = random.randint(20, 35)
            cv2.circle(mixed_image, (x, y), radius, color, -1)
        
        test_images['mixed_contrasts'] = mixed_image
        
        # 4. Kleine Unkräuter (Grenzfall)
        small_image = np.zeros((480, 640, 3), dtype=np.uint8)
        small_image[:, :] = [35, 120, 35]
        
        # Viele kleine Unkräuter
        for _ in range(8):
            x = random.randint(50, 590)
            y = random.randint(50, 430)
            radius = random.randint(8, 20)  # Sehr klein
            color = [55, 170, 55]
            cv2.circle(small_image, (x, y), radius, color, -1)
        
        test_images['small_weeds'] = small_image
        
        # Bilder speichern
        for name, img in test_images.items():
            filename = os.path.join(self.output_dir, f"test_{name}.jpg")
            cv2.imwrite(filename, img)
            print(f"   💾 {filename}")
        
        return test_images
    
    def test_detection_scenarios(self):
        """Verschiedene Erkennungsszenarien testen"""
        print("\n🎯 Teste Erkennungsszenarien...")
        print("=" * 50)
        
        if not self.detector:
            print("❌ Kein Detector verfügbar")
            return
        
        # Test-Bilder erstellen
        test_images = self.create_realistic_test_images()
        
        scenario_results = []
        
        for name, image in test_images.items():
            print(f"\n📊 Szenario: {name}")
            print("-" * 30)
            
            # Mehrere Tests pro Szenario
            scenario_detections = []
            scenario_times = []
            
            for i in range(3):  # 3 Tests pro Szenario
                start_time = time.time()
                result = self.detector.detect_in_image(image)
                end_time = time.time()
                
                scenario_detections.append(result.get('count', 0))
                scenario_times.append(end_time - start_time)
                
                if i == 0:  # Detaillierte Ausgabe nur beim ersten Test
                    print(f"   Erkennungen: {result.get('count', 0)}")
                    print(f"   Konfidenz: {result.get('confidence', 0):.3f}")
                    print(f"   Methode: {result.get('method', 'unknown')}")
                    print(f"   Zeit: {end_time - start_time:.3f}s")
                    
                    # Detaillierte Ergebnisse
                    detections = result.get('detections', [])
                    for j, detection in enumerate(detections[:2]):  # Max 2 anzeigen
                        print(f"   • Unkraut {j+1}: {detection.get('subclass', 'unknown')}, "
                              f"Konfidenz {detection.get('confidence', 0):.3f}, "
                              f"Größe {detection.get('area', 0)}px²")
                    
                    # Erstes Ergebnis-Bild speichern
                    if hasattr(self.detector, 'draw_detections'):
                        marked_image = self.detector.draw_detections(image, detections)
                        filename = os.path.join(self.output_dir, f"result_{name}.jpg")
                        cv2.imwrite(filename, marked_image)
                        print(f"   💾 {filename}")
            
            # Statistiken für Szenario
            avg_detections = sum(scenario_detections) / len(scenario_detections)
            avg_time = sum(scenario_times) / len(scenario_times)
            
            print(f"   📈 Durchschnitt: {avg_detections:.1f} Erkennungen in {avg_time:.3f}s")
            
            scenario_results.append({
                'name': name,
                'avg_detections': avg_detections,
                'avg_time': avg_time,
                'consistency': len(set(scenario_detections)) == 1  # Alle gleich?
            })
        
        # Gesamtstatistiken
        print(f"\n📋 Gesamtstatistiken:")
        for result in scenario_results:
            consistency = "✅ Konsistent" if result['consistency'] else "⚠️ Variabel"
            print(f"   {result['name']}: {result['avg_detections']:.1f} Erkennungen, "
                  f"{result['avg_time']:.3f}s, {consistency}")
        
        return scenario_results
    
    def test_sensitivity_adjustment(self):
        """Empfindlichkeits-Anpassung testen"""
        print("\n⚡ Teste Empfindlichkeits-Anpassung...")
        print("=" * 50)
        
        if not self.detector or not hasattr(self.detector, 'sensitivity'):
            print("❌ Empfindlichkeits-Anpassung nicht verfügbar")
            return
        
        # Test-Bild mit mittlerem Unkrautbefall
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        test_image[:, :] = [35, 120, 35]
        
        # Verschiedene Unkraut-Größen
        positions = [(150, 150, 25), (350, 200, 40), (500, 300, 15)]  # (x, y, radius)
        for x, y, radius in positions:
            color = [55, 170, 55]
            cv2.circle(test_image, (x, y), radius, color, -1)
        
        # Verschiedene Empfindlichkeiten testen
        sensitivities = [0.3, 0.5, 0.7, 0.9]
        
        for sensitivity in sensitivities:
            print(f"\n🎚️ Empfindlichkeit: {sensitivity}")
            
            # Einstellung ändern
            if hasattr(self.detector, 'sensitivity'):
                self.detector.sensitivity = sensitivity
            
            # Test durchführen
            result = self.detector.detect_in_image(test_image)
            
            print(f"   Erkennungen: {result.get('count', 0)}")
            print(f"   Konfidenz: {result.get('confidence', 0):.3f}")
            
            # Ergebnis speichern
            if hasattr(self.detector, 'draw_detections'):
                detections = result.get('detections', [])
                marked_image = self.detector.draw_detections(test_image, detections)
                filename = os.path.join(self.output_dir, f"sensitivity_{sensitivity}.jpg")
                cv2.imwrite(filename, marked_image)
                print(f"   💾 {filename}")
    
    def test_camera_detection(self):
        """Kamera-Erkennung testen (falls verfügbar)"""
        print("\n📷 Teste Kamera-Erkennung...")
        print("=" * 50)
        
        if not self.camera:
            print("❌ Kein CameraManager verfügbar")
            return
        
        if not self.detector:
            print("❌ Kein Detector verfügbar")
            return
        
        try:
            print("📸 Versuche Kamera-Frame zu erfassen...")
            
            # Frame erfassen
            frame_data = self.camera.get_frame()
            
            if frame_data and len(frame_data) > 1000:
                print("✅ Kamera-Frame erfolgreich erhalten")
                
                # Frame dekodieren
                nparr = np.frombuffer(frame_data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if frame is not None:
                    print(f"📊 Frame-Größe: {frame.shape}")
                    
                    # Erkennung durchführen
                    result = self.detector.detect_in_image(frame)
                    
                    print(f"🔍 Erkennungen: {result.get('count', 0)}")
                    print(f"📈 Konfidenz: {result.get('confidence', 0):.3f}")
                    print(f"🛠️ Methode: {result.get('method', 'unknown')}")
                    
                    # Frame speichern
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    frame_filename = os.path.join(self.output_dir, f"camera_frame_{timestamp}.jpg")
                    cv2.imwrite(frame_filename, frame)
                    print(f"💾 Frame: {frame_filename}")
                    
                    # Ergebnis speichern
                    if hasattr(self.detector, 'draw_detections'):
                        detections = result.get('detections', [])
                        marked_frame = self.detector.draw_detections(frame, detections)
                        result_filename = os.path.join(self.output_dir, f"camera_result_{timestamp}.jpg")
                        cv2.imwrite(result_filename, marked_frame)
                        print(f"💾 Ergebnis: {result_filename}")
                    
                    return True
                else:
                    print("❌ Frame-Dekodierung fehlgeschlagen")
            else:
                print("⚠️ Kein gültiger Frame - möglicherweise Kamera-Problem")
                
        except Exception as e:
            print(f"❌ Kamera-Test fehlgeschlagen: {e}")
            print("💡 Tipp: Prüfe ob Kamera korrekt angeschlossen ist")
        
        return False
    
    def quick_performance_test(self):
        """Schneller Performance-Test"""
        print("\n⚡ Schneller Performance-Test...")
        print("=" * 50)
        
        if not self.detector:
            print("❌ Kein Detector verfügbar")
            return
        
        # Einfaches Test-Bild
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        test_image[:, :] = [30, 120, 30]
        
        # Einige Unkräuter
        for _ in range(3):
            x = random.randint(100, 540)
            y = random.randint(100, 380)
            radius = random.randint(20, 40)
            cv2.circle(test_image, (x, y), radius, (60, 180, 60), -1)
        
        # 10 Tests
        times = []
        detections_counts = []
        
        print("🚀 Führe 10 schnelle Tests durch...")
        
        for i in range(10):
            start = time.time()
            result = self.detector.detect_in_image(test_image)
            end = time.time()
            
            times.append(end - start)
            detections_counts.append(result.get('count', 0))
        
        # Statistiken
        avg_time = sum(times) / len(times)
        avg_detections = sum(detections_counts) / len(detections_counts)
        
        print(f"📊 Ergebnisse:")
        print(f"   Durchschnittliche Zeit: {avg_time * 1000:.1f}ms")
        print(f"   Durchschnittliche Erkennungen: {avg_detections:.1f}")
        print(f"   FPS: {1/avg_time:.1f}")
        print(f"   Konsistenz: {len(set(detections_counts))} verschiedene Ergebnisse")
    
    def run_comprehensive_test(self):
        """Umfassender Test"""
        print("🌱 Unkraut-2025 - Verbesserter Grün-Erkennungstest")
        print("=" * 60)
        print(f"📂 Output-Verzeichnis: {self.output_dir}")
        
        # System-Status
        print(f"\n🔧 System-Status:")
        print(f"   WeedDetector: {'✅' if self.detector else '❌'}")
        print(f"   CameraManager: {'✅' if self.camera else '❌'}")
        print(f"   Hardware initialisiert: {'✅' if HARDWARE_INITIALIZED else '❌'}")
        
        # Tests durchführen
        self.test_detection_scenarios()
        self.test_sensitivity_adjustment()
        self.test_camera_detection()
        self.quick_performance_test()
        
        print(f"\n✅ Alle Tests abgeschlossen!")
        print(f"📁 Ergebnisse verfügbar in: {self.output_dir}")
        
        # Dateien auflisten
        if os.path.exists(self.output_dir):
            files = [f for f in os.listdir(self.output_dir) if f.endswith('.jpg')]
            if files:
                print(f"\n📋 Generierte Bilder ({len(files)}):")
                for f in sorted(files):
                    print(f"   📄 {f}")

def main():
    """Hauptfunktion"""
    tester = ImprovedGreenDetectionTester()
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == 'scenarios':
            tester.test_detection_scenarios()
        elif mode == 'sensitivity':
            tester.test_sensitivity_adjustment()
        elif mode == 'camera':
            tester.test_camera_detection()
        elif mode == 'performance':
            tester.quick_performance_test()
        else:
            print(f"❌ Unbekannter Modus: {mode}")
            print("Verfügbare Modi: scenarios, sensitivity, camera, performance")
    else:
        tester.run_comprehensive_test()

if __name__ == "__main__":
    main()
