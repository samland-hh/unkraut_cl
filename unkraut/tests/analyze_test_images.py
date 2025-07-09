# unkraut/test/analyze_test_images.py
"""
Analysiert die generierten Test-Bilder und zeigt warum keine Unkräuter erkannt werden
"""
import cv2
import numpy as np
import os
import sys
import glob

# Pfad-Setup
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

def analyze_image_colors(image_path):
    """Analysiert Farben in einem Bild"""
    print(f"\n🔍 Analysiere: {os.path.basename(image_path)}")
    print("=" * 60)
    
    # Bild laden
    image = cv2.imread(image_path)
    if image is None:
        print("❌ Bild konnte nicht geladen werden")
        return
    
    h, w = image.shape[:2]
    print(f"📊 Bild-Größe: {w}x{h}")
    
    # Zu HSV konvertieren
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Aktuelle WeedDetector HSV-Werte
    current_lower = np.array([25, 40, 40])
    current_upper = np.array([95, 255, 255])
    
    print(f"\n🎨 Aktuelle HSV-Filter:")
    print(f"   Lower: {current_lower}")
    print(f"   Upper: {current_upper}")
    
    # Test mit aktuellen Werten
    current_mask = cv2.inRange(hsv, current_lower, current_upper)
    current_pixels = cv2.countNonZero(current_mask)
    current_percentage = (current_pixels / (w * h)) * 100
    
    print(f"   Gefilterte Pixel: {current_pixels} ({current_percentage:.1f}%)")
    
    # Konturen mit aktuellen Werten
    contours, _ = cv2.findContours(current_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    large_contours = []
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 300:  # Mindestgröße
            large_contours.append((contour, area))
    
    print(f"   Konturen gesamt: {len(contours)}")
    print(f"   Große Konturen (>300px²): {len(large_contours)}")
    
    # Farbverteilung analysieren
    print(f"\n📈 Farbverteilung (HSV):")
    h_channel = hsv[:, :, 0]
    s_channel = hsv[:, :, 1]
    v_channel = hsv[:, :, 2]
    
    print(f"   Hue (H):        {h_channel.min():3} - {h_channel.max():3} (Ø{h_channel.mean():.1f})")
    print(f"   Saturation (S): {s_channel.min():3} - {s_channel.max():3} (Ø{s_channel.mean():.1f})")
    print(f"   Value (V):      {v_channel.min():3} - {v_channel.max():3} (Ø{v_channel.mean():.1f})")
    
    # Verschiedene Grün-Bereiche testen
    print(f"\n🧪 Teste verschiedene Grün-Bereiche:")
    
    test_ranges = {
        'sehr_weit': (np.array([15, 20, 20]), np.array([105, 255, 255])),
        'weit': (np.array([20, 30, 30]), np.array([100, 255, 255])),
        'standard': (np.array([25, 40, 40]), np.array([95, 255, 255])),
        'eng': (np.array([35, 50, 50]), np.array([85, 255, 255])),
        'sehr_eng': (np.array([45, 60, 60]), np.array([75, 255, 255]))
    }
    
    best_range = None
    best_count = 0
    
    for name, (lower, upper) in test_ranges.items():
        mask = cv2.inRange(hsv, lower, upper)
        pixels = cv2.countNonZero(mask)
        percentage = (pixels / (w * h)) * 100
        
        # Konturen zählen
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        large_contours_count = len([c for c in contours if cv2.contourArea(c) > 300])
        
        print(f"   {name:10}: {pixels:6} Pixel ({percentage:5.1f}%) → {large_contours_count} große Konturen")
        
        if large_contours_count > best_count:
            best_count = large_contours_count
            best_range = (name, lower, upper)
    
    if best_range:
        name, lower, upper = best_range
        print(f"\n💡 Bester Bereich: {name}")
        print(f"   Lower: {lower}")
        print(f"   Upper: {upper}")
        print(f"   Erkennungen: {best_count}")
        
        return lower, upper
    
    return None, None

def create_improved_test_image():
    """Erstellt ein Test-Bild mit besseren Grün-Werten"""
    print(f"\n🎨 Erstelle verbessertes Test-Bild...")
    
    # 640x480 Bild
    image = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Dunkler Hintergrund (BGR)
    image[:, :] = [20, 80, 20]  # Sehr dunkles Grün
    
    # Unkraut-Positionen mit verschiedenen Grün-Tönen
    weed_data = [
        # (x, y, radius, BGR-Color)
        (150, 200, 35, [40, 160, 40]),   # Mittelgrün
        (400, 150, 28, [50, 180, 50]),   # Hellgrün
        (500, 350, 42, [60, 200, 60]),   # Sehr hell
        (200, 380, 30, [35, 140, 35]),   # Dunkler
        (320, 120, 25, [55, 190, 55])    # Gelbgrün
    ]
    
    print(f"   Unkraut-Positionen:")
    for i, (x, y, radius, color) in enumerate(weed_data):
        cv2.circle(image, (x, y), radius, color, -1)
        
        # Kleine Satelliten-Unkräuter
        for j in range(3):
            offset_x = np.random.randint(-radius//2, radius//2)
            offset_y = np.random.randint(-radius//2, radius//2)
            small_radius = np.random.randint(5, radius//3)
            cv2.circle(image, (x + offset_x, y + offset_y), small_radius, color, -1)
        
        print(f"     Unkraut {i+1}: ({x}, {y}), Radius {radius}, BGR {color}")
    
    # Speichern
    output_path = "test/output/debug_test_image.jpg"
    cv2.imwrite(output_path, image)
    print(f"   💾 Gespeichert: {output_path}")
    
    return output_path

def test_opencv_detection_on_image(image_path):
    """Testet OpenCV-Erkennung auf einem Bild"""
    print(f"\n🧪 Teste OpenCV-Erkennung auf: {os.path.basename(image_path)}")
    print("=" * 60)
    
    try:
        from ai.weed_detection import WeedDetector
        detector = WeedDetector()
        detector.debug_mode = True  # Debug aktivieren
        
        # Bild laden
        image = cv2.imread(image_path)
        if image is None:
            print("❌ Bild konnte nicht geladen werden")
            return
        
        # Erkennung durchführen
        result = detector.detect_in_image(image)
        
        print(f"📊 Ergebnisse:")
        print(f"   Erkennungen: {result.get('count', 0)}")
        print(f"   Konfidenz: {result.get('confidence', 0):.3f}")
        print(f"   Methode: {result.get('method', 'unknown')}")
        print(f"   Zeit: {result.get('processing_time', 0):.3f}s")
        
        # Detaillierte Ergebnisse
        detections = result.get('detections', [])
        if detections:
            print(f"   Detaillierte Erkennungen:")
            for i, detection in enumerate(detections):
                print(f"     {i+1}. {detection.get('subclass', 'unknown')}: "
                      f"Konfidenz {detection.get('confidence', 0):.3f}, "
                      f"Position ({detection.get('x', 0)}, {detection.get('y', 0)}), "
                      f"Größe {detection.get('area', 0)}px²")
        else:
            print(f"   ❌ Keine Erkennungen!")
        
        # Ergebnis-Bild speichern
        if hasattr(detector, 'draw_detections'):
            marked_image = detector.draw_detections(image, detections)
            result_path = image_path.replace('.jpg', '_debug_result.jpg')
            cv2.imwrite(result_path, marked_image)
            print(f"   💾 Ergebnis: {result_path}")
        
        return result
        
    except Exception as e:
        print(f"❌ Fehler bei OpenCV-Test: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Hauptfunktion"""
    print("🔍 Unkraut-2025 - Test-Bilder Analyse")
    print("=" * 70)
    
    # Suche Test-Bilder
    test_dir = "test/output"
    if not os.path.exists(test_dir):
        print(f"❌ Verzeichnis {test_dir} nicht gefunden")
        return
    
    # Finde alle Test-Bilder
    test_images = glob.glob(os.path.join(test_dir, "test_*.jpg"))
    
    if not test_images:
        print(f"❌ Keine Test-Bilder in {test_dir} gefunden")
        return
    
    print(f"📁 Gefundene Test-Bilder: {len(test_images)}")
    
    # Analysiere jedes Bild
    optimal_ranges = {}
    
    for image_path in sorted(test_images):
        lower, upper = analyze_image_colors(image_path)
        if lower is not None:
            optimal_ranges[image_path] = (lower, upper)
        
        # Teste aktuelle OpenCV-Erkennung
        test_opencv_detection_on_image(image_path)
    
    # Erstelle verbessertes Test-Bild
    improved_image = create_improved_test_image()
    
    # Teste verbesserte Erkennung
    if improved_image:
        analyze_image_colors(improved_image)
        test_opencv_detection_on_image(improved_image)
    
    # Empfehlungen
    print(f"\n💡 Empfehlungen:")
    print(f"=" * 70)
    
    if optimal_ranges:
        # Durchschnittliche optimale Werte berechnen
        all_lowers = [lower for lower, upper in optimal_ranges.values()]
        all_uppers = [upper for lower, upper in optimal_ranges.values()]
        
        if all_lowers:
            avg_lower = np.mean(all_lowers, axis=0).astype(int)
            avg_upper = np.mean(all_uppers, axis=0).astype(int)
            
            print(f"1. Verbesserte HSV-Werte verwenden:")
            print(f"   Lower: np.array({avg_lower})")
            print(f"   Upper: np.array({avg_upper})")
            print(f"")
            print(f"2. In ai/weed_detection.py ändern:")
            print(f"   'mixed': {{")
            print(f"       'lower': np.array({avg_lower}),")
            print(f"       'upper': np.array({avg_upper}),")
            print(f"       'name': 'Optimiertes Grün'")
            print(f"   }}")
    
    print(f"")
    print(f"3. Confidence-Threshold senken (aktuell: 0.5):")
    print(f"   detector.confidence_threshold = 0.3")
    print(f"")
    print(f"4. Mindestgröße reduzieren (aktuell: 300px²):")
    print(f"   detector.min_area = 200")
    
    print(f"\n📁 Alle Ergebnisse in: {test_dir}")
    print(f"🔍 Schaue dir die *_debug_result.jpg Bilder an!")

if __name__ == "__main__":
    main()
