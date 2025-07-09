# unkraut/test/mock_weed_detection.py
"""
Mock-System für Unkraut-Erkennung Tests
Simuliert verschiedene Szenarien und Hardware-Zustände
"""
import cv2
import numpy as np
import random
import time
from datetime import datetime
import json
import os

class MockWeedDetector:
    """Mock-Implementierung für Tests ohne echte Hardware"""
    
    def __init__(self):
        self.scenario_mode = 'random'  # random, empty, heavy, progression
        self.current_scenario = 0
        self.detection_count = 0
        self.scenarios = self._create_scenarios()
        self.stats = {
            'total_detections': 0,
            'total_weeds_found': 0,
            'average_confidence': 0.0,
            'session_start': datetime.now()
        }
        print("🎭 Mock-Detektor initialisiert")
    
    def _create_scenarios(self):
        """Verschiedene Test-Szenarien definieren"""
        return {
            'empty_field': {
                'description': 'Leeres Feld - keine Unkräuter',
                'weed_count': 0,
                'confidence_range': (0.0, 0.0),
                'sizes': []
            },
            'light_infestation': {
                'description': 'Leichter Unkrautbefall',
                'weed_count': (1, 2),
                'confidence_range': (0.6, 0.8),
                'sizes': [(20, 40), (30, 50)]
            },
            'medium_infestation': {
                'description': 'Mittlerer Unkrautbefall',
                'weed_count': (2, 4),
                'confidence_range': (0.5, 0.85),
                'sizes': [(25, 45), (35, 60), (40, 70)]
            },
            'heavy_infestation': {
                'description': 'Starker Unkrautbefall',
                'weed_count': (4, 7),
                'confidence_range': (0.4, 0.9),
                'sizes': [(15, 35), (25, 55), (40, 80), (30, 90)]
            },
            'mixed_sizes': {
                'description': 'Gemischte Unkrautgrößen',
                'weed_count': (3, 5),
                'confidence_range': (0.3, 0.95),
                'sizes': [(10, 25), (30, 50), (60, 100), (20, 40)]
            },
            'edge_cases': {
                'description': 'Grenzfälle - sehr kleine/große Objekte',
                'weed_count': (2, 3),
                'confidence_range': (0.2, 0.7),
                'sizes': [(5, 15), (100, 150), (8, 12)]
            }
        }
    
    def set_scenario(self, scenario_name):
        """Szenario manuell setzen"""
        if scenario_name in self.scenarios:
            self.scenario_mode = scenario_name
            print(f"🎯 Szenario gesetzt: {self.scenarios[scenario_name]['description']}")
        else:
            print(f"❌ Unbekanntes Szenario: {scenario_name}")
            print(f"Verfügbare Szenarien: {list(self.scenarios.keys())}")
    
    def detect_in_image(self, image):
        """Mock-Erkennung mit verschiedenen Szenarien"""
        start_time = time.time()
        
        # Szenario auswählen
        if self.scenario_mode == 'random':
            scenario_name = random.choice(list(self.scenarios.keys()))
        elif self.scenario_mode == 'progression':
            scenario_names = list(self.scenarios.keys())
            scenario_name = scenario_names[self.current_scenario % len(scenario_names)]
            self.current_scenario += 1
        else:
            scenario_name = self.scenario_mode
        
        scenario = self.scenarios[scenario_name]
        
        # Erkennungen generieren
        detections = self._generate_detections(image, scenario)
        
        # Statistiken aktualisieren
        self._update_stats(detections)
        
        processing_time = time.time() - start_time
        self.detection_count += 1
        
        # Ergebnis zusammenstellen
        result = {
            'detections': detections,
            'count': len(detections),
            'confidence': self._calculate_average_confidence(detections),
            'processing_time': round(processing_time, 3),
            'timestamp': int(time.time()),
            'detection_id': self.detection_count,
            'image_size': {'width': image.shape[1], 'height': image.shape[0]},
            'method': 'mock_enhanced',
            'scenario': scenario_name,
            'scenario_description': scenario['description'],
            'mock_info': {
                'scenario_mode': self.scenario_mode,
                'current_scenario': self.current_scenario,
                'session_stats': self.stats.copy()
            }
        }
        
        print(f"🔍 Mock-Erkennung #{self.detection_count}: {len(detections)} Unkräuter ({scenario_name})")
        return result
    
    def _generate_detections(self, image, scenario):
        """Erkennungen für Szenario generieren"""
        detections = []
        h, w = image.shape[:2]
        
        # Anzahl Unkräuter bestimmen
        if scenario['weed_count'] == 0:
            return detections
        
        if isinstance(scenario['weed_count'], tuple):
            num_weeds = random.randint(*scenario['weed_count'])
        else:
            num_weeds = scenario['weed_count']
        
        # Unkräuter generieren
        for i in range(num_weeds):
            detection = self._generate_single_weed(image, scenario, i + 1)
            if detection:
                detections.append(detection)
        
        return detections
    
    def _generate_single_weed(self, image, scenario, weed_id):
        """Einzelnes Unkraut generieren"""
        h, w = image.shape[:2]
        
        # Größe bestimmen
        if scenario['sizes']:
            size_range = random.choice(scenario['sizes'])
            width = random.randint(*size_range)
            height = random.randint(*size_range)
        else:
            width = random.randint(20, 60)
            height = random.randint(20, 60)
        
        # Position bestimmen (nicht zu nah am Rand)
        margin = max(width, height) // 2
        x = random.randint(margin, w - margin - width)
        y = random.randint(margin, h - margin - height)
        
        # Confidence bestimmen
        conf_min, conf_max = scenario['confidence_range']
        base_confidence = random.uniform(conf_min, conf_max)
        
        # Confidence basierend auf Größe anpassen
        optimal_size = 40
        size_factor = 1.0 - abs(width - optimal_size) / optimal_size * 0.2
        confidence = base_confidence * max(0.5, size_factor)
        
        # Unkraut-Typ basierend auf Größe und Form
        aspect_ratio = height / width
        if width > 60:
            weed_type = 'large_weed'
        elif aspect_ratio > 1.5:
            weed_type = 'tall_weed'
        elif aspect_ratio < 0.7:
            weed_type = 'wide_weed'
        else:
            weed_type = 'common_weed'
        
        # Zusätzliche realistische Eigenschaften
        area = width * height
        perimeter = 2 * (width + height)
        circularity = (4 * np.pi * area) / (perimeter ** 2)
        
        detection = {
            'class': 'weed',
            'subclass': weed_type,
            'confidence': round(confidence, 3),
            'bbox': {'x': x, 'y': y, 'width': width, 'height': height},
            'center': {'x': x + width//2, 'y': y + height//2},
            'area': area,
            'circularity': round(circularity, 3),
            'aspect_ratio': round(aspect_ratio, 3),
            'perimeter': round(perimeter, 1),
            'x': x + width//2,
            'y': y + height//2,
            'id': weed_id,
            'mock': True,
            'generated_at': datetime.now().isoformat()
        }
        
        return detection
    
    def _update_stats(self, detections):
        """Statistiken aktualisieren"""
        self.stats['total_detections'] += 1
        self.stats['total_weeds_found'] += len(detections)
        
        if detections:
            confidences = [d['confidence'] for d in detections]
            avg_conf = sum(confidences) / len(confidences)
            
            # Gleitender Durchschnitt
            current_avg = self.stats['average_confidence']
            self.stats['average_confidence'] = (current_avg + avg_conf) / 2
    
    def _calculate_average_confidence(self, detections):
        """Durchschnittliche Confidence berechnen"""
        if not detections:
            return 0.0
        
        total_confidence = sum(d['confidence'] for d in detections)
        return round(total_confidence / len(detections), 3)
    
    def create_mock_image(self, width=640, height=480, scenario_name=None):
        """Mock-Bild mit simulierten Unkräutern erstellen"""
        # Basis-Bild (Gras-Textur)
        image = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Gras-Hintergrund
        image[:, :] = [34, 139, 34]  # Waldgrün
        
        # Textur hinzufügen
        noise = np.random.randint(-20, 20, (height, width, 3))
        image = np.clip(image.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        
        # Wenn Szenario angegeben, Unkräuter hinzufügen
        if scenario_name and scenario_name in self.scenarios:
            scenario = self.scenarios[scenario_name]
            
            # Unkräuter als grüne Kreise/Ellipsen zeichnen
            if scenario['weed_count'] > 0:
                if isinstance(scenario['weed_count'], tuple):
                    num_weeds = random.randint(*scenario['weed_count'])
                else:
                    num_weeds = scenario['weed_count']
                
                for _ in range(num_weeds):
                    # Zufällige Position und Größe
                    x = random.randint(50, width - 50)
                    y = random.randint(50, height - 50)
                    
                    if scenario['sizes']:
                        size_range = random.choice(scenario['sizes'])
                        radius = random.randint(size_range[0]//2, size_range[1]//2)
                    else:
                        radius = random.randint(15, 40)
                    
                    # Unkraut-Farbe (helleres Grün)
                    weed_color = (50, 205, 50)  # Gelbgrün
                    
                    # Unkraut zeichnen
                    cv2.circle(image, (x, y), radius, weed_color, -1)
                    
                    # Leichte Unregelmäßigkeit
                    for _ in range(3):
                        offset_x = random.randint(-radius//2, radius//2)
                        offset_y = random.randint(-radius//2, radius//2)
                        small_radius = random.randint(5, radius//2)
                        cv2.circle(image, (x + offset_x, y + offset_y), small_radius, weed_color, -1)
        
        return image
    
    def run_scenario_test(self, scenario_name, num_tests=5):
        """Vollständiger Test für ein Szenario"""
        print(f"\n🧪 Starte Szenario-Test: {scenario_name}")
        print("=" * 50)
        
        # Szenario setzen
        self.set_scenario(scenario_name)
        
        results = []
        for i in range(num_tests):
            # Mock-Bild erstellen
            test_image = self.create_mock_image(scenario_name=scenario_name)
            
            # Erkennung durchführen
            result = self.detect_in_image(test_image)
            results.append(result)
            
            # Ergebnis ausgeben
            print(f"Test {i+1}: {result['count']} Unkräuter, Konfidenz: {result['confidence']:.3f}")
        
        # Zusammenfassung
        total_detections = sum(r['count'] for r in results)
        avg_confidence = sum(r['confidence'] for r in results) / len(results)
        avg_processing_time = sum(r['processing_time'] for r in results) / len(results)
        
        print(f"\n📊 Zusammenfassung ({num_tests} Tests):")
        print(f"   Durchschnittliche Erkennungen: {total_detections / num_tests:.1f}")
        print(f"   Durchschnittliche Konfidenz: {avg_confidence:.3f}")
        print(f"   Durchschnittliche Verarbeitungszeit: {avg_processing_time:.3f}s")
        
        return results
    
    def run_all_scenarios(self):
        """Alle Szenarien testen"""
        print("🚀 Starte alle Szenario-Tests")
        print("=" * 60)
        
        all_results = {}
        for scenario_name in self.scenarios.keys():
            results = self.run_scenario_test(scenario_name, num_tests=3)
            all_results[scenario_name] = results
        
        # Gesamtstatistiken
        print(f"\n📈 Gesamtstatistiken:")
        print(f"   Gesamte Erkennungen: {self.stats['total_detections']}")
        print(f"   Gefundene Unkräuter: {self.stats['total_weeds_found']}")
        print(f"   Durchschnittliche Konfidenz: {self.stats['average_confidence']:.3f}")
        print(f"   Session-Dauer: {datetime.now() - self.stats['session_start']}")
        
        return all_results
    
    def export_test_results(self, filename=None):
        """Test-Ergebnisse exportieren"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"unkraut/test/mock_results_{timestamp}.json"
        
        export_data = {
            'test_info': {
                'timestamp': datetime.now().isoformat(),
                'scenario_mode': self.scenario_mode,
                'total_detections': self.detection_count
            },
            'scenarios': self.scenarios,
            'stats': self.stats,
            'available_scenarios': list(self.scenarios.keys())
        }
        
        # Datei erstellen
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"💾 Test-Ergebnisse exportiert: {filename}")
        return filename

# Convenience-Funktionen für schnelle Tests
def quick_test():
    """Schneller Test aller Grundfunktionen"""
    detector = MockWeedDetector()
    
    # Verschiedene Szenarien testen
    scenarios = ['empty_field', 'light_infestation', 'heavy_infestation']
    
    for scenario in scenarios:
        print(f"\n🎯 Teste {scenario}...")
        detector.set_scenario(scenario)
        
        # Mock-Bild erstellen und testen
        image = detector.create_mock_image(scenario_name=scenario)
        result = detector.detect_in_image(image)
        
        print(f"   Ergebnis: {result['count']} Unkräuter, Konfidenz: {result['confidence']:.3f}")

def performance_test():
    """Performance-Test mit vielen Erkennungen"""
    detector = MockWeedDetector()
    detector.set_scenario('heavy_infestation')
    
    print("⚡ Performance-Test (100 Erkennungen)...")
    
    start_time = time.time()
    for i in range(100):
        image = detector.create_mock_image(scenario_name='heavy_infestation')
        detector.detect_in_image(image)
        
        if (i + 1) % 20 == 0:
            print(f"   {i + 1}/100 Erkennungen verarbeitet...")
    
    total_time = time.time() - start_time
    print(f"✅ Performance-Test abgeschlossen:")
    print(f"   100 Erkennungen in {total_time:.2f}s")
    print(f"   Durchschnitt: {total_time/100*1000:.1f}ms pro Erkennung")

if __name__ == "__main__":
    print("🎭 Mock-Weed-Detector Test-Suite")
    print("=" * 40)
    
    # Verschiedene Tests ausführen
    print("\n1. Schnelltest...")
    quick_test()
    
    print("\n2. Performance-Test...")
    performance_test()
    
    print("\n3. Alle Szenarien testen...")
    detector = MockWeedDetector()
    detector.run_all_scenarios()
    
    print("\n✅ Alle Tests abgeschlossen!")
