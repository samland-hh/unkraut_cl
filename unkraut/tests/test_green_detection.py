# unkraut/test/test_green_detection.py
"""
Test-Script für Grün-Erkennung und Mock-Funktionen
Zeigt verschiedene Erkennungsszenarien und Konfigurationen
"""
import cv2
import numpy as np
import os
import sys
import time
from datetime import datetime

# Pfad zum Projekt-Root hinzufügen
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from ai.weed_detection_optimized import WeedDetector
    from test.mock_weed_detection import MockWeedDetector
    OPTIMIZED_AVAILABLE = True
except ImportError:
    print("⚠️ Optimierte Module nicht gefunden - verwende Basis-Implementierung")
    OPTIMIZED_AVAILABLE = False

class GreenDetectionTester:
    """Test-Klasse für Grün-Erkennung"""
    
    def __init__(self):
        self.test_results = []
        self.output_dir = "unkraut/test/output"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Detektoren initialisieren
        if OPTIMIZED_AVAILABLE:
            self.detector = WeedDetector()
            self.mock_detector = MockWeedDetector()
        else:
            print("❌ Optimierte Detektoren nicht verfügbar")
            self.detector = None
            self.mock_detector = None
    
    def create_test_images(self):
        """Verschiedene Test-Bilder erstellen"""
        test_images = {}
        
        # 1. Einfaches Gras-Bild
        grass_image = np.zeros((480, 640, 3), dtype=np.uint8)
        grass_image[:, :] = [40, 120, 40]  # Dunkelgrün
        
        # Einige hellere Gras-Flecken
        for _ in range(5):
            x = np.random.randint(50, 590)
            y = np.random.randint(50, 430)
            radius = np.random.randint(20, 60)
            cv2.circle(grass_image, (x, y), radius, (50, 180, 50), -1)
        
        test_images['simple_grass'] = grass_image
        
        # 2. Gras mit deutlichen Unkräutern
        weed_image = grass_image.copy()
        
        # Große Unkräuter (helleres Grün)
        weed_positions = [(150, 200), (400, 150), (500, 350), (200, 380)]
        for x, y in weed_positions:
            radius = np.random.randint(30, 50)
            cv2.circle(weed_image, (x, y), radius, (60, 220, 60), -1)
            
            # Kleine Satelliten-Unkräuter
            for _ in range(3):
                offset_x = np.random.randint(-40, 40)
                offset_y = np.random.randint(-40, 40)
                small_radius = np.random.randint(8, 15)
                cv2.circle(weed_image, (x + offset_x, y + offset_y), small_radius, (70, 240, 70), -1)
        
        test_images['grass_with_weeds'] = weed_image
        
        # 3. Schwieriges Bild mit verschiedenen Grüntönen
        complex_image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Verschiedene Grün-Bereiche
        complex_image[0:240, 0:320] = [30, 100, 30]    # Dunkelgrün
        complex_image[0:240, 320:640] = [50, 150, 50]  # Mittelgrün
        complex_image[240:480, 0:320] = [70, 200, 70]  # Hellgrün
        complex_image[240:480, 320:640] = [40, 130, 40] # Gemischtes Grün
        
        # Unkräuter in verschiedenen Bereichen
        cv2.circle(complex_image, (100, 100), 25, (80, 255, 80), -1)  # Sehr hell
        cv2.circle(complex_image, (500, 100), 35, (45, 180, 45), -1)  # Mittel
        cv2.circle(complex_image, (100, 350), 30, (90, 220, 90), -1)  # Hell
        cv2.circle(complex_image, (500, 350), 40, (35, 140, 35), -1)  # Dunkel
        
        test_images['complex_greens'] = complex_image
        
        # 4. Realistische Aufnahme simulieren
        realistic_image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Boden-Textur
        realistic_image[:, :] = [25, 80, 25]  # Dunkelgrüner Boden
        
        # Rauschen hinzufügen
        noise = np.random.randint(-15, 15, (480, 640, 3))
        realistic_image = np.clip(realistic_image.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        
        # Realistische Unkraut-Cluster
        cluster_centers = [(120, 180), (380, 220), (500, 120), (200, 350), (450, 380)]
        
        for center_x, center_y in cluster_centers:
            # Hauptunkraut
            main_radius = np.random.randint(25, 45)
            cv2.circle(realistic_image, (center_x, center_y), main_radius, (55, 190, 55), -1)
            
            # Umgebende kleine Unkräuter
            for _ in range(np.random.randint(3, 8)):
                offset_x = np.random.randint(-60, 60)
                offset_y = np.random.randint(-60, 60)
                small_radius = np.random.randint(8, 20)
                brightness = np.random.randint(40, 80)
                color = (brightness, brightness + 100, brightness)
                cv2.circle(realistic_image, (center_x + offset_x, center_y + offset_y), 
                          small_radius, color, -1)
        
        test_images['realistic_field'] = realistic_image
        
        test_images['realistic_field'] = realistic_image
        
        return test_images
    
    def test_green_profiles(self):
        """Verschiedene Grün-Profile testen"""
        if not OPTIMIZED_AVAILABLE:
            print("❌ Optimierte Detektoren nicht verfügbar")
            return
        
        print("🎨 Teste verschiedene Grün-Profile...")
        print("=" * 50)
        
        # Test-Bild erstellen
        test_images = self.create_test_images()
        test_image = test_images['grass_with_weeds']
        
        # Verfügbare Profile testen
        profiles = ['bright', 'dark', 'mixed']
        
        for profile in profiles:
            print(f"\n🔍 Teste Profil: {profile}")
            
            # Profil setzen
            self.detector.change_green_profile(profile)
            
            # Erkennung durchführen
            result = self.detector.detect_in_image(test_image)
            
            # Ergebnis ausgeben
            print(f"   Erkennungen: {result['count']}")
            print(f"   Durchschnittliche Konfidenz: {result['confidence']:.3f}")
            print(f"   Verarbeitungszeit: {result['processing_time']:.3f}s")
            
            # Bild mit Erkennungen speichern
            marked_image = self.detector.draw_detections(test_image, result['detections'])
            filename = f"{self.output_dir}/profile_{profile}_test.jpg"
            cv2.imwrite(filename, marked_image)
            print(f"   Gespeichert: {filename}")
    
    def test_sensitivity_settings(self):
        """Verschiedene Empfindlichkeits-Einstellungen testen"""
        if not OPTIMIZED_AVAILABLE:
            print("❌ Optimierte Detektoren nicht verfügbar")
            return
        
        print("\n⚡ Teste Empfindlichkeits-Einstellungen...")
        print("=" * 50)
        
        test_images = self.create_test_images()
        test_image = test_images['complex_greens']
        
        # Verschiedene Empfindlichkeiten testen
        sensitivities = [0.3, 0.5, 0.7, 0.9]
        
        for sensitivity in sensitivities:
            print(f"\n📊 Empfindlichkeit: {sensitivity}")
            
            # Einstellungen aktualisieren
            self.detector.update_settings({'sensitivity': sensitivity})
            
            # Erkennung durchführen
            result = self.detector.detect_in_image(test_image)
            
            # Ergebnis ausgeben
            print(f"   Erkennungen: {result['count']}")
            print(f"   Konfidenz: {result['confidence']:.3f}")
            
            # Detailierte Ergebnisse
            if result['detections']:
                for i, detection in enumerate(result['detections']):
                    print(f"   Unkraut {i+1}: {detection['subclass']}, "
                          f"Konfidenz: {detection['confidence']:.3f}, "
                          f"Größe: {detection['area']}px²")
    
    def test_mock_scenarios(self):
        """Mock-Szenarien testen"""
        if not OPTIMIZED_AVAILABLE:
            print("❌ Mock-Detektor nicht verfügbar")
            return
        
        print("\n🎭 Teste Mock-Szenarien...")
        print("=" * 50)
        
        scenarios = ['empty_field', 'light_infestation', 'medium_infestation', 'heavy_infestation']
        
        for scenario in scenarios:
            print(f"\n🎯 Szenario: {scenario}")
            
            # Mock-Bild erstellen
            mock_image = self.mock_detector.create_mock_image(scenario_name=scenario)
            
            # Echte Erkennung
            real_result = self.detector.detect_in_image(mock_image)
            
            # Mock-Erkennung
            mock_result = self.mock_detector.detect_in_image(mock_image)
            
            print(f"   Echte Erkennung: {real_result['count']} Unkräuter, "
                  f"Konfidenz: {real_result['confidence']:.3f}")
            print(f"   Mock-Erkennung: {mock_result['count']} Unkräuter, "
                  f"Konfidenz: {mock_result['confidence']:.3f}")
            
            # Bilder speichern
            real_marked = self.detector.draw_detections(mock_image, real_result['detections'])
            cv2.imwrite(f"{self.output_dir}/real_{scenario}.jpg", real_marked)
            
            # Mock-Bild mit Mock-Markierungen (simuliert)
            mock_marked = mock_image.copy()
            for detection in mock_result['detections']:
                bbox = detection['bbox']
                cv2.rectangle(mock_marked, (bbox['x'], bbox['y']), 
                            (bbox['x'] + bbox['width'], bbox['y'] + bbox['height']), 
                            (0, 0, 255), 2)  # Rot für Mock
            cv2.imwrite(f"{self.output_dir}/mock_{scenario}.jpg", mock_marked)
    
    def performance_benchmark(self):
        """Performance-Benchmark durchführen"""
        print("\n⚡ Performance-Benchmark...")
        print("=" * 50)
        
        # Test-Bild erstellen
        test_images = self.create_test_images()
        test_image = test_images['realistic_field']
        
        # Benchmark-Parameter
        num_iterations = 50
        
        print(f"Führe {num_iterations} Erkennungen durch...")
        
        # Echte Erkennung benchmarken
        if OPTIMIZED_AVAILABLE:
            start_time = time.time()
            for i in range(num_iterations):
                result = self.detector.detect_in_image(test_image)
                if (i + 1) % 10 == 0:
                    print(f"   {i + 1}/{num_iterations} Erkennungen...")
            
            real_time = time.time() - start_time
            
            print(f"\n📊 Echte Erkennung:")
            print(f"   Gesamtzeit: {real_time:.2f}s")
            print(f"   Durchschnitt: {real_time/num_iterations*1000:.1f}ms pro Erkennung")
            print(f"   FPS: {num_iterations/real_time:.1f}")
        
        # Mock-Erkennung benchmarken
        if OPTIMIZED_AVAILABLE:
            start_time = time.time()
            for i in range(num_iterations):
                result = self.mock_detector.detect_in_image(test_image)
            
            mock_time = time.time() - start_time
            
            print(f"\n🎭 Mock-Erkennung:")
            print(f"   Gesamtzeit: {mock_time:.2f}s")
            print(f"   Durchschnitt: {mock_time/num_iterations*1000:.1f}ms pro Erkennung")
            print(f"   FPS: {num_iterations/mock_time:.1f}")
    
    def comprehensive_test(self):
        """Umfassender Test aller Funktionen"""
        print("🚀 Umfassender Grün-Erkennungstest")
        print("=" * 60)
        
        # Test-Bilder erstellen und speichern
        print("\n📸 Erstelle Test-Bilder...")
        test_images = self.create_test_images()
        
        for name, image in test_images.items():
            filename = f"{self.output_dir}/test_image_{name}.jpg"
            cv2.imwrite(filename, image)
            print(f"   Gespeichert: {filename}")
        
        # Einzelne Tests durchführen
        if OPTIMIZED_AVAILABLE:
            self.test_green_profiles()
            self.test_sensitivity_settings()
            self.test_mock_scenarios()
            self.performance_benchmark()
            
            # Statistiken ausgeben
            print("\n📈 Detector-Statistiken:")
            stats = self.detector.get_statistics()
            for key, value in stats.items():
                print(f"   {key}: {value}")
            
            # Mock-Statistiken
            print("\n🎭 Mock-Statistiken:")
            mock_stats = self.mock_detector.stats
            for key, value in mock_stats.items():
                print(f"   {key}: {value}")
        
        print(f"\n✅ Alle Tests abgeschlossen! Ergebnisse in: {self.output_dir}")
    
    def interactive_test(self):
        """Interaktiver Test-Modus"""
        print("\n🎮 Interaktiver Test-Modus")
        print("=" * 40)
        
        if not OPTIMIZED_AVAILABLE:
            print("❌ Optimierte Detektoren nicht verfügbar")
            return
        
        test_images = self.create_test_images()
        
        while True:
            print("\nVerfügbare Optionen:")
            print("1. Grün-Profile testen")
            print("2. Empfindlichkeit ändern")
            print("3. Mock-Szenario testen")
            print("4. Test-Bild anzeigen")
            print("5. Performance-Test")
            print("6. Einstellungen anzeigen")
            print("0. Beenden")
            
            choice = input("\nWahl (0-6): ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                self.test_green_profiles()
            elif choice == '2':
                sens = input("Empfindlichkeit (0.1-1.0): ").strip()
                try:
                    sensitivity = float(sens)
                    if 0.1 <= sensitivity <= 1.0:
                        self.detector.update_settings({'sensitivity': sensitivity})
                        print(f"✅ Empfindlichkeit auf {sensitivity} gesetzt")
                    else:
                        print("❌ Wert muss zwischen 0.1 und 1.0 liegen")
                except ValueError:
                    print("❌ Ungültiger Wert")
            elif choice == '3':
                print("Verfügbare Szenarien:")
                scenarios = list(self.mock_detector.scenarios.keys())
                for i, scenario in enumerate(scenarios):
                    print(f"  {i+1}. {scenario}")
                
                try:
                    scenario_idx = int(input("Szenario-Nummer: ")) - 1
                    if 0 <= scenario_idx < len(scenarios):
                        scenario = scenarios[scenario_idx]
                        self.mock_detector.set_scenario(scenario)
                        
                        # Test durchführen
                        mock_image = self.mock_detector.create_mock_image(scenario_name=scenario)
                        result = self.detector.detect_in_image(mock_image)
                        
                        print(f"✅ Szenario {scenario}: {result['count']} Erkennungen")
                    else:
                        print("❌ Ungültige Nummer")
                except ValueError:
                    print("❌ Ungültige Eingabe")
            elif choice == '4':
                print("Verfügbare Test-Bilder:")
                for i, name in enumerate(test_images.keys()):
                    print(f"  {i+1}. {name}")
                
                try:
                    img_idx = int(input("Bild-Nummer: ")) - 1
                    img_names = list(test_images.keys())
                    if 0 <= img_idx < len(img_names):
                        img_name = img_names[img_idx]
                        test_image = test_images[img_name]
                        
                        result = self.detector.detect_in_image(test_image)
                        print(f"✅ Bild {img_name}: {result['count']} Erkennungen")
                        
                        # Bild mit Markierungen speichern
                        marked = self.detector.draw_detections(test_image, result['detections'])
                        filename = f"{self.output_dir}/interactive_{img_name}.jpg"
                        cv2.imwrite(filename, marked)
                        print(f"Gespeichert: {filename}")
                    else:
                        print("❌ Ungültige Nummer")
                except ValueError:
                    print("❌ Ungültige Eingabe")
            elif choice == '5':
                self.performance_benchmark()
            elif choice == '6':
                stats = self.detector.get_statistics()
                print("\n📊 Aktuelle Einstellungen:")
                for key, value in stats.items():
                    print(f"   {key}: {value}")
            else:
                print("❌ Ungültige Option")

def main():
    """Hauptfunktion"""
    print("🌱 Unkraut-2025 - Grün-Erkennungstest")
    print("=" * 50)
    
    # Tester initialisieren
    tester = GreenDetectionTester()
    
    # Kommandozeilen-Argument prüfen
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == 'quick':
            print("⚡ Schnelltest...")
            tester.test_green_profiles()
        elif mode == 'performance':
            print("🚀 Performance-Test...")
            tester.performance_benchmark()
        elif mode == 'interactive':
            print("🎮 Interaktiver Modus...")
            tester.interactive_test()
        elif mode == 'mock':
            print("🎭 Mock-Tests...")
            tester.test_mock_scenarios()
        else:
            print(f"❌ Unbekannter Modus: {mode}")
            print("Verfügbare Modi: quick, performance, interactive, mock")
    else:
        # Vollständiger Test
        tester.comprehensive_test()

if __name__ == "__main__":
    main()