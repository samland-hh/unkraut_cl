# unkraut/test/direct_hsv_analysis.py
"""
Direkte HSV-Analyse der Test-Bilder und Live-Anpassung der Filter
"""
import cv2
import numpy as np
import os
import sys

# Pfad-Setup
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

def analyze_actual_image_colors(image_path):
    """Analysiert die tatsächlichen Farben in einem Bild"""
    print(f"\n🔍 Direkte HSV-Analyse: {os.path.basename(image_path)}")
    print("=" * 60)
    
    # Bild laden
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ Bild nicht gefunden: {image_path}")
        return None, None
    
    # Zu HSV konvertieren
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, w = image.shape[:2]
    
    print(f"📊 Bild-Größe: {w}x{h}")
    
    # Finde alle einzigartigen Farben
    unique_colors_bgr = {}
    unique_colors_hsv = {}
    
    # Sample verschiedene Bereiche
    sample_points = [
        (w//4, h//4),     # Links oben
        (3*w//4, h//4),   # Rechts oben  
        (w//2, h//2),     # Mitte
        (w//4, 3*h//4),   # Links unten
        (3*w//4, 3*h//4)  # Rechts unten
    ]
    
    print(f"\n🎨 Farb-Samples:")
    for i, (x, y) in enumerate(sample_points):
        if 0 <= x < w and 0 <= y < h:
            bgr = image[y, x]
            hsv_val = hsv[y, x]
            
            print(f"   Point {i+1} ({x:3}, {y:3}): BGR{tuple(bgr)} → HSV{tuple(hsv_val)}")
    
    # Analysiere Grün-Bereiche systematisch
    print(f"\n🔬 Grün-Bereich-Analyse:")
    
    # Finde hellere Bereiche (potentielle Unkräuter)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    mean_brightness = gray.mean()
    bright_mask = gray > (mean_brightness + 10)  # Hellere Bereiche
    
    # HSV-Werte der hellen Bereiche
    bright_hsv_pixels = hsv[bright_mask]
    
    if len(bright_hsv_pixels) > 0:
        h_values = bright_hsv_pixels[:, 0]
        s_values = bright_hsv_pixels[:, 1] 
        v_values = bright_hsv_pixels[:, 2]
        
        print(f"   Helle Bereiche (potentielle Unkräuter):")
        print(f"   H (Hue):        {h_values.min():3} - {h_values.max():3} (Ø{h_values.mean():.1f})")
        print(f"   S (Saturation): {s_values.min():3} - {s_values.max():3} (Ø{s_values.mean():.1f})")
        print(f"   V (Value):      {v_values.min():3} - {v_values.max():3} (Ø{v_values.mean():.1f})")
        
        # Optimale HSV-Bereiche berechnen
        h_margin = 10
        s_margin = 30
        v_margin = 40
        
        optimal_lower = np.array([
            max(0, h_values.min() - h_margin),
            max(0, s_values.min() - s_margin), 
            max(0, v_values.min() - v_margin)
        ])
        
        optimal_upper = np.array([
            min(179, h_values.max() + h_margin),
            min(255, s_values.max() + s_margin),
            min(255, v_values.max() + v_margin)
        ])
        
        print(f"\n💡 Optimale HSV-Bereiche für dieses Bild:")
        print(f"   Lower: np.array({optimal_lower})")
        print(f"   Upper: np.array({optimal_upper})")
        
        return optimal_lower, optimal_upper
    else:
        print(f"   ❌ Keine hellen Bereiche gefunden")
        return None, None

def test_hsv_range_on_image(image_path, lower_hsv, upper_hsv):
    """Testet einen HSV-Bereich auf einem Bild"""
    print(f"\n🧪 Teste HSV-Bereich: {lower_hsv} - {upper_hsv}")
    
    image = cv2.imread(image_path)
    if image is None:
        return False
    
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_hsv, upper_hsv)
    
    # Pixel zählen
    total_pixels = image.shape[0] * image.shape[1]
    green_pixels = cv2.countNonZero(mask)
    percentage = (green_pixels / total_pixels) * 100
    
    print(f"   Gefilterte Pixel: {green_pixels} ({percentage:.1f}%)")
    
    # Konturen finden
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    large_contours = [c for c in contours if cv2.contourArea(c) > 200]
    
    print(f"   Konturen: {len(contours)} total, {len(large_contours)} groß (>200px²)")
    
    # Visualisierung speichern
    result_image = image.copy()
    cv2.drawContours(result_image, large_contours, -1, (0, 0, 255), 2)
    
    output_path = image_path.replace('.jpg', '_hsv_test.jpg')
    cv2.imwrite(output_path, result_image)
    print(f"   💾 Test-Ergebnis: {os.path.basename(output_path)}")
    
    return len(large_contours) > 0

def create_guaranteed_test_image():
    """Erstellt ein Test-Bild mit garantiert erkennbaren Unkräutern"""
    print(f"\n🎨 Erstelle garantiert erkennbares Test-Bild...")
    
    # 640x480 Bild
    image = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Sehr dunkler Hintergrund
    image[:, :] = [15, 60, 15]  # Sehr dunkles Grün (BGR)
    
    # Unkräuter mit klarem Kontrast
    weed_data = [
        # (x, y, radius, BGR-Color)
        (150, 200, 35, [30, 120, 30]),   # Etwas heller
        (400, 150, 28, [40, 140, 40]),   # Noch heller
        (500, 350, 42, [50, 160, 50]),   # Deutlich heller
        (200, 380, 30, [25, 100, 25]),   # Leicht heller
        (320, 120, 25, [45, 150, 45])    # Sehr hell
    ]
    
    print(f"   Unkraut-Farben (BGR):")
    for i, (x, y, radius, color) in enumerate(weed_data):
        cv2.circle(image, (x, y), radius, color, -1)
        
        # Konvertiere zu HSV für Anzeige
        color_bgr = np.uint8([[color]])
        color_hsv = cv2.cvtColor(color_bgr, cv2.COLOR_BGR2HSV)[0][0]
        
        print(f"     Unkraut {i+1}: BGR{color} → HSV{tuple(color_hsv)}")
        
        # Kleine Satelliten
        for j in range(2):
            offset_x = np.random.randint(-radius//3, radius//3)
            offset_y = np.random.randint(-radius//3, radius//3)
            small_radius = radius // 4
            cv2.circle(image, (x + offset_x, y + offset_y), small_radius, color, -1)
    
    # Speichern
    output_path = "test/output/guaranteed_test_image.jpg"
    cv2.imwrite(output_path, image)
    print(f"   💾 Gespeichert: {output_path}")
    
    # HSV-Bereich berechnen
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Alle nicht-schwarzen Bereiche analysieren
    non_bg_mask = cv2.inRange(hsv, np.array([0, 0, 20]), np.array([179, 255, 255]))
    non_bg_pixels = hsv[non_bg_mask > 0]
    
    if len(non_bg_pixels) > 0:
        h_vals = non_bg_pixels[:, 0]
        s_vals = non_bg_pixels[:, 1]
        v_vals = non_bg_pixels[:, 2]
        
        # Toleranter Bereich
        guaranteed_lower = np.array([
            max(0, h_vals.min() - 5),
            max(0, s_vals.min() - 20),
            max(0, v_vals.min() - 20)
        ])
        
        guaranteed_upper = np.array([
            min(179, h_vals.max() + 5),
            min(255, s_vals.max() + 20), 
            min(255, v_vals.max() + 20)
        ])
        
        print(f"\n💡 Garantierte HSV-Werte:")
        print(f"   Lower: np.array({guaranteed_lower})")
        print(f"   Upper: np.array({guaranteed_upper})")
        
        return output_path, guaranteed_lower, guaranteed_upper
    
    return output_path, None, None

def update_weed_detector_live(lower_hsv, upper_hsv):
    """Aktualisiert den WeedDetector mit neuen HSV-Werten"""
    print(f"\n🔄 Aktualisiere WeedDetector mit neuen HSV-Werten...")
    
    try:
        from ai.weed_detection import weed_detector
        
        # Neues Profil hinzufügen
        weed_detector.green_profiles['live_optimized'] = {
            'lower': lower_hsv,
            'upper': upper_hsv,
            'name': 'Live-optimiert'
        }
        
        # Profil wechseln
        weed_detector.current_profile = 'live_optimized'
        
        print(f"   ✅ HSV-Profil aktualisiert:")
        print(f"   Lower: {lower_hsv}")
        print(f"   Upper: {upper_hsv}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Update fehlgeschlagen: {e}")
        return False

def main():
    """Hauptfunktion - Direkte HSV-Optimierung"""
    print("🎯 Direkte HSV-Optimierung für OpenCV-Erkennung")
    print("=" * 70)
    
    # 1. Analysiere existierende Test-Bilder
    test_images = [
        "test/output/test_light_infestation.jpg",
        "test/output/test_heavy_infestation.jpg"
    ]
    
    optimal_ranges = []
    
    for image_path in test_images:
        if os.path.exists(image_path):
            lower, upper = analyze_actual_image_colors(image_path)
            if lower is not None:
                optimal_ranges.append((lower, upper))
                
                # Teste den Bereich
                test_hsv_range_on_image(image_path, lower, upper)
    
    # 2. Erstelle garantiert funktionierendes Test-Bild
    guaranteed_image, guaranteed_lower, guaranteed_upper = create_guaranteed_test_image()
    
    if guaranteed_lower is not None:
        # Teste garantierte Werte
        test_hsv_range_on_image(guaranteed_image, guaranteed_lower, guaranteed_upper)
        
        # Aktualisiere WeedDetector
        if update_weed_detector_live(guaranteed_lower, guaranteed_upper):
            print(f"\n🧪 Teste aktualisierte Erkennung...")
            
            # Test mit aktualisierten Werten
            try:
                from ai.weed_detection import weed_detector
                
                image = cv2.imread(guaranteed_image)
                weed_detector.debug_mode = True
                result = weed_detector.detect_in_image(image)
                
                print(f"   📊 Ergebnis:")
                print(f"   Erkennungen: {result.get('count', 0)}")
                print(f"   Methode: {result.get('method', 'unknown')}")
                print(f"   Konfidenz: {result.get('confidence', 0):.3f}")
                
                # Ergebnis speichern
                if result.get('count', 0) > 0:
                    detections = result.get('detections', [])
                    marked_image = weed_detector.draw_detections(image, detections)
                    result_path = guaranteed_image.replace('.jpg', '_live_result.jpg')
                    cv2.imwrite(result_path, marked_image)
                    print(f"   💾 Live-Ergebnis: {os.path.basename(result_path)}")
                
            except Exception as e:
                print(f"   ❌ Live-Test fehlgeschlagen: {e}")
    
    # 3. Empfehlungen
    print(f"\n💡 Empfehlungen:")
    print("=" * 70)
    
    if optimal_ranges:
        # Berechne durchschnittliche optimale Werte
        avg_lower = np.mean([lower for lower, upper in optimal_ranges], axis=0).astype(int)
        avg_upper = np.mean([upper for lower, upper in optimal_ranges], axis=0).astype(int)
        
        print(f"1. Verwende diese HSV-Werte in ai/weed_detection.py:")
        print(f"   'optimized': {{")
        print(f"       'lower': np.array({avg_lower}),")
        print(f"       'upper': np.array({avg_upper}),")
        print(f"       'name': 'Direkt analysiert'")
        print(f"   }}")
    
    if guaranteed_lower is not None:
        print(f"\n2. Oder verwende die garantierten Werte:")
        print(f"   'guaranteed': {{")
        print(f"       'lower': np.array({guaranteed_lower}),")
        print(f"       'upper': np.array({guaranteed_upper}),")
        print(f"       'name': 'Garantiert funktionierend'")
        print(f"   }}")
    
    print(f"\n📁 Alle Test-Ergebnisse in: test/output/*_hsv_test.jpg")
    print(f"🔍 Schaue dir die Bilder an um zu sehen welche HSV-Bereiche funktionieren!")

if __name__ == "__main__":
    main()
