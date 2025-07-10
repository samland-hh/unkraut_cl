# unkraut/test/test_green_detection.py
"""
Test-Script für visuelle Grün-Erkennung
Lädt Bilder aus data/images und zeigt Erkennungen visuell
"""
import cv2
import numpy as np
import os
import sys
import time
from datetime import datetime

# Pfad-Setup für Imports
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

def setup_directories():
    """Erstelle notwendige Verzeichnisse"""
    os.makedirs("data/images", exist_ok=True)
    os.makedirs("data/images/results", exist_ok=True)
    os.makedirs("test", exist_ok=True)

def find_green_areas(image):
    """
    Findet grüne Bereiche im Bild (vereinfachte Version des KI-Moduls)
    """
    # BGR zu HSV konvertieren
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Grün-Bereich definieren (wie im KI-Modul)
    lower_green = np.array([35, 40, 40])
    upper_green = np.array([85, 255, 255])
    
    # Grün-Maske erstellen
    green_mask = cv2.inRange(hsv, lower_green, upper_green)
    
    # Morphological Operations für bessere Erkennung
    kernel = np.ones((5,5), np.uint8)
    green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_CLOSE, kernel)
    green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_OPEN, kernel)
    
    # Konturen finden
    contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    detections = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 500:  # Mindestgröße (wie im KI-Modul)
            # Bounding Box
            x, y, w, h = cv2.boundingRect(contour)
            
            # Zentrum berechnen
            center_x = x + w // 2
            center_y = y + h // 2
            
            # Confidence basierend auf Größe
            confidence = min(0.9, area / 5000)
            
            detection = {
                'bbox': {'x': x, 'y': y, 'width': w, 'height': h},
                'center': {'x': center_x, 'y': center_y},
                'area': int(area),
                'confidence': round(confidence, 2),
                'contour': contour
            }
            
            detections.append(detection)
    
    return detections, green_mask

def draw_detections(image, detections, green_mask):
    """
    Zeichnet Erkennungen auf das Bild
    """
    # Kopie des Originalbildes
    result_image = image.copy()
    
    # Grün-Maske als Overlay (transparent)
    overlay = image.copy()
    overlay[green_mask > 0] = [0, 255, 0]  # Grün markieren
    result_image = cv2.addWeighted(result_image, 0.7, overlay, 0.3, 0)
    
    for i, detection in enumerate(detections):
        bbox = detection['bbox']
        center = detection['center']
        confidence = detection['confidence']
        contour = detection['contour']
        
        # Bounding Box zeichnen (Rot)
        cv2.rectangle(result_image, 
                     (bbox['x'], bbox['y']), 
                     (bbox['x'] + bbox['width'], bbox['y'] + bbox['height']), 
                     (0, 0, 255), 2)
        
        # Kontur zeichnen (Blau)
        cv2.drawContours(result_image, [contour], -1, (255, 0, 0), 2)
        
        # Zentrum markieren (Gelb)
        cv2.circle(result_image, (center['x'], center['y']), 5, (0, 255, 255), -1)
        
        # Roboterarm-Koordinaten anzeigen
        cv2.circle(result_image, (center['x'], center['y']), 10, (0, 255, 255), 2)
        
        # Text mit Informationen
        label = f"#{i+1} ({center['x']},{center['y']}) {confidence:.2f}"
        cv2.putText(result_image, label, 
                   (bbox['x'], bbox['y'] - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        cv2.putText(result_image, label, 
                   (bbox['x'], bbox['y'] - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    
    # Statistiken oben links
    stats_text = f"Grüne Bereiche: {len(detections)}"
    cv2.putText(result_image, stats_text, (10, 30), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3)
    cv2.putText(result_image, stats_text, (10, 30), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    return result_image

def process_images():
    """
    Hauptfunktion: Verarbeitet alle Bilder
    """
    setup_directories()
    
    print("🌿 Grün-Erkennung Test-Script")
    print("=" * 40)
    
    # Bilder-Verzeichnis prüfen
    images_dir = "data/images"
    if not os.path.exists(images_dir):
        print(f"❌ Verzeichnis {images_dir} existiert nicht!")
        return
    
    # Alle Bilddateien finden
    image_files = []
    for filename in os.listdir(images_dir):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
            filepath = os.path.join(images_dir, filename)
            if os.path.isfile(filepath):
                image_files.append((filename, filepath))
    
    if not image_files:
        print(f"❌ Keine Bilder in {images_dir} gefunden!")
        print("💡 Lege Testbilder in data/images/ und führe das Script erneut aus")
        return
    
    print(f"📸 {len(image_files)} Bilder gefunden")
    print("")
    
    total_detections = 0
    processing_times = []
    
    for i, (filename, filepath) in enumerate(image_files):
        print(f"🔍 Verarbeite: {filename}")
        
        try:
            # Bild laden
            image = cv2.imread(filepath)
            if image is None:
                print(f"  ❌ Fehler beim Laden von {filename}")
                continue
            
            # Grün-Erkennung durchführen
            start_time = time.time()
            detections, green_mask = find_green_areas(image)
            processing_time = time.time() - start_time
            processing_times.append(processing_time)
            
            # Erkennungen visualisieren
            result_image = draw_detections(image, detections, green_mask)
            
            # Ergebnis speichern
            result_filename = f"result_{filename}"
            result_path = os.path.join("data/images/results", result_filename)
            cv2.imwrite(result_path, result_image)
            
            # Statistiken
            total_detections += len(detections)
            
            print(f"  ✅ {len(detections)} grüne Bereiche erkannt")
            print(f"  ⏱️ Verarbeitung: {processing_time:.3f}s")
            print(f"  💾 Ergebnis: {result_path}")
            
            # Detaillierte Ausgabe
            if detections:
                print("  📍 Roboterarm-Koordinaten:")
                for j, det in enumerate(detections):
                    center = det['center']
                    area = det['area']
                    conf = det['confidence']
                    print(f"    {j+1}. ({center['x']}, {center['y']}) - "
                          f"Fläche: {area}px² - Konfidenz: {conf:.2f}")
            
            print("")
            
        except Exception as e:
            print(f"  ❌ Fehler bei {filename}: {e}")
            continue
    
    # Zusammenfassung
    print("📊 Zusammenfassung:")
    print("=" * 20)
    print(f"📸 Bilder verarbeitet: {len(image_files)}")
    print(f"🌿 Grüne Bereiche gesamt: {total_detections}")
    print(f"📊 Durchschnitt pro Bild: {total_detections / len(image_files):.1f}")
    
    if processing_times:
        avg_time = sum(processing_times) / len(processing_times)
        print(f"⏱️ Durchschnittliche Verarbeitungszeit: {avg_time:.3f}s")
    
    print(f"💾 Ergebnisse gespeichert in: data/images/results/")
    print("")
    print("🎯 Legende der Ergebnisbilder:")
    print("   🟢 Grüne Bereiche: Transparentes Grün-Overlay")
    print("   🔴 Bounding-Boxes: Rote Rechtecke")
    print("   🔵 Konturen: Blaue Linien")
    print("   🟡 Zentrum/Roboterarm-Ziel: Gelbe Kreise")
    print("   📝 Labels: Koordinaten und Konfidenz")

if __name__ == "__main__":
    process_images()
